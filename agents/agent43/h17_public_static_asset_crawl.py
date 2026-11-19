"""Read-only crawl of public Noyes site pages and same-origin static assets.

No authentication, forms, /admin, or /api. Intended to discover whether the public
HTML itself references a preserved H-17 object or static source asset.
"""
from __future__ import annotations

import hashlib
import html.parser
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = "https://noyes-energy-group.pages.dev/"
SEEDS = [
    ROOT,
    urllib.parse.urljoin(ROOT, "company/"),
    urllib.parse.urljoin(ROOT, "expertise/"),
    urllib.parse.urljoin(ROOT, "projects/"),
    urllib.parse.urljoin(ROOT, "insights/"),
    urllib.parse.urljoin(ROOT, "contact/"),
    urllib.parse.urljoin(ROOT, "robots.txt"),
]
PUBLIC_PAGE_PATHS = {"/", "/company/", "/expertise/", "/projects/", "/insights/", "/contact/", "/robots.txt"}
STATIC_EXT = {
    ".js", ".mjs", ".css", ".json", ".txt", ".xml", ".svg", ".png", ".jpg", ".jpeg",
    ".webp", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".map", ".pdf"
}
KEYWORDS = [
    "h-17", "h17", "ir-261003", "ps-261003", "mug-stock", "caption", "emily",
    "esc-n", "rec8", "0417", "keeper", "incident"
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/141 Safari/537.36"


class Links(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        for key in ("href", "src"):
            value = d.get(key)
            if value:
                self.urls.append(value)


def allowed(url: str) -> bool:
    p = urllib.parse.urlparse(url)
    if p.scheme != "https" or p.netloc != "noyes-energy-group.pages.dev":
        return False
    path = p.path or "/"
    low = path.lower()
    if low.startswith("/admin") or low.startswith("/api"):
        return False
    if path in PUBLIC_PAGE_PATHS:
        return True
    ext = "." + low.rsplit(".", 1)[-1] if "." in low.rsplit("/", 1)[-1] else ""
    return ext in STATIC_EXT


def fetch(url: str) -> tuple[int, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read(8_000_000)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read(100_000)


queue = list(SEEDS)
seen: set[str] = set()
rows: list[dict[str, object]] = []

while queue and len(seen) < 120:
    url = urllib.parse.urldefrag(queue.pop(0))[0]
    if url in seen or not allowed(url):
        continue
    seen.add(url)
    try:
        status, ctype, data = fetch(url)
    except Exception as exc:
        rows.append({"url": url, "error": type(exc).__name__ + ": " + str(exc)})
        continue

    text = data.decode("utf-8", errors="ignore")
    low = text.lower()
    hits = sorted(k for k in KEYWORDS if k in low)
    row: dict[str, object] = {
        "url": url,
        "status": status,
        "content_type": ctype,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "hits": hits,
    }
    if hits:
        snippets = []
        for k in hits:
            pos = low.find(k)
            snippets.append(re.sub(r"\s+", " ", text[max(0, pos - 120):pos + 220]))
        row["snippets"] = snippets
    rows.append(row)

    if status == 200 and ("html" in ctype.lower() or url.endswith("/")):
        parser = Links()
        parser.feed(text)
        for raw in parser.urls:
            child = urllib.parse.urljoin(url, raw)
            if allowed(child) and child not in seen:
                queue.append(child)

for row in rows:
    print(json.dumps(row, sort_keys=True, ensure_ascii=True))

interesting = [r for r in rows if r.get("hits")]
print("SUMMARY", json.dumps({
    "seen": len(seen),
    "ok": sum(r.get("status") == 200 for r in rows),
    "interesting": len(interesting),
    "interesting_urls": [r["url"] for r in interesting],
}, sort_keys=True))

if any(any(k in r.get("hits", []) for k in ("h-17", "h17", "ir-261003", "ps-261003", "mug-stock", "emily", "esc-n", "rec8")) for r in interesting):
    print("TARGET_RELEVANT_PUBLIC_ASSET_FOUND")
