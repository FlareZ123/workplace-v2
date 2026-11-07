#!/usr/bin/env python3
"""Test the H-17 K08 ticket-page / word-103 hypothesis against a public 1903 Riddle scan.

This is an exploratory candidate test. It does not assert that the physical map-back
book was The Riddle of the Sands, or that ticket suffixes are page numbers.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.parse
import urllib.request
from io import BytesIO

from pypdf import PdfReader

FILE_TITLE = "The Riddle of the Sands- A Record of Secret Service (IA dli.granth.107255).pdf"
TICKET_PAGE_ORDER = [94, 81, 106, 99, 112, 130, 151, 121, 135, 142]
PDF_PAGE_OFFSET = 4  # Wikisource PDF page 13 is printed roman page ix.
WORD_POSITIONS = (103, 104)  # 1-based word 103, plus an explicit off-by-one control.
DESK_NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_SLOT_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

TOKENIZERS = {
    "apostrophes-kept": re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*"),
    "punctuation-split": re.compile(r"[A-Za-z0-9]+"),
}


def download_public_pdf() -> bytes:
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": f"File:{FILE_TITLE}",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    })
    api_url = f"https://commons.wikimedia.org/w/api.php?{params}"
    request = urllib.request.Request(
        api_url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public-domain source retrieval)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        metadata = json.load(response)

    pages = metadata["query"]["pages"]
    page = next(iter(pages.values()))
    imageinfo = page.get("imageinfo")
    if not imageinfo:
        raise RuntimeError(f"Commons returned no file URL: {metadata!r}")
    pdf_url = imageinfo[0]["url"]
    print(f"Public scan: {page.get('title')}")
    print(f"PDF source: {pdf_url}")

    request = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public-domain source retrieval)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    print(f"PDF bytes downloaded: {len(data)}")
    return data


def clean_page_text(text: str, printed_page: int) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.casefold() in {"the riddle of the sands", "erskine childers"}:
            continue
        if line == str(printed_page):
            continue
        lines.append(line)
    return "\n".join(lines)


def normalized_phrase(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def slot_digest(phrase: str) -> tuple[str, str]:
    slot = hmac.new(DESK_NONCE, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    return slot.hex().upper(), hashlib.sha256(slot).hexdigest()


def main() -> None:
    pdf_bytes = download_public_pdf()
    reader = PdfReader(BytesIO(pdf_bytes))
    print(f"PDF page count: {len(reader.pages)}")

    # Check the published scan/page crosswalk before extracting ticket pages.
    page13 = reader.pages[12].extract_text() or ""
    print(f"PDF page 13 excerpt: {page13[:220]!r}")
    page19 = reader.pages[18].extract_text() or ""
    print(f"PDF page 19 excerpt: {page19[:320]!r}")
    first_chapter_pages = [
        index + 1 for index, page in enumerate(reader.pages)
        if re.search(r"\bTHE\s+LETTER\b", page.extract_text() or "", re.I)
    ]
    print(f"Pages containing chapter heading 'The Letter': {first_chapter_pages[:12]}")

    page_texts: dict[int, str] = {}
    for printed_page in TICKET_PAGE_ORDER:
        pdf_page_number = printed_page + PDF_PAGE_OFFSET
        if not 1 <= pdf_page_number <= len(reader.pages):
            raise RuntimeError(f"Mapped PDF page {pdf_page_number} is out of range")
        page_text = reader.pages[pdf_page_number - 1].extract_text() or ""
        if not page_text.strip():
            raise RuntimeError(
                f"No embedded OCR text on printed page {printed_page} "
                f"(PDF page {pdf_page_number})"
            )
        page_texts[printed_page] = clean_page_text(page_text, printed_page)

    for tokenizer_name, tokenizer in TOKENIZERS.items():
        page_tokens = {
            page: tokenizer.findall(text)
            for page, text in page_texts.items()
        }
        print(f"\nTokenizer: {tokenizer_name}")
        print("Page token counts:", {page: len(tokens) for page, tokens in page_tokens.items()})

        for word_position in WORD_POSITIONS:
            words = []
            missing = []
            for page in TICKET_PAGE_ORDER:
                tokens = page_tokens[page]
                if len(tokens) < word_position:
                    missing.append((page, len(tokens)))
                else:
                    words.append(tokens[word_position - 1])

            if missing:
                print(f"word {word_position}: insufficient tokens {missing}")
                continue

            phrase = normalized_phrase(words)
            slot_hex, digest = slot_digest(phrase)
            matched = digest == EXPECTED_SLOT_SHA256
            print({
                "word_position_1based": word_position,
                "words_in_ticket_tab_order": words,
                "normalized_phrase": phrase,
                "derived_slot_hex": slot_hex,
                "slot_sha256": digest,
                "acceptance_match": matched,
            })
            if matched:
                print("K08 PAGE-WORD CANDIDATE ACCEPTED BY THE PUBLISHED COMMITMENT")


if __name__ == "__main__":
    main()
