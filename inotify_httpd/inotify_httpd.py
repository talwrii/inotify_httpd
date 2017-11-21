import argparse
import logging
import mimetypes
import os
import sys
import threading

if sys.version_info[0] != 3:
    # FileNotFoundError does not exist in python 2
    raise Exception('Only works with python 3')


from http.server import BaseHTTPRequestHandler, HTTPServer

import pyinotify
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

LOGGER = logging.getLogger()

def build_parser():
    parser = argparse.ArgumentParser(description='Serve files. Update on change.')
    parser.add_argument('--debug', action='store_true', help='Print debug output')
    parser.add_argument('file', type=str, help='Server this file')
    parser.add_argument('--port', type=int, help='Port', default=10000)
    return parser

def call_on_modify(func, files):
    wm = pyinotify.WatchManager()
    monitored_files = []
    files = [os.path.abspath(f) for f in files]
    class EventProcessor(pyinotify.ProcessEvent):
        def process_IN_MODIFY(self, event):
            LOGGER.debug('Modify event')
            func()

        def process_IN_CREATE(self, event):
            LOGGER.debug('Create event')
            if event.pathname in files:
                monitor(event.pathname)

            func()

        def process_IN_DELETE(self, event):
            LOGGER.debug('Delete event')
            func()


    def monitor(filename):
        nonlocal monitored_files
        LOGGER.debug('Monitoring %r', f)
        wm.add_watch(f, flags['IN_MODIFY'])
        monitored_files.append(f)

    notifier = pyinotify.AsyncNotifier(wm, EventProcessor())
    flags = pyinotify.EventsCodes.ALL_FLAGS

    for f in files:
        if os.path.exists(f):
            monitor(f)

        directory = os.path.dirname(f)
        if not os.path.isdir(f):
            wm.add_watch(directory, flags['IN_CREATE'] | flags['IN_DELETE'])

    return notifier.loop

class JustWaitWebSocket(WebSocket):
    def handleMessage(self):
        self.sendMessage('Does not handle messages. Sends an event message when something happens')

class WebSocketEvent:
    def __init__(self, event):
        self._event = event
        self._connections = []

    def make_handler(self, *args, **kwargs):
        result = JustWaitWebSocket(*args, **kwargs)
        self._connections.append(result)
        return result

    def run(self):
        while True:
            self._event.wait()
            # sets that happen here get bunched into a single call, but a set will
            # always result in an event to be fired after the set (but this might be shared)
            self._event.clear()
            for c in self._connections:
                c.sendMessage('event')

WRAPPER = '''
<html>
<head>
    <script>
var exampleSocket = new WebSocket("ws://localhost:{port}/ws", ["protocolOne", "protocolTwo"]);

exampleSocket.onmessage = function (event) {{
    /* console.log("refresh event") ; */
    var el = document.getElementsByTagName('iframe')[0];
    /* console.log("Refreshing" + el.src); */
    el.contentWindow.location.reload(true);
    /* el.src = el.src; */
}}
    </script>
</head>
<body>
<iframe src="/_content{path}" style="width:100%; height:100%; border:0; padding:0"/>
</body>
</html>
'''

def file_change_http_handler(socket_port, default_file, serve_dir):
    class S(BaseHTTPRequestHandler):

        def _set_headers(self):
            filesystem_path = self._get_filesystem_path(self.path)
            if filesystem_path is not None and os.path.exists(filesystem_path):
                no_file = False
                self.send_response(200)
            else:
                no_file = True
                self.send_response(404)

            mime_type = guess_mime(filesystem_path)[0] if filesystem_path is not None else 'text/html'
            LOGGER.debug('Mime type for %r -> %r is %r', self.path, filesystem_path, mime_type)
            self.send_header('Content-type', mime_type)
            self.end_headers()
            return no_file

        def do_GET(self):
            no_file = self._set_headers()
            filesystem_path = self._get_filesystem_path(self.path)
            if filesystem_path:
                if no_file:
                    self.wfile.write('404: FILE DOES NOT EXIST'.encode('utf8'))
                else:
                    with open(filesystem_path, 'rb') as stream:
                        self.wfile.write(stream.read())
            else:
                self.wfile.write(WRAPPER.replace('\n', '\r\n').format(port=socket_port, path=self.path).encode('utf8'))

        def _get_filesystem_path(self, path):
            if path.startswith('/_content/'):
                _, _, content_path = path.split('/', 2)
                if content_path == '':
                    return default_file
                else:
                    return os.path.join(serve_dir, content_path)
            else:
                return None


        def do_HEAD(self):
            self._set_headers()
    return S

def spawn(f, *args, **kwargs):
	thread = threading.Thread(target=f, args=args, kwargs=kwargs)
	thread.setDaemon(True)
	thread.start()
	return thread


class ThreadWaiter(object):
    def __init__(self):
        self._event = threading.Event()

    # waiter.spawn(func, *args, **kwargs)
    def spawn(self, func, *args, **kwargs):
        return spawn(self.wrap, func, *args, **kwargs)

    def wrap(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            LOGGER.debug('Func exited %r', func)
            self._event.set()

    def wait(self):
        self._event.wait()


def run(*, port, filename):
    server_address = ('', port)
    file_change_event = threading.Event()
    websocket_event = WebSocketEvent(file_change_event)
    webserver_port = port + 1
    websocket_server = SimpleWebSocketServer('', webserver_port, websocket_event.make_handler)

    if os.path.isdir(filename):
        default_filename = os.path.join(filename, 'index.html')
        root_dir = filename
    else:
        default_filename = filename
        root_dir = None

    httpd = HTTPServer(server_address, file_change_http_handler(webserver_port, default_filename, root_dir))

    waiter = ThreadWaiter()
    waiter.spawn(websocket_server.serveforever)
    waiter.spawn(httpd.serve_forever)
    waiter.spawn(websocket_event.run)
    waiter.spawn(call_on_modify(file_change_event.set, [filename]))

    waiter.wait()
    sys.exit()

def main():
    args = build_parser().parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    print('Serving on http://localhost:{}/'.format(args.port))
    run(port=args.port, filename=args.file)

def guess_mime(filename):
    return mimetypes.guess_type(filename)
