#!/usr/bin/env python3
"""Bounded Google Books zoom=1 probe for the frozen Cowper Part I pages.

Only the exact HathiTrust Part I alias and the five frozen North page labels
are requested. This script does not probe other editions, offsets or pages.
"""
from __future__ import annotations

import hashlib
import json
import struct
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "assets" / "cowper" / "part1-1892-zoom1"
BOOK_ID = "hvd.hn5w2p"
PAGE_ORDER = [94, 81, 106, 99, 112]
BASE = "https://books.google.com/books/content"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data: bytes) -> list[int] | None:
    if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
        return None
    return list(struct.unpack(">II", data[16:24]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pages = []
    for page in PAGE_ORDER:
        params = {
            "id": BOOK_ID,
            "pg": f"PA{page}",
            "img": "1",
            "zoom": "1",
            "hl": "en",
        }
        url = BASE + "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
                ),
                "Accept": "image/avif,image/webp,image/apng,image/png,image/*,*/*;q=0.8",
            },
        )
        record = {
            "printed_page": page,
            "request_url": url,
            "zoom": 1,
        }
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
                content_type = response.headers.get_content_type()
                record.update(
                    {
                        "status": response.status,
                        "final_url": response.geturl(),
                        "content_type": content_type,
                        "content_length_header": response.headers.get("Content-Length"),
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "png_dimensions": png_dimensions(data),
                    }
                )
                if content_type == "image/png" and png_dimensions(data):
                    image_path = OUT / f"p{page}.png"
                    image_path.write_bytes(data)
                    record["saved_path"] = str(image_path.relative_to(ROOT))
                else:
                    record["body_prefix_hex"] = data[:32].hex()
        except urllib.error.HTTPError as exc:
            body = exc.read()
            record.update(
                {
                    "status": exc.code,
                    "error": str(exc),
                    "content_type": exc.headers.get_content_type(),
                    "body_prefix": body[:200].decode("utf-8", "replace"),
                }
            )
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
        pages.append(record)

    hashes = [p.get("sha256") for p in pages if p.get("sha256")]
    unique_hashes = sorted(set(hashes))
    result = {
        "book_id": BOOK_ID,
        "claimed_part": "Part I",
        "catalog_caution": (
            "HathiTrust item-level 974 date is 1896; verify the printed title-page "
            "imprint before treating this as the exact 1892 issue."
        ),
        "frozen_north_page_order": PAGE_ORDER,
        "request_rule": "Exact Google Books image endpoint, zoom=1 only.",
        "summary": {
            "page_count": len(pages),
            "successful_png_count": sum(
                1 for p in pages if p.get("content_type") == "image/png" and p.get("png_dimensions")
            ),
            "unique_sha256_count": len(unique_hashes),
            "all_pages_same_hash": len(hashes) == len(pages) and len(unique_hashes) == 1,
        },
        "pages": pages,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
