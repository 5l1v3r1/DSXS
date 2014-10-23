Damn Small XSS Scanner (DSXS) is a fully functional XSS scanner (supporting GET and POST parameters) written in under 100 lines of code.

As of optional settings it supports HTTP proxy together with HTTP header values "User-Agent", "Referer" and "Cookie".

```
$ python dsxs.py -h
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1g
 by: Miroslav Stampar (@stamparm)

Usage: dsxs.py [options]

Options:
  --version          show program's version number and exit
  -h, --help         show this help message and exit
  -u URL, --url=URL  Target URL (e.g. "http://www.target.com/page.htm?id=1")
  --data=DATA        POST data (e.g. "query=test")
  --cookie=COOKIE    HTTP Cookie header value
  --user-agent=UA    HTTP User-Agent header value
  --random-agent     Use randomly selected HTTP User-Agent header value
  --referer=REFERER  HTTP Referer header value
  --proxy=PROXY      HTTP proxy address (e.g. "http://127.0.0.1:8080")
```

```
$ python dsxs.py -u "http://testphp.vulnweb.com/search.php?test=query" --data="searchFor=foobar"
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1g
 by: Miroslav Stampar (@stamparm)

* scanning GET parameter 'test'
* scanning POST parameter 'searchFor'
 (i) POST parameter 'searchFor' appears to be XSS vulnerable (">.xss.<", outside of tags, no filtering)

scan results: possible vulnerabilities found
```

p.s. Python v2.6 or v2.7 is required for running this program
