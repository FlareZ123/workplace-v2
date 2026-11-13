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


def header_page_number(block: str) -> int | None:
    # In this scan the running title/author line carries the printed page number.
    for line in block.splitlines():
        upper = line.upper()
        if "THE RIDDLE OF THE SANDS" in upper or "ERSKINE CHILDERS" in upper:
            m = re.search(r"(?<!\d)(\d{1,3})\s*$", line)
            if m:
                return int(m.group(1))
    return None


def body_words(block: str) -> list[str]:
    kept = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if "THE RIDDLE OF THE SANDS" in upper or "ERSKINE CHILDERS" in upper:
            continue
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        kept.append(stripped)
    text = " ".join(kept).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip().split()


def hmac_match(words: list[str]) -> tuple[str, str, bool]:
    normalized = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", " ".join(words).lower())).strip()
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
    page_map: dict[int, tuple[int, str]] = {}
    offsets: list[int] = []
    for pdf_index, block in enumerate(pages):
        if not block.strip():
            continue
        printed = header_page_number(block)
        if printed is None:
            continue
        offsets.append(pdf_index - printed)
        page_map.setdefault(printed, (pdf_index, block))

    if offsets:
        from collections import Counter
        counts = Counter(offsets)
        offset, frequency = counts.most_common(1)[0]
    else:
        offset, frequency = None, 0
    print("PAGE_OFFSETS", dict(sorted(__import__("collections").Counter(offsets).items())))
    print("OFFSET_MODE", offset, "frequency", frequency)
    target_pages = sorted({p for p, _ in COORDS})
    resolved: dict[int, tuple[int, str]] = {}
    for target in target_pages:
        if target in page_map:
            resolved[target] = page_map[target]
        elif offset is not None and 0 <= target + offset < len(pages):
            idx = target + offset
            resolved[target] = (idx, pages[idx])
    print("MAPPED_TARGETS", {
        p: (resolved[p][0] if p in resolved else None)
        for p in target_pages
    })
    print("HEADER_MATCH_COUNT", len(page_map), "PDF_PAGE_COUNT", len(pages))

    words_by_page = {p: body_words(block) for p, (_, block) in resolved.items()}
    picked: list[str] = []
    valid = True
    for page, word in COORDS:
        words = words_by_page.get(page)
        idx = word - 1
        if words is None or idx < 0 or idx >= len(words):
            valid = False
            picked.append(f"<missing:{page}/{word}:count={len(words) if words is not None else 'no-page'}>")
        else:
            picked.append(words[idx])
    if not valid:
        print("CANDIDATE INVALID", picked)
    else:
        phrase, component, matched = hmac_match(picked)
        print("CANDIDATE words", picked, "phrase", phrase,
              "component", component, "K08_MATCH", matched)

    print("CHILDERS_PAGEWORD_PROBE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
