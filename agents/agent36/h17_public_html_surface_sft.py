"""Read-only public HTML/sitemap surface audit for the H-17 correspondence host.

Only anonymous HTTPS pages on the exact public host are fetched. Redirects,
forms, scripts, authentication routes and third-party links are never followed.
The purpose is to inspect homepage HTML and source-linked public pages, which
prior asset-only probes did not print.
"""
import hashlib
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlsplit, unquote
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

HOST = "https://noyes-energy-group.pages.dev"
HOSTNAME = "noyes-energy-group.pages.dev"
USER_AGENT = "H17-public-HTML-research/1.0"
MAX_BYTES = 500_000
MAX_PAGES = 50
BLOCKED = ("/admin", "/api", "/partner", "/account", "/signin", "/login",
           "/auth", "/oauth", "/graphql", "/dashboard")

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, new_url):
        return None

OPEN = build_opener(NoRedirect)

def safe_url(url):
    p = urlsplit(url)
    path = unquote(p.path).lower()
    return (p.scheme == "https" and p.hostname == HOSTNAME and p.port is None
            and p.username is None and p.password is None
            and not any(path == x or path.startswith(x + "/") for x in BLOCKED)
            and not path.startswith("/.well-known/private"))

def fetch(url):
    assert safe_url(url), "unsafe URL rejected: " + url
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml,text/plain"})
    with OPEN.open(req, timeout=15) as response:
        assert response.status == 200
        assert response.geturl() == url
        raw = response.read(MAX_BYTES + 1)
        assert len(raw) <= MAX_BYTES, "response exceeded bounded read"
        return raw, dict(response.headers.items())

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.links = []
        self.images = []
        self.meta = []
        self.jsonld = []
        self.current_link = None
        self.skip = 0
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = dict(attrs)
        if tag == "meta":
            self.meta.append({k: a.get(k) for k in ("name", "property", "content", "itemprop") if a.get(k) is not None})
        if tag == "img":
            self.images.append({k: a.get(k) for k in ("src", "alt", "title", "data-src", "srcset") if a.get(k) is not None})
        if tag == "a" and a.get("href"):
            self.current_link = {"href": a["href"], "text": ""}
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
        elif tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a" and self.current_link is not None:
            self.links.append(self.current_link)
            self.current_link = None
        if tag == "script" and self.in_jsonld:
            self.in_jsonld = False
        elif tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld.append(data)
        elif not self.skip and data.strip():
            self.text.append(data.strip())
        if self.current_link is not None and data.strip():
            self.current_link["text"] += " " + data.strip()

def same_host_links(base, links):
    out = []
    for item in links:
        href = item["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        url = urldefrag(urljoin(base, href))[0]
        if safe_url(url) and url not in out:
            out.append(url)
    return out

def sitemap_urls(raw):
    root = ET.fromstring(raw)
    out = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "loc" and node.text:
            url = urldefrag(node.text.strip())[0]
            if safe_url(url) and url not in out:
                out.append(url)
    return out

def main():
    robots_url = HOST + "/robots.txt"
    sitemap_url = HOST + "/sitemap.xml"
    robot = RobotFileParser()
    robot.set_url(robots_url)
    try:
        raw, headers = fetch(robots_url)
        lines = raw.decode("utf-8", "replace").splitlines()
        robot.parse(lines)
        print("ROBOTS", len(raw), hashlib.sha256(raw).hexdigest(), repr("\n".join(lines[:80])), flush=True)
    except (HTTPError, URLError, OSError, AssertionError, ValueError) as exc:
        robot.parse([])
        print("ROBOTS_UNAVAILABLE", type(exc).__name__, str(exc)[:180], flush=True)

    queue = [HOST + "/"]
    try:
        raw, headers = fetch(sitemap_url)
        discovered = sitemap_urls(raw)
        queue.extend(x for x in discovered if x not in queue)
        print("SITEMAP", len(raw), hashlib.sha256(raw).hexdigest(), "same_host_urls", len(discovered), flush=True)
    except (HTTPError, URLError, OSError, AssertionError, ValueError, ET.ParseError) as exc:
        print("SITEMAP_UNAVAILABLE", type(exc).__name__, str(exc)[:180], flush=True)

    seen = set()
    while queue and len(seen) < MAX_PAGES:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        if not robot.can_fetch(USER_AGENT, url):
            print("ROBOTS_SKIP", url, flush=True)
            continue
        try:
            raw, headers = fetch(url)
        except (HTTPError, URLError, OSError, AssertionError, ValueError) as exc:
            code = getattr(exc, "code", None)
            print("PAGE_UNAVAILABLE", url, code, type(exc).__name__, str(exc)[:160], flush=True)
            continue
        ctype = headers.get("Content-Type", "")
        print("\nPAGE", url, "status=200", "bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest(), "content_type", ctype, flush=True)
        if "html" not in ctype.lower() and "xml" not in ctype.lower() and "text/plain" not in ctype.lower():
            print("NON_TEXT_PAGE", url, flush=True)
            continue
        if "xml" in ctype.lower() or url.endswith(".xml"):
            try:
                extra = sitemap_urls(raw)
                queue.extend(x for x in extra if x not in seen and x not in queue)
                print("XML_LOCATIONS", len(extra), extra[:100], flush=True)
            except ET.ParseError:
                print("XML_PARSE_NOT_SITEMAP", url, flush=True)
            continue
        parser = Page()
        parser.feed(raw.decode("utf-8", "replace"))
        visible = " ".join(" ".join(parser.text).split())
        title = re.search(r"(?is)<title[^>]*>(.*?)</title>", raw.decode("utf-8", "replace"))
        title_text = " ".join(title.group(1).split()) if title else ""
        links = same_host_links(url, parser.links)
        print("TITLE", title_text, flush=True)
        print("VISIBLE_TEXT", visible[:16000], flush=True)
        print("META", parser.meta[:100], flush=True)
        print("IMAGES", parser.images[:80], flush=True)
        print("JSON_LD", " ".join(" ".join(parser.jsonld).split())[:12000], flush=True)
        print("SAME_HOST_LINKS", [{"url": x["href"], "text": x["text"].strip()} for x in parser.links if safe_url(urldefrag(urljoin(url, x["href"]))[0])][:100], flush=True)
        for link in links:
            if link not in seen and link not in queue:
                queue.append(link)

    print("PUBLIC_HTML_AUDIT_COMPLETE", "pages_seen", len(seen), "queued_remaining", len(queue), flush=True)

if __name__ == "__main__":
    main()
