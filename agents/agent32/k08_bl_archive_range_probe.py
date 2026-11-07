#!/usr/bin/env python3
"""Probe the British Library 1890s OCR archive for HTTP range support and format."""
from __future__ import annotations

import urllib.request

URL = "https://bl.iro.bl.uk/downloads/54ed2842-089a-439a-b751-2179b3ffba28?locale=en"
HEADERS = {"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"}


def main() -> None:
    request = urllib.request.Request(URL, headers=HEADERS, method="HEAD")
    with urllib.request.urlopen(request, timeout=90) as response:
        print("HEAD status:", response.status)
        print("Final URL:", response.geturl())
        print("Headers:", dict(response.headers.items()))

    request = urllib.request.Request(
        URL,
        headers={**HEADERS, "Range": "bytes=0-63"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        prefix = response.read(64)
        print("Range status:", response.status)
        print("Range headers:", dict(response.headers.items()))
        print("First 64 bytes:", prefix.hex())
        print("First 64 bytes repr:", repr(prefix))


if __name__ == "__main__":
    main()
