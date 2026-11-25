#!/usr/bin/env python3
"""Read-only raw-BIFF8 exact-cell text probe for the conditional K08 workbook path.

The default is M10; the only alternate is the pre-registered P212 locator.
The probe reads original OLE/BIFF8 records and never recalculates formula
caches. Supported text carriers are LABEL, RSTRING, LABELSST (single-record
SST), and FORMULA with an original cached STRING. Unsupported forms fail
closed. CLI output redacts phrase text, HMAC bytes, nonce and raw records.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import struct
import sys
from pathlib import Path

from h17_redaction import redact_sensitive
from typing import Any

EXPECTED_SYNTHETIC_HMAC16 = "D80E9E725D394C7F1B60CCDD801F7407"
RID_BOF = 0x0809
RID_EOF = 0x000A
RID_FILEPASS = 0x002F
RID_BOUNDSHEET = 0x0085
RID_SST = 0x00FC
RID_CONTINUE = 0x003C
RID_LABEL = 0x0204
RID_RSTRING = 0x00D6
RID_LABELSST = 0x00FD
RID_FORMULA = 0x0006
RID_STRING = 0x0207
DEFAULT_CELL = "M10"
SUPPORTED_CELLS = ("M10", "P212")


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def component(nonce: bytes, phrase: str) -> bytes:
    return hmac.new(nonce, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def load_rules(resources: Path) -> tuple[bytes, bytes]:
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if len(nonce) != 16 or len(target) != 32:
        raise ValueError("invalid K08 nonce or commitment width")
    if component(bytes(range(16)), "A good watch leaves the room ready for the next pair of hands").hex().upper() != EXPECTED_SYNTHETIC_HMAC16:
        raise ValueError("K08 normalization/HMAC known-answer control failed")
    return nonce, target


def decode_xl_unicode(data: bytes, offset: int = 0) -> tuple[str, int]:
    """Decode one BIFF8 XLUnicodeRichExtendedString, returning next offset."""
    if offset + 3 > len(data):
        raise ValueError("truncated XLUnicodeString header")
    char_count = struct.unpack_from("<H", data, offset)[0]
    flags = data[offset + 2]
    offset += 3
    high_byte = bool(flags & 0x01)
    rich_text = bool(flags & 0x08)
    extended = bool(flags & 0x04)
    run_count = 0
    ext_size = 0
    if rich_text:
        if offset + 2 > len(data):
            raise ValueError("truncated XLUnicodeString rich-text count")
        run_count = struct.unpack_from("<H", data, offset)[0]
        offset += 2
    if extended:
        if offset + 4 > len(data):
            raise ValueError("truncated XLUnicodeString extension size")
        ext_size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
    char_bytes = char_count * (2 if high_byte else 1)
    end_chars = offset + char_bytes
    end_runs = end_chars + run_count * 4
    end_ext = end_runs + ext_size
    if end_ext > len(data):
        raise ValueError("XLUnicodeString data exceeds record bounds")
    raw = data[offset:end_chars]
    text = raw.decode("utf-16le" if high_byte else "latin1")
    return text, end_ext


def parse_sst(payload: bytes) -> list[str]:
    if len(payload) < 8:
        raise ValueError("short SST record")
    total_count, unique_count = struct.unpack_from("<II", payload, 0)
    if unique_count > total_count:
        raise ValueError("SST unique-string count exceeds total-string count")
    if unique_count > 100_000:
        raise ValueError("SST unique-string count exceeds safety bound")
    strings = []
    offset = 8
    for _ in range(unique_count):
        text, offset = decode_xl_unicode(payload, offset)
        strings.append(text)
    if offset != len(payload):
        raise ValueError("SST payload has unparsed trailing bytes")
    return strings


def parse_boundsheet(payload: bytes) -> dict[str, Any]:
    if len(payload) < 8:
        raise ValueError("short BOUNDSHEET record")
    sheet_offset = struct.unpack_from("<I", payload, 0)[0]
    visibility, sheet_type, char_count, flags = payload[4:8]
    width = 2 if flags & 0x01 else 1
    end = 8 + char_count * width
    if end > len(payload):
        raise ValueError("truncated BOUNDSHEET name")
    raw = payload[8:end]
    name = raw.decode("utf-16le" if width == 2 else "latin1")
    return {"offset": sheet_offset, "visibility": visibility, "sheet_type": sheet_type, "name": name}


def _record_bytes(record_id: int, payload: bytes) -> bytes:
    return struct.pack("<HH", record_id, len(payload)) + payload


def parse_a1_address(address: str) -> tuple[int, int]:
    """Return zero-based BIFF8 (row, column) for one exact A1 address."""
    match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", address.upper())
    if not match:
        raise ValueError(f"invalid A1 cell address: {address!r}")
    letters, row_text = match.groups()
    column = 0
    for character in letters:
        column = column * 26 + ord(character) - ord("A") + 1
    row = int(row_text)
    if not (1 <= row <= 65536 and 1 <= column <= 256):
        raise ValueError(f"A1 cell address is outside BIFF8 limits: {address!r}")
    return row - 1, column - 1


def _biff_record_iterator():
    work_dir = Path(__file__).resolve().parent
    work_dir_text = str(work_dir)
    if work_dir_text not in sys.path:
        sys.path.insert(0, work_dir_text)
    from h17_biff_officeart import _iter_biff_records
    return _iter_biff_records


def parse_workbook_stream(workbook: bytes) -> dict[str, Any]:
    _iter_biff_records = _biff_record_iterator()
    globals_records = []
    for record in _iter_biff_records(workbook, 0):
        globals_records.append(record)
        if record[1] == RID_EOF:
            break
    if not globals_records or globals_records[-1][1] != RID_EOF:
        raise ValueError("workbook globals have no EOF")
    if globals_records[0][1] != RID_BOF or len(globals_records[0][2]) < 4:
        raise ValueError("workbook stream does not begin with a BIFF BOF record")
    version, substream_type = struct.unpack_from("<HH", globals_records[0][2], 0)
    if version != 0x0600 or substream_type != 0x0005:
        raise ValueError("workbook globals are not BIFF8 workbook-global substream")
    if any(record_id == RID_FILEPASS for _, record_id, _ in globals_records):
        raise ValueError("encrypted BIFF8 workbook is out of scope; refusing decryption")

    sheets = []
    sst = None
    for i, (_offset, record_id, payload) in enumerate(globals_records):
        if record_id == RID_BOUNDSHEET:
            sheets.append(parse_boundsheet(payload))
        elif record_id == RID_SST:
            if sst is not None:
                raise ValueError("multiple SST records are unsupported")
            if i + 1 < len(globals_records) and globals_records[i + 1][1] == RID_CONTINUE:
                raise ValueError("SST CONTINUE chain is unsupported; refusing partial string-table decode")
            sst = parse_sst(payload)
    if not sheets:
        raise ValueError("no BOUNDSHEET records found")
    global_end = globals_records[-1][0] + 4 + len(globals_records[-1][2])
    for sheet in sheets:
        if not global_end <= sheet["offset"] < len(workbook):
            raise ValueError(f"sheet {sheet['name']!r} offset is outside the workbook stream")
    return {"sheets": sheets, "sst": sst}


def extract_cell(workbook: bytes, cell_address: str = DEFAULT_CELL) -> list[dict[str, Any]]:
    """Extract original BIFF text records for one exact cell; never serialize this raw result."""
    address = cell_address.upper()
    target_row, target_col = parse_a1_address(address)
    _iter_biff_records = _biff_record_iterator()
    parsed = parse_workbook_stream(workbook)
    results = []
    for sheet in parsed["sheets"]:
        if sheet["sheet_type"] != 0:
            continue
        records = list(_iter_biff_records(workbook, sheet["offset"]))
        eof_index = next((i for i, record in enumerate(records) if record[1] == RID_EOF), None)
        if eof_index is None:
            raise ValueError(f"worksheet {sheet['name']!r} has no EOF")
        records = records[:eof_index + 1]
        if records[0][1] != RID_BOF or len(records[0][2]) < 4:
            raise ValueError(f"worksheet {sheet['name']!r} does not begin with BOF")
        sheet_version, sheet_type = struct.unpack_from("<HH", records[0][2], 0)
        if sheet_version != 0x0600 or sheet_type != 0x0010:
            raise ValueError(f"worksheet {sheet['name']!r} is not a BIFF8 worksheet substream")
        for index, (record_offset, record_id, payload) in enumerate(records):
            if record_id == RID_EOF:
                break
            if record_id not in {RID_LABEL, RID_RSTRING, RID_LABELSST, RID_FORMULA}:
                continue
            if len(payload) < 6:
                raise ValueError(f"short BIFF cell record 0x{record_id:04X}")
            row, col, xf = struct.unpack_from("<HHH", payload, 0)
            if (row, col) != (target_row, target_col):
                continue
            base = {
                "sheet": sheet["name"],
                "sheet_visibility": sheet["visibility"],
                "sheet_type": sheet["sheet_type"],
                "cell": address,
                "record_id": f"0x{record_id:04X}",
                "xf_index": xf,
                "record_offset": record_offset,
                "raw_record_hex": _record_bytes(record_id, payload).hex().upper(),
            }
            if record_id in {RID_LABEL, RID_RSTRING}:
                text, end = decode_xl_unicode(payload, 6)
                base.update({"value_kind": "literal_label", "raw_text": text,
                             "trailing_record_bytes_hex": payload[end:].hex().upper()})
            elif record_id == RID_LABELSST:
                if len(payload) < 10:
                    raise ValueError("short LABELSST record")
                sst_index = struct.unpack_from("<I", payload, 6)[0]
                if parsed["sst"] is None or sst_index >= len(parsed["sst"]):
                    raise ValueError("LABELSST references unavailable or out-of-range SST entry")
                base.update({"value_kind": "shared_string", "sst_index": sst_index,
                             "raw_text": parsed["sst"][sst_index]})
            else:
                if len(payload) < 22:
                    raise ValueError("short FORMULA record")
                result_bytes = payload[6:14]
                formula_length = struct.unpack_from("<H", payload, 20)[0]
                formula_tokens = payload[22:22 + formula_length]
                if len(formula_tokens) != formula_length:
                    raise ValueError("FORMULA token length exceeds record bounds")
                base["formula_tokens_hex"] = formula_tokens.hex().upper()
                if result_bytes[6:8] == b"\xff\xff" and result_bytes[0] == 0:
                    if index + 1 >= len(records) or records[index + 1][1] != RID_STRING:
                        raise ValueError("formula string result has no immediately following STRING record")
                    string_payload = records[index + 1][2]
                    text, end = decode_xl_unicode(string_payload, 0)
                    base.update({"value_kind": "formula_cached_string", "raw_text": text,
                                 "string_record_hex": _record_bytes(RID_STRING, string_payload).hex().upper(),
                                 "string_record_trailing_hex": string_payload[end:].hex().upper(),
                                 "formula_cached_result_hex": result_bytes.hex().upper()})
                else:
                    result_type = "numeric_or_nontext"
                    if result_bytes[6:8] == b"\xff\xff":
                        result_type = {1: "boolean", 2: "error", 3: "empty"}.get(result_bytes[0], "special_nontext")
                    base.update({"value_kind": result_type, "formula_cached_result_hex": result_bytes.hex().upper()})
            results.append(base)
    return results


def extract_m10(workbook: bytes) -> list[dict[str, Any]]:
    """Backward-compatible exact M10 extractor."""
    return extract_cell(workbook, "M10")


def _safe_record_summary(cell: dict[str, Any]) -> dict[str, Any]:
    """Summarize source record identity without exposing phrase or raw record bytes."""
    summary = {
        key: cell[key]
        for key in ("sheet", "sheet_visibility", "sheet_type", "cell",
                    "record_id", "xf_index", "record_offset", "value_kind")
        if key in cell
    }
    raw_record_hex = cell.get("raw_record_hex")
    if isinstance(raw_record_hex, str):
        summary["raw_record_sha256"] = hashlib.sha256(bytes.fromhex(raw_record_hex)).hexdigest()
    raw_text = cell.get("raw_text")
    if isinstance(raw_text, str):
        summary["text_length"] = len(raw_text)
        summary["text_sha256"] = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    for source_key, output_key in (
        ("formula_tokens_hex", "formula_tokens_sha256"),
        ("string_record_hex", "string_record_sha256"),
        ("formula_cached_result_hex", "formula_cached_result_sha256"),
    ):
        raw_hex = cell.get(source_key)
        if isinstance(raw_hex, str):
            summary[output_key] = hashlib.sha256(bytes.fromhex(raw_hex)).hexdigest()
    if "sst_index" in cell:
        summary["sst_index"] = cell["sst_index"]
    return summary


def inspect_workbook(
    path: Path, resources: Path, cell_address: str = DEFAULT_CELL
) -> dict[str, Any]:
    work_dir = Path(__file__).resolve().parent
    work_dir_text = str(work_dir)
    if work_dir_text not in sys.path:
        sys.path.insert(0, work_dir_text)
    from h17_biff_officeart import CompoundFile

    cell_address = cell_address.upper()
    if cell_address not in SUPPORTED_CELLS:
        raise ValueError(f"cell must be one of {SUPPORTED_CELLS}; got {cell_address!r}")
    path = path.expanduser().absolute()
    info = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ValueError("workbook must be a regular, non-symlink file")
    if info.st_size <= 0 or info.st_size > 64 * 1024 * 1024:
        raise ValueError("workbook size must be 1..64 MiB")
    source_bytes = path.read_bytes()
    before = hashlib.sha256(source_bytes).hexdigest()
    nonce, target = load_rules(resources)
    cfb = CompoundFile(source_bytes)
    stream_name, workbook_stream = cfb.read_stream(("Workbook", "Book"))
    cells = extract_cell(workbook_stream, cell_address)
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError("original workbook bytes changed during raw BIFF inspection")
    candidates = []
    for cell in cells:
        raw_text = cell.get("raw_text")
        if isinstance(raw_text, str) and raw_text.strip():
            normalized = normalize(raw_text)
            hmac16 = component(nonce, normalized)
            digest = hashlib.sha256(hmac16).hexdigest()
            candidates.append({
                "sheet": cell["sheet"],
                "sheet_visibility": cell["sheet_visibility"],
                "cell": cell_address,
                "record_id": cell["record_id"],
                "value_kind": cell["value_kind"],
                "text_sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                "normalized_text_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
                "component_sha256": digest,
                "match": hmac.compare_digest(digest, target.hex()),
                "value_provenance": "original BIFF8 cell record/cache bytes; no LibreOffice recalculation",
            })
    matches = [item for item in candidates if item["match"]]
    safe_records = [_safe_record_summary(cell) for cell in cells]
    return {
        "status": "MATCH_REQUIRES_SOURCE_REVIEW" if matches else
                  f"NO_RAW_{cell_address}_VALUE_MATCH" if candidates else
                  f"NO_RAW_{cell_address}_TEXT_VALUE",
        "cell": cell_address,
        "workbook": {"name": path.name, "size_bytes": info.st_size, "sha256_before": before,
                     "sha256_after": after, "source_unchanged": True, "stream_name": stream_name},
        "candidate_material_redacted": True,
        "cell_records": safe_records,
        "candidate_count": len(candidates),
        "match_count": len(matches),
        "candidates": candidates,
        "limitations": [
            f"Only exact {cell_address} on worksheet substreams is examined; no neighboring cells or comments are scanned.",
            "Only LABEL, RSTRING, LABELSST with a single-record SST, and FORMULA cached STRING are decoded.",
            "SST CONTINUE chains, encrypted workbooks, and unsupported record forms fail closed.",
            "Formula expression tokens are preserved only as hashes and never treated as phrase text.",
            "Candidate text, normalized phrase, HMAC bytes, nonce, and raw BIFF records are not emitted.",
            "A hash hit still requires original workbook custody and independent authorship/context review.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, type=Path)
    parser.add_argument("--resources", type=Path, default=Path("resources"))
    parser.add_argument("--cell", choices=SUPPORTED_CELLS, default=DEFAULT_CELL,
                        help="inspect only this pre-registered exact cell (default: M10)")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = inspect_workbook(args.workbook, args.resources, args.cell)
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
