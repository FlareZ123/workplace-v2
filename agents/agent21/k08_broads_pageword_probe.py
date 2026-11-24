#!/usr/bin/env python3
"""Test the source-selected K01 page/word coordinates against a public map-back book.

This is a bounded hypothesis test, not an assertion that this is the authenticated
book. It reads the accepted K01 bytes and K08 commitment from the repository,
locates printed page numbers in the supplied PDF, and tests the eight (page,word)
pairs in signed A/B/C/D order. It also searches contiguous spans on those eight
pages. No candidate or acceptance file is modified.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "resources" / "candidate.json"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"
ROUTING = ROOT / "resources" / "evidence" / "recovery-routing.json"

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*")
TARGET_PAGES = (4, 171, 28, 122, 205, 96, 67, 201)


def normalize(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def words(value: str) -> list[str]:
    return WORD_RE.findall(normalize(value))


def k08_matches(phrase: str, nonce: bytes, target: str) -> tuple[bool, str, str]:
    normalized = normalize(phrase)
    mac = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(mac).hexdigest()
    return digest == target, mac.hex().upper(), digest


def line_texts(page: fitz.Page) -> list[tuple[float, float, str]]:
    result: list[tuple[float, float, str]] = []
    data = page.get_text("dict")
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(span.get("text", "") for span in spans).strip()
            if text:
                y0 = min(span["bbox"][1] for span in spans)
                y1 = max(span["bbox"][3] for span in spans)
                result.append((y0, y1, text))
    return sorted(result, key=lambda item: (item[0], item[1]))


def locate_printed_pages(doc: fitz.Document) -> dict[int, list[tuple[int, list[tuple[float, float, str]]]]]:
    located: dict[int, list[tuple[int, list[tuple[float, float, str]]]]] = {
        p: [] for p in TARGET_PAGES
    }
    for page_index, page in enumerate(doc):
        lines = line_texts(page)
        for target in TARGET_PAGES:
            marker = str(target)
            # Printed folios are isolated numeric lines in this scan. Keep all
            # hits so the report exposes ambiguous page-number matches.
            if any(text.strip() == marker for _, _, text in lines):
                located[target].append((page_index, lines))
    return located


def extract_modes(lines: list[tuple[float, float, str]], page_height: float, page_no: int) -> dict[str, list[str]]:
    all_lines = [text for _, _, text in lines if text.strip() != str(page_no)]
    # Running headers/folios are outside the main text block. The PDF has
    # variable top/bottom placement, so retain a second full-page mode.
    body_lines = [
        text for y0, y1, text in lines
        if y0 >= 34 and y1 <= page_height - 34 and text.strip() != str(page_no)
        and "THE LAND OF THE BROADS" not in text.upper()
    ]
    # A conservative mode strips only the book-title running header and folio.
    no_running_header = [
        text for text in all_lines
        if "THE LAND OF THE BROADS" not in text.upper()
    ]
    return {
        "all_except_folio": words(" ".join(all_lines)),
        "body_blocks": words(" ".join(body_lines)),
        "no_running_header": words(" ".join(no_running_header)),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: k08_broads_pageword_probe.py BOOK.pdf", file=sys.stderr)
        return 2

    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    k01 = bytes.fromhex(candidate["K01"])
    coords = [(k01[i], k01[i + 1]) for i in range(0, 16, 2)]
    assert tuple(page for page, _ in coords) == TARGET_PAGES
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    pdf_path = Path(sys.argv[1])
    pdf_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    doc = fitz.open(pdf_path)
    located = locate_printed_pages(doc)

    report: dict[str, object] = {
        "book_hypothesis": "The Land of the Broads (Ernest R. Suffling, 1887)",
        "pdf_sha256": pdf_hash,
        "pdf_pages": len(doc),
        "k01_page_word_pairs": coords,
        "k08_target_sha256": target,
        "pages": {},
        "candidate_sequences": {},
        "contiguous_span_hits": [],
    }

    page_modes: dict[int, dict[str, list[str]]] = {}
    page_candidates: dict[int, list[int]] = {}
    for page_no in TARGET_PAGES:
        hits = located[page_no]
        page_candidates[page_no] = [idx for idx, _ in hits]
        page_report: dict[str, object] = {"pdf_page_indices": page_candidates[page_no], "modes": {}}
        if hits:
            # If the scan has duplicate folios, report each, but use the first
            # exact folio hit for the canonical extraction.
            page_index, lines = hits[0]
            modes = extract_modes(lines, doc[page_index].rect.height, page_no)
            page_modes[page_no] = modes
            for mode, tokens in modes.items():
                page_report["modes"][mode] = {
                    "word_count": len(tokens),
                    "selected_1based": tokens[coords[TARGET_PAGES.index(page_no)][1] - 1]
                    if len(tokens) >= coords[TARGET_PAGES.index(page_no)][1] else None,
                    "selected_0based": tokens[coords[TARGET_PAGES.index(page_no)][1]]
                    if len(tokens) > coords[TARGET_PAGES.index(page_no)][1] else None,
                    "excerpt_first_24": tokens[:24],
                }
        else:
            page_report["missing"] = True
        report["pages"][str(page_no)] = page_report

    orderings = {
        "signed_ABCD_order": list(TARGET_PAGES),
        "reverse_signed_order": list(reversed(TARGET_PAGES)),
        "ascending_page_order": sorted(TARGET_PAGES),
    }
    for mode in ("all_except_folio", "body_blocks", "no_running_header"):
        for index_base in (0, 1):
            for ordering_name, page_order in orderings.items():
                selected: list[str] = []
                complete = True
                for page_no in page_order:
                    modes = page_modes.get(page_no)
                    if not modes:
                        complete = False
                        break
                    word_index = coords[TARGET_PAGES.index(page_no)][1] - index_base
                    tokens = modes[mode]
                    if word_index < 0 or word_index >= len(tokens):
                        complete = False
                        break
                    selected.append(tokens[word_index])
                if not complete:
                    continue
                phrase = " ".join(selected)
                match, mac_hex, digest = k08_matches(phrase, nonce, target)
                key = f"{mode}|index_base={index_base}|{ordering_name}"
                report["candidate_sequences"][key] = {
                    "words": selected,
                    "phrase": phrase,
                    "normalized": normalize(phrase),
                    "hmac16": mac_hex,
                    "sha256": digest,
                    "match": match,
                }

    # The source-selected pages are also a bounded text corpus. Search all
    # contiguous spans of 2..20 words on those pages for the exact K08 commitment.
    for page_no in TARGET_PAGES:
        modes = page_modes.get(page_no)
        if not modes:
            continue
        tokens = modes["body_blocks"]
        for start in range(len(tokens)):
            for width in range(2, min(20, len(tokens) - start) + 1):
                phrase = " ".join(tokens[start:start + width])
                match, mac_hex, digest = k08_matches(phrase, nonce, target)
                if match:
                    report["contiguous_span_hits"].append({
                        "page": page_no, "start_1based": start + 1,
                        "width": width, "phrase": phrase,
                        "hmac16": mac_hex, "sha256": digest,
                    })

    out = ROOT / "agents" / "agent21" / "broads-pageword-results.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    any_match = any(x["match"] for x in report["candidate_sequences"].values())
    any_match = any_match or bool(report["contiguous_span_hits"])
    print("K08_MATCH", any_match)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
