#!/usr/bin/env python3
"""Read-only, exact-cell K08 candidate test for every worksheet's M10 value.

This is a narrow extension of the source-derived mug-stock.xls lead. It does
not search arbitrary workbook cells or comments. It evaluates only M10's
literal cell value and, separately, the cached result of an M10 formula.
Formula text itself is preserved as context but is never treated as the
keeper's phrase. LibreOffice-derived formula caches are explicitly provisional
because conversion may recalculate them.

Run from workplace-v2:
  python work/h17_k08_m10_value_probe.py --workbook /path/to/mug-stock.xls
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

from h17_redaction import redact_sensitive
from typing import Any

EXPECTED_SYNTHETIC_HMAC16 = "D80E9E725D394C7F1B60CCDD801F7407"


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def k08_component(nonce: bytes, phrase: str) -> bytes:
    return hmac.new(nonce, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def load_rules(resources: Path) -> tuple[bytes, bytes]:
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if len(nonce) != 16 or len(target) != 32:
        raise ValueError("invalid K08 nonce or commitment width")
    control = k08_component(bytes(range(16)), "A good watch leaves the room ready for the next pair of hands")
    if control.hex().upper() != EXPECTED_SYNTHETIC_HMAC16:
        raise ValueError("K08 normalization/HMAC known-answer control failed")
    return nonce, target


def _candidate(source: str, sheet: str, sheet_state: str, value_kind: str,
               raw_text: str, nonce: bytes, target: bytes, **extra: Any) -> dict[str, Any]:
    normalized = normalize(raw_text)
    component = k08_component(nonce, normalized)
    digest = hashlib.sha256(component).hexdigest()
    return {
        "source": source,
        "sheet": sheet,
        "sheet_state": sheet_state,
        "cell": "M10",
        "value_kind": value_kind,
        "raw_text": raw_text,
        "normalized_phrase": normalized,
        "hmac16": component.hex().upper(),
        "component_sha256": digest,
        "match": hmac.compare_digest(digest, target.hex()),
        **extra,
    }


def evaluate_m10_values(extracted: dict[str, Any], nonce: bytes,
                        target: bytes) -> dict[str, Any]:
    """Evaluate only exact M10 cell-value streams from the XLS intake adapter."""
    sheet_states = {
        str(meta.get("name", "")): str(meta.get("state", "unknown"))
        for meta in extracted.get("sheets", [])
    }
    candidates: list[dict[str, Any]] = []
    formulas: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for stream in extracted.get("text_streams", []):
        if stream.get("kind") != "cell":
            continue
        source = str(stream.get("source", ""))
        if "!" not in source:
            continue
        sheet, address = source.rsplit("!", 1)
        if address.upper() != "M10":
            continue
        state = sheet_states.get(sheet, "unknown")
        data_type = str(stream.get("data_type", "unknown"))
        raw_value = stream.get("text")
        cached_value = stream.get("converted_cached_value")

        if data_type.casefold() == "f":
            formula_record = {
                "source": source,
                "sheet": sheet,
                "sheet_state": state,
                "cell": "M10",
                "formula_text": raw_value,
                "cached_value_available": isinstance(cached_value, str) and bool(cached_value.strip()),
                "cache_provenance": "LibreOffice-converted data_only value; may have been recalculated",
            }
            formulas.append(formula_record)
            if isinstance(cached_value, str) and cached_value.strip():
                key = (source, "converted_formula_cache", cached_value)
                if key not in seen:
                    seen.add(key)
                    candidates.append(_candidate(
                        source, sheet, state, "converted_formula_cache",
                        cached_value, nonce, target,
                        formula_text=raw_value,
                        cache_provenance="LibreOffice-converted data_only value; may have been recalculated",
                    ))
            continue

        if data_type.casefold() in {"e", "b"}:
            continue
        if isinstance(raw_value, str) and raw_value.strip():
            key = (source, "literal_cell_value", raw_value)
            if key not in seen:
                seen.add(key)
                candidates.append(_candidate(
                    source, sheet, state, "literal_cell_value",
                    raw_value, nonce, target, data_type=data_type,
                    value_provenance="cell value from converted read-only workbook copy",
                ))
        if isinstance(cached_value, str) and cached_value.strip() and cached_value != raw_value:
            key = (source, "converted_cached_value", cached_value)
            if key not in seen:
                seen.add(key)
                candidates.append(_candidate(
                    source, sheet, state, "converted_cached_value",
                    cached_value, nonce, target, data_type=data_type,
                    cache_provenance="LibreOffice-converted data_only value; may have been recalculated",
                ))

    matches = [item for item in candidates if item["match"]]
    status = "MATCH_REQUIRES_SOURCE_REVIEW" if matches else (
        "NO_M10_VALUE_MATCH" if candidates else
        "NO_M10_TEXT_VALUE" if not formulas else
        "M10_FORMULA_WITHOUT_TEXT_CACHE"
    )
    return {
        "status": status,
        "candidate_count": len(candidates),
        "match_count": len(matches),
        "candidates": candidates,
        "formula_records": formulas,
        "scope": [
            "Only exact M10 cell values are evaluated, on each worksheet listed by the source intake adapter.",
            "No sheet ordering, hidden-sheet priority, neighboring-cell search, or comment search is inferred.",
            "Formula text is context only and is never hashed as the keeper phrase.",
            "Formula cached values are separate provisional candidates because LibreOffice may recalculate them.",
            "A commitment hit is a candidate requiring verification against the original BIFF cell/cache bytes and historical authorship; it is not by itself an authenticity finding.",
            "No workbook source bytes are modified.",
        ],
    }


def inspect_workbook(workbook: Path, resources: Path) -> dict[str, Any]:
    workbook = workbook.expanduser().absolute()
    info = workbook.lstat()
    if workbook.is_symlink() or not workbook.is_file():
        raise ValueError("workbook must be a regular, non-symlink file")
    nonce, target = load_rules(resources)
    work_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(work_dir))
    try:
        from h17_xls_lo_fallback import extract as extract_xls
    except ImportError as exc:
        raise RuntimeError("work/h17_xls_lo_fallback.py and its optional dependencies are required") from exc
    extracted = extract_xls(workbook)
    before = extracted.get("source_sha256_before")
    after = extracted.get("source_sha256_after")
    if not extracted.get("source_unchanged") or not before or before != after:
        raise RuntimeError("legacy XLS intake did not confirm unchanged source bytes")
    evaluated = evaluate_m10_values(extracted, nonce, target)
    return {
        "workbook": {
            "path": str(workbook),
            "size_bytes": info.st_size,
            "sha256_before": before,
            "sha256_after": after,
            "source_unchanged": True,
            "converter": extracted.get("converter"),
            "formula_values_note": extracted.get("formula_values_note"),
        },
        "k08_target_sha256": target.hex(),
        "k08_desk_nonce_hex": nonce.hex().upper(),
        "sheet_inventory": extracted.get("sheets", []),
        **evaluated,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, type=Path)
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_workbook(args.workbook, args.resources)
    except Exception as exc:
        parser.error(str(exc))
    result = redact_sensitive(result)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        out = args.json_out.expanduser().absolute()
        if out == args.workbook.expanduser().absolute():
            parser.error("--json-out must not overwrite the source workbook")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
