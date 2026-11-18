#!/usr/bin/env python3
"""Probe Google Books SearchWithinVolume2 for true page IDs in the 1889 Falcon volume."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

VOLUME = "fQYN_SZzCFgC"
QUERY = "her mainsail was smaller and her mizen larger"
BASES = (
    "https://www.google.com/books",
    "http://www.google.com/books",
    "https://books.google.com/books",
)

for base in BASES:
    params = urllib.parse.urlencode({
        "id": VOLUME,
        "jscmd": "SearchWithinVolume2",
        "q": f'"{QUERY}"',
    })
    url = base + "?" + params
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 H17-Archive-Preservation/1.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read(65536)
            print("PROBE", json.dumps({
                "requested_url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "content_type": response.headers.get("Content-Type"),
                "bytes_read": len(body),
                "body_prefix": body[:500].decode("utf-8", "replace"),
            }, ensure_ascii=False))
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                continue
            print("JSON", json.dumps(data, sort_keys=True, ensure_ascii=False))
    except Exception as exc:
        print("ERROR", base, type(exc).__name__, str(exc))
