#!/usr/bin/env python3
"""One-shot K08 test for the signed-WN-14 byte-pair book-coordinate hypothesis.

Input pages must be transcribed from the exact, physically identified book and
edition, retaining printed page numbers. The script deliberately tests only the
frozen A-D, page-then-word, one-based interpretation.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any

GROUPS = {
    "A": "049AAB2E",
    "B": "1CDE7A82",
    "C": "CD7C6023",
    "D": "4303C91A",
}


def coordinates() -> list[tuple[str, int, int]]:
    result: list[tuple[str, int, int]] = []
    for group, value in GROUPS.items():
        raw = bytes.fromhex(value)
        result.extend(((group, raw[0], raw[1]), (group, raw[2], raw[3])))
    return result


def normalize(text: str) -> str:
    lowered = text.lower()
    spaced = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return " ".join(spaced.split())


def extract_phrase(pages: dict[str, str]) -> tuple[str, list[dict[str, Any]]]:
    words_by_page = {
        str(page): normalize(text).split()
        for page, text in pages.items()
    }
    extracted: list[str] = []
    trace: list[dict[str, Any]] = []
    for group, page, word in coordinates():
        page_words = words_by_page.get(str(page))
        if page_words is None:
            raise ValueError(f"Missing printed page {page}")
        if word < 1 or word > len(page_words):
            raise ValueError(
                f"Page {page} has {len(page_words)} normalized words; "
                f"cannot read one-based word {word}"
            )
        token = page_words[word - 1]
        extracted.append(token)
        trace.append({"group": group, "page": page, "word": word, "token": token})
    return normalize(" ".join(extracted)), trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", required=True, type=Path,
                        help="JSON object mapping printed page numbers to page text")
    parser.add_argument("--routing", required=True, type=Path,
                        help="recovery-routing.json from the surviving export")
    parser.add_argument("--acceptance", required=True, type=Path,
                        help="acceptance.json from the surviving export")
    args = parser.parse_args()

    pages = json.loads(args.pages.read_text(encoding="utf-8"))
    if not isinstance(pages, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in pages.items()
    ):
        raise ValueError("--pages must be a JSON object of page-number strings to text")

    routing = json.loads(args.routing.read_text(encoding="utf-8"))
    acceptance = json.loads(args.acceptance.read_text(encoding="utf-8"))
    phrase, trace = extract_phrase(pages)
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    component = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    component_hash = hashlib.sha256(component).hexdigest()
    target = acceptance["slot_sha256"]["K08"]

    print(json.dumps({
        "hypothesis": "signed WN-14 groups A-D as ordered one-based (page, word) byte pairs",
        "coordinates": trace,
        "normalized_phrase": phrase,
        "component_hex": component.hex().upper(),
        "component_sha256": component_hash,
        "target_sha256": target,
        "K08": "PASS" if component_hash == target else "NO_MATCH",
    }, indent=2))
    return 0 if component_hash == target else 1


if __name__ == "__main__":
    raise SystemExit(main())
