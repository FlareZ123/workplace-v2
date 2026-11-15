"""Anonymous, read-only probes of exact local file bookmarks on the public company host.

The host is named in the preserved BX25/08 PDF; the paths are taken verbatim
from the separately preserved retired-office-bookmarks.html. This is only an
exploratory mirror hypothesis: a local file:// URI does not establish that the
same path exists on the public web host.

No credentials, cookies, login/API/admin paths, or guessed routes are used.
Successful responses are saved only in the CI workspace for short-lived review.
"""
import hashlib
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOST = "https://noyes-energy-group.pages.dev"
HOST_NETLOC = urlparse(HOST).netloc
BOOKMARKS_PATH = Path("resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html")
EXPECTED_BOOKMARK_SHA256 = "b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096"
ALREADY_PROBED = "/Records/INDEX/IR-261003-H17.txt"
MAX_BYTES = 5_000_000
TEXT_SUFFIXES = {".htm", ".html", ".txt"}

class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlparse(newurl)
        if target.scheme != "https" or target.netloc != HOST_NETLOC:
            raise HTTPError(req.full_url, code, "cross-host redirect refused", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(opener, path):
    assert path.startswith("/") and not path.startswith("//")
    assert ".." not in Path(path).parts
    assert not path.lower().startswith(("/api/", "/admin", "/login", "/signin", "/account"))
    url = HOST + quote(path, safe="/-._~")
    req = Request(url, headers={
        "User-Agent": "H17-historical-bookmark-probe/1.0",
        "Accept": "text/html,application/xhtml+xml,text/plain,application/octet-stream,*/*;q=0.5",
    })
    try:
        with opener.open(req, timeout=15) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                print("PUBLIC_OVERSIZE", path, response.status, "limit", MAX_BYTES, flush=True)
                return None, None
            final = urlparse(response.geturl())
            assert final.scheme == "https" and final.netloc == HOST_NETLOC
            content_type = response.headers.get("Content-Type", "")
            digest = hashlib.sha256(raw).hexdigest()
            print("PUBLIC_HTTP", path, response.status, "type", content_type,
                  "bytes", len(raw), "sha256", digest, flush=True)
            return raw, content_type
    except HTTPError as error:
        print("PUBLIC_HTTP", path, error.code, flush=True)
    except (URLError, OSError, AssertionError, ValueError) as error:
        print("SOURCE_UNAVAILABLE", path, type(error).__name__, str(error)[:200], flush=True)
    return None, None

def main():
    raw_bookmarks = BOOKMARKS_PATH.read_bytes()
    assert hashlib.sha256(raw_bookmarks).hexdigest() == EXPECTED_BOOKMARK_SHA256
    text = raw_bookmarks.decode("utf-8")
    relatives = re.findall(r'href="file:///R:/([^"]+)"', text, flags=re.I)
    paths = tuple("/" + value.replace("\\", "/") for value in relatives)
    assert len(paths) == 14 and len(paths) == len(set(paths))
    assert ALREADY_PROBED in paths
    # Exclude the previously tested incident-index locator; probe only the
    # other exact, source-named R: bookmark paths. No path expansion occurs.
    probes = tuple(path for path in paths if path != ALREADY_PROBED)
    assert len(probes) == 13
    assert all(path.startswith(("/Stores/", "/Finance/", "/Risk/", "/IT/", "/Records/")) for path in probes)
    print("BOOKMARK_SOURCE_PIN_PASS", EXPECTED_BOOKMARK_SHA256, "exact_paths", len(probes), flush=True)

    opener = build_opener(SameHostRedirect())
    root, _ = fetch(opener, "/")
    root_hash = hashlib.sha256(root).hexdigest() if root is not None else None
    print("PUBLIC_ROOT_SHA256", root_hash or "UNAVAILABLE", flush=True)

    saved = 0
    for path in probes:
        raw, content_type = fetch(opener, path)
        if raw is None:
            continue
        digest = hashlib.sha256(raw).hexdigest()
        if root_hash and digest == root_hash:
            print("SPA_OR_ROOT_FALLBACK", path, flush=True)
            continue
        dest = Path("public_bookmark_mirror") / path.lstrip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        saved += 1
        if Path(path).suffix.lower() in TEXT_SUFFIXES or "text/" in content_type.lower():
            print("PUBLIC_TEXT_PREVIEW", path, raw[:8000].decode("utf-8", "replace"), flush=True)
        else:
            print("PUBLIC_BINARY_SAVED", path, "bytes", len(raw), "sha256", digest, flush=True)
    print("PUBLIC_BOOKMARK_PROBE_COMPLETE", "responses_saved", saved, flush=True)

if __name__ == "__main__":
    main()
