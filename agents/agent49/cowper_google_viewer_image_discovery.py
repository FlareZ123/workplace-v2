"""Inspect Google Books viewer HTML for signed page-image URLs; read-only."""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PART2_ID = "o7P-qis2u9IC"
VIEWER = f"https://books.google.es/books?hl=en&id={PART2_ID}&pg=PA130"
SEARCH_URLS = {
    "search_within_id": f"https://books.google.es/books?jscmd=SearchWithinVolume2&q=sea&id={PART2_ID}",
    "search_within_vid": f"https://books.google.es/books?jscmd=SearchWithinVolume2&q=sea&vid={PART2_ID}",
}

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = []
        self.links = []
        self.meta = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.imgs.append(a)
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "meta":
            self.meta.append(a)

def fetch(name, url):
    print(f"FETCH_START name={name} url={url}")
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
    })
    try:
        with urlopen(req, timeout=45) as resp:
            body = resp.read(5_000_001)
            ctype = resp.headers.get("Content-Type", "")
            status = resp.status
        rec = {"name": name, "status": status, "content_type": ctype, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "final_url": url}
        if "html" in ctype:
            html = body.decode("utf-8", "replace")
            parser = Tags()
            parser.feed(html)
            title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
            rec["title"] = re.sub(r"\\s+", " ", title.group(1)).strip() if title else None
            rec["img_tags"] = parser.imgs[:50]
            rec["image_links"] = [x for x in parser.links if "books/content" in x or "img=" in x or "sig=" in x][:100]
            rec["meta"] = [x for x in parser.meta if any(k in json.dumps(x).lower() for k in ("book", "image", "page", "volume"))][:50]
            for term in ("pageImage", "imageUrl", "imgUrl", "sig=", "books/content", "pageImageUrl", "page_image"):
                matches = list(re.finditer(re.escape(term), html, re.I))
                if matches:
                    rec[term] = [html[max(0,m.start()-180):m.start()+500] for m in matches[:5]]
        else:
            rec["body_preview"] = body[:4000].decode("utf-8", "replace")
        print("FETCH_RESULT " + json.dumps(rec, ensure_ascii=False, sort_keys=True))
    except HTTPError as exc:
        print("FETCH_RESULT " + json.dumps({"name": name, "status": exc.code, "error": str(exc)}))
    except (URLError, TimeoutError, OSError) as exc:
        print("FETCH_RESULT " + json.dumps({"name": name, "error": f"{type(exc).__name__}: {exc}"}))

fetch("part2_viewer_page130", VIEWER)
for name, url in SEARCH_URLS.items():
    fetch(name, url)
