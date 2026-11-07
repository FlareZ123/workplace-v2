#!/usr/bin/env python3
"""Retrieve DataCite metadata for British Library OCR dataset DOIs."""
from __future__ import annotations

import json
import urllib.request

DOIS = ["10.21250/db12", "10.23636/r7w6-zy15"]


def main() -> None:
    for doi in DOIS:
        url = f"https://api.datacite.org/dois/{doi}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "H17-Archive-Research/1.0 (public DataCite metadata)"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
        attributes = payload["data"]["attributes"]
        print({
            "doi": doi,
            "titles": attributes.get("titles"),
            "url": attributes.get("url"),
            "publisher": attributes.get("publisher"),
            "publicationYear": attributes.get("publicationYear"),
            "descriptions": attributes.get("descriptions"),
            "relatedIdentifiers": attributes.get("relatedIdentifiers"),
            "relatedItems": attributes.get("relatedItems"),
            "sizes": attributes.get("sizes"),
            "formats": attributes.get("formats"),
            "contentUrl": attributes.get("contentUrl"),
            "schemaVersion": attributes.get("schemaVersion"),
        })


if __name__ == "__main__":
    main()
