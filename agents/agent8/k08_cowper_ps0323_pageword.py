#!/usr/bin/env python3
"""One bounded exploratory K08 test: PS-0323 AES plaintext as Cowper Part II page/word pairs.

This tests only the source-order, high-byte-page / low-byte-word, one-based
interpretation already used by the signed WN-14 Cowper page-word harness.
Cowper Part II is a candidate book, not an authenticated identification of
David's physical book. A commitment hit would be candidate evidence only.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from PIL import Image, ImageOps
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
ASSET_DIR = ROOT / "results" / "assets" / "cowper" / "part2-ps0323"
EXISTING_MANIFEST = ROOT / "results" / "assets" / "cowper" / "part2-1893" / "manifest.json"

EXPECTED_CIPHERTEXT = "1E51EFD2E5CA8F4E1FC8B49297B3D74F"
EXPECTED_PLAINTEXT = "E5407654D33238607DFA324B94656E1D"
EXPECTED_CALIBRATION_SHA256 = "3b1e1b88244b2c0e15eeabf1f3f0d72d4cc6f0127256c55e0bc8e3978c3d0083"
EXPECTED_CALIBRATION_WORD103 = "sailing"
TOP_CROP_PX = 150
BOTTOM_CROP_PX = 60
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_k08(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def join_line_wrap_hyphens(text: str) -> str:
    return re.sub(r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])", "", text)


def decrypt_payload(key: bytes, ciphertext: bytes) -> bytes:
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def extract_word(image_path: Path, one_based_index: int) -> dict:
    image_bytes = image_path.read_bytes()
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Page image is not PNG: " + image_path.name)
    image = Image.open(image_path).convert("L")
    width, height = image.size
    if height <= TOP_CROP_PX + BOTTOM_CROP_PX:
        raise ValueError("Unexpected image dimensions: " + str(image.size))
    body = image.crop((0, TOP_CROP_PX, width, height - BOTTOM_CROP_PX))
    body = ImageOps.autocontrast(body)
    raw_ocr = pytesseract.image_to_string(body, lang="eng", config="--psm 6")
    joined_body = join_line_wrap_hyphens(raw_ocr)
    tokens = WORD_PATTERN.findall(joined_body)
    if len(tokens) < one_based_index:
        raise ValueError(
            image_path.name + " has only " + str(len(tokens)) +
            " body tokens; requested one-based word " + str(one_based_index)
        )
    start = max(0, one_based_index - 7)
    end = min(len(tokens), one_based_index + 6)
    return {
        "image_sha256": sha256(image_bytes),
        "image_bytes": len(image_bytes),
        "image_dimensions": [width, height],
        "main_body_word_token_count": len(tokens),
        "requested_word_index_1based": one_based_index,
        "selected_word": tokens[one_based_index - 1],
        "context_tokens": tokens[start:end],
        "ocr_text_sha256": sha256(raw_ocr.encode("utf-8")),
        "joined_body_sha256": sha256(joined_body.encode("utf-8")),
    }


def main() -> None:
    spool_path = EVIDENCE / "print" / "spool-reconstruction.log"
    spool_text = spool_path.read_text(encoding="utf-8")
    matches = re.findall(
        r"JOB=PS-261003-0323\s+ATTEMPT=1\s+STATE=ACK\s+CLASS=RECOVER\s+PAYLOAD=([0-9A-F]{32})\s+DEST=store",
        spool_text,
    )
    if len(matches) != 1:
        raise ValueError("Expected exactly one ACK/RECOVER/store PS-0323 payload")
    ciphertext_hex = matches[0]
    if ciphertext_hex != EXPECTED_CIPHERTEXT:
        raise ValueError("PS-0323 source payload differs from pinned ciphertext")

    route_path = EVIDENCE / "recovery-routing.json"
    acceptance_path = ROOT / "resources" / "acceptance.json"
    route_bytes = route_path.read_bytes()
    acceptance_bytes = acceptance_path.read_bytes()
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    plaintext = decrypt_payload(nonce, bytes.fromhex(ciphertext_hex))
    plaintext_hex = plaintext.hex().upper()
    if plaintext_hex != EXPECTED_PLAINTEXT:
        raise ValueError("PS-0323 AES-ECB plaintext differs from pinned value")

    pairs = [(plaintext[i], plaintext[i + 1]) for i in range(0, 16, 2)]
    # Frozen convention: each pair is (printed page, one-based main-body word).
    page_word_pairs = [{"page": page, "word_1based": word} for page, word in pairs]

    manifest_bytes = (ASSET_DIR / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_by_page = {entry["printed_page"]: entry for entry in manifest}
    existing_manifest = json.loads(EXISTING_MANIFEST.read_text(encoding="utf-8"))
    calibration_expected = next(
        item for item in existing_manifest if item["printedPage"] == 121
    )
    if calibration_expected["sha256"] != EXPECTED_CALIBRATION_SHA256:
        raise ValueError("Existing Cowper page-121 calibration pin changed")

    # Positive control: same edition/page capture and same OCR convention.
    calibration_path = ASSET_DIR / "p121.png"
    calibration = extract_word(calibration_path, 103)
    if calibration["image_sha256"] != EXPECTED_CALIBRATION_SHA256:
        raise ValueError("Captured p.121 image does not match the pinned Cowper scan")
    if calibration["selected_word"].lower() != EXPECTED_CALIBRATION_WORD103:
        raise ValueError("Cowper p.121 word-103 OCR calibration failed")

    pages = []
    selected_words = []
    for page, word_index in pairs:
        entry = manifest_by_page.get(page)
        if entry is None:
            raise ValueError("Missing captured printed page " + str(page))
        image_path = ASSET_DIR / entry["filename"]
        extracted = extract_word(image_path, word_index)
        if extracted["image_sha256"] != entry["sha256"]:
            raise ValueError("Page image hash mismatch on printed page " + str(page))
        selected_words.append(extracted["selected_word"])
        pages.append({
            "printed_page": page,
            "word_index_1based": word_index,
            **extracted,
        })

    raw_phrase = " ".join(selected_words)
    normalized_phrase = normalize_k08(raw_phrase)
    component = hmac.new(nonce, normalized_phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    component_hash = sha256(component)
    target_hash = acceptance["slot_sha256"]["K08"]

    result = {
        "status": "MATCH" if component_hash == target_hash else "NO_MATCH",
        "hypothesis": (
            "Decrypt PS-0323 ACK/RECOVER payload with the documented K08 desk nonce "
            "as AES-128-ECB key; interpret plaintext bytes left-to-right as eight "
            "(printed page, one-based main-body word) pairs in Cowper Sailing Tours, "
            "Part II (1893)."
        ),
        "book": {
            "title": "Sailing Tours",
            "author": "Frank Cowper",
            "part": "Part II",
            "edition": 1893,
            "google_books_id": "o7P-qis2u9IC",
            "identity_status": "candidate only; not authenticated as David's map-back book",
        },
        "source_pins": {
            "spool_reconstruction_sha256": sha256(spool_path.read_bytes()),
            "recovery_routing_sha256": sha256(route_bytes),
            "acceptance_sha256": sha256(acceptance_bytes),
            "capture_manifest_sha256": sha256(manifest_bytes),
            "ciphertext_hex": ciphertext_hex,
            "desk_nonce_hex": nonce.hex().upper(),
            "plaintext_hex": plaintext_hex,
        },
        "coordinate_convention": (
            "High byte is printed page; low byte is one-based main-body word; "
            "source byte order is preserved; no alternate orientation, offset, "
            "edition, page order, or tokenization is tested."
        ),
        "page_word_pairs": page_word_pairs,
        "calibration": {
            "printed_page": 121,
            "expected_image_sha256": EXPECTED_CALIBRATION_SHA256,
            "expected_word103": EXPECTED_CALIBRATION_WORD103,
            **calibration,
        },
        "candidate": {
            "selected_words": selected_words,
            "raw_phrase": raw_phrase,
            "normalized_phrase": normalized_phrase,
            "hmac16_hex": component.hex().upper(),
            "component_sha256": component_hash,
            "target_sha256": target_hash,
            "commitment_match": component_hash == target_hash,
        },
        "pages": pages,
        "ocr_engine": subprocess.run(
            ["tesseract", "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0],
        "limitations": [
            "The AES use of desk_nonce is speculative; the routing file documents it as the K08 HMAC key.",
            "The PS-0323-to-envelope relationship is not authenticated by a native print manifest.",
            "Cowper Part II is not authenticated as David's physical book.",
            "The byte-pair page/word interpretation is inferred, not stated in the source.",
            "A commitment hit would be a strong candidate result but would not establish source provenance or physical-book identity.",
            "A miss rejects only this exact Cowper Part II coordinate hypothesis.",
        ],
    }
    out = ASSET_DIR / "result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
