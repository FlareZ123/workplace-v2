"""Bounded read-only audit of an explicitly declared public JavaScript source map."""
import hashlib
import json
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

BASE = "https://noyes-energy-group.pages.dev"
SCRIPT = BASE + "/assets/site.js"
DECL = re.compile(r"(?:#|@)\s*sourceMappingURL\s*=\s*([^\s*]+)")
TARGET = re.compile(r"(?i)\bh[\W_]?17\b|PS-261003|IR-261003|ESC[\W_]?N|\bEmily\b|\bkeeper\b|\bRECOVER\b|final.{0,25}margin")
UA = {"User-Agent": "Mozilla/5.0 (compatible; read-only H17 public-records audit)"}


def public_get(url, limit):
    parts = urlsplit(url)
    assert parts.scheme == "https" and parts.netloc == "noyes-energy-group.pages.dev"
    assert not parts.path.startswith(("/api", "/admin"))
    with urlopen(Request(url, headers=UA), timeout=12) as response:
        assert response.status == 200
        data = response.read(limit + 1)
    assert len(data) <= limit
    return data


def declared_map(script_text):
    directives = DECL.findall(script_text)
    if not directives:
        return None
    assert len(directives) == 1
    url = directives[0].strip("\"' ")
    assert not url.startswith("data:")
    url = urljoin(SCRIPT, url)
    parts = urlsplit(url)
    assert parts.scheme == "https" and parts.netloc == "noyes-energy-group.pages.dev"
    assert not parts.path.startswith(("/admin", "/api"))
    return url


def main():
    assert declared_map("x();\n//# sourceMappingURL=site.js.map\n") == BASE + "/assets/site.js.map"
    assert declared_map("x();\n") is None
    print("SYNTHETIC_DIRECTIVE_CONTROL PASS", flush=True)
    script = public_get(SCRIPT, 1000000)
    print("SOURCE_SCRIPT", len(script), hashlib.sha256(script).hexdigest(), flush=True)
    url = declared_map(script.decode("utf-8", "replace"))
    print("DECLARED_SOURCE_MAP", url or "NONE", flush=True)
    if not url:
        print("STOP: no public script-declared source map", flush=True)
        return
    raw = public_get(url, 2000000)
    print("MAP_SHA256", hashlib.sha256(raw).hexdigest(), flush=True)
    obj = json.loads(raw)
    assert obj["version"] == 3
    sources = obj.get("sources", [])
    content = obj.get("sourcesContent", [])
    assert len(sources) == len(content)
    print("ORIGINAL_SOURCE_ENTRIES", len(content), flush=True)
    hits = 0
    for i, (name, body) in enumerate(zip(sources, content)):
        if not isinstance(body, str):
            continue
        for match in list(TARGET.finditer(body))[:10]:
            hits += 1
            print("SOURCE_MARKER", i, name, repr(body[max(0, match.start()-90):match.end()+90]), flush=True)
    print("SOURCE_MARKERS", hits, flush=True)
    print("Any marker needs independent historic target attribution", flush=True)


if __name__ == "__main__":
    main()
