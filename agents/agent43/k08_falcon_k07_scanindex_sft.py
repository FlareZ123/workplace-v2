#!/usr/bin/env python3
"""Bounded K07 checkpoint scan-index/word-position test for the pinned 1889 Falcon scan.

This tests only the two byte orders of the eight accepted AX-7782 checkpoints
as (zero-based Google Books scan index, body-word position), with word bases
0 and 1. Printed folios are recorded as metadata, never used to select a page.
A hit is an experimental K08 candidate, not proof of David's physical copy.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "work" / "agent43-k07-falcon-scanindex"
VOLUME_ID = "fQYN_SZzCFgC"
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
        raise RuntimeError(
            f"expected one non-dry-run AX-7782 8-chunk COMMIT, found {len(commits)}"
        )

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

    if [row["seq"] for row in selected] != list(range(8)):
        raise RuntimeError("AX-7782 checkpoint sequence is not 0..7")
    if any(row.get("bytes") != 1048576 for row in selected):
        raise RuntimeError("AX-7782 chunk size differs from source record")

    values = [int(row["checkpoint"], 16) for row in selected]
    raw = b"".join(bytes.fromhex(row["checkpoint"]) for row in selected)
    component = hashlib.sha256(raw).digest()[:16]
    actual = sha256(component)
    expected = acceptance["slot_sha256"]["K07"]
    if actual != expected:
        raise RuntimeError(
            f"reconstructed K07 fails unchanged commitment: {actual} != {expected}"
        )
    return values, raw, component


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "images").mkdir(exist_ok=True)
    (OUT / "ocr").mkdir(exist_ok=True)

    acceptance = json.loads(
        (ROOT / "resources/acceptance.json").read_text(encoding="utf-8")
    )
    routing = json.loads(
        (ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8")
    )
    values, k07_preimage, k07_component = load_k07_checkpoints(acceptance)

    dual = importlib.import_module("agents.agent16.k08_falcon_dual_batch")
    falcon = dual.load_falcon_helper()
    cache_stats = dual.install_shared_cache(falcon, VOLUME_ID)

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    if nonce != falcon.DESK_NONCE:
        raise RuntimeError("desk nonce differs from pinned K08 source")
    if acceptance["slot_sha256"]["K08"] != EXPECTED_K08_SHA256:
        raise RuntimeError("K08 acceptance commitment changed")

    n02 = falcon.verify_phrase(
        [
            "a", "good", "watch", "leaves", "the", "room", "ready",
            "for", "the", "next", "pair", "of", "hands",
        ]
    )
    if (
        n02["derived_K08_component_hex"] != EXPECTED_N02_HMAC16
        or n02["acceptance_match"]
    ):
        raise RuntimeError("N02 known-answer HMAC control failed")

    metadata = falcon.fetch_metadata()
    if (
        metadata.get("pageCount") != 308
        or not str(metadata.get("publishedDate", "")).startswith("1889")
    ):
        raise RuntimeError(f"wrong pinned Falcon edition metadata: {metadata}")

    # Interpret each 16-bit checkpoint in both byte orders:
    # first byte = zero-based Google Books scan index; second = body-word position.
    coordinate_sets = {
        "checkpoint_hi_scan_lo_word": [
            (value >> 8, value & 0xFF) for value in values
        ],
        "checkpoint_lo_scan_hi_word": [
            (value & 0xFF, value >> 8) for value in values
        ],
    }
    unique_scan_indices = sorted(
        {scan for coords in coordinate_sets.values() for scan, _ in coords}
    )
    for scan in unique_scan_indices:
        if not 0 <= scan < int(metadata["pageCount"]):
            raise RuntimeError(f"scan index {scan} outside pinned volume")

    report: dict[str, Any] = {
        "status": "INCOMPLETE",
        "hypothesis": (
            "The eight accepted AX-7782 K07 checkpoints may be (zero-based scan "
            "index, body-word position) pairs in the exact pinned 1889 Falcon "
            "Google Books volume. Both byte orders and word bases 0/1 are tested. "
            "This does not establish that Falcon was David's physical book."
        ),
        "source": {
            "transfer": "AX-7782",
            "commit_receipt": commits[0] if (commits := [
                row for row in rows_from_audit()
                if row.get("kind") == "COMMIT" and row.get("transfer") == "AX-7782"
            ]) else None,
            "checkpoint_values_hex": [f"{value:04X}" for value in values],
            "checkpoint_preimage_hex": k07_preimage.hex().upper(),
            "accepted_K07_component_hex": k07_component.hex().upper(),
            "K07_commitment_verified": True,
            "candidate_book": 'Knight, The "Falcon" on the Baltic, W. H. Allen, 1889',
            "google_books_volume_id": VOLUME_ID,
            "page_count": metadata["pageCount"],
            "edition_status": (
                "public candidate only; no evidence proves this was David's physical copy"
            ),
        },
        "coordinate_sets": coordinate_sets,
        "word_position_bases_tested": [0, 1],
        "unique_zero_based_scan_indices": unique_scan_indices,
        "selection_rule": (
            "Use the first byte as a direct zero-based Google Books scan index. "
            "Do not call resolve_printed_page and do not require the visible folio "
            "to equal the scan index. Record margin folio OCR separately."
        ),
        "body_word_rule": {
            "position": "body word after Agent10 clean_body_lines()",
            "preprocessing": (
                "remove standalone numeric folios, title/running heads and all-uppercase "
                "display lines; join line-wrap hyphenation"
            ),
            "word_pattern": falcon.WORD_PATTERN.pattern,
        },
        "volume_metadata": metadata,
        "n02_positive_control": n02,
        "page_results": {},
        "candidate_results": {},
        "cache_stats": vars(cache_stats),
    }
    write_report(report)

    page_tokens: dict[int, list[str]] = {}
    for scan_index in unique_scan_indices:
        try:
            image_bytes, content_type, source_url = falcon.fetch_page_image(
                scan_index, zoom=3
            )
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            margin = falcon.read_margin_folio(image)
            ocr = pytesseract.image_to_string(
                image, lang="eng", config="--psm 4"
            )
            body = falcon.clean_body_lines(ocr, scan_index)
            tokens = falcon.WORD_PATTERN.findall(body)
            page_tokens[scan_index] = tokens

            source_path = OUT / "images" / f"source-scan-index-{scan_index}.bin"
            source_path.write_bytes(image_bytes)
            image_path = OUT / "images" / f"scan-index-{scan_index}.png"
            image.save(image_path, format="PNG")
            ocr_path = OUT / "ocr" / f"scan-index-{scan_index}.txt"
            ocr_path.write_text(ocr, encoding="utf-8")

            report["page_results"][str(scan_index)] = {
                "status": "RESOLVED_SCAN_INDEX",
                "zero_based_scan_index": scan_index,
                "visible_folio_margin_ocr": margin,
                "source_url": source_url,
                "content_type": content_type,
                "source_image_bytes": len(image_bytes),
                "source_image_sha256": sha256(image_bytes),
                "normalized_png_sha256": sha256(image_path.read_bytes()),
                "ocr_sha256": sha256(ocr.encode("utf-8")),
                "body_sha256": sha256(body.encode("utf-8")),
                "body_word_count": len(tokens),
                "source_image_path": str(source_path.relative_to(ROOT)),
                "ocr_path": str(ocr_path.relative_to(ROOT)),
            }
        except Exception as exc:
            report["page_results"][str(scan_index)] = {
                "status": "INCOMPLETE",
                "error": f"{type(exc).__name__}: {exc}",
            }

        report["cache_stats"] = vars(cache_stats)
        write_report(report)
        print(
            "PAGE_RESULT "
            + json.dumps(report["page_results"][str(scan_index)], sort_keys=True),
            flush=True,
        )

    for name, coords in coordinate_sets.items():
        for base in (0, 1):
            label = f"{name}_word_base_{base}"
            selected_words = []
            contexts = []
            error = None
            for scan_index, word_position in coords:
                tokens = page_tokens.get(scan_index)
                if tokens is None:
                    error = f"scan index {scan_index} was not resolved"
                    break
                index = word_position - base
                if not 0 <= index < len(tokens):
                    error = (
                        f"scan index {scan_index} has {len(tokens)} body words; "
                        f"requested position {word_position} with base {base}"
                    )
                    break
                selected_words.append(tokens[index])
                contexts.append(
                    {
                        "zero_based_scan_index": scan_index,
                        "body_word_position": word_position,
                        "index_base": base,
                        "body_word_count": len(tokens),
                        "selected_word": tokens[index],
                        "context": tokens[max(0, index - 4) : index + 3],
                    }
                )

            if error:
                report["candidate_results"][label] = {
                    "status": "INCOMPLETE",
                    "error": error,
                    "coordinate_pairs": coords,
                }
            else:
                result = falcon.verify_phrase(selected_words)
                report["candidate_results"][label] = {
                    **result,
                    "status": (
                        "MATCH" if result["acceptance_match"] else "NO_MATCH"
                    ),
                    "coordinate_pairs": coords,
                    "word_position_base": base,
                    "selected_word_context": contexts,
                }

            write_report(report)
            print(
                "CANDIDATE_RESULT "
                + label
                + " "
                + json.dumps(report["candidate_results"][label], sort_keys=True),
                flush=True,
            )

    statuses = [row["status"] for row in report["candidate_results"].values()]
    report["status"] = (
        "COMPLETE"
        if len(statuses) == 4 and all(s in {"MATCH", "NO_MATCH"} for s in statuses)
        else "PARTIAL"
    )
    report["cache_stats"] = vars(cache_stats)
    write_report(report)
    print(
        "K07_FALCON_SCANINDEX_COMPLETE "
        + json.dumps(
            {
                "status": report["status"],
                "candidate_statuses": statuses,
                "cache_stats": report["cache_stats"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0 if report["status"] == "COMPLETE" else 2


def rows_from_audit() -> list[dict[str, Any]]:
    path = ROOT / "resources/evidence/transfers/transfer-audit.jsonl"
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        report_path = OUT / "summary.json"
        partial = (
            json.loads(report_path.read_text(encoding="utf-8"))
            if report_path.exists()
            else {"status": "INCOMPLETE"}
        )
        partial["status"] = "INCOMPLETE"
        partial["error"] = f"{type(exc).__name__}: {exc}"
        write_report(partial)
        print("INCOMPLETE " + json.dumps({"error": partial["error"]}), flush=True)
        raise
