#!/usr/bin/env python3
"""Bounded Google Books SearchWithinVolume2 probe for the P212 Praeger lead."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

VOLUMES = {
    "uT5RAQAAIAAJ": "1947 third edition",
    "in7VAAAAMAAJ": "1937 first edition",
    "HbENAAAAIAAJ": "1939 second edition",
}
QUERIES = [
    "Boulder-clay",
    '"Percolating water"',
    '"right angles"',
    '"Lough Conn"',
    "Cong",
    '"naked limestone"',
    '"Central Plain"',
]


def fetch(volume: str, query: str) -> dict:
    params = urllib.parse.urlencode({
        "jscmd": "SearchWithinVolume2",
        "q": query,
        "vid": volume,
    })
    url = "https://books.google.com/books?" + params
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    text = raw.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = {"raw_text": text[:2000]}
    return {
        "url": url,
        "http_bytes": len(raw),
        "payload": payload,
    }


def main() -> None:
    output = {}
    for volume, label in VOLUMES.items():
        rows = {}
        for query in QUERIES:
            try:
                row = fetch(volume, query)
            except Exception as error:
                row = {"error": repr(error)}
            rows[query] = row
            print("SEARCHWITHIN " + json.dumps({
                "volume": volume,
                "edition": label,
                "query": query,
                **row,
            }, ensure_ascii=False))
        output[volume] = {"edition": label, "queries": rows}
    with open("praeger-searchwithin.json", "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
