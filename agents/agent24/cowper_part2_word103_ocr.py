#!/usr/bin/env python3
"""Reproduce the frozen Cowper Part II one-based word-103 extraction.

The image files are the signed Google Books page captures committed beside
manifest.json. This script does not try alternate offsets, editions, books,
page orders, or tokenization rules.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageOps
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "results" / "assets" / "cowper" / "part2-1893"
PAGE_ORDER = [130, 151, 121, 135, 142]
WORD_INDEX = 103
TOP_CROP_PX = 150
BOTTOM_CROP_PX = 60
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def normalize(text: str) -> str:
    """Apply the exact K08 normalization to the selected phrase only."""
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def join_line_wrap_hyphens(text: str) -> str:
    """Join a printed word split by a line-end hyphen and newline."""
    return re.sub(
        r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])",
        "",
        text,
    )


def main() -> None:
    manifest_path = ASSET_DIR / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_by_page = {entry["printedPage"]: entry for entry in manifest}

    version = subprocess.run(
        ["tesseract", "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()[0]

    pages = []
    selected_words = []
    for page_number in PAGE_ORDER:
        entry = manifest_by_page[page_number]
        image_path = ASSET_DIR / f"p{page_number}.img"
        image_bytes = image_path.read_bytes()
        image_sha = hashlib.sha256(image_bytes).hexdigest()
        if len(image_bytes) != entry["bytes"] or image_sha != entry["sha256"]:
            raise ValueError(f"Source image pin failed for printed page {page_number}")
        if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"Expected PNG image for printed page {page_number}")

        image = Image.open(image_path).convert("L")
        width, height = image.size
        if height <= TOP_CROP_PX + BOTTOM_CROP_PX:
            raise ValueError(f"Unexpected image dimensions for page {page_number}")
        body = image.crop((0, TOP_CROP_PX, width, height - BOTTOM_CROP_PX))
        body = ImageOps.autocontrast(body)
        raw_ocr = pytesseract.image_to_string(body, lang="eng", config="--psm 6")
        joined_body = join_line_wrap_hyphens(raw_ocr)
        tokens = WORD_PATTERN.findall(joined_body)
        if len(tokens) < WORD_INDEX:
            raise ValueError(
                f"Only {len(tokens)} main-body word tokens on page {page_number}"
            )

        word = tokens[WORD_INDEX - 1]
        selected_words.append(word)
        context_start = max(0, WORD_INDEX - 7)
        context_end = min(len(tokens), WORD_INDEX + 6)
        pages.append(
            {
                "printed_page": page_number,
                "image_path": str(image_path.relative_to(ROOT)),
                "image_bytes": len(image_bytes),
                "image_sha256": image_sha,
                "image_dimensions": [width, height],
                "body_crop_pixels": {
                    "top_excluded": TOP_CROP_PX,
                    "bottom_excluded": BOTTOM_CROP_PX,
                },
                "main_body_word_token_count": len(tokens),
                "word_index_1based": WORD_INDEX,
                "word_103": word,
                "context_tokens_97_to_109": tokens[context_start:context_end],
                "tokens_1_to_110": tokens[:110],
                "joined_body_sha256": hashlib.sha256(
                    joined_body.encode("utf-8")
                ).hexdigest(),
                "ocr_text_sha256": hashlib.sha256(
                    raw_ocr.encode("utf-8")
                ).hexdigest(),
            }
        )

    south_raw = " ".join(selected_words)
    result = {
        "status": "PART_II_WORDS_EXTRACTED_ONLY",
        "supersedes": (
            "The initial run used K08-normalized page tokens before selection. "
            "That was not the Critic's specified order of operations and is superseded."
        ),
        "frozen_candidate": {
            "book": "Frank Cowper, Sailing Tours, Part II",
            "edition": 1893,
            "binder_tab_order_south_pages": PAGE_ORDER,
            "word_index_1based": WORD_INDEX,
            "part_ii_words_in_order": selected_words,
            "part_ii_fragment_after_single_k08_normalization": normalize(south_raw),
        },
        "counting_convention": (
            "Main body only: exclude running head, printed folio and Google "
            "watermark using the recorded crop; include all visible body "
            "headings, captions, tables and footnotes. Join line-wrap "
            "hyphenation across a line break, retain genuine in-line "
            "hyphenated compounds as one word, and count visual-order word "
            "tokens (including dotted abbreviations and fractions) before "
            "normalization. Select token 103, one-based, from each page. "
            "Concatenate selected words in binder-tab order and apply the "
            "unchanged K08 normalizer once to the resulting phrase. No "
            "alternate offsets, tokenizations, page orders or editions were tested."
        ),
        "ocr": {
            "engine": version,
            "language": "eng",
            "page_segmentation_mode": 6,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        },
        "pages": pages,
        "limitations": [
            "OCR word positions require visual review against each captured page.",
            "This is only the South/Part II half of the frozen ten-page candidate.",
            "No K08 HMAC or acceptance test is performed until the five North words are available.",
        ],
    }

    output = ASSET_DIR / "word103-ocr.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
