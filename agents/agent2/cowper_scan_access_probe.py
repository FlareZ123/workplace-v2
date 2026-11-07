#!/usr/bin/env python3
"""Probe public HathiTrust and Google Books access for the identified Cowper scans."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

USER_AGENT = "H17-Cowper-Scan-Access-Probe/1.0"
HATHI_ID = "hvd.hn5w2p"
GOOGLE_ID = "o7P-qis2u9IC"
TIMEOUT = 25


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        for key in ("src", "href", "data-src", "data-url"):
            value = attrs_dict.get(key)
            if value and value not in self.links:
                self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if not stripped:
            return
        self.text_parts.append(stripped)
        if self.in_title:
            self.title_parts.append(stripped)


def fetch(url: str) -> tuple[int, str, str, bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/json,text/plain,*/*",
            "Referer": "https://babel.hathitrust.org/",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise RuntimeError(f"response too large: {url}")
        return response.status, response.headers.get("Content-Type", ""), response.geturl(), body


def probe(label: str, url: str) -> None:
    print("\nPROBE", label, url, flush=True)
    try:
        status, content_type, final_url, body = fetch(url)
        print("HTTP", status, "TYPE", content_type, "FINAL", final_url, "BYTES", len(body), flush=True)
        text = body.decode("utf-8", errors="replace")
        if "json" in content_type or text.lstrip().startswith("{"):
            try:
                data = json.loads(text)
                if label == "Google Books API":
                    vi = data.get("volumeInfo", {})
                    ai = data.get("accessInfo", {})
                    print("TITLE", vi.get("title"), flush=True)
                    print("AUTHORS", vi.get("authors"), flush=True)
                    print("PUBLISHED", vi.get("publishedDate"), "PAGES", vi.get("pageCount"), flush=True)
                    print("VIEWABILITY", ai.get("viewability"), "PUBLIC_DOMAIN", ai.get("publicDomain"), flush=True)
                    print("WEB_READER", ai.get("webReaderLink"), flush=True)
                    print("PDF", ai.get("pdf"), "EPUB", ai.get("epub"), flush=True)
                else:
                    print("JSON_PREFIX", json.dumps(data, ensure_ascii=False)[:3000], flush=True)
            except json.JSONDecodeError:
                print("BODY_PREFIX", text[:1500], flush=True)
            return
        parser = PageParser()
        parser.feed(text)
        print("HTML_TITLE", " ".join(parser.title_parts)[:300], flush=True)
        print("TEXT_PREFIX", " ".join(parser.text_parts)[:2500], flush=True)
        relevant = [
            link for link in parser.links
            if any(term in link.lower() for term in ("imgsrv", "image", "text", "ocr", "seq", "page", "pdf"))
        ]
        for link in relevant[:40]:
            print("LINK", link[:1000], flush=True)
        if not relevant:
            print("HTML_PREFIX", text[:1800], flush=True)
    except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
        print("FETCH_ERROR", type(exc).__name__, str(exc)[:1000], flush=True)


def main() -> int:
    probe(
        "HathiTrust viewer seq7",
        f"https://babel.hathitrust.org/cgi/pt?id={HATHI_ID}&seq=7&view=1up",
    )
    for fmt in ("html", "plaintext", "txt"):
        probe(
            f"HathiTrust format={fmt}",
            f"https://babel.hathitrust.org/cgi/pt?id={HATHI_ID}&seq=7&view=1up&format={fmt}",
        )
    probe(
        "Google Books API",
        f"https://www.googleapis.com/books/v1/volumes/{GOOGLE_ID}",
    )
    probe(
        "Google Books page121 html_text",
        f"https://books.google.com/books?id={GOOGLE_ID}&pg=PA121&output=html_text",
    )
    probe(
        "Google Books viewer page121",
        f"https://books.google.com/books?id={GOOGLE_ID}&pg=PA121&jscmd=SearchWithinVolume2&q=the",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
