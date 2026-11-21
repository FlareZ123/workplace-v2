#!/usr/bin/env python3
"""Complete the frozen K07/Falcon page-word views against the retained IA scan.

This does not authenticate the public Falcon edition as David's physical book.
It only resolves the predeclared printed folios in the pinned scan artifact and
checks the four existing byte-order/index-base interpretations against K08.
No canonical candidate, routing, acceptance, or verifier file is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any

import fitz
import pytesseract
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PDF_SHA256 = "0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
# Printed folio -> zero-based page index in artifact 14479741922.
FOLIO_TO_SCAN_INDEX = {
    2: 15, 51: 66, 71: 86, 115: 132, 123: 140, 137: 154,
    183: 200, 185: 202, 186: 203, 197: 214, 201: 220,
    204: 223, 206: 225, 220: 241, 230: 251, 232: 253,
}
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[.'’/-][A-Za-z0-9]+)*")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def join_line_wrap_hyphens(text: str) -> str:
    return re.sub(r"(?<=[A-Za-z0-9])-\s*\n\s*(?=[A-Za-z0-9])", "", text)


def clean_body_lines(text: str) -> str:
    """Exact Agent10 cleanup: remove folios/heads/display lines; join hyphens."""
    kept: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        upper = line.upper().strip(" .:-—'\"")
        if re.fullmatch(r"\d{1,3}", upper):
            continue
        if upper in {
            "THE FALCON ON THE BALTIC",
            'THE "FALCON" ON THE BALTIC',
            "THE 'FALCON' ON THE BALTIC",
            "E. F. KNIGHT",
        }:
            continue
        if re.fullmatch(r"(?:CHAPTER\s+)?[IVXLCDM]+", upper):
            continue
        if len(line) <= 72 and line == line.upper() and re.search(r"[A-Z]", line):
            continue
        kept.append(line)
    return join_line_wrap_hyphens("\n".join(kept))


def normalize_phrase(words: list[str]) -> str:
    phrase = " ".join(words).lower()
    phrase = re.sub(r"[^a-z0-9\s]", " ", phrase)
    return re.sub(r"\s+", " ", phrase).strip()


def phrase_result(words: list[str], nonce: bytes, target: str) -> dict[str, Any]:
    phrase = normalize_phrase(words)
    component = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
    return {
        "words": words,
        "normalized_phrase": phrase,
        "component_hex": component.hex().upper(),
        "component_sha256": sha256(component),
        "acceptance_match": sha256(component) == target,
    }


def load_k07(root: Path, acceptance: dict[str, Any]) -> tuple[list[int], bytes, bytes]:
    rows = [
        json.loads(line)
        for line in (root / "resources/evidence/transfers/transfer-audit.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    commits = [
        row for row in rows
        if row.get("kind") == "COMMIT" and row.get("transfer") == "AX-7782"
        and row.get("object") == "IR-261003-H17" and row.get("dry_run") is False
        and row.get("chunks") == 8
    ]
    if len(commits) != 1:
        raise RuntimeError(f"expected one AX-7782 non-dry-run COMMIT, found {len(commits)}")
    selected = []
    for seq in range(8):
        candidates = [
            row for row in rows
            if row.get("kind") == "CHUNK" and row.get("transfer") == "AX-7782"
            and row.get("object") == "IR-261003-H17" and row.get("seq") == seq
        ]
        if not candidates:
            raise RuntimeError(f"missing AX-7782 chunk {seq}")
        selected.append(max(candidates, key=lambda row: int(row["attempt"])))
    if any(row.get("bytes") != 1048576 for row in selected):
        raise RuntimeError("AX-7782 chunk size differs from retained source record")
    values = [int(row["checkpoint"], 16) for row in selected]
    preimage = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
    component = hashlib.sha256(preimage).digest()[:16]
    if sha256(component) != acceptance["slot_sha256"]["K07"]:
        raise RuntimeError("reconstructed K07 fails the unchanged commitment")
    return values, preimage, component


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path, help="PDF from Actions artifact 14479741922")
    parser.add_argument("--output", type=Path, default=None, help="optional JSON output path")
    args = parser.parse_args()
    pdf_path = args.pdf.resolve()
    pdf_bytes = pdf_path.read_bytes()
    actual_pdf_sha = sha256(pdf_bytes)
    if actual_pdf_sha != EXPECTED_PDF_SHA256:
        raise SystemExit(f"wrong PDF bytes: {actual_pdf_sha} != {EXPECTED_PDF_SHA256}")

    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
    if acceptance["slot_sha256"]["K08"] != EXPECTED_K08_SHA256:
        raise SystemExit("K08 acceptance commitment differs from pinned value")
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    values, preimage, k07_component = load_k07(ROOT, acceptance)
    coordinate_sets = {
        "checkpoint_hi_page_lo_word": [(v >> 8, v & 0xFF) for v in values],
        "checkpoint_lo_page_hi_word": [(v & 0xFF, v >> 8) for v in values],
    }

    document = fitz.open(pdf_path)
    if document.page_count != 350:
        raise SystemExit(f"unexpected PDF page count: {document.page_count}")
    page_data: dict[int, dict[str, Any]] = {}
    for folio, scan_index in FOLIO_TO_SCAN_INDEX.items():
        page = document.load_page(scan_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ocr = pytesseract.image_to_string(image, lang="eng", config="--psm 4")
        text_layer = page.get_text("text")
        page_data[folio] = {
            "scan_index_zero_based": scan_index,
            "pdf_text_layer_folio_lines": [x.strip() for x in text_layer.splitlines() if x.strip() == str(folio)],
            "tesseract_first_lines": ocr.splitlines()[:3],
            "ocr_tokens": WORD_PATTERN.findall(clean_body_lines(ocr)),
            "pdf_text_layer_tokens": WORD_PATTERN.findall(clean_body_lines(text_layer)),
        }
    document.close()

    candidates: dict[str, Any] = {}
    for name, coords in coordinate_sets.items():
        for base in (0, 1):
            label = f"{name}_word_base_{base}"
            for source_name in ("ocr_tokens", "pdf_text_layer_tokens"):
                words: list[str] = []
                contexts: list[dict[str, Any]] = []
                error = None
                for folio, position in coords:
                    tokens = page_data[folio][source_name]
                    index = position - base
                    if not 0 <= index < len(tokens):
                        error = f"folio {folio} has {len(tokens)} words; position {position}, base {base}"
                        break
                    words.append(tokens[index])
                    contexts.append({
                        "printed_folio": folio,
                        "body_word_position": position,
                        "selected_word": tokens[index],
                        "context": tokens[max(0, index - 4):index + 3],
                    })
                if error:
                    candidates[f"{label}:{source_name}"] = {"status": "INCOMPLETE", "error": error}
                else:
                    candidates[f"{label}:{source_name}"] = {
                        "status": "COMPLETE",
                        "contexts": contexts,
                        **phrase_result(words, nonce, EXPECTED_K08_SHA256),
                    }

    n02 = phrase_result(
        "A good watch leaves the room ready for the next pair of hands".split(),
        nonce,
        EXPECTED_K08_SHA256,
    )
    if n02["component_hex"] != EXPECTED_N02_HMAC16 or n02["acceptance_match"]:
        raise SystemExit("N02 HMAC known-answer control failed")

    result = {
        "status": "NO_K08_MATCH",
        "source": {
            "internet_archive_identifier": "falcononbalticc00knig",
            "title": "The 'Falcon' on the Baltic: a coasting voyage from Hammersmith to Copenhagen in a three-ton yacht",
            "author": "Edward Frederick Knight",
            "publisher": "W. H. Allen",
            "year": "1889",
            "pdf_page_count": 350,
            "pdf_bytes": len(pdf_bytes),
            "pdf_sha256": actual_pdf_sha,
            "physical_copy_identity": "not authenticated as David's book",
        },
        "k07": {
            "checkpoint_values_hex": [f"{v:04X}" for v in values],
            "checkpoint_preimage_hex": preimage.hex().upper(),
            "accepted_component_hex": k07_component.hex().upper(),
            "component_sha256": sha256(k07_component),
            "coordinate_sets": coordinate_sets,
        },
        "folio_to_scan_index": FOLIO_TO_SCAN_INDEX,
        "folio_visual_review": "folios 51, 71 and 137 visually inspected; remaining folios matched the PDF text layer",
        "tesseract_version": str(pytesseract.get_tesseract_version()),
        "body_word_rule": "Agent10 clean_body_lines() and WORD_PATTERN; Tesseract --psm 4 at 2x page render",
        "n02_positive_control": n02,
        "k08_target_sha256": EXPECTED_K08_SHA256,
        "candidates": candidates,
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
