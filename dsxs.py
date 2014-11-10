#!/usr/bin/env python

import cookielib, optparse, random, re, string, urllib2, urlparse

NAME    = "Damn Small XSS Scanner (DSXS) < 100 LoC (Lines of Code)"
VERSION = "0.1g"
AUTHOR  = "Miroslav Stampar (@stamparm)"
LICENSE = "Public domain (FREE)"

SMALLER_CHAR_POOL    = ('<', '>')                               # characters used for XSS tampering of parameter values (smaller set - for avoiding possible SQLi errors)
LARGER_CHAR_POOL     = ('\'', '"', '>', '<')                    # characters used for XSS tampering of parameter values (larger set)
GET, POST            = "GET", "POST"                            # enumerator-like values used for marking current phase
PREFIX_SUFFIX_LENGTH = 5                                        # length of random prefix/suffix used in XSS tampering
CONTEXT_DISPLAY_OFFSET = 10                                     # offset outside the affected context for displaying in vulnerability report
COOKIE, UA, REFERER = "Cookie", "User-Agent", "Referer"         # optional HTTP header names
REGEX_SPECIAL_CHARS = ('\\', '*', '.', '+', '[', ']', ')', '(') # characters reserved for regular expressions

XSS_PATTERNS = (                                                # each (pattern) item consists of ((context regex), (prerequisite unfiltered characters), "info text")
    (r'\A[^<>]*%(chars)s[^<>]*\Z', ('<', '>'), "\".xss.\", pure text response, %(filtering)s filtering"),
    (r"<script[^>]*>(?!.*<script).*'[^>']*%(chars)s[^>']*'.*</script>", ('\''), "\"<script>.'.xss.'.</script>\", enclosed by <script> tags, inside single-quotes, %(filtering)s filtering"),
    (r'<script[^>]*>(?!.*<script).*"[^>"]*%(chars)s[^>"]*".*</script>', ('"'), "'<script>.\".xss.\".</script>', enclosed by <script> tags, inside double-quotes, %(filtering)s filtering"),
    (r'<script[^>]*>(?!.*<script).*?%(chars)s.*?</script>', (), "\"<script>.xss.</script>\", enclosed by <script> tags, %s"),
    (r'>[^<]*%(chars)s[^<]*(<|\Z)', ('<', '>'), "\">.xss.<\", outside of tags, %(filtering)s filtering"),
    (r"<[^>]*'[^>']*%(chars)s[^>']*'[^>]*>", ('\'',), "\"<.'.xss.'.>\", inside the tag, inside single-quotes, %(filtering)s filtering"),
    (r'<[^>]*"[^>"]*%(chars)s[^>"]*"[^>]*>', ('"',), "'<.\".xss.\".>', inside the tag, inside double-quotes, %(filtering)s filtering"),
    (r'<[^>]*%(chars)s[^>]*>', (), "\"<.xss.>\", inside the tag, outside of quotes, %(filtering)s filtering")
)

USER_AGENTS = (                                                 # items used for picking random HTTP User-Agent header value
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_0; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:0.9.2) Gecko/20020508 Netscape6/6.1",
    "Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10"
)

_headers = {}                                                   # used for storing dictionary with optional header values

def _retrieve_content(url, data=None):
    try:
        req = urllib2.Request("".join(url[i].replace(' ', '%20') if i > url.find('?') else url[i] for i in xrange(len(url))), data, _headers)
        retval = urllib2.urlopen(req).read()
    except Exception, ex:
        retval = ex.read() if hasattr(ex, "read") else getattr(ex, "msg", str())
    return retval or ""

def scan_page(url, data=None):
    def _contains(content, chars):
        content = re.sub(r"\\[%s]" % re.escape("".join(chars)), "", content, re.S) if chars else content
        return all(char in content for char in chars)
    retval, usable = False, False
    try:
        for phase in (GET, POST):
            current = url if phase is GET else (data or "")
            for match in re.finditer(r"((\A|[?&])(?P<parameter>[\w\[\]]+)=)(?P<value>[^&]+)", current):
                found, usable = False, True
                print "* scanning %s parameter '%s'" % (phase, match.group("parameter"))
                prefix, suffix = ["".join(random.sample(string.ascii_lowercase, PREFIX_SUFFIX_LENGTH)) for i in xrange(2)]
                for pool in (LARGER_CHAR_POOL, SMALLER_CHAR_POOL):
                    if not found:
                        tampered = current.replace(match.group(0), "%s%s%s%s" % (match.group(1), prefix, "".join(random.sample(pool, len(pool))), suffix))
                        content = _retrieve_content(tampered, data) if phase is GET else _retrieve_content(url, tampered)
                        for sample in re.finditer("%s(.+?)%s" % (prefix, suffix), content, re.I|re.S):
                            for regex, condition, info in XSS_PATTERNS:
                                context = re.search(regex % dict((("chars", reduce(lambda filtered, char: filtered.replace(char, "\\%s" % char), REGEX_SPECIAL_CHARS, sample.group(0))),)), content, re.I|re.S)
                                if context and not found and sample.group(1).strip():
                                    if _contains(sample.group(1), condition):
                                        print " (i) %s parameter '%s' appears to be XSS vulnerable (%s)" % (phase, match.group("parameter"), info % dict((("filtering", "no" if all(char in sample.group(1) for char in LARGER_CHAR_POOL) else "some"),)))
                                        found = retval = True
                                    break
        if not usable:
            print " (x) no usable GET/POST parameters found"
    except KeyboardInterrupt:
        print "\r (x) Ctrl-C pressed"
    return retval

def init_options(proxy=None, cookie=None, ua=None, referer=None):
    global _headers
    _headers = dict(filter(lambda _: _[1], ((COOKIE, cookie), (UA, ua), (REFERER, referer))))
    urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': proxy})) if proxy else None)

if __name__ == "__main__":
    print "%s #v%s\n by: %s\n" % (NAME, VERSION, AUTHOR)
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-u", "--url", dest="url", help="Target URL (e.g. \"http://www.target.com/page.php?id=1\")")
    parser.add_option("--data", dest="data", help="POST data (e.g. \"query=test\")")
    parser.add_option("--cookie", dest="cookie", help="HTTP Cookie header value")
    parser.add_option("--user-agent", dest="ua", help="HTTP User-Agent header value")
    parser.add_option("--random-agent", dest="randomAgent", action="store_true", help="Use randomly selected HTTP User-Agent header value")
    parser.add_option("--referer", dest="referer", help="HTTP Referer header value")
    parser.add_option("--proxy", dest="proxy", help="HTTP proxy address (e.g. \"http://127.0.0.1:8080\")")
    options, _ = parser.parse_args()
    if options.url:
        init_options(options.proxy, options.cookie, options.ua if not options.randomAgent else random.choice(USER_AGENTS), options.referer)
        result = scan_page(options.url if options.url.startswith("http") else "http://%s" % options.url, options.data)
        print "\nscan results: %s vulnerabilities found" % ("possible" if result else "no")
    else:
        parser.print_help()
