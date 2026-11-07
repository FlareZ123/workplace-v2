#!/usr/bin/env python3
"""Probe the public British Library Books OCR dataset for K08 source pages.

The dataset is a public, per-page OCR corpus. This probe checks whether its
dataset-viewer API exposes the Cuthill and Cowper records before attempting
page/word extraction.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://datasets-server.huggingface.co"
DATASET = "TheBritishLibrary/blbooks"
CONFIG = "1800_1899"
SPLIT = "train"


def api_get(endpoint: str, params: dict[str, str | int]) -> dict | None:
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print({
            "endpoint": endpoint,
            "status": error.code,
            "url": url,
            "body": body[:3000],
        })
        return None
    print(f"API {endpoint} returned successfully")
    return result


def summarize_rows(rows: list[dict]) -> list[dict]:
    records: dict[str, dict] = {}
    for item in rows:
        row = item["row"]
        record_id = row.get("record_id")
        if record_id is None:
            continue
        summary = records.setdefault(record_id, {
            "record_id": record_id,
            "title": row.get("title"),
            "name": row.get("name"),
            "date": row.get("date"),
            "rows": 0,
            "min_pg": None,
            "max_pg": None,
            "sample_text": (row.get("text") or "")[:100],
        })
        summary["rows"] += 1
        pg = row.get("pg")
        if pg is not None:
            summary["min_pg"] = pg if summary["min_pg"] is None else min(summary["min_pg"], pg)
            summary["max_pg"] = pg if summary["max_pg"] is None else max(summary["max_pg"], pg)
    return list(records.values())


def main() -> None:
    print("Dataset:", DATASET, CONFIG, SPLIT)
    validity = api_get("is-valid", {"dataset": DATASET})
    print("Validity:", validity)
    splits = api_get("splits", {"dataset": DATASET})
    print("Splits:", splits)

    for query in (
        "000843241",
        "A Sailing Guide to the Solent and Poole Harbour",
        "Sailing Tours",
        "The Coasts of Essex and Suffolk",
        "Frank Cowper",
    ):
        result = api_get("search", {
            "dataset": DATASET,
            "config": CONFIG,
            "split": SPLIT,
            "query": query,
            "offset": 0,
            "length": 100,
        })
        if result is None:
            continue
        rows = result.get("rows", [])
        print("Search result:", {
            "query": query,
            "num_rows_total": result.get("num_rows_total"),
            "partial": result.get("partial"),
            "returned_rows": len(rows),
            "records": summarize_rows(rows),
        })


if __name__ == "__main__":
    main()
