#!/usr/bin/env python3
"""Bounded read-only K04 probe for the K01-selected cells in mug-stock.xls.

The only cells inspected are the eight addresses derived from the accepted
K01 component. For each worksheet, the probe checks two bounded, complete
16-byte candidates: the native little-endian cell-XF (ixfe) indexes and the
effective BIFF8 icvFore/icvBack index pairs. It does not scan arbitrary cells,
images, or OfficeArt. Candidate bytes, raw XF records, and mask material are
redacted from its output.

Run from a repository checkout:
  python work/h17_k04_mug_stock_xf_probe.py /path/to/mug-stock.xls
  python work/h17_k04_mug_stock_xf_probe.py /path/to/mug-stock.xls --sheet Stock
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

from h17_redaction import redact_by_default, redact_sensitive

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from h17_biff_officeart import CompoundFile, _iter_biff_records  # noqa: E402
from h17_k04_biff8_xf_candidate import (  # noqa: E402
    XFError,
    assemble_k04_payload,
    check_k04_commitment,
    effective_cell_pattern,
    parse_palette_payload,
    verify_and_derive_k01_cells,
)

RID_EOF = 0x000A
RID_FILEPASS = 0x002F
RID_BOUNDSHEET = 0x0085
RID_XF = 0x00E0
RID_PALETTE = 0x0092
RID_MULRK = 0x00BD
RID_MULBLANK = 0x00BE
CELL_RECORDS = {
    0x0006,  # FORMULA
    0x0201,  # BLANK
    0x0203,  # NUMBER
    0x0204,  # LABEL
    0x0205,  # BOOLERR
    0x00D6,  # RSTRING
    0x00FD,  # LABELSST
    0x027E,  # RK
}


class ProbeError(ValueError):
    """Malformed or unsupported workbook structure."""


def parse_boundsheet(payload: bytes) -> dict:
    if len(payload) < 8:
        raise ProbeError("short BOUNDSHEET record")
    stream_offset = struct.unpack_from("<I", payload, 0)[0]
    visibility, sheet_type, char_count, flags = payload[4:8]
    width = 2 if (flags & 0x01) else 1
    name_bytes = payload[8:8 + char_count * width]
    if len(name_bytes) != char_count * width:
        raise ProbeError("truncated BOUNDSHEET name")
    name = name_bytes.decode("utf-16le" if width == 2 else "latin1")
    return {
        "offset": stream_offset,
        "visibility": visibility,
        "sheet_type": sheet_type,
        "name": name,
    }


def parse_sheet_cells(stream: bytes, sheet_offset: int) -> dict[tuple[int, int], int]:
    """Return (zero-based row, zero-based col) -> XF index for explicit cell records."""
    cells: dict[tuple[int, int], int] = {}

    def add(row: int, col: int, xf_index: int, record_id: int) -> None:
        key = (row, col)
        if key in cells:
            raise ProbeError(
                f"duplicate cell XF record at row={row+1}, col={col+1} "
                f"(record 0x{record_id:04X})"
            )
        cells[key] = xf_index

    saw_eof = False
    for _offset, record_id, payload in _iter_biff_records(stream, sheet_offset):
        if record_id == RID_EOF:
            saw_eof = True
            break
        if record_id in CELL_RECORDS:
            if len(payload) < 6:
                raise ProbeError(f"short cell record 0x{record_id:04X}")
            row, col, xf_index = struct.unpack_from("<HHH", payload, 0)
            add(row, col, xf_index, record_id)
        elif record_id == RID_MULRK:
            if len(payload) < 12:
                raise ProbeError("short MULRK record")
            row, first_col = struct.unpack_from("<HH", payload, 0)
            last_col = struct.unpack_from("<H", payload, len(payload) - 2)[0]
            entries = payload[4:-2]
            if len(entries) % 6:
                raise ProbeError("malformed MULRK entry array")
            count = len(entries) // 6
            if count == 0 or last_col != first_col + count - 1:
                raise ProbeError("MULRK column range mismatch")
            for i in range(count):
                xf_index = struct.unpack_from("<H", entries, i * 6)[0]
                add(row, first_col + i, xf_index, record_id)
        elif record_id == RID_MULBLANK:
            if len(payload) < 8:
                raise ProbeError("short MULBLANK record")
            row, first_col = struct.unpack_from("<HH", payload, 0)
            last_col = struct.unpack_from("<H", payload, len(payload) - 2)[0]
            entries = payload[4:-2]
            if len(entries) % 2:
                raise ProbeError("malformed MULBLANK entry array")
            count = len(entries) // 2
            if count == 0 or last_col != first_col + count - 1:
                raise ProbeError("MULBLANK column range mismatch")
            for i in range(count):
                xf_index = struct.unpack_from("<H", entries, i * 2)[0]
                add(row, first_col + i, xf_index, record_id)
    if not saw_eof:
        raise ProbeError("worksheet substream has no EOF record")
    return cells


def parse_workbook_stream(stream: bytes) -> dict:
    """Parse global XF/PALETTE/BOUNDSHEET records and exact worksheet cell XFs."""
    xfs: list[bytes] = []
    palette: dict[int, tuple[int, int, int, int]] = {}
    palette_payload = None
    sheets: list[dict] = []
    saw_global_eof = False
    global_end = None
    for record_offset, record_id, payload in _iter_biff_records(stream, 0):
        if record_id == RID_FILEPASS:
            raise ProbeError("encrypted workbook stream is out of scope; refusing decryption")
        if record_id == RID_XF:
            if len(payload) != 20:
                raise ProbeError(f"unexpected XF payload length {len(payload)}")
            xfs.append(payload)
        elif record_id == RID_PALETTE:
            if palette_payload is not None:
                raise ProbeError("multiple PALETTE records are not supported")
            palette_payload = payload
            palette = parse_palette_payload(payload)
        elif record_id == RID_BOUNDSHEET:
            sheets.append(parse_boundsheet(payload))
        elif record_id == RID_EOF:
            saw_global_eof = True
            global_end = record_offset + 4 + len(payload)
            break
    if not saw_global_eof:
        raise ProbeError("workbook globals have no EOF record")
    if not xfs:
        raise ProbeError("workbook has no XF records")
    if not sheets:
        raise ProbeError("workbook has no BOUNDSHEET records")
    for sheet in sheets:
        offset = sheet["offset"]
        if not global_end <= offset < len(stream):
            raise ProbeError(
                f"sheet {sheet['name']!r} offset is out of range or overlaps workbook globals"
            )
        sheet["cell_xfs"] = parse_sheet_cells(stream, offset)
    return {
        "xfs": xfs,
        "palette": palette,
        "palette_payload": palette_payload,
        "sheets": sheets,
    }


def load_rules(repo_root: Path) -> tuple[str, str, bytes, tuple[str, ...]]:
    candidate = json.loads((repo_root / "candidate.json").read_text())
    acceptance = json.loads((repo_root / "resources" / "acceptance.json").read_text())
    routing = json.loads(
        (repo_root / "resources" / "evidence" / "recovery-routing.json").read_text()
    )
    k01_hex = candidate.get("K01")
    if not isinstance(k01_hex, str):
        raise ProbeError("candidate.json does not contain a recovered K01 component")
    k01_cells = verify_and_derive_k01_cells(
        k01_hex, acceptance["slot_sha256"]["K01"]
    )
    k04_mask = bytes.fromhex(routing["K04"]["masked_component"])
    k04_hash = acceptance["slot_sha256"]["K04"]
    if len(k04_mask) != 16:
        raise ProbeError("official K04 masked_component is not 16 bytes")
    return k04_hash, k01_hex, k04_mask, k01_cells


@redact_by_default
def probe_sheet(
    sheet: dict,
    xfs: list[bytes],
    palette: dict,
    cells: tuple[str, ...],
    mask: bytes,
    target_hash: str,
) -> dict:
    # Convert the already-verified A1 selector to zero-based coordinates.
    import re

    cell_xf_indices = []
    missing = []
    for address in cells:
        match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", address)
        if not match:
            raise ProbeError(f"invalid derived A1 address: {address}")
        col_letters, row_text = match.groups()
        col = 0
        for ch in col_letters:
            col = col * 26 + (ord(ch) - ord("A") + 1)
        key = (int(row_text) - 1, col - 1)
        xf_index = sheet["cell_xfs"].get(key)
        if xf_index is None:
            missing.append(address)
        else:
            cell_xf_indices.append(xf_index)
    result = {
        "sheet": sheet["name"],
        "visibility": sheet["visibility"],
        "selected_cells": list(cells),
        "missing_cells": missing,
    }
    if sheet["sheet_type"] != 0:
        result["status"] = "SKIPPED_NON_WORKSHEET"
        return result
    if missing:
        result["status"] = "INCOMPLETE"
        return result
    colour_payload = assemble_k04_payload(cell_xf_indices, xfs)
    colour_check = check_k04_commitment(colour_payload, mask, target_hash, reveal=True)

    # BIFF8 cell records store ixfe as a uint16 little-endian field. Preserve
    # those native field bytes in K01 selector order as a distinct candidate.
    ixfe_payload = b"".join(struct.pack("<H", index) for index in cell_xf_indices)
    ixfe_check = check_k04_commitment(ixfe_payload, mask, target_hash, reveal=True)

    effective_patterns = [
        effective_cell_pattern(xf_index, xfs) for xf_index in cell_xf_indices
    ]
    any_match = colour_check["pass"] or ixfe_check["pass"]
    status = (
        "COMMITMENT_MATCH_REQUIRES_SOURCE_REVIEW"
        if any_match
        else "MISS_WITHIN_TESTED_XF_MODEL"
    )
    result.update(
        {
            "status": status,
            "candidate_material_redacted": True,
            "colour_index_check": {
                "pass": colour_check["pass"],
                "sha256": colour_check["sha256"],
            },
            "raw_ixfe_little_endian_check": {
                "pass": ixfe_check["pass"],
                "sha256": ixfe_check["sha256"],
            },
            "style_coherence": {
                "effective_fill_patterns_uniform": len(
                    {pattern.fill_pattern for pattern in effective_patterns}
                ) == 1,
                "custom_palette_present": bool(palette),
            },
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="authenticated original mug-stock.xls")
    parser.add_argument(
        "--sheet",
        help="restrict to one exact worksheet name; default tests exact cells on each sheet",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=ROOT, help="workplace-v2 checkout root"
    )
    args = parser.parse_args()
    if not args.workbook.is_file():
        parser.error(f"workbook does not exist: {args.workbook}")
    try:
        target_hash, k01_hex, mask, k01_cells = load_rules(args.repo_root)
        workbook_bytes = args.workbook.read_bytes()
        cfb = CompoundFile(workbook_bytes)
        stream = cfb.read_stream("Workbook")
        if stream is None:
            stream = cfb.read_stream("Book")
        if stream is None:
            raise ProbeError("OLE container has neither Workbook nor Book stream")
        parsed = parse_workbook_stream(stream)
        sheets = parsed["sheets"]
        if args.sheet:
            sheets = [s for s in sheets if s["name"] == args.sheet]
            if not sheets:
                raise ProbeError(f"worksheet not found: {args.sheet}")
        results = [
            probe_sheet(s, parsed["xfs"], parsed["palette"], k01_cells, mask, target_hash)
            for s in sheets
        ]
        output = {
            "workbook_name": args.workbook.name,
            "workbook_sha256": hashlib.sha256(workbook_bytes).hexdigest(),
            "k01_component_sha256": hashlib.sha256(bytes.fromhex(k01_hex)).hexdigest(),
            "k01_cells": list(k01_cells),
            "xf_count": len(parsed["xfs"]),
            "custom_palette_count": len(parsed["palette"]),
            "candidate_material_redacted": True,
            "results": results,
        }
        output = redact_sensitive(output)
        print(json.dumps(output, indent=2))
        return 0
    except (OSError, KeyError, ValueError, XFError) as exc:
        print(json.dumps(redact_sensitive({"status": "ERROR", "error": str(exc)}), indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
