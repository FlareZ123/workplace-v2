#!/usr/bin/env python3
"""Bounded, read-only test of the PS-0323-derived K08 mug-stock cell selector.

This is a conditional hypothesis, not an authenticated source rule: AES-128-ECB
with the K08 desk nonce as key decrypts the retained PS-0323 ACK payload to
sixteen bytes interpreted as eight (row, column) pairs. The tool tests only
those eight cells, in their original order, with the two byte orientations and
zero-/one-based coordinate conventions. If it has one sheet, all eight cells are read from that sheet. Any multi-sheet
workbook requires an explicit --sheet; no A-D sheet ordering is inferred. No
permutations, paraphrases, or broad workbook text searches are performed. Install optional dependencies with
work/requirements-h17-k08-cell-selector.txt.

The input workbook is opened from bytes and never written. Cell comments,
embedded OfficeArt, formulas without cached values, and external links are not
interpreted here; use the separate OfficeArt/BIFF intake for those structures.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any, Iterable

PS0323_PAYLOAD_HEX = "1E51EFD2E5CA8F4E1FC8B49297B3D74F"
PS0323_PLAINTEXT_HEX = "E5407654D33238607DFA324B94656E1D"
N02_CONTROL_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def k08_component(nonce: bytes, normalized_phrase: str) -> bytes:
    return hmac.new(nonce, normalized_phrase.encode("utf-8"), hashlib.sha256).digest()[:16]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_k08_rules(resources: Path) -> tuple[bytes, bytes]:
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if len(nonce) != 16 or len(target) != 32:
        raise ValueError("invalid K08 nonce or commitment width")
    control = k08_component(nonce, normalize("A good watch leaves the room ready for the next pair of hands"))
    if control.hex().upper() != N02_CONTROL_HMAC16:
        raise ValueError("K08 normalization/HMAC known-answer control failed")
    return nonce, target


def aes_ecb_decrypt(nonce: bytes, ciphertext: bytes) -> bytes:
    if len(nonce) != 16 or len(ciphertext) != 16:
        raise ValueError("AES-128-ECB requires a 16-byte key and one 16-byte block")
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError as exc:
        raise RuntimeError("cryptography is required for the conditional PS-0323 AES test") from exc
    decryptor = Cipher(algorithms.AES(nonce), modes.ECB()).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def decrypt_ps0323(resources: Path, nonce: bytes) -> tuple[bytes, bytes]:
    spool_path = resources / "evidence" / "print" / "spool-reconstruction.log"
    lines = [line for line in spool_path.read_text(encoding="utf-8").splitlines()
             if "JOB=PS-261003-0323 " in line]
    if len(lines) != 1:
        raise ValueError(f"expected one PS-0323 spool row, found {len(lines)}")
    line = lines[0]
    required = ("ATTEMPT=1", "STATE=ACK", "CLASS=RECOVER", "DEST=store")
    if not all(token in line for token in required):
        raise ValueError("PS-0323 row no longer has the pinned ACK/RECOVER/store role")
    match = re.search(r"\bPAYLOAD=([0-9A-Fa-f]{32})\b", line)
    if not match or match.group(1).upper() != PS0323_PAYLOAD_HEX:
        raise ValueError("PS-0323 payload differs from the pinned source value")
    ciphertext = bytes.fromhex(match.group(1))
    plaintext = aes_ecb_decrypt(nonce, ciphertext)
    if plaintext.hex().upper() != PS0323_PLAINTEXT_HEX:
        raise ValueError("PS-0323 AES plaintext differs from the pinned result")
    return ciphertext, plaintext


def coordinate_sets(plaintext: bytes) -> dict[str, list[tuple[int, int]]]:
    if len(plaintext) != 16:
        raise ValueError("PS-0323 selector must contain exactly 16 bytes")
    high_low = [(plaintext[i], plaintext[i + 1]) for i in range(0, 16, 2)]
    low_high = [(plaintext[i + 1], plaintext[i]) for i in range(0, 16, 2)]
    return {"high_byte_row_low_byte_column": high_low,
            "low_byte_row_high_byte_column": low_high}


def excel_column(column: int) -> str:
    if column < 1:
        raise ValueError("Excel columns are one-based")
    out = ""
    while column:
        column, rem = divmod(column - 1, 26)
        out = chr(65 + rem) + out
    return out


def excel_address(row: int, column: int) -> str:
    if row < 1 or column < 1:
        raise ValueError("Excel rows and columns are one-based")
    return f"{excel_column(column)}{row}"


def map_sheets(sheet_names: list[str], explicit_sheet: str | None) -> dict[str, list[str]] | None:
    """Return only source-explicit mappings; never infer sheet order."""
    if explicit_sheet is not None:
        if explicit_sheet not in sheet_names:
            raise ValueError(f"requested sheet {explicit_sheet!r} not found; sheets={sheet_names}")
        return {"single": [explicit_sheet] * 8}
    if len(sheet_names) == 1:
        return {"single": [sheet_names[0]] * 8}
    return None


def sample_cells(sheet: Any, coordinates: Iterable[tuple[int, int]], base: int) -> list[dict[str, Any]]:
    if base not in (0, 1):
        raise ValueError("base must be 0 or 1")
    cells: list[dict[str, Any]] = []
    for index, (raw_row, raw_column) in enumerate(coordinates):
        row = raw_row + (1 if base == 0 else 0)
        column = raw_column + (1 if base == 0 else 0)
        address = excel_address(row, column)
        row0, column0 = row - 1, column - 1
        item: dict[str, Any] = {"index": index, "row": row, "column": column,
                                "address": address, "sheet": sheet.name,
                                "sheet_rows": sheet.nrows, "sheet_columns": sheet.ncols}
        if row0 >= sheet.nrows or column0 >= sheet.ncols:
            item.update({"in_bounds": False, "value": None, "reason": "outside worksheet dimensions"})
        else:
            cell = sheet.cell(row0, column0)
            value = cell.value
            item.update({"in_bounds": True, "value": value,
                         "cell_type": getattr(cell, "ctype", None)})
        cells.append(item)
    return cells


def evaluate_candidate(cells: list[dict[str, Any]], nonce: bytes, target: bytes,
                       orientation: str, base: int, mapping: str) -> dict[str, Any]:
    complete = all(cell["in_bounds"] and cell["value"] is not None and str(cell["value"]) != ""
                   for cell in cells)
    result: dict[str, Any] = {"orientation": orientation, "input_base": base,
                              "sheet_mapping": mapping, "cells": cells,
                              "complete": complete, "match": False}
    if not complete:
        result["reason"] = "one or more selected cells are blank or out of bounds"
        return result
    phrase = " ".join(str(cell["value"]) for cell in cells)
    normalized = normalize(phrase)
    component = k08_component(nonce, normalized)
    digest = sha256(component)
    result.update({"raw_joined_values": phrase, "normalized_phrase": normalized,
                   "hmac16": component.hex().upper(), "component_sha256": digest,
                   "match": digest == target.hex()})
    return result


def inspect_workbook(workbook_path: Path, resources: Path, explicit_sheet: str | None = None) -> dict[str, Any]:
    if not workbook_path.is_file() or workbook_path.is_symlink():
        raise ValueError("workbook must be a regular, non-symlink file")
    source_bytes = workbook_path.read_bytes()
    source_hash = sha256(source_bytes)
    nonce, target = load_k08_rules(resources)
    ciphertext, plaintext = decrypt_ps0323(resources, nonce)
    try:
        import xlrd
    except ImportError as exc:
        raise RuntimeError("xlrd is required to read the original BIFF .xls workbook") from exc
    book = xlrd.open_workbook(file_contents=source_bytes, on_demand=False)
    sheet_names = book.sheet_names()
    mapping = map_sheets(sheet_names, explicit_sheet)
    coordinates = coordinate_sets(plaintext)
    candidates: list[dict[str, Any]] = []
    if mapping is not None:
        sheet_name = mapping["single"][0]
        sheet = book.sheet_by_name(sheet_name)
        for orientation, pairs in coordinates.items():
            for base in (0, 1):
                cells = sample_cells(sheet, pairs, base)
                candidates.append(evaluate_candidate(cells, nonce, target,
                                                     orientation, base, "single"))
    result = {
        "status": ("MATCH_REVIEW" if any(x["match"] for x in candidates) else
                   "NO_K08_MATCH" if candidates and all(x["complete"] for x in candidates) else
                   "INCOMPLETE_OR_NO_MAPPING"),
        "workbook": {"path": str(workbook_path), "size": len(source_bytes),
                     "sha256_before": source_hash, "sha256_after": sha256(workbook_path.read_bytes())},
        "ps0323_selector": {"payload_hex": ciphertext.hex().upper(),
                             "desk_nonce_hex": nonce.hex().upper(),
                             "aes_plaintext_hex": plaintext.hex().upper(),
                             "coordinate_sets": {k: [[r, c] for r, c in v] for k, v in coordinates.items()}},
        "sheets": [{"name": name, "rows": book.sheet_by_name(name).nrows,
                    "columns": book.sheet_by_name(name).ncols} for name in sheet_names],
        "sheet_mapping": mapping,
        "k08_target_sha256": target.hex(),
        "candidates": candidates,
        "scope": [
            "Conditional test only: PS-0323-to-keeper-envelope identity is not authenticated by the surviving export.",
            "Only the eight PS-0323-derived cells, their original order, two byte orientations, and zero-/one-based coordinates are tested.",
            "No sheet ordering is inferred; multi-sheet workbooks require an explicit --sheet.",
            "Cell values are joined with one space and processed under the original REC8/1 normalization/HMAC rule.",
            "No sheet permutation, cell permutation, paraphrase, comments, embedded OfficeArt, formula recalculation, or broad text search is performed.",
            "The source workbook is read-only; hash is checked before and after."
        ]
    }
    book.release_resources()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, type=Path, help="authorized local copy of mug-stock.xls")
    parser.add_argument("--resources", type=Path, default=Path("resources"),
                        help="extracted source root containing acceptance.json and evidence/recovery-routing.json")
    parser.add_argument("--sheet", help="explicit single sheet to use when the workbook is not a one-sheet or A-D workbook")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_workbook(args.workbook, args.resources, args.sheet)
    except Exception as exc:
        parser.error(str(exc))
    encoded = json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
    if args.json_out:
        output_path = args.json_out.resolve()
        if output_path == args.workbook.resolve() or args.workbook.resolve() in output_path.parents:
            parser.error("--json-out must be outside the source workbook")
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
