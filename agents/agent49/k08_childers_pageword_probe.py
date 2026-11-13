"""Bounded K08 page/word test against the public-domain 1903 Childers edition.

Hypothesis: each signed WN14 4-byte group encodes two (page, word) pairs;
the eight selected words, in A->D group order, form the keeper phrase.
This test downloads only the public-domain book scan and emits the candidate
words/hash result, never a copy of the book text.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import subprocess
import sys
from pathlib import Path

COORDS = [
    (4, 154), (171, 46),
    (28, 222), (122, 130),
    (205, 124), (96, 35),
    (67, 3), (201, 26),
]
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_K08_SHA256 = "285EB6B4196D21EAF47E251449E61E0BCE28749881CCC5A065CA733B0C3FD747"


def run(args: list[str]) -> str:
    p = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout


def page_columns(block: str) -> list[list[str]]:
    left: list[str] = []
    right: list[str] = []
    for line in block.splitlines():
        # pdftotext -layout preserves the gutter between a two-page spread.
        parts = re.split(r" {5,}", line.rstrip(), maxsplit=1)
        left.append(parts[0].strip())
        if len(parts) == 2:
            right.append(parts[1].strip())
    cols = [left, right]
    return [c for c in cols if any(x for x in c)]


def printed_page_number(lines: list[str]) -> int | None:
    for line in reversed([x for x in lines if x][-8:]):
        # Page numbers in this scan occur at the bottom, sometimes after the running title.
        m = re.search(r"(?<!\d)(\d{1,3})\s*$", line)
        if m:
            return int(m.group(1))
        m = re.match(r"^\s*(\d{1,3})(?!\d)", line)
        if m:
            return int(m.group(1))
    return None


def body_words(lines: list[str], keep_running_matter: bool = False) -> list[str]:
    kept = []
    for line in lines:
        if not line:
            continue
        if not keep_running_matter and (
            "THE RIDDLE OF THE SANDS" in line.upper()
            or "ERSKINE CHILDERS" in line.upper()
            or re.fullmatch(r"\s*\d{1,3}\s*", line)
            or re.search(r"(?<!\d)\d{1,3}\s*$", line)
        ):
            continue
        kept.append(line)
    text = " ".join(kept).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip().split()


def hmac_match(phrase: str) -> tuple[str, str, bool]:
    normalized = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", phrase.lower())).strip()
    component = hmac.new(NONCE, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    commitment = hashlib.sha256(component).hexdigest().upper()
    return normalized, component.hex().upper(), commitment == EXPECTED_K08_SHA256


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: k08_childers_pageword_probe.py BOOK.pdf", file=sys.stderr)
        return 2
    pdf = Path(sys.argv[1])
    info = run(["pdfinfo", str(pdf)])
    m = re.search(r"^Pages:\s+(\d+)", info, re.M)
    print("PDF_PAGES", m.group(1) if m else "unknown")
    extracted = run(["pdftotext", "-layout", str(pdf), "-"])
    pages = extracted.split("\f")
    page_map: dict[int, list[str]] = {}
    duplicates: dict[int, list[tuple[int, int]]] = {}

    for pdf_index, block in enumerate(pages):
        if not block.strip():
            continue
        for col_index, col in enumerate(page_columns(block)):
            printed = printed_page_number(col)
            if printed is None:
                continue
            duplicates.setdefault(printed, []).append((pdf_index, col_index))
            # Keep the first exact page-number match; duplicate OCR hits are reported.
            page_map.setdefault(printed, col)

    print("MAPPED_TARGETS", {p: (p in page_map) for p, _ in COORDS})
    print("DUPLICATE_TARGETS", {p: v for p, v in duplicates.items() if p in {x for x, _ in COORDS} and len(v) > 1})

    for keep_headers in (False, True):
        words_by_page = {p: body_words(lines, keep_headers) for p, lines in page_map.items()}
        for index_base in (1, 0):
            picked = []
            valid = True
            for page, word in COORDS:
                words = words_by_page.get(page)
                idx = word - index_base
                if words is None or idx < 0 or idx >= len(words):
                    valid = False
                    picked.append(f"<missing:{page}/{word}:count={len(words) if words is not None else 'no-page'}>")
                else:
                    picked.append(words[idx])
            if not valid:
                print("CANDIDATE", "keep_headers", keep_headers, "index_base", index_base,
                      "INVALID", picked)
                continue
            phrase, component, matched = hmac_match(" ".join(picked))
            print("CANDIDATE", "keep_headers", keep_headers, "index_base", index_base,
                  "words", picked, "phrase", phrase, "component", component, "K08_MATCH", matched)

    print("CHILDERS_PAGEWORD_PROBE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
