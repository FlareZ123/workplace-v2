#!/usr/bin/env python3
"""Probe the British Library IRO entity and DSpace APIs for the 1890s OCR files."""
from __future__ import annotations

import urllib.error
import urllib.request

UUID = "e06c3cf8-8fe1-4084-b434-16199053e72c"
URLS = [
    f"https://bl.iro.bl.uk/entities/product/{UUID}",
    f"https://bl.iro.bl.uk/server/api/core/items/{UUID}",
    "https://bl.iro.bl.uk/server/api/core/items?size=5&query=dc.identifier:000843241",
    "https://doi.org/10.21250/db12",
]
HEADERS = {"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"}


def main() -> None:
    for url in URLS:
        request = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = response.read(6000).decode("utf-8", errors="replace")
                print({
                    "url": url,
                    "status": response.status,
                    "final_url": response.geturl(),
                    "content_type": response.headers.get("Content-Type"),
                    "headers": dict(response.headers.items()),
                    "body": body,
                })
        except urllib.error.HTTPError as error:
            print({
                "url": url,
                "status": error.code,
                "final_url": error.geturl(),
                "content_type": error.headers.get("Content-Type"),
                "body": error.read(3000).decode("utf-8", errors="replace"),
            })


if __name__ == "__main__":
    main()
