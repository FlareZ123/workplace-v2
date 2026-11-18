#!/usr/bin/env python3
"""Probe Google Books SearchWithinVolume2 for true page IDs in the 1889 Falcon volume."""
from __future__ import annotations
import json
import urllib.parse
import urllib.request

VOLUME = "fQYN_SZzCFgC"
QUERIES = [
    "her mainsail was smaller and her mizen larger",
    "water tight compartments had been taken out",
    "appliance for covering over this well in bad weather",
]

for query in QUERIES:
    params = urllib.parse.urlencode({
        "id": VOLUME,
        "jscmd": "SearchWithinVolume2",
        "q": f'"{query}"',
    })
    url = "https://www.google.com/books?" + params
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 H17-Archive-Preservation/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    print("QUERY", query)
    print(json.dumps(data, sort_keys=True))
