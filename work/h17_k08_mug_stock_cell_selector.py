#!/usr/bin/env python3
"""Bounded, read-only test of the PS-0323-derived K08 mug-stock cell selector.

This is a conditional hypothesis, not an authenticated source rule: AES-128-ECB
with the K08 desk nonce as key decrypts the retained PS-0323 ACK payload to
sixteen bytes interpreted as eight (row, column) pairs. The tool tests only
those eight cells, in their original order, with the two byte orientations and
zero-/one-based coordinate conventions. If it has one sheet, all eight cells are read from that sheet. Any multi-sheet workbook requires an explicit --sheet; no A-D sheet ordering
is inferred. No permutations, paraphrases, or broad workbook text searches
are performed. Install optional dependencies with
work/requirements-h17-k08-cell-selector.txt.

The input workbook is opened from bytes and never written. Only the exact M10
cell comment on the explicit or sole worksheet is additionally tested; other
cell comments, embedded OfficeArt, formulas without cached values, and
external links are not interpreted here. The separate OfficeArt/BIFF intake
covers native shape/image records. CLI output is redacted by default; raw
candidate material is available only to explicit in-process callers.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any, Iterable



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
    if not match:
        raise ValueError("PS-0323 ACK row has no 16-byte payload")
    ciphertext = bytes.fromhex(match.group(1))
    plaintext = aes_ecb_decrypt(nonce, ciphertext)
    if len(plaintext) != 16:
        raise ValueError("PS-0323 AES plaintext is not a 16-byte selector")
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


def evaluate_m10_comments(extracted: dict[str, Any], selected_sheet: str | None,
                          nonce: bytes, target: bytes) -> list[dict[str, Any]]:
    if not selected_sheet:
        return []
    expected_source = f"{selected_sheet}!M10<comment>".casefold()
    results: list[dict[str, Any]] = []
    for stream in extracted.get("text_streams", []):
        if stream.get("kind") != "comment":
            continue
        if str(stream.get("source", "")).casefold() != expected_source:
            continue
        text = str(stream.get("text", ""))
        if not text.strip():
            continue
        normalized = normalize(text)
        component = k08_component(nonce, normalized)
        digest = sha256(component)
        results.append({
            "source": stream.get("source"),
            "cell": "M10",
            "sheet": selected_sheet,
            "comment_author": stream.get("comment_author"),
            "raw_comment_text": text,
            "normalized_phrase": normalized,
            "hmac16": component.hex().upper(),
            "component_sha256": digest,
            "match": digest == target.hex(),
            "interpretation": "M10 margin/comment candidate; author metadata is not independent authentication",
        })
    return results

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


class FallbackSheet:
    def __init__(self, name: str, rows: int, columns: int,
                 cell_records: dict[tuple[str, str], dict[str, Any]]):
        self.name = name
        self.nrows = rows
        self.ncols = columns
        self._cell_records = cell_records

    def cell(self, row0: int, column0: int) -> Any:
        address = excel_address(row0 + 1, column0 + 1)
        record = self._cell_records.get((self.name, address))
        if record is None:
            return type("Cell", (), {"value": None, "ctype": None})()
        data_type = record.get("data_type")
        # Do not use LibreOffice-recalculated formula results as historical text.
        value = None if data_type in ("f", "e") else record.get("text")
        return type("Cell", (), {"value": value, "ctype": data_type})()


class FallbackBook:
    def __init__(self, extracted: dict[str, Any]):
        self._sheets: dict[str, FallbackSheet] = {}
        self._sheet_meta = extracted.get("sheets", [])
        self._cell_records: dict[tuple[str, str], dict[str, Any]] = {}
        for stream in extracted.get("text_streams", []):
            if stream.get("kind") != "cell":
                continue
            source = str(stream.get("source", ""))
            if "!" not in source:
                continue
            sheet_name, address = source.rsplit("!", 1)
            self._cell_records[(sheet_name, address.upper())] = stream
        for meta in self._sheet_meta:
            name = str(meta["name"])
            self._sheets[name] = FallbackSheet(
                name, int(meta.get("max_row", 0)), int(meta.get("max_column", 0)),
                self._cell_records,
            )

    def sheet_names(self) -> list[str]:
        return list(self._sheets)

    def sheet_by_name(self, name: str) -> FallbackSheet:
        return self._sheets[name]

    def release_resources(self) -> None:
        return None


def inspect_workbook(workbook_path: Path, resources: Path, explicit_sheet: str | None = None,
                     reveal: bool = False) -> dict[str, Any]:
    """Inspect the bounded selector. Raw values require explicit reveal=True."""

    if not workbook_path.is_file() or workbook_path.is_symlink():
        raise ValueError("workbook must be a regular, non-symlink file")
    nonce, target = load_k08_rules(resources)
    ciphertext, plaintext = decrypt_ps0323(resources, nonce)
    try:
        from h17_xls_lo_fallback import extract as extract_xls
    except ImportError as exc:
        raise RuntimeError("work/h17_xls_lo_fallback.py must be available beside this tool") from exc
    extracted = extract_xls(workbook_path)
    if not extracted.get("source_unchanged"):
        raise RuntimeError("legacy XLS intake did not confirm source immutability")
    before_hash = extracted.get("source_sha256_before")
    after_hash = extracted.get("source_sha256_after")
    if not before_hash or before_hash != after_hash:
        raise RuntimeError("legacy XLS intake source hashes differ or are missing")
    book = FallbackBook(extracted)
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
    comment_sheet = explicit_sheet if explicit_sheet else (
        sheet_names[0] if len(sheet_names) == 1 else None
    )
    m10_comment_candidates = evaluate_m10_comments(
        extracted, comment_sheet, nonce, target
    )
    result = {
        "status": ("MATCH_REVIEW" if (
                       any(x["match"] for x in candidates)
                       or any(x["match"] for x in m10_comment_candidates)
                   ) else
                   "NO_K08_MATCH" if candidates and all(x["complete"] for x in candidates) else
                   "INCOMPLETE_OR_NO_MAPPING"),
        "workbook": {"path": str(workbook_path), "size": extracted.get("source_bytes"),
                     "sha256_before": before_hash, "sha256_after": after_hash,
                     "source_unchanged": True, "converter": extracted.get("converter")},
        "ps0323_selector": {"payload_hex": ciphertext.hex().upper(),
                             "desk_nonce_hex": nonce.hex().upper(),
                             "aes_plaintext_hex": plaintext.hex().upper(),
                             "coordinate_sets": {k: [[r, c] for r, c in v] for k, v in coordinates.items()}},
        "sheets": [{"name": meta.get("name"), "rows": meta.get("max_row"),
                    "columns": meta.get("max_column"), "state": meta.get("state")}
                   for meta in extracted.get("sheets", [])],
        "sheet_mapping": mapping,
        "k08_target_sha256": target.hex(),
        "candidates": candidates,
        "m10_comment_candidates": m10_comment_candidates,
        "m10_comment_sheet": comment_sheet,
        "scope": [
            "Conditional test only: PS-0323-to-keeper-envelope identity is not authenticated by the surviving export.",
            "Only the eight PS-0323-derived cells, their original order, two byte orientations, and zero-/one-based coordinates are tested.",
            "No sheet ordering is inferred; multi-sheet workbooks require an explicit --sheet.",
            "Cell values are joined with one space and processed under the original REC8/1 normalization/HMAC rule.",
            "Formula cells are not used as phrase values because LibreOffice may recalculate them.",
            "Only the M10 cell comment on an explicit or sole worksheet is tested; no broad comment search is performed.",
            "Comment author metadata is preserved as a clue, not treated as independent identity authentication.",
            "The existing XLS intake converts a temporary copy and confirms the original workbook hash is unchanged."
        ]
    }
    book.release_resources()
    return result if reveal else redact_result(result)


def redact_result(result: dict[str, Any]) -> dict[str, Any]:
    """Return a public-safe summary with all candidate/selector material removed."""
    public = dict(result)
    workbook = result.get("workbook", {})
    public["workbook"] = {
        "name": Path(str(workbook.get("path", ""))).name,
        "size": workbook.get("size"),
        "source_unchanged": workbook.get("source_unchanged"),
        "converter": workbook.get("converter"),
    }
    public["ps0323_selector"] = {
        "redacted": True,
        "cell_count": 8,
        "orientation_count": 2,
    }
    public.pop("k08_target_sha256", None)
    public["candidates"] = [
        {
            "orientation": item.get("orientation"),
            "input_base": item.get("input_base"),
            "sheet_mapping": item.get("sheet_mapping"),
            "complete": item.get("complete"),
            "match": item.get("match"),
            "reason": item.get("reason"),
            "selected_cell_count": len(item.get("cells", [])),
        }
        for item in result.get("candidates", [])
    ]
    public["m10_comment_candidates"] = [
        {
            "source": item.get("source"),
            "cell": item.get("cell"),
            "sheet": item.get("sheet"),
            "author_present": bool(item.get("comment_author")),
            "match": item.get("match"),
            "interpretation": item.get("interpretation"),
        }
        for item in result.get("m10_comment_candidates", [])
    ]
    public["redaction"] = [
        "K08 nonce, PS-0323 ciphertext/plaintext, coordinates, target digest, cell values, phrases, HMACs and component digests are withheld.",
        "Comment-author identity is withheld; only author presence is reported.",
        "Use inspect_workbook(..., reveal=True) only for authorized in-process local analysis; never log or publish that result.",
    ]
    return public


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
