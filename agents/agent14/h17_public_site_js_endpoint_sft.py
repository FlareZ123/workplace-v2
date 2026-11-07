"""Read-only inspection of the explicitly published corporate site JavaScript.

Only GET /assets/site.js. Discovered paths are reported, never fetched.
Protected-looking routes are classified and never followed.
"""
import hashlib
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HOST = "https://noyes-energy-group.pages.dev"
SCRIPT = HOST + "/assets/site.js"
MAX_BYTES = 100_000
PROTECTED = ("/api", "/admin", "/login", "/signin", "/account")
ABS_URL = re.compile(r"""https?://[^\s"'<>\\)]+""", re.I)
PATH_LITERAL = re.compile(r"""(?P<q>['"])(?P<path>/(?:[A-Za-z0-9._~!$&'()*+,;=:@%-]+/?)+)(?P=q)""")
CALL = re.compile(r"""(?:fetch|XMLHttpRequest|axios\.(?:get|post)|window\.open|location\.(?:href|assign|replace))""", re.I)

def main():
    req = Request(SCRIPT, headers={"User-Agent": "H17-public-site-js-endpoint-screen/1.0"})
    try:
        with urlopen(req, timeout=20) as response:
            final = urlparse(response.geturl())
            assert response.status == 200
            assert final.scheme == "https" and final.netloc == urlparse(HOST).netloc
            raw = response.read(MAX_BYTES + 1)
            assert len(raw) <= MAX_BYTES
    except (HTTPError, URLError, OSError, AssertionError) as exc:
        print("SOURCE_UNAVAILABLE", type(exc).__name__, str(exc)[:200], flush=True)
        return
    text = raw.decode("utf-8", "replace")
    print("PUBLIC_JS", "bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest(), flush=True)
    urls = sorted(set(ABS_URL.findall(text)))
    paths = sorted(set(m.group("path") for m in PATH_LITERAL.finditer(text)))
    print("ABSOLUTE_URL_LITERALS", urls, flush=True)
    print("PATH_LITERALS", paths, flush=True)
    print("CALL_SITES", [text[max(0,m.start()-100):m.end()+160] for m in CALL.finditer(text)], flush=True)
    print("PROTECTED_REFERENCES_NOT_FETCHED", [p for p in paths if p.lower().startswith(PROTECTED)], flush=True)
    print("PUBLIC_STATIC_REFERENCES_NOT_FETCHED", [p for p in paths if not p.lower().startswith(PROTECTED)], flush=True)
    print("BEGIN_SITE_JS", flush=True)
    print(text, flush=True)
    print("END_SITE_JS", flush=True)

if __name__ == "__main__":
    main()
