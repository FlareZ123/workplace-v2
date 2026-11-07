#!/usr/bin/env python3
"""Retrieve British Library page OCR and test K08 page/word candidates.

The query is limited to the public British Library Books OCR dataset. It tests
three source hypotheses: Cuthill's 1893 Solent guide, and Cowper's Sailing Tours
Part I / Part II. Ticket order follows the source binder tabs.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.parse
import urllib.request

API_BASE = "https://datasets-server.huggingface.co"
DATASET = "TheBritishLibrary/blbooks"
CONFIG = "1800_1899"
SPLIT = "train"
TICKET_PAGE_ORDER = [94, 81, 106, 99, 112, 130, 151, 121, 135, 142]
NORTH_PAGES = TICKET_PAGE_ORDER[:5]
SOUTH_PAGES = TICKET_PAGE_ORDER[5:]
WORD_POSITIONS = (103, 104)
DESK_NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_SLOT_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
TOKENIZERS = {
    "apostrophes-kept": re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*"),
    "punctuation-split": re.compile(r"[A-Za-z0-9]+"),
}


def api_get(endpoint: str, params: dict[str, str | int]) -> dict:
    url = f"{API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public British Library OCR dataset)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def fetch_filtered_record(record_id: str) -> tuple[list[dict], dict]:
    params = {
        "dataset": DATASET,
        "config": CONFIG,
        "split": SPLIT,
        "where": f'"record_id"=\'{record_id}\'',
        "offset": 0,
        "length": 100,
    }
    first = api_get("filter", params)
    rows = list(first.get("rows", []))
    total = int(first.get("num_rows_total", len(rows)))
    offset = len(rows)
    while offset < total:
        params["offset"] = offset
        next_page = api_get("filter", params)
        batch = next_page.get("rows", [])
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    return rows, first


def search_records(query: str) -> tuple[list[dict], dict]:
    params = {
        "dataset": DATASET,
        "config": CONFIG,
        "split": SPLIT,
        "query": query,
        "offset": 0,
        "length": 100,
    }
    first = api_get("search", params)
    rows = list(first.get("rows", []))
    total = int(first.get("num_rows_total", len(rows)))
    offset = len(rows)
    while offset < total:
        params["offset"] = offset
        next_page = api_get("search", params)
        batch = next_page.get("rows", [])
        if not batch:
            break
        rows.extend(batch)
        offset += len(batch)
    return rows, first


def unique_record_summaries(rows: list[dict]) -> list[dict]:
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
            "pages": 0,
            "min_pg": None,
            "max_pg": None,
            "row_indices": [],
        })
        summary["pages"] += 1
        pg = row.get("pg")
        if pg is not None:
            summary["min_pg"] = pg if summary["min_pg"] is None else min(summary["min_pg"], pg)
            summary["max_pg"] = pg if summary["max_pg"] is None else max(summary["max_pg"], pg)
        summary["row_indices"].append(item.get("row_idx"))
    return list(records.values())


def normalized_phrase(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def slot_digest(words: list[str]) -> tuple[str, str, str]:
    phrase = normalized_phrase(words)
    slot = hmac.new(DESK_NONCE, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    return phrase, slot.hex().upper(), hashlib.sha256(slot).hexdigest()


def ordered_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda item: item.get("row_idx", 0))


def extract_by_page_field(rows: list[dict], pages: list[int], tokenizer: re.Pattern[str], word_position: int) -> list[str] | None:
    by_page = {item["row"].get("pg"): item["row"].get("text") or "" for item in rows}
    words = []
    for page in pages:
        text = by_page.get(page)
        if not text:
            return None
        tokens = tokenizer.findall(text)
        if len(tokens) < word_position:
            return None
        words.append(tokens[word_position - 1])
    return words


def extract_by_scan_order(rows: list[dict], pages: list[int], tokenizer: re.Pattern[str], word_position: int) -> list[str] | None:
    ordered = ordered_rows(rows)
    words = []
    for page in pages:
        if not 1 <= page <= len(ordered):
            return None
        text = ordered[page - 1]["row"].get("text") or ""
        tokens = tokenizer.findall(text)
        if len(tokens) < word_position:
            return None
        words.append(tokens[word_position - 1])
    return words


def test_candidate(label: str, words: list[str], tokenizer_name: str, word_position: int, page_mode: str) -> None:
    phrase, slot_hex, digest = slot_digest(words)
    print({
        "candidate": label,
        "page_mode": page_mode,
        "tokenizer": tokenizer_name,
        "word_position_1based": word_position,
        "words": words,
        "normalized_phrase": phrase,
        "derived_slot_hex": slot_hex,
        "slot_sha256": digest,
        "acceptance_match": digest == EXPECTED_SLOT_SHA256,
    })


def main() -> None:
    print("British Library OCR dataset:", DATASET, CONFIG, SPLIT)
    print("Ticket tab order:", TICKET_PAGE_ORDER)

    cuthill_rows, cuthill_meta = fetch_filtered_record("000843241")
    print("Cuthill filter metadata:", {
        "num_rows_total": cuthill_meta.get("num_rows_total"),
        "partial": cuthill_meta.get("partial"),
        "returned_rows": len(cuthill_rows),
    })
    print("Cuthill record summary:", unique_record_summaries(cuthill_rows))

    cowper_queries = [
        "Sailing Tours",
        "The Coasts of Essex and Suffolk",
        "Frank Cowper",
    ]
    cowper_rows: list[dict] = []
    for query in cowper_queries:
        rows, metadata = search_records(query)
        print(f"Cowper search {query!r}:", {
            "num_rows_total": metadata.get("num_rows_total"),
            "partial": metadata.get("partial"),
            "returned_rows": len(rows),
            "records": unique_record_summaries(rows)[:20],
        })
        cowper_rows.extend(rows)

    cowper_summaries = unique_record_summaries(cowper_rows)
    print("Unique Cowper candidate records:", cowper_summaries)

    # Test the Cuthill guide using both its original-page field and scan order.
    if cuthill_rows:
        for tokenizer_name, tokenizer in TOKENIZERS.items():
            for word_position in WORD_POSITIONS:
                for page_mode, extractor in (
                    ("record_pg", extract_by_page_field),
                    ("scan_order", extract_by_scan_order),
                ):
                    words = extractor(cuthill_rows, TICKET_PAGE_ORDER, tokenizer, word_position)
                    if words:
                        test_candidate("Cuthill 1893 guide", words, tokenizer_name, word_position, page_mode)
                    else:
                        print(f"Cuthill unavailable for {page_mode}, {tokenizer_name}, word {word_position}")

    # If both Cowper volumes are in the OCR collection, test North tabs against
    # Part I and South tabs against Part II. Candidate records are printed above
    # so the exact catalogue match remains auditable.
    candidate_ids = [item["record_id"] for item in cowper_summaries]
    for record_id in candidate_ids:
        rows, metadata = fetch_filtered_record(record_id)
        print("Cowper record fetch:", {
            "record_id": record_id,
            "num_rows_total": metadata.get("num_rows_total"),
            "partial": metadata.get("partial"),
            "returned_rows": len(rows),
            "summary": unique_record_summaries(rows),
        })


if __name__ == "__main__":
    main()
