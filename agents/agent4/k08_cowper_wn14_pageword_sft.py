#!/usr/bin/env python3
"""One frozen K08 candidate: signed WN-14 byte pairs as Cowper Part II page/word coordinates.

This is a hypothesis test, not an assertion that David's map-back book was Cowper.
It uses the signed groups A-D in source order, interprets each consecutive byte
pair as (printed page, one-based main-body word), and tests exactly one phrase.
No alternate editions, offsets, page orders, tokenizations, or paraphrases.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import struct
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
OUT = ROOT / "results" / "assets" / "cowper" / "part2-wn14"
BOOK_ID = "o7P-qis2u9IC"
EDITION = 1893
CALIBRATION_PAGE = 121
TOP_CROP_PX = 150
BOTTOM_CROP_PX = 60
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")
GROUP_PATTERN = re.compile(r"WN-14\s*/\s*group\s+([A-D])\s*/\s*([0-9A-F]{8})", re.I)
EXPECTED_GROUPS = OrderedDict([
    ("A", "049AAB2E"),
    ("B", "1CDE7A82"),
    ("C", "CD7C6023"),
    ("D", "4303C91A"),
])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_k08(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def join_line_wrap_hyphens(text: str) -> str:
    return re.sub(
        r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])",
        "",
        text,
    )


def source_groups() -> tuple[dict[str, str], dict[str, str]]:
    found: dict[str, str] = {}
    source_hashes: dict[str, str] = {}
    for filename in ("mail/03.eml", "mail/06.eml"):
        path = EVIDENCE / filename
        data = path.read_bytes()
        source_hashes[filename] = sha256(data)
        for group, value in GROUP_PATTERN.findall(data.decode("utf-8")):
            group = group.upper()
            value = value.upper()
            if group in found and found[group] != value:
                raise ValueError(f"Conflicting WN-14 group {group}")
            found[group] = value

    confirmation_path = EVIDENCE / "mail/14.eml"
    confirmation = confirmation_path.read_bytes()
    confirmation_text = confirmation.decode("utf-8")
    if "No replacement groups were issued." not in confirmation_text:
        raise ValueError("MAIL-14 no-replacement confirmation changed")
    if "A, then B, then C, then D remains the order." not in " ".join(confirmation_text.split()):
        raise ValueError("MAIL-14 group-order confirmation changed")
    source_hashes["mail/14.eml"] = sha256(confirmation)

    if found != dict(EXPECTED_GROUPS):
        raise ValueError(f"Signed WN-14 source groups changed: {found!r}")
    return found, source_hashes


def page_word_pairs(groups: dict[str, str]) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for group in "ABCD":
        raw = bytes.fromhex(groups[group])
        pairs.extend((raw[i], raw[i + 1]) for i in range(0, 4, 2))
    return pairs


def png_dimensions(data: bytes) -> list[int] | None:
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    return list(struct.unpack(">II", data[16:24]))


def request_page(page: int) -> tuple[dict, bytes | None]:
    """Use source-pinned signed viewer captures; unsigned image URLs did not calibrate."""
    captured = OUT / "captured"
    manifest = json.loads((captured / "manifest.json").read_text(encoding="utf-8"))
    match = next((entry for entry in manifest if entry["printed_page"] == page), None)
    if match is None:
        return {"printed_page": page, "error": "Missing signed-viewer page record"}, None
    record = dict(match)
    if "error" in record:
        return record, None
    data = (captured / record["filename"]).read_bytes()
    if sha256(data) != record["sha256"]:
        raise ValueError(f"Captured signed page {page} digest mismatch")
    record["png_dimensions"] = png_dimensions(data)
    return record, data


def extract_word(image_bytes: bytes, one_based_index: int, page_number: int) -> dict:
    image = Image.open(BytesIO(image_bytes)).convert("L")
    width, height = image.size
    if height <= TOP_CROP_PX + BOTTOM_CROP_PX:
        raise ValueError(f"Unexpected page image dimensions: {image.size}")
    body = image.crop((0, TOP_CROP_PX, width, height - BOTTOM_CROP_PX))
    body = ImageOps.autocontrast(body)
    raw_ocr = pytesseract.image_to_string(body, lang="eng", config="--psm 6")
    joined_body = join_line_wrap_hyphens(raw_ocr)
    manual_ocr_corrections = []
    if page_number == 121:
        # Source-visible page 121 reads "have 24ft. over them"; Tesseract
        # outputs "have 2¢ft. over them". Use the same single correction
        # already frozen by Agent24's signed-image word103 calibration.
        match = re.search(
            r"\bhave\b(?P<middle>.{0,40}?)\bover\s+them\b",
            joined_body,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match is None or " ".join(match.group("middle").split()) != "2¢ft.":
            raise ValueError("Signed page 121 source-visible OCR span changed")
        joined_body = (
            joined_body[:match.start("middle")]
            + " 24ft "
            + joined_body[match.end("middle"):]
        )
        manual_ocr_corrections.append({
            "original_ocr_span": "2¢ft.",
            "source_visible_print": "24ft.",
            "corrected_ocr_span": "24ft",
        })
    tokens = WORD_PATTERN.findall(joined_body)
    if len(tokens) < one_based_index:
        return {
            "image_dimensions": [width, height],
            "manual_ocr_corrections": manual_ocr_corrections,
            "main_body_word_token_count": len(tokens),
            "requested_word_index_1based": one_based_index,
            "selected_word": None,
            "context_tokens": [],
            "ocr_text_sha256": sha256(raw_ocr.encode("utf-8")),
        }
    start = max(0, one_based_index - 7)
    end = min(len(tokens), one_based_index + 6)
    return {
        "image_dimensions": [width, height],
        "manual_ocr_corrections": manual_ocr_corrections,
        "main_body_word_token_count": len(tokens),
        "requested_word_index_1based": one_based_index,
        "selected_word": tokens[one_based_index - 1],
        "context_tokens": tokens[start:end],
        "ocr_text_sha256": sha256(raw_ocr.encode("utf-8")),
        "joined_body_sha256": sha256(joined_body.encode("utf-8")),
    }

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    groups, group_source_hashes = source_groups()
    pairs = page_word_pairs(groups)

    route_path = EVIDENCE / "recovery-routing.json"
    acceptance_path = ROOT / "resources" / "acceptance.json"
    route_bytes = route_path.read_bytes()
    acceptance_bytes = acceptance_path.read_bytes()
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target_hash = acceptance["slot_sha256"]["K08"]

    existing_manifest = json.loads(
        (ROOT / "results" / "assets" / "cowper" / "part2-1893" / "manifest.json")
        .read_text(encoding="utf-8")
    )
    calibration = next(x for x in existing_manifest if x["printedPage"] == CALIBRATION_PAGE)

    result = {
        "hypothesis": (
            "Interpret each consecutive pair of bytes in the signed WN-14 groups "
            "A-D as (printed page, one-based main-body word) in Frank Cowper, "
            "Sailing Tours, Part II (1893)."
        ),
        "book": {"title": "Sailing Tours", "author": "Frank Cowper", "part": "Part II", "edition": EDITION, "google_books_id": BOOK_ID},
        "wn14_groups_hex": groups,
        "wn14_source_sha256": group_source_hashes,
        "source_file_sha256": {
            "recovery-routing.json": sha256(route_bytes),
            "acceptance.json": sha256(acceptance_bytes),
        },
        "page_word_pairs_in_source_order": [
            {"group": "ABCD"[i // 2], "page": page, "word_1based": word}
            for i, (page, word) in enumerate(pairs)
        ],
        "coordinate_convention": (
            "Read bytes left-to-right within groups A, B, C, D; each adjacent "
            "pair is (printed page number, one-based main-body word index)."
        ),
        "calibration": {
            "printed_page": CALIBRATION_PAGE,
            "known_image_sha256": calibration["sha256"],
            "known_word103": "sailing",
        },
        "pages": [],
        "status": None,
        "candidate": None,
        "counting_convention": (
            "Use the existing Cowper Part II OCR convention: grayscale page; "
            "exclude the top 150 and bottom 60 pixels (running head and folio); "
            "autocontrast; Tesseract English PSM 6; join line-end hyphenation; "
            "count visual-order main-body tokens matching the existing "
            "WORD_PATTERN; include body headings, captions, tables and footnotes. "
            "Select one-based word positions before K08 normalization."
        ),
        "limitations": [
            "Cowper Part II is a conditional book candidate, not an authenticated identification of David's physical map-back book.",
            "The WN-14 byte-pair page/word interpretation is a hypothesis; the signed source itself does not label these bytes as coordinates.",
            "Only this one page/word order, edition, volume and counting convention are tested.",
        ],
    }

    # Positive retrieval control: the un-signed endpoint must reproduce an
    # already authenticated page image byte-for-byte before any new page is read.
    calibration_record, calibration_bytes = request_page(CALIBRATION_PAGE)
    result["calibration"].update(calibration_record)
    if calibration_bytes is None or sha256(calibration_bytes) != calibration["sha256"]:
        result["status"] = "ACCESS_OR_CALIBRATION_MISMATCH"
        result["calibration"]["match"] = False
        (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return
    result["calibration"]["match"] = True
    calibration_word = extract_word(calibration_bytes, 103, CALIBRATION_PAGE)
    result["calibration"]["ocr_word103"] = calibration_word["selected_word"]
    result["calibration"]["ocr_engine"] = subprocess_version()
    result["calibration"]["ocr_token_count"] = calibration_word["main_body_word_token_count"]
    if calibration_word["selected_word"] != result["calibration"]["known_word103"]:
        result["status"] = "OCR_CALIBRATION_MISMATCH"
        (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return

    selected_words = []
    for page, word_index in pairs:
        record, image_bytes = request_page(page)
        if image_bytes is None:
            record["selected_word"] = None
            result["pages"].append(record)
            result["status"] = "INCOMPLETE_PAGE_ACCESS"
            (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result, indent=2))
            return
        image_path = OUT / f"p{page}.png"
        image_path.write_bytes(image_bytes)
        record["image_path"] = str(image_path.relative_to(ROOT))
        extracted = extract_word(image_bytes, word_index, page)
        record.update(extracted)
        result["pages"].append(record)
        if extracted["selected_word"] is None:
            result["status"] = "INCOMPLETE_WORD_INDEX"
            (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(result, indent=2))
            return
        selected_words.append(extracted["selected_word"])

    raw_phrase = " ".join(selected_words)
    normalized = normalize_k08(raw_phrase)
    component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    component_hash = sha256(component)
    result["candidate"] = {
        "selected_words": selected_words,
        "raw_phrase": raw_phrase,
        "normalized_phrase": normalized,
        "hmac16_hex": component.hex().upper(),
        "component_sha256": component_hash,
        "target_sha256": target_hash,
        "commitment_match": component_hash == target_hash,
    }
    result["status"] = "MATCH" if component_hash == target_hash else "NO_MATCH"
    result["ocr_engine"] = subprocess_version()
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def subprocess_version() -> str:
    import subprocess
    return subprocess.run(
        ["tesseract", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]


if __name__ == "__main__":
    main()
