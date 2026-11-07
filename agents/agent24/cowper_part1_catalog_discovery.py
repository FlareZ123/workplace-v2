#!/usr/bin/env python3
"""Exact-title public metadata discovery for Cowper Part I, no content bypass."""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "assets" / "cowper" / "part1-scan-discovery.json"


def fetch_json(label: str, url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17 archival catalog research/1.0)",
            "Accept": "application/json,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            return {
                "label": label,
                "requested_url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "content_type": response.headers.get_content_type(),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "json": parsed,
                "body_prefix": None if parsed is not None else body[:500].decode("utf-8", "replace"),
                "body_text": None if parsed is not None or len(body) > 20000 else body.decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read()
        return {
            "label": label,
            "requested_url": url,
            "status": exc.code,
            "error": str(exc),
            "content_type": exc.headers.get_content_type(),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "body_prefix": body[:500].decode("utf-8", "replace"),
        }
    except Exception as exc:
        return {
            "label": label,
            "requested_url": url,
            "error": f"{type(exc).__name__}: {exc}",
        }


def query_url(base: str, params: list[tuple[str, str]]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def main() -> None:
    google_queries = [
        'intitle:"The Coasts of Essex and Suffolk" inauthor:"Frank Cowper"',
        'intitle:"Sailing Tours" inauthor:"Frank Cowper"',
        "oclc:7504145",
    ]
    requests = []
    for q in google_queries:
        requests.append(
            (
                f"Google Books API: {q}",
                query_url(
                    "https://www.googleapis.com/books/v1/volumes",
                    [("q", q), ("maxResults", "40"), ("printType", "books")],
                ),
            )
        )

    ia_queries = [
        'title:"The Coasts of Essex and Suffolk" AND creator:"Frank Cowper"',
        'title:"Sailing Tours" AND creator:"Frank Cowper"',
        'title:"The Coasts of Essex and Suffolk"',
        'title:"Sailing Tours"',
        'creator:"Frank Cowper" AND mediatype:texts',
    ]
    ia_fields = ["identifier", "title", "creator", "date", "mediatype"]
    for q in ia_queries:
        params = [("q", q)] + [("fl[]", f) for f in ia_fields] + [
            ("rows", "100"),
            ("page", "1"),
            ("output", "json"),
        ]
        requests.append(
            (
                f"Internet Archive Advanced Search: {q}",
                query_url("https://archive.org/advancedsearch.php", params),
            )
        )

    open_library_url = query_url(
        "https://openlibrary.org/search.json",
        [
            ("title", "The Coasts of Essex and Suffolk"),
            ("author", "Frank Cowper"),
            ("fields", "key,title,author_name,first_publish_year,edition_key,ia,has_fulltext,public_scan_b"),
            ("limit", "100"),
        ],
    )
    requests.append(("Open Library exact title and author", open_library_url))

    requests.extend(
        [
            (
                "HathiTrust OCLC 7504145 catalog metadata",
                "https://catalog.hathitrust.org/api/volumes/brief/oclc/7504145.json",
            ),
            (
                "HathiTrust Part I item metadata",
                "https://catalog.hathitrust.org/api/volumes/brief/htid/hvd.hn5w2p.json",
            ),
            (
                "HathiTrust full Part I item metadata",
                "https://catalog.hathitrust.org/api/volumes/full/htid/hvd.hn5w2p.json",
            ),
            (
                "HathiTrust full OCLC 7504145 metadata",
                "https://catalog.hathitrust.org/api/volumes/full/oclc/7504145.json",
            ),
            (
                "HathiTrust MARC record 100485750",
                "https://catalog.hathitrust.org/Record/100485750.marc",
            ),
            (
                "Internet Archive metadata for Cowper Sailing Tours candidate",
                "https://archive.org/metadata/sailingtoursyach0000cowp",
            ),
        ]
    )

    results = [fetch_json(label, url) for label, url in requests]
    output = {
        "purpose": "Find an alternate authorized scan or exact 1892 Part I bibliographic item.",
        "frozen_part_i_pages": [94, 81, 106, 99, 112],
        "frozen_part_i_hathitrust_alias": "hvd.hn5w2p",
        "queries": results,
        "limits": [
            "Public catalog metadata only; no authentication or access controls bypassed.",
            "A metadata hit is not proof of a page scan or exact 1892 imprint.",
            "Any candidate scan must be checked for title-page imprint and printed page labels before extraction.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
