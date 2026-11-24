#!/usr/bin/env python3
"""Read-only K04 probe for an explicitly mapped four-tab BIFF8 workbook.

K01 contains four ordered ink-control groups A/B/C/D, with two cell
coordinates per group. Supply the four worksheet names explicitly in that
order; this tool never infers worksheet order or names. It tests only the
existing bounded BIFF8 candidates: native little-endian ixfe indexes and
effective icvFore/icvBack pairs. Candidate bytes are redacted.

Example:
  python work/h17_k04_mug_stock_xf_multitab_probe.py mug-stock.xls --group-sheets StockA,StockB,StockC,StockD
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from h17_k04_mug_stock_xf_probe import (  # noqa: E402
    CompoundFile, ProbeError, load_rules, parse_workbook_stream, probe_sheet,
)

GROUPS = ("A", "B", "C", "D")


def parse_group_sheets(value: str) -> tuple[str, str, str, str]:
    names = tuple(part.strip() for part in value.split(","))
    if len(names) != 4 or any(not name for name in names):
        raise ProbeError("--group-sheets requires exactly four non-empty worksheet names")
    if len(set(names)) != 4:
        raise ProbeError("--group-sheets must name four distinct worksheets")
    return names  # type: ignore[return-value]


def _a1_key(address: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", address)
    if not match:
        raise ProbeError(f"invalid derived A1 address: {address}")
    letters, row = match.groups()
    column = 0
    for ch in letters:
        column = column * 26 + ord(ch) - ord("A") + 1
    return int(row) - 1, column - 1


def probe_group_mapping(
    parsed: dict,
    group_sheets: tuple[str, str, str, str],
    cells: tuple[str, ...],
    mask: bytes,
    target_hash: str,
) -> dict:
    """Assemble only the two K01-selected cells from each explicit A/B/C/D tab."""
    if len(group_sheets) != 4 or len(set(group_sheets)) != 4:
        raise ProbeError("four distinct group worksheet names are required")
    if len(cells) != 8:
        raise ProbeError("K01 selector must contain exactly eight ordered cells")

    by_name = {}
    for sheet in parsed["sheets"]:
        name = sheet["name"]
        if name in by_name:
            raise ProbeError(f"duplicate worksheet name in workbook: {name!r}")
        by_name[name] = sheet

    mapping = dict(zip(GROUPS, group_sheets))
    missing_sheets = [name for name in group_sheets if name not in by_name]
    if missing_sheets:
        return {
            "status": "INCOMPLETE",
            "reason": "an explicitly requested worksheet is absent",
            "group_sheet_mapping": mapping,
            "missing_sheets": missing_sheets,
            "candidate_material_redacted": True,
        }

    non_worksheets = [
        {"group": group, "sheet": name}
        for group, name in zip(GROUPS, group_sheets)
        if by_name[name]["sheet_type"] != 0
    ]
    if non_worksheets:
        return {
            "status": "SKIPPED_NON_WORKSHEET",
            "group_sheet_mapping": mapping,
            "non_worksheets": non_worksheets,
            "candidate_material_redacted": True,
        }

    merged = {}
    missing_cells = []
    selected = []
    for i, (group, sheet_name) in enumerate(zip(GROUPS, group_sheets)):
        sheet = by_name[sheet_name]
        for address in cells[2 * i: 2 * i + 2]:
            key = _a1_key(address)
            xf_index = sheet["cell_xfs"].get(key)
            selected.append({"group": group, "sheet": sheet_name, "cell": address})
            if xf_index is None:
                missing_cells.append(address)
            elif key in merged:
                raise ProbeError(f"duplicate K01 coordinate across groups: {address}")
            else:
                merged[key] = xf_index

    combined = {
        "name": "explicit A/B/C/D four-tab mapping",
        "visibility": 0,
        "sheet_type": 0,
        "cell_xfs": merged,
    }
    result = probe_sheet(
        combined, parsed["xfs"], parsed["palette"], cells, mask, target_hash
    )
    result["group_sheet_mapping"] = mapping
    result["selected_cell_sheets"] = selected
    result["candidate_material_redacted"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="authenticated original mug-stock.xls")
    parser.add_argument(
        "--group-sheets", required=True,
        help="four explicit worksheet names in K01 group order A,B,C,D",
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    if not args.workbook.is_file() or args.workbook.is_symlink():
        parser.error(f"workbook must be a regular, non-symlink file: {args.workbook}")

    try:
        group_sheets = parse_group_sheets(args.group_sheets)
        target_hash, k01_hex, mask, cells = load_rules(args.repo_root)
        workbook_bytes = args.workbook.read_bytes()
        cfb = CompoundFile(workbook_bytes)
        stream = cfb.read_stream("Workbook") or cfb.read_stream("Book")
        if stream is None:
            raise ProbeError("OLE container has neither Workbook nor Book stream")
        parsed = parse_workbook_stream(stream)
        result = probe_group_mapping(parsed, group_sheets, cells, mask, target_hash)
        print(json.dumps({
            "workbook_name": args.workbook.name,
            "workbook_sha256": hashlib.sha256(workbook_bytes).hexdigest(),
            "k01_component_sha256": hashlib.sha256(bytes.fromhex(k01_hex)).hexdigest(),
            "k01_cells": list(cells),
            "group_order": list(GROUPS),
            "group_sheets": list(group_sheets),
            "xf_count": len(parsed["xfs"]),
            "custom_palette_count": len(parsed["palette"]),
            "candidate_material_redacted": True,
            "result": result,
        }, indent=2))
        return 0
    except (OSError, KeyError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
