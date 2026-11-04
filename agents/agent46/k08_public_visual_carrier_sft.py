"""Read-only inventory of image captions and metadata from the folio-linked public host.

Scope: anonymous, exact same-host assets linked from public HTML and CSS only.
The /admin, /api and account/login paths are categorically excluded.
No forms, credentials, stateful actions or protected-route discovery.
"""
from __future__ import annotations

import hashlib
import re
import struct
import zlib
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = "https://noyes-energy-group.pages.dev"
BLOCK = ("/admin", "/api", "/account", "/login", "/signin", "/partner")
TOKEN = re.compile(r"(?i)h[- ]?17|PS-261003|ESC[- ]?N|caption|keeper|envelope|Emily|late watch|galley|night crew|photograph|photo|mug|lamp|sea|table|records|archive|recover")
CSS_URL = re.compile(r"url\(\s*['\"]?([^'\"\)]+)", re.I)
ASCII = re.compile(rb"[\x20-\x7e]{5,}")
SRCSET = re.compile(r"^\s*(\S+)")

def allowed(link: str, base: str) -> str | None:
    value, _ = urldefrag(urljoin(base, link.strip()))
    p = urlparse(value)
    if p.scheme != "https" or p.netloc != urlparse(ROOT).netloc:
        return None
    if p.path.lower().startswith(BLOCK):
        return None
    if not p.path or not p.path.startswith("/"):
        return None
    return value

def get(url: str) -> tuple[str, bytes] | None:
    try:
        with urlopen(Request(url, headers={"User-Agent": "H17-public-image-metadata-census/1.0"}), timeout=15) as r:
            if allowed(r.url, ROOT) != r.url:
                print("SKIP_REDIRECT", url, r.url, flush=True)
                return None
            body = r.read(5_000_001)
            if len(body) > 5_000_000:
                print("SKIP_SIZE", url, flush=True)
                return None
            mime = r.headers.get("content-type", "").split(";")[0].lower()
            print("GET", urlparse(url).path, r.status, mime, len(body), hashlib.sha256(body).hexdigest(), flush=True)
            return mime, body
    except Exception as e:
        print("GET_ERROR", urlparse(url).path, type(e).__name__, str(e)[:140], flush=True)
        return None

def extracted_text(blob: bytes, mime: str) -> list[str]:
    output = []
    if mime == "image/png" and blob.startswith(b"\x89PNG\r\n\x1a\n"):
        pos = 8
        while pos + 12 <= len(blob):
            n = int.from_bytes(blob[pos:pos+4], "big")
            kind = blob[pos+4:pos+8]
            data = blob[pos+8:pos+8+n]
            pos += 12+n
            if kind in (b"tEXt", b"iTXt"):
                output.append(data.decode("utf-8", "replace")[:4000])
            elif kind == b"zTXt":
                a, _, b = data.partition(b"\x00")
                if len(b)>1:
                    try: output.append((a + b"=" + zlib.decompress(b[1:]))[:4000].decode("utf-8","replace"))
                    except zlib.error: pass
            if kind == b"IEND": break
    if mime in ("image/svg+xml", "text/xml"):
        output.append(blob[:200000].decode("utf-8", "replace"))
    # Generic embedded EXIF/XMP/IPTC/GIF comment/WebP strings; no OCR or image fetching.
    if mime.startswith("image/"):
        for m in ASCII.finditer(blob):
            term=m.group().decode("ascii", "replace")
            if TOKEN.search(term):
                output.append(term[:350])
    return output

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.assets=[]
        self.captions=[]
        self.style=False
        self.style_data=[]
    def handle_starttag(self, tag, attributes):
        a=dict(attributes)
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag in ("img","source","video","picture"):
            for k in ("src","poster"):
                if a.get(k):self.assets.append(a[k])
            if a.get("srcset"):
                for s in a["srcset"].split(","):
                    m=SRCSET.match(s)
                    if m:self.assets.append(m.group(1))
            for k in ("alt","title","aria-label"):
                if a.get(k):self.captions.append((tag,k,a[k]))
        if tag=="link" and a.get("href") and ("stylesheet" in a.get("rel","") or "preload" in a.get("rel","") or "icon" in a.get("rel","")):
            self.assets.append(a["href"])
        if tag=="meta" and a.get("content") and ("image" in a.get("property","") or "image" in a.get("name","")):
            self.assets.append(a["content"])
        if tag=="style": self.style=True
        if a.get("style"): self.style_data.append(a["style"])
    def handle_endtag(self,tag):
        if tag=="style":self.style=False
    def handle_data(self,data):
        if self.style:self.style_data.append(data)

def main():
    html_queue=deque([ROOT+"/"])
    seen_html=set()
    assets=set()
    while html_queue and len(seen_html)<24:
        url=html_queue.popleft()
        if url in seen_html: continue
        seen_html.add(url)
        got=get(url)
        if not got or "html" not in got[0]:continue
        p=Page(); p.feed(got[1].decode("utf-8","replace"))
        for tag,key,val in p.captions:
            print("VISIBLE_CAPTION",urlparse(url).path,tag,key,repr(val[:500]),flush=True)
        for href in p.links:
            nxt=allowed(href,url)
            if nxt and nxt not in seen_html and nxt not in html_queue:
                html_queue.append(nxt)
        for src in p.assets:
            nxt=allowed(src,url)
            if nxt: assets.add(nxt)
        for style in p.style_data:
            for src in CSS_URL.findall(style):
                nxt=allowed(src,url)
                if nxt:assets.add(nxt)
    print("PUBLIC_HTML_PAGES",len(seen_html),"EXPLICIT_ASSETS",len(assets),flush=True)
    css_queue=deque(a for a in sorted(assets) if urlparse(a).path.lower().endswith(".css"))
    seen_css=set()
    while css_queue and len(seen_css)<12:
        url=css_queue.popleft()
        if url in seen_css:continue
        seen_css.add(url)
        got=get(url)
        if not got or "css" not in got[0]: continue
        for src in CSS_URL.findall(got[1].decode("utf-8","replace")):
            nxt=allowed(src,url)
            if nxt: assets.add(nxt)
    print("CSS_SCAN",len(seen_css),"FINAL_ASSETS",len(assets),flush=True)
    images=0
    possible=[]
    for url in sorted(assets)[:160]:
        path=urlparse(url).path.lower()
        if not path.endswith((".png",".jpg",".jpeg",".webp",".gif",".svg",".avif",".bmp")):
            continue
        got=get(url)
        if not got:continue
        mime,body=got
        images+=1
        for text in extracted_text(body,mime):
            for line in text.splitlines():
                if TOKEN.search(line):
                    possible.append((urlparse(url).path,line[:350]))
                    print("IMAGE_TEXT_HIT",repr(urlparse(url).path),repr(line[:350]),flush=True)
    print("SUMMARY html_pages=",len(seen_html),"image_assets=",images,"image_text_hits=",len(possible),flush=True)
    print("IMAGE_H17_KEYS",sum(bool(re.search(r"(?i)h[- ]?17|PS-261003|ESC[- ]?N|keeper|Emily|desk caption",line)) for _,line in possible),flush=True)

if __name__=="__main__":
    main()
