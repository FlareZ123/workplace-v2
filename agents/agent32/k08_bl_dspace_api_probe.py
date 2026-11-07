#!/usr/bin/env python3
"""Probe DSpace REST endpoints for the British Library 1890s OCR archive."""
from __future__ import annotations

import urllib.error
import urllib.request

UUID = "54ed2842-089a-439a-b751-2179b3ffba28"
URLS = [
    f"https://bl.iro.bl.uk/server/api/core/bitstreams/{UUID}",
    f"https://bl.iro.bl.uk/server/api/core/bitstreams/{UUID}/content",
    f"https://bl.iro.bl.uk/downloads/{UUID}?locale=en",
]
HEADERS = {"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"}


def main() -> None:
    for url in URLS:
        request = urllib.request.Request(
            url,
            headers={**HEADERS, "Range": "bytes=0-63"},
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                prefix = response.read(64)
                print({
                    "url": url,
                    "status": response.status,
                    "final_url": response.geturl(),
                    "headers": dict(response.headers.items()),
                    "first_64_hex": prefix.hex(),
                    "first_64_repr": repr(prefix),
                })
        except urllib.error.HTTPError as error:
            print({
                "url": url,
                "status": error.code,
                "reason": error.reason,
                "final_url": error.geturl(),
                "headers": dict(error.headers.items()),
                "body": error.read(1024).decode("utf-8", errors="replace"),
            })


if __name__ == "__main__":
    main()
