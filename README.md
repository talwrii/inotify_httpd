# inotify_httpd
Serve files over HTTP; immediately refresh browsers when the files change on disk.

This is achieved using  [Linux's inotify system calls](http://man7.org/linux/man-pages/man7/inotify.7.html), *JavaScript*, [WebSockets](https://www.w3.org/TR/websockets/), and an HTML [iframe](https://www.w3.org/wiki/HTML/Elements/iframe).

This tool requires Python 3 (but can happily coexist with Python 2). Requires Linux (or a system with `inotify` system calls).

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
* The browser's URLs are not updated when following links, due to the `iframe` wrapper
* Only tested with *Firefox*.
* The actions that cause refresh could be a lot more targeted: changing an unrelated but watched file may result in a browser refresh.

* There are no automated tests of behaviour.

# Alternatives and prior work

 * [Browsersync](https://www.browsersync.io/) is a nodejs framework that provides a similar utility. It provides a [command line utility](https://browsersync.io/docs/command-line#start) that has similar features: `browser-sync --server --files '.'`.
 * There are many browser extensions that will periodically refresh a web-page. These refreshes may create visual artefacts (unless some form of "render caching" is used) and one must trade-off the polling rate against responsiveness.
 * [bcat](https://rtomayko.github.io/bcat/) is a utility that can feed bash pipe-line output into the browser and refresh. This can result in a large number of open tabs and does not interact well with [multiple browser profiles](https://lifehacker.com/5481213/master-multiple-firefox-profiles-for-more-productive-browsing). Nevertheless, `while true; do inotifywait /tmp/file ; bcat /tmp/file; done` may be a good alternative to this tool.
* [This question on StackOverflow](https://stackoverflow.com/questions/1346716/how-do-i-make-firefox-auto-refresh-on-file-change) addresses a similar topic.
* [LiveJs](http://livejs.com/) is an in-code / bookmarklet solution that works by continually polling with [HEAD requests](https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html). This will dynamically apply *CSS*s.
* [reload](https://www.npmjs.com/package/reload) is an *NPM* command line program that supports [a very similar mode of execution](https://www.npmjs.com/package/reload#usage-for-command-line-application). This is achieved through filesystem polling by [executing a script called supervisor](https://github.com/petruisfan/node-supervisor). Depending on the poll rate this may result in delays or moderate resource usage.
