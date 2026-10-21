"""Bounded anonymous original-folio public HTML comment/source-marker audit."""
from __future__ import annotations

import hashlib
import re
from collections import deque
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = "https://noyes-energy-group.pages.dev"
MARK = re.compile(r"H[- ]?17|IR-261003|PS-261003|ESC[- ]?N|WN[- ]?14|Emily|keeper|caption|coupon", re.I)
BEFORE_SHA = "5d4aa1dd3f82e3ed63095a24b6ad76a08ac0e1536c0fd7ec7ea96be91431b653"

class Probe(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.comments = []
        self.hidden_values = []
        self.inline = []
        self.script = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        for key, value in attrs:
            if key.startswith("data-") and value:
                self.hidden_values.append((key, value))
        if tag == "script" and not a.get("src"):
            self.script = a.get("type", "text/javascript")

    def handle_endtag(self, tag):
        if tag == "script":
            self.script = None

    def handle_data(self, data):
        if self.script and data.strip():
            self.inline.append((self.script, data))

    def handle_comment(self, data):
        self.comments.append(data)

def source_snip(text, match):
    return " ".join(text[max(0, match.start()-80):match.end()+100].split())[:210]

def normalize_link(href):
    url,_ = urldefrag(urljoin(ROOT, href))
    p = urlparse(url)
    if p.scheme != "https" or p.netloc != urlparse(ROOT).netloc:
        return None
    if p.path.startswith(("/admin","/api/")):
        return None
    return p.path or "/"

def fetch_page(path):
    try:
        with urlopen(Request(urljoin(ROOT,path), headers={"User-Agent":"H17-preservation-public-HTML-comment-audit/1.0"}), timeout=12) as r:
            if urlparse(r.url).netloc != urlparse(ROOT).netloc:
                print("REDIRECT_EXTERNAL_SKIP",path)
                return None
            kind=r.headers.get("Content-Type","")
            body=r.read(250001)
    except (HTTPError, URLError) as exc:
        print("GET_SKIP",path,type(exc).__name__,str(exc)[:100])
        return None
    if len(body)>250000 or "html" not in kind.lower():
        print("NOT_HTML_OR_TOO_BIG",path,len(body),kind)
        return None
    return body

def main():
    queue=deque(["/"])
    visited=set()
    total_comments=0
    total_hits=0
    while queue and len(visited)<24:
        path=queue.popleft()
        if path in visited or path.startswith(("/admin","/api/")):
            continue
        visited.add(path)
        raw=fetch_page(path)
        if raw is None:
            continue
        digest=hashlib.sha256(raw).hexdigest()
        if path=="/":
            print("HOMEPAGE_SHA",digest,"matches_20261020",digest==BEFORE_SHA)
        text=raw.decode("utf-8", errors="replace")
        doc=Probe()
        doc.feed(text)
        print("PAGE",path,"sha",digest[:14],"comments",len(doc.comments),"inline",len(doc.inline),"data_attrs",len(doc.hidden_values))
        total_comments+=len(doc.comments)
        for kind, items in (("COMMENT",[(i,s) for i,s in enumerate(doc.comments)]),
                            ("INLINE",[(i,s) for i,(t,s) in enumerate(doc.inline)]),
                            ("DATA_ATTR",[(key,s) for key,s in doc.hidden_values])):
            for identity,s in items:
                hits=list(MARK.finditer(s))
                if hits:
                    total_hits+=len(hits)
                    print("MARKER",kind,path,identity,"len",len(s),"sha",hashlib.sha256(s.encode()).hexdigest()[:16],"hits",len(hits))
                    for m in hits[:3]:
                        print("CONTEXT",source_snip(s,m))
                elif kind=="COMMENT" and len(s)>200:
                    print("LARGE_COMMENT_NO_MARKER",path,identity,"len",len(s),"sha",hashlib.sha256(s.encode()).hexdigest()[:16])
        for href in doc.links:
            next_path=normalize_link(href)
            if next_path is not None and next_path not in visited and next_path not in queue:
                queue.append(next_path)
    print("FINAL",len(visited),"public_paths",total_comments,"comments",total_hits,"hidden_hits")
    print("PATHS",sorted(visited))

if __name__=="__main__":
    main()
