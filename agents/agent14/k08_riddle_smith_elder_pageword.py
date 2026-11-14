#!/usr/bin/env python3
"""Fetch and test the signed-WN14/K01 page-word hypothesis against the 1903 Smith, Elder Childers edition.

Frozen input: K01's eight A/B/C/D byte pairs as (printed page, 1-based body word).
This is a bounded candidate construction, not an assertion that the book-cipher rule is authentic.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image
import pytesseract

VOLUME_ID = "vwMYAAAAYAAJ"  # Google Books: Smith, Elder, 1903; 336 printed pages
COORDINATES = [
    (4, 154), (171, 46), (28, 222), (122, 130),
    (205, 124), (96, 35), (67, 3), (201, 26),
]
DESK_NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
EXPECTED_SLOT_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
OUT = Path("riddle-smith-elder-probe")
(OUT / "images").mkdir(parents=True, exist_ok=True)
(OUT / "ocr").mkdir(parents=True, exist_ok=True)


def fetch_page_image(page: int) -> tuple[bytes, str]:
    last_error = None
    for host in ("books.google.com", "books.google.es"):
        url = (
            f"https://{host}/books/content?id={VOLUME_ID}"
            f"&pg=PA{page}&img=1&zoom=3&edge=curl&source=gbs_api"
        )
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; H17-Archive-Preservation/1.0)",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        })
        try:
            with urlopen(req, timeout=45) as response:
                content_type = response.headers.get("Content-Type", "")
                data = response.read()
                if not content_type.startswith("image/"):
                    raise RuntimeError(f"page {page} returned {content_type}: {data[:200]!r}")
                print(f"PAGE_FETCH page={page} host={host} status={response.status} "
                      f"type={content_type} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
                return data, url
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = f"{host}: {type(exc).__name__}: {exc}"
            print(f"PAGE_FETCH_FAIL page={page} {last_error}")
    raise RuntimeError(f"Could not fetch printed page {page}: {last_error}")


def clean_body_lines(text: str, printed_page: int) -> str:
    """Exclude running heads, folios and chapter display headings; retain body prose."""
    kept = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        upper = line.upper().strip(" .:-—")
        if upper in {"THE RIDDLE OF THE SANDS", "ERSKINE CHILDERS"}:
            continue
        if re.fullmatch(r"\d{1,3}", upper):
            continue
        if re.fullmatch(r"(?:CHAPTER\s+)?[IVXLCDM]+", upper):
            continue
        # The known Chapter XX display title is not body prose.
        if upper == "THE LITTLE DRAB BOOK":
            continue
        kept.append(line)
    return "\n".join(kept)


def normalize_phrase(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def verify_phrase(words: list[str]) -> dict[str, object]:
    phrase = normalize_phrase(words)
    slot = hmac.new(DESK_NONCE, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    digest = hashlib.sha256(slot).hexdigest()
    return {
        "words": words,
        "normalized_phrase": phrase,
        "derived_slot_hex": slot.hex().upper(),
        "slot_sha256": digest,
        "acceptance_match": digest == EXPECTED_SLOT_SHA256,
    }


def main() -> None:
    results = []
    page_texts = {}
    for page in sorted({p for p, _ in COORDINATES}):
        image_bytes, source_url = fetch_page_image(page)
        image_path = OUT / "images" / f"page-{page}.png"
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image.save(image_path)
        print(f"PAGE_IMAGE page={page} size={image.size} file={image_path}")
        # PSM 4 is the frozen single-column body-text OCR mode.
        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        (OUT / "ocr" / f"page-{page}.txt").write_text(ocr, encoding="utf-8")
        body = clean_body_lines(ocr, page)
        tokens = re.findall(r"[A-Za-z0-9]+", body.lower())
        page_texts[page] = tokens
        print(f"PAGE_OCR page={page} tokens={len(tokens)} "
              f"selected_positions={[w for p, w in COORDINATES if p == page]} "
              f"first_tokens={tokens[:12]}")
        results.append({
            "printed_page": page,
            "source_url": source_url,
            "image_size": image.size,
            "ocr_token_count": len(tokens),
            "selected_positions": [w for p, w in COORDINATES if p == page],
        })

    selected = []
    missing = []
    for page, word_position in COORDINATES:
        tokens = page_texts[page]
        if not 1 <= word_position <= len(tokens):
            missing.append({"page": page, "word_position": word_position, "token_count": len(tokens)})
        else:
            selected.append(tokens[word_position - 1])

    report = {
        "volume_id": VOLUME_ID,
        "coordinates_page_word_1based_body_tokens": COORDINATES,
        "token_rule": "OCR body text only; exclude running heads, folios and chapter display headings; split on ASCII letters/digits",
        "page_results": results,
        "missing": missing,
    }
    if not missing:
        report["candidate"] = verify_phrase(selected)
        print("K08_CANDIDATE " + json.dumps(report["candidate"], sort_keys=True))
        if report["candidate"]["acceptance_match"]:
            print("K08_ORIGINAL_COMMITMENT_MATCH")
    else:
        print("K08_CANDIDATE_INCOMPLETE " + json.dumps(missing, sort_keys=True))

    (OUT / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PROBE_COMPLETE")


if __name__ == "__main__":
    main()
