#!/usr/bin/env python3
"""Retrieve Cowper Sailing Tours Part I metadata and page OCR from HathiTrust."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

HTID_PART1 = "hvd.hn5w2p"
BIB_URL = f"https://catalog.hathitrust.org/api/volumes/full/htid/{HTID_PART1}.json"
DATA_BASE = "https://babel.hathitrust.org/cgi/htd"
HEADERS = {"User-Agent": "H17-Archive-Research/1.0 (public HathiTrust bibliographic and page metadata)"}


def fetch(url: str, limit: int = 12000) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read(limit).decode("utf-8", errors="replace")
            return response.status, body, dict(response.headers.items())
    except urllib.error.HTTPError as error:
        body = error.read(limit).decode("utf-8", errors="replace")
        return error.code, body, dict(error.headers.items())


def main() -> None:
    status, body, headers = fetch(BIB_URL, 50000)
    print("Bibliographic API:", {"status": status, "headers": headers, "body": body})
    if status == 200:
        metadata = json.loads(body)
        print("Bibliographic summary:", {
            "records": metadata.get("records"),
            "items": metadata.get("items"),
        })

    for resource in ("structure", "pageocr", "pagemeta"):
        if resource == "structure":
            url = f"{DATA_BASE}/{resource}/{HTID_PART1}?v=1"
            limit = 10000
        else:
            for seq in (81, 94, 99, 106, 112):
                url = f"{DATA_BASE}/{resource}/{HTID_PART1}/{seq}?v=1&alt=json"
                status, text, response_headers = fetch(url, 5000)
                print({
                    "resource": resource,
                    "seq": seq,
                    "status": status,
                    "headers": response_headers,
                    "body": text[:1800],
                })
            continue
        status, text, response_headers = fetch(url, limit)
        print({
            "resource": resource,
            "status": status,
            "headers": response_headers,
            "body": text,
        })


if __name__ == "__main__":
    main()
