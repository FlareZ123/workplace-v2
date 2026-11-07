#!/usr/bin/env python3
"""OCR the public 1903 Nelson Riddle scan and test K08 ticket-page word 103.

This tests a speculative page-word interpretation only. It does not establish that
The Riddle of the Sands was the physical map-back book in the H-17 archive.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.parse
import urllib.request
from io import BytesIO

import fitz
import pytesseract
from PIL import Image

FILE_TITLE = "The Riddle of the Sands- A Record of Secret Service (IA dli.granth.107255).pdf"
TICKET_PAGE_ORDER = [94, 81, 106, 99, 112, 130, 151, 121, 135, 142]
PDF_PAGE_OFFSET = 4  # PDF page 13 is printed roman page ix; page 19 starts printed p.15.
WORD_POSITIONS = (103, 104)
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
    request = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{params}",
        headers={"User-Agent": "H17-Archive-Research/1.0 (public-domain source retrieval)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        metadata = json.load(response)
    page = next(iter(metadata["query"]["pages"].values()))
    pdf_url = page["imageinfo"][0]["url"]
    print("Public scan:", page.get("title"))
    print("PDF URL:", pdf_url)

    request = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "H17-Archive-Research/1.0 (public-domain source retrieval)"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    print("Downloaded PDF bytes:", len(data))
    return data


def ocr_pdf_page(document: fitz.Document, pdf_page_number: int) -> str:
    page = document.load_page(pdf_page_number - 1)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
    image = Image.open(BytesIO(pixmap.tobytes("png")))
    return pytesseract.image_to_string(image, lang="eng", config="--psm 6")


def clean_page_text(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.casefold() in {"the riddle of the sands", "erskine childers"}:
            continue
        if re.fullmatch(r"[ivxlcdm]+|\d+", line, re.I):
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
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    print("PDF page count:", document.page_count)

    first_chapter = clean_page_text(ocr_pdf_page(document, 19))
    print("PDF page 19 OCR check:", first_chapter[:360])

    page_texts = {}
    for printed_page in TICKET_PAGE_ORDER:
        pdf_page_number = printed_page + PDF_PAGE_OFFSET
        text = clean_page_text(ocr_pdf_page(document, pdf_page_number))
        if not text.strip():
            raise RuntimeError(f"OCR returned no text for printed page {printed_page}")
        page_texts[printed_page] = text
        print(f"Printed page {printed_page} / PDF page {pdf_page_number} OCR words:",
              len(re.findall(r"[A-Za-z0-9]+", text)))

    for tokenizer_name, tokenizer in TOKENIZERS.items():
        tokens_by_page = {
            page: tokenizer.findall(text)
            for page, text in page_texts.items()
        }
        for word_position in WORD_POSITIONS:
            words = []
            for page in TICKET_PAGE_ORDER:
                tokens = tokens_by_page[page]
                if len(tokens) < word_position:
                    raise RuntimeError(
                        f"Page {page} has only {len(tokens)} tokens for word {word_position}"
                    )
                words.append(tokens[word_position - 1])

            phrase = normalized_phrase(words)
            slot_hex, digest = slot_digest(phrase)
            print({
                "tokenizer": tokenizer_name,
                "word_position_1based": word_position,
                "ticket_tab_order": TICKET_PAGE_ORDER,
                "words": words,
                "normalized_phrase": phrase,
                "derived_slot_hex": slot_hex,
                "slot_sha256": digest,
                "acceptance_match": digest == EXPECTED_SLOT_SHA256,
            })
            if digest == EXPECTED_SLOT_SHA256:
                print("K08 PAGE-WORD CANDIDATE ACCEPTED BY THE PUBLISHED COMMITMENT")


if __name__ == "__main__":
    main()
