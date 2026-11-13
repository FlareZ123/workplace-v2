"""Bounded K08 page/word test against the public-domain 1903 Childers edition.

Hypothesis: each signed WN14 4-byte group encodes two (page, word) pairs;
the eight selected words, in A->D group order, form the keeper phrase.
The scan's OCR text layer carries page headers only, so this script OCRs just
the eight mapped page images. It emits selected words and hash results, not
the surrounding book text.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import subprocess
import sys
import tempfile
from pathlib import Path

COORDS = [
    (4, 154), (171, 46),
    (28, 222), (122, 130),
    (205, 124), (96, 35),
    (67, 3), (201, 26),
]
PDF_PAGE_OFFSET = 4  # printed page n is PDF page n+4 (1-based), confirmed by scan headers
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_K08_SHA256 = "285EB6B4196D21EAF47E251449E61E0BCE28749881CCC5A065CA733B0C3FD747"


def run(args: list[str]) -> str:
    p = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout


def tokenize_ocr(text: str) -> list[str]:
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if "THE RIDDLE OF THE SANDS" in upper or "ERSKINE CHILDERS" in upper:
            continue
        if re.fullmatch(r"[0-9]{1,3}[.]?", stripped):
            continue
        kept.append(stripped)
    normalized = re.sub(r"[^a-z0-9\s]", " ", " ".join(kept).lower())
    return re.sub(r"\s+", " ", normalized).strip().split()


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
    page_count = int(m.group(1)) if m else 0
    print("PDF_PAGES", page_count, "PRINTED_TO_PDF_OFFSET", PDF_PAGE_OFFSET)

    page_texts: dict[int, dict[int, list[str]]] = {}
    with tempfile.TemporaryDirectory(prefix="h17-childers-ocr-") as td:
        temp = Path(td)
        for printed_page in sorted({p for p, _ in COORDS}):
            pdf_page = printed_page + PDF_PAGE_OFFSET
            if pdf_page < 1 or pdf_page > page_count:
                print("PAGE_OUT_OF_RANGE", printed_page, pdf_page)
                continue
            prefix = temp / f"printed-{printed_page}"
            run([
                "pdftoppm", "-f", str(pdf_page), "-l", str(pdf_page),
                "-r", "400", "-png", "-singlefile", str(pdf), str(prefix),
            ])
            image = prefix.with_suffix(".png")
            modes: dict[int, list[str]] = {}
            for psm in (3, 4, 6):
                ocr = run(["tesseract", str(image), "stdout", "--psm", str(psm)])
                modes[psm] = tokenize_ocr(ocr)
            page_texts[printed_page] = modes
            print("PAGE_OCR_COUNTS", printed_page, {
                psm: len(words) for psm, words in modes.items()
            })

    for psm in (3, 4, 6):
        picked: list[str] = []
        valid = True
        for page, word in COORDS:
            words = page_texts.get(page, {}).get(psm)
            idx = word - 1
            if words is None or idx < 0 or idx >= len(words):
                valid = False
                picked.append(f"<missing:{page}/{word}:count={len(words) if words is not None else 'no-page'}>")
            else:
                picked.append(words[idx])
        if not valid:
            print("CANDIDATE", "psm", psm, "INVALID", picked)
            continue
        phrase, component, matched = hmac_match(picked)
        print("CANDIDATE", "psm", psm, "words", picked, "phrase", phrase,
              "component", component, "K08_MATCH", matched)

    print("CHILDERS_PAGEWORD_PROBE_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
