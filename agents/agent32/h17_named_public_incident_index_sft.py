"""Read-only original-name recovery from the public host cited by BX25/08.

Derive HTTP path candidates strictly from the separately preserved retired-profile
file URI, preserving only its source filename and relative Records/INDEX suffix.
Never request administrative, sign-in, or API endpoints.
"""
import hashlib
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HOST = "https://noyes-energy-group.pages.dev"
EXPECTED_BOOKMARK_SHA256 = "b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096"
ORIGINAL_URI = "file:///R:/Records/INDEX/IR-261003-H17.txt"
CANDIDATES = (
    "/IR-261003-H17.txt",
    "/Records/INDEX/IR-261003-H17.txt",
    "/records/index/IR-261003-H17.txt",
)

def main():
    bookmarks = Path("resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html").read_bytes()
    assert hashlib.sha256(bookmarks).hexdigest() == EXPECTED_BOOKMARK_SHA256
    assert ORIGINAL_URI.encode() in bookmarks
    parsed = urlparse(ORIGINAL_URI)
    assert parsed.scheme == "file" and parsed.path.endswith("/Records/INDEX/IR-261003-H17.txt")
    assert len(CANDIDATES) == len(set(CANDIDATES))
    assert CANDIDATES[0] == "/" + Path(parsed.path).name
    print("ORIGINAL_BOOKMARK_PIN_PASS", flush=True)

    for path in CANDIDATES:
        assert path.startswith("/") and path.endswith(".txt")
        assert not path.lower().startswith(("/api/", "/admin", "/login", "/signin", "/account"))
        url = HOST + path
        try:
            with urlopen(Request(url, headers={"User-Agent": "H17-historical-public-document/1.0"}), timeout=15) as r:
                raw = r.read(200001)
                assert len(raw) <= 200000
                final = urlparse(r.url)
                assert final.scheme == "https" and final.netloc == urlparse(HOST).netloc
                assert not final.path.lower().startswith(("/api/", "/admin", "/login", "/signin", "/account"))
                print("PUBLIC_HTTP", path, r.status, "bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest(), flush=True)
                print("PUBLIC_TEXT_PREVIEW", raw[:12000].decode("utf-8", "replace"), flush=True)
        except HTTPError as e:
            print("PUBLIC_HTTP", path, e.code, flush=True)
        except (URLError, OSError, AssertionError, ValueError) as e:
            print("SOURCE_UNAVAILABLE", path, type(e).__name__, str(e)[:200], flush=True)

if __name__ == "__main__":
    main()
