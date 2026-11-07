#!/usr/bin/env python3
"""Fetch only the public correspondence-index landing page linked by BX25-08."""
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


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            label = " ".join(" ".join(self._text).split())
            absolute = urllib.parse.urljoin(URL, self._href)
            if urllib.parse.urlparse(absolute).netloc == urllib.parse.urlparse(URL).netloc:
                self.links.append({"text": label, "url": absolute})
            self._href = None
            self._text = []


def main() -> None:
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17 archival index retrieval/1.0)",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        },
    )
    result = {"requested_url": URL}
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            html = body.decode("utf-8", "replace")
            parser = LinkParser()
            parser.feed(html)
            result.update(
                {
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": response.headers.get_content_type(),
                    "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "html_path": "results/assets/cowper/noyes-index-root.html",
                    "links": parser.links,
                    "html_title": (
                        html.split("<title>", 1)[1].split("</title>", 1)[0]
                        if "<title>" in html and "</title>" in html
                        else None
                    ),
                }
            )
            (OUT / "noyes-index-root.html").write_bytes(body)
    except urllib.error.HTTPError as exc:
        body = exc.read()
        result.update(
            {
                "status": exc.code,
                "error": str(exc),
                "content_type": exc.headers.get_content_type(),
                "body_prefix": body[:1000].decode("utf-8", "replace"),
            }
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "noyes-index-root.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
