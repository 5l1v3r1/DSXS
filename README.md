Damn Small XSS Scanner (DSXS) is a fully functional XSS scanner (supporting GET and POST parameters) written in under 100 lines of code.

As of optional settings it supports HTTP proxy together with HTTP header values "User-Agent", "Referer" and "Cookie".

Some sample runs against LEGAL targets:

$ python dsxs.py
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1e
 by: Miroslav Stampar (http://unconciousmind.blogspot.com | @stamparm)

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

$ python dsxs.py -u http://zero.webappsecurity.com/login1.asp --data="login=test&password=test&graphicOption=minimum" --random-agent
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1e
 by: Miroslav Stampar (http://unconciousmind.blogspot.com | @stamparm)

* scanning POST parameter 'login'
 (i) POST parameter 'login' appears to be XSS vulnerable (">...<", outside tags, some filtering))
* scanning POST parameter 'password'
* scanning POST parameter 'graphicOption'

scan results: possible vulnerabilities found

$ python dsxs.py -u http://xss.progphp.com/xss8.html?input=1 --random-agent
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1e
 by: Miroslav Stampar (http://unconciousmind.blogspot.com | @stamparm)

* scanning GET parameter 'input'
 (i) GET parameter 'input' appears to be XSS vulnerable ("...", pure text response, no filtering))

scan results: possible vulnerabilities found

$ python dsxs.py -u http://xss.progphp.com/xss12.html --data="bar=secret&foo=test"
Damn Small XSS Scanner (DSXS) < 100 LOC (Lines of Code) #v0.1e
 by: Miroslav Stampar (http://unconciousmind.blogspot.com | @stamparm)

* scanning POST parameter 'bar'
* scanning POST parameter 'foo'
 (i) POST parameter 'foo' appears to be XSS vulnerable ("<.'...'.>", inside tag, inside single-quotes, some filtering))

scan results: possible vulnerabilities found

p.s. Python v2.6 or v2.7 is required for running this program