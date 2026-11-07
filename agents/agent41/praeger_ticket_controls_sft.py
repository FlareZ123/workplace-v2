#!/usr/bin/env python3
"""Pinned source-only control for the Praeger ticket-suffix page hypothesis.

Run from the repository root:
    python agents/agent41/praeger_ticket_controls_sft.py
Or pass the supplemental source directory explicitly with --source-root.
This test reads official source files only. It does not open or extract book text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


EXPECTED_SHA256 = {
    "supplier-reconciliation-L29.csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "print-fleet-retirement-note.txt": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
}

PRIMARY_NORTH = ("ST-094", "ST-081", "ST-106", "ST-099", "ST-112")
PRIMARY_SOUTH = ("ST-130", "ST-151", "ST-121", "ST-135", "ST-142")
CONTROL_ROWS = {
    "ST-157": {
        "source": "L29",
        "run": "R3",
        "posting": "POSTED",
        "account": "ST-09",
        "folio_or_jacket": "STORES/FLT",
        "amount_eur": "0.00",
        "description": "spare inspection",
    },
    "ST-164": {
        "source": "L29",
        "run": "R3",
        "posting": "POSTED",
        "account": "ST-09",
        "folio_or_jacket": "STORES/FLT",
        "amount_eur": "0.00",
        "description": "spare inspection",
    },
    "ST-176": {
        "source": "L30",
        "run": "R1",
        "posting": "PENDING",
        "account": "LV-42",
        "folio_or_jacket": "CS-18/5",
        "amount_eur": "4.80",
        "description": "following period",
    },
}
PAGE_BOUNDARIES = {
    "Praeger 1947 third edition": 118,
    "Praeger 1997 reprint": 111,
}


def normalized_sha256(path: Path) -> str:
    """Hash source bytes with CRLF normalized for Windows checkout portability."""
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def load_csv_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(line for line in source if not line.lstrip().startswith("#"))
        return {row["line_ref"]: row for row in rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("resources/evidence/h17-supplemental-office-files"),
        help="directory containing the two official source files",
    )
    args = parser.parse_args()

    csv_path = args.source_root / "supplier-reconciliation-L29.csv"
    fleet_path = args.source_root / "print-fleet-retirement-note.txt"

    for path in (csv_path, fleet_path):
        actual = normalized_sha256(path)
        expected = EXPECTED_SHA256[path.name]
        assert actual == expected, f"{path.name}: SHA256 mismatch: {actual}"

    rows = load_csv_rows(csv_path)
    fleet_note = fleet_path.read_text(encoding="utf-8-sig")

    for ticket in PRIMARY_NORTH + PRIMARY_SOUTH:
        assert ticket in fleet_note, f"primary binder ticket missing from fleet note: {ticket}"

    for ticket, expected_fields in CONTROL_ROWS.items():
        row = rows[ticket]
        for field, expected_value in expected_fields.items():
            assert row[field] == expected_value, (
                f"{ticket} {field}: expected {expected_value!r}, got {row[field]!r}"
            )

    watch_spare_anchor = re.search(
        r"PS-261003-0420\s+WATCH-SPARE\s+L-29/W\s+ST-09\s+STORES/FLT",
        fleet_note,
    )
    assert watch_spare_anchor, "L-29/W Watch-Spare anchor not found in fleet note"

    primary_pages = {
        **{ticket: int(ticket[3:]) for ticket in PRIMARY_NORTH},
        **{ticket: int(ticket[3:]) for ticket in PRIMARY_SOUTH},
    }
    control_pages = {ticket: int(ticket[3:]) for ticket in CONTROL_ROWS}

    print("Pinned official-source hashes: PASS")
    print("Primary L-29/N and L-29/S binder references: PASS")
    print("Out-of-set control rows and exact CSV fields: PASS")
    print("L-29/W Watch-Spare account/folio anchor: PASS")
    print()
    print("Control rows:")
    for ticket, row in CONTROL_ROWS.items():
        print(
            f"  {ticket}: page-candidate={control_pages[ticket]}, "
            f"{row['source']}/{row['run']}/{row['posting']}, "
            f"{row['account']} {row['folio_or_jacket']}, "
            f"{row['description']} EUR {row['amount_eur']}"
        )
    print()
    for edition, boundary in PAGE_BOUNDARIES.items():
        control_sections = {
            ticket: ("North" if page < boundary else "South")
            for ticket, page in control_pages.items()
        }
        primary_north_count = sum(
            page < boundary for ticket, page in primary_pages.items()
            if ticket in PRIMARY_NORTH
        )
        primary_south_count = sum(
            page >= boundary for ticket, page in primary_pages.items()
            if ticket in PRIMARY_SOUTH
        )
        print(
            f"{edition}: primary target split "
            f"{primary_north_count}/5 North, {primary_south_count}/5 South; "
            f"all three controls {control_sections}"
        )

    assert all(page >= 118 for page in control_pages.values())
    assert all(page >= 111 for page in control_pages.values())
    print()
    print("Conclusion: controls are South under both tested boundaries.")
    print("They do not discriminate 1947 from 1997 and do not authenticate ticket suffixes as page numbers.")


if __name__ == "__main__":
    main()
