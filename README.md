# inotify_httpd
Serve files over HTTP; immediately refresh browsers when the files change on disk.

This is achieved using  [Linux's inotify system calls](http://man7.org/linux/man-pages/man7/inotify.7.html), *JavaScript*, [WebSockets](https://www.w3.org/TR/websockets/), and an HTML [iframe](https://www.w3.org/wiki/HTML/Elements/iframe).

This tool requires Python 3 (but this can happily coexist with Python 2). Requires Linux (or a system with `inotify` system calls).

# Usage
```
# Serve a single file on port 10000
# ( a WebSocket port is opened on 10001)
inotify_httpd /tmp/file.html

# Serve a directory on port 10000
inotify_httpd /tmp/www

```

# Installation
```
# Ensure pip3 is install
sudo apt-get install python3-pip


# release version
pip3 install inotify_httpd

# latest development version
pip3 install git+https://github.com/talwrii/inotify_httpd#egg=inotify_http
```

# Caveats
* Content is served by a JavaScript wrapper, so may not interact very well with tools like curl.
* URLs are not updated due to the `iframe` wrapper
* Only tested with *Firefox*.
* The actions that cause refresh could be a lot more targeted: changing an unrelated but watched file may result in a browser refresh.

* There are no automated tests of behaviour.

# Alternatives and prior work

 * There are many browser extensions that will periodically refresh a web-page. These refreshes may create visual artefacts (unless some form of "render caching" is used) and one must trade-off the polling rate against responsiveness.
 * [bcat](https://rtomayko.github.io/bcat/) is a utility that can feed bash pipe-line output into the browser and refresh. This can result in a large number of open tabs and does not interact well with [multiple browser profiles](https://lifehacker.com/5481213/master-multiple-firefox-profiles-for-more-productive-browsing). Nevertheless, `while true; do inotifywait /tmp/file ; bcat /tmp/file; done` may be a good alternative to this tool
