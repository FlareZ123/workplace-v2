"""Read only the published site.js and any source map it explicitly advertises."""
import hashlib
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

HOST = "https://noyes-energy-group.pages.dev"
SCRIPT = HOST + "/assets/site.js"
REF = re.compile(r"(?m)//[#@]\s*sourceMappingURL\s*=\s*([^\s]+)")
TOKENS = re.compile(r"(?i)h[- ]?17|ps-261003|esc[- ]?n|coupon|keeper|emily|caption|archive|recovery|incident")

def safe_url(parent, target):
    url = urljoin(parent, target)
    p = urlparse(url)
    assert p.scheme == "https" and p.netloc == urlparse(HOST).netloc
    assert not p.path.lower().startswith(("/admin", "/api/", "/login", "/signin", "/account"))
    return url

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "H17-public-original-map-audit/1.0"}), timeout=20) as r:
        assert r.status == 200 and safe_url(HOST, r.url) == r.url
        raw = r.read(4000001)
        assert len(raw) <= 4000000
        return raw, dict(r.headers.items())

def scan(raw, label):
    s = raw.decode("utf8", "replace")
    hits = list(TOKENS.finditer(s))
    print(label, "size", len(raw), "sha256", hashlib.sha256(raw).hexdigest(), "markers", len(hits), flush=True)
    for m in hits[:12]:
        print("SOURCE_MARKER", repr(s[max(0,m.start()-90):m.end()+100]), flush=True)

def main():
    assert REF.findall("//# sourceMappingURL=site.js.map") == ["site.js.map"]
    assert safe_url(SCRIPT, "site.js.map") == HOST + "/assets/site.js.map"
    print("SELF_TEST_PASS", flush=True)
    try:
        raw, headers = fetch(SCRIPT)
    except (HTTPError, URLError, OSError, ValueError, AssertionError) as e:
        print("SOURCE_UNAVAILABLE", type(e).__name__, str(e)[:160], flush=True)
        return
    scan(raw, "PUBLIC_JS")
    txt = raw.decode("utf8", "replace")
    refs = REF.findall(txt)
    refs.extend(headers.get(h) for h in ("SourceMap", "X-SourceMap") if headers.get(h))
    print("ADVERTISED_MAPS", refs, flush=True)
    for ref in sorted(set(refs))[:2]:
        try:
            url = safe_url(SCRIPT, ref)
            mapraw, _ = fetch(url)
            scan(mapraw, "PUBLIC_DECLARED_MAP " + url)
        except (HTTPError, URLError, OSError, ValueError, AssertionError) as e:
            print("MAP_UNAVAILABLE", type(e).__name__, str(e)[:160], flush=True)

if __name__ == "__main__":
    main()
