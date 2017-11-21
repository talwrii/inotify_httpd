# inotify_httpd

Serve files over HTTP; immediately refresh browsers when the files change on disk.

This is achieved using  [Linux's inotify syscalls](http://man7.org/linux/man-pages/man7/inotify.7.html), *Javascript*, [WebSockets](https://www.w3.org/TR/websockets/), and an HTML [iframe](https://www.w3.org/wiki/HTML/Elements/iframe).

# Usage

```
# Serve a single file on port 10000
# ( a websocket port is opened on 10001)
inotify_httpd /tmp/file.html

# Serve a directory on port 10000
inotify_httpd /tmp/www

```

# Caveats

* Content is served by a wrapper so may not interact very well with tools like curl.

*
