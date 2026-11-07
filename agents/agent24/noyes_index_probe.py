#!/usr/bin/env python3
"""Read-only probe of the public Noyes site linked by the BX25-08 annex."""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "assets" / "cowper"
URL = "https://noyes-energy-group.pages.dev/"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
        self.inputs = []
        self.title_parts = []
        self.text_parts = []
        self.in_title = False
        self._href = None
        self._anchor_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "form":
            self.forms.append(
                {"action": attrs.get("action"), "method": attrs.get("method", "get")}
            )
        if tag.lower() == "input":
            self.inputs.append(
                {
                    "type": attrs.get("type", "text"),
                    "name": attrs.get("name"),
                    "autocomplete": attrs.get("autocomplete"),
                }
            )
        if tag.lower() == "a":
            self._href = attrs.get("href")
            self._anchor_text = []

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        self.text_parts.append(data)
        if self._href is not None:
            self._anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False
        if tag.lower() == "a" and self._href is not None:
            absolute = urllib.parse.urljoin(URL, self._href)
            if urllib.parse.urlparse(absolute).netloc == urllib.parse.urlparse(URL).netloc:
                self.links.append(
                    {"text": " ".join(" ".join(self._anchor_text).split()), "url": absolute}
                )
            self._href = None
            self._anchor_text = []

    def result(self):
        return {
            "title": " ".join(" ".join(self.title_parts).split()) or None,
            "text_excerpt": " ".join(" ".join(self.text_parts).split())[:4000],
            "links": self.links,
            "forms": self.forms,
            "inputs": self.inputs,
        }


def fetch_page(label: str, url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17 archival index retrieval/1.0)",
            "Accept": "text/html,text/plain,application/xhtml+xml,*/*;q=0.8",
        },
    )
    record = {"label": label, "requested_url": url}
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            content_type = response.headers.get_content_type()
            record.update(
                {
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": content_type,
                    "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                }
            )
            if "html" in content_type:
                parser = PageParser()
                parser.feed(body.decode("utf-8", "replace"))
                record.update(parser.result())
            else:
                record["text"] = body.decode("utf-8", "replace")[:4000]
            return record
    except urllib.error.HTTPError as exc:
        body = exc.read()
        record.update(
            {
                "status": exc.code,
                "error": str(exc),
                "content_type": exc.headers.get_content_type(),
                "body_prefix": body[:1000].decode("utf-8", "replace"),
            }
        )
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [
        fetch_page("robots.txt", urllib.parse.urljoin(URL, "robots.txt")),
        fetch_page("admin landing page (read-only; no login submitted)", urllib.parse.urljoin(URL, "admin")),
    ]
    output = {
        "source_url_in_bx25_08": URL,
        "scope": "Read-only GET of robots.txt and the linked admin landing page; no credentials or forms submitted.",
        "pages": results,
    }
    (OUT / "noyes-index-readonly-probe.json").write_text(
        json.dumps(output, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
