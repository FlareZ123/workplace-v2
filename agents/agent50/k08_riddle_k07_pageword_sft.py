#!/usr/bin/env python3
"""Test accepted AX-7782 K07 checkpoints as page/word coordinates in the 1903 Riddle candidate.

This is a bounded cross-slot hypothesis, distinct from the already-tested
absolute-word-offset interpretation. The book identity is not authenticated as
David's physical map-back book.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import re
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "work" / "agent50-k07-riddle-pageword"
EXPECTED_K08_SHA256 = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_report(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_k07_checkpoints(acceptance: dict[str, Any]) -> tuple[list[int], bytes, bytes]:
    audit_path = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
    rows = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    commits = [
        row for row in rows
        if row.get("kind") == "COMMIT"
        and row.get("transfer") == "AX-7782"
        and row.get("dry_run") is False
        and row.get("chunks") == 8
        and row.get("object") == "IR-261003-H17"
    ]
    if len(commits) != 1:
        raise RuntimeError(f"expected one committed AX-7782 8-chunk transfer, found {len(commits)}")
    selected = []
    for seq in range(8):
        candidates = [
            row for row in rows
            if row.get("kind") == "CHUNK"
            and row.get("transfer") == "AX-7782"
            and row.get("object") == "IR-261003-H17"
            and row.get("seq") == seq
        ]
        if not candidates:
            raise RuntimeError(f"no AX-7782 checkpoint for seq {seq}")
        selected.append(max(candidates, key=lambda row: int(row["attempt"])))
    values = [int(row["checkpoint"], 16) for row in selected]
    raw = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
    component = hashlib.sha256(raw).digest()[:16]
    actual = sha256(component)
    expected = acceptance["slot_sha256"]["K07"]
    if actual != expected:
        raise RuntimeError(f"reconstructed K07 fails unchanged commitment: {actual} != {expected}")
    return values, raw, component


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
    if acceptance["slot_sha256"]["K08"] != EXPECTED_K08_SHA256:
        raise RuntimeError("K08 acceptance commitment changed")

    values, k07_preimage, k07_component = load_k07_checkpoints(acceptance)
    big_endian = [(value >> 8, value & 0xFF) for value in values]
    little_endian = [(value & 0xFF, value >> 8) for value in values]
    coordinate_sets = {
        "checkpoint_hi_page_lo_word": big_endian,
        "checkpoint_lo_page_hi_word": little_endian,
    }

    riddle = importlib.import_module("agents.agent32.k08_riddle_pageword_sft")
    if bytes.fromhex(routing["K08"]["desk_nonce"].replace(" ", "")) != riddle.DESK_NONCE:
        raise RuntimeError("desk nonce differs from pinned K08 source")
    n02 = riddle.slot_digest(riddle.normalized_phrase(
        "a good watch leaves the room ready for the next pair of hands".split()
    ))
    if n02[0] != EXPECTED_N02_HMAC16 or n02[1] == EXPECTED_K08_SHA256:
        raise RuntimeError("N02 positive HMAC control failed")

    pdf_bytes = riddle.download_public_pdf()
    reader = PdfReader(BytesIO(pdf_bytes))
    if len(reader.pages) < 336 + riddle.PDF_PAGE_OFFSET:
        raise RuntimeError(f"public Riddle PDF unexpectedly short: {len(reader.pages)} pages")

    # Retain the same printed-page crosswalk and text cleanup as the existing
    # Riddle page-word method. Test standard 0/1-based page and word conventions.
    page_texts: dict[int, str] = {}
    page_reports: dict[str, Any] = {}
    requested_pages = sorted({
        page + page_base
        for coords in coordinate_sets.values()
        for page, _ in coords
        for page_base in (0, 1)
    })
    for printed_page in requested_pages:
        pdf_page_number = printed_page + riddle.PDF_PAGE_OFFSET
        if not 1 <= pdf_page_number <= len(reader.pages):
            page_reports[str(printed_page)] = {"status": "OUT_OF_RANGE", "pdf_page": pdf_page_number}
            continue
        text = reader.pages[pdf_page_number - 1].extract_text() or ""
        if not text.strip():
            page_reports[str(printed_page)] = {"status": "NO_EMBEDDED_TEXT", "pdf_page": pdf_page_number}
            continue
        clean = riddle.clean_page_text(text, printed_page)
        page_texts[printed_page] = clean
        page_reports[str(printed_page)] = {
            "status": "EXTRACTED",
            "printed_page": printed_page,
            "pdf_page": pdf_page_number,
            "raw_text_sha256": sha256(text.encode("utf-8")),
            "clean_text_sha256": sha256(clean.encode("utf-8")),
            "raw_characters": len(text),
            "clean_characters": len(clean),
        }

    report: dict[str, Any] = {
        "status": "INCOMPLETE",
        "hypothesis": (
            "The eight accepted AX-7782 K07 16-bit checkpoints are (printed page, "
            "body-word position) pairs into the map-back 1903 Riddle candidate. "
            "This is a cross-slot test, not proof of the physical book identity."
        ),
        "source": {
            "transfer": "AX-7782",
            "checkpoint_values_hex": [f"{value:04X}" for value in values],
            "checkpoint_preimage_hex": k07_preimage.hex().upper(),
            "accepted_K07_component_hex": k07_component.hex().upper(),
            "K07_commitment_verified": True,
            "book_candidate": "The Riddle of the Sands, Smith, Elder, 1903",
            "public_pdf_source": riddle.FILE_TITLE,
            "pdf_page_count": len(reader.pages),
            "printed_page_offset": riddle.PDF_PAGE_OFFSET,
            "book_identity_status": "candidate only; not authenticated as David's physical book",
        },
        "coordinate_sets": coordinate_sets,
        "page_bases_tested": [0, 1],
        "word_bases_tested": [0, 1],
        "tokenizers": {name: pattern.pattern for name, pattern in riddle.TOKENIZERS.items()},
        "N02_positive_control": {"hmac16": n02[0], "sha256": n02[1]},
        "page_results": page_reports,
        "candidate_results": {},
    }
    write_report(report)

    for orientation, coords in coordinate_sets.items():
        for page_base in (0, 1):
            for word_base in (0, 1):
                for tokenizer_name, tokenizer in riddle.TOKENIZERS.items():
                    label = f"{orientation}_page_base_{page_base}_word_base_{word_base}_{tokenizer_name}"
                    words = []
                    contexts = []
                    error = None
                    for page, word_position in coords:
                        printed_page = page + page_base
                        clean = page_texts.get(printed_page)
                        if clean is None:
                            error = f"printed page {printed_page} has no embedded text"
                            break
                        tokens = tokenizer.findall(clean)
                        index = word_position - word_base
                        if not 0 <= index < len(tokens):
                            error = (
                                f"printed page {printed_page} has {len(tokens)} tokens; "
                                f"requested word {word_position} with base {word_base}"
                            )
                            break
                        words.append(tokens[index])
                        contexts.append({
                            "printed_page": printed_page,
                            "pdf_page": printed_page + riddle.PDF_PAGE_OFFSET,
                            "word_position": word_position,
                            "word_base": word_base,
                            "selected_word": tokens[index],
                            "context": tokens[max(0, index - 4):index + 3],
                            "token_count": len(tokens),
                        })
                    if error:
                        report["candidate_results"][label] = {
                            "status": "INCOMPLETE",
                            "error": error,
                            "coordinate_pairs": coords,
                        }
                    else:
                        phrase = riddle.normalized_phrase(words)
                        slot_hex, digest = riddle.slot_digest(phrase)
                        report["candidate_results"][label] = {
                            "status": "MATCH" if digest == EXPECTED_K08_SHA256 else "NO_MATCH",
                            "words": words,
                            "normalized_phrase": phrase,
                            "derived_slot_hex": slot_hex,
                            "slot_sha256": digest,
                            "acceptance_match": digest == EXPECTED_K08_SHA256,
                            "coordinate_pairs": coords,
                            "page_base": page_base,
                            "word_base": word_base,
                            "tokenizer": tokenizer_name,
                            "selected_word_context": contexts,
                        }
                    write_report(report)
                    print("K07_RIDDLE_CANDIDATE " + label + " " + json.dumps(report["candidate_results"][label], sort_keys=True), flush=True)

    statuses = [row["status"] for row in report["candidate_results"].values()]
    report["status"] = (
        "COMPLETE" if len(statuses) == 16 and all(s in {"MATCH", "NO_MATCH"} for s in statuses)
        else "PARTIAL"
    )
    write_report(report)
    print("K07_RIDDLE_PAGEWORD_COMPLETE " + json.dumps({
        "status": report["status"],
        "candidate_statuses": statuses,
    }, sort_keys=True), flush=True)
    return 0 if report["status"] == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
