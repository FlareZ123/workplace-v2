#!/usr/bin/env python3
"""Reconstruct Agent16's bounded L-29/N five-tab set-digest family.

The original scratch record preserves binder order, row filter, digest family,
header/line-ending variants and 32/0 outcome, but not the terminal-newline
choice. This script makes that missing detail explicit by using no terminal
line ending. It is a reproducible reconstruction, not a guaranteed bitwise
replay of the old scratch run. It never emits candidate bytes or modifies
source or acceptance files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAB_ORDER = ("ST-094", "ST-081", "ST-106", "ST-099", "ST-112")
REQUIRED = {
    "source": "L29",
    "run": "R3",
    "posting": "POSTED",
    "account": "FA-17",
    "folio_or_jacket": "H17-POL-17/A3",
}
DIGESTS = ("md5", "sha256_16", "blake2s_16", "blake2b_16")
SEPARATORS = (("LF", b"\n"), ("CRLF", b"\r\n"))
PINS = {
    "supplier_reconciliation_L29_csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "print_fleet_retirement_note": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    "recovery_routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(name: str, data: bytes) -> bytes:
    if name == "md5":
        return hashlib.md5(data).digest()
    if name == "sha256_16":
        return hashlib.sha256(data).digest()[:16]
    if name == "blake2s_16":
        return hashlib.blake2s(data, digest_size=16).digest()
    if name == "blake2b_16":
        return hashlib.blake2b(data, digest_size=16).digest()
    raise AssertionError(name)


def selected_raw_rows(raw: bytes) -> tuple[bytes, list[bytes]]:
    # Preserve the exact header/data row bytes; the first two records are
    # comments and are not part of the CSV header or candidate material.
    lines = raw.splitlines()
    header_index = next(i for i, line in enumerate(lines) if line.startswith(b"line_ref,"))
    header = lines[header_index]
    raw_data = [line for line in lines[header_index + 1:] if line]
    reader = csv.DictReader([header.decode("utf-8")] + [line.decode("utf-8") for line in raw_data])
    parsed = list(reader)
    assert len(raw_data) == len(parsed)
    selected: dict[str, bytes] = {}
    for line, row in zip(raw_data, parsed):
        if all(row.get(k) == v for k, v in REQUIRED.items()) and row.get("line_ref") in TAB_ORDER:
            ticket = row["line_ref"]
            assert ticket not in selected, f"duplicate selected row: {ticket}"
            selected[ticket] = line
    assert set(selected) == set(TAB_ORDER), (set(selected), set(TAB_ORDER))
    return header, [selected[ticket] for ticket in TAB_ORDER]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=ROOT,
        help="repository root (or extracted archive root for local reproduction)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    evidence = root / "resources/evidence"
    acceptance_path = root / "resources/acceptance.json"
    if not evidence.exists():  # uploaded ZIP layout has evidence/ at its root
        evidence = root / "evidence"
        acceptance_path = root / "acceptance.json"

    csv_path = evidence / "h17-supplemental-office-files/supplier-reconciliation-L29.csv"
    fleet_path = evidence / "h17-supplemental-office-files/print-fleet-retirement-note.txt"
    route_path = evidence / "recovery-routing.json"
    raw = csv_path.read_bytes()
    fleet_raw = fleet_path.read_bytes()
    route_raw = route_path.read_bytes()
    acceptance_raw = acceptance_path.read_bytes()

    observed_pins = {
        "supplier_reconciliation_L29_csv": sha256(raw),
        "print_fleet_retirement_note": sha256(fleet_raw),
        "recovery_routing": sha256(route_raw),
        "acceptance": sha256(acceptance_raw),
    }
    assert observed_pins == PINS, observed_pins

    route = json.loads(route_raw)
    acceptance = json.loads(acceptance_raw)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    header, rows = selected_raw_rows(raw)

    # Binder order is independently stated in the print-fleet register.
    fleet_text = fleet_raw.decode("utf-8")
    tab_positions = [
        fleet_text.index(f"L-29/N    {i:02d}     {ticket}")
        for i, ticket in enumerate(TAB_ORDER, 1)
    ]
    assert tab_positions == sorted(tab_positions)
    assert len(mask) == 16

    candidates = []
    for sep_name, sep in SEPARATORS:
        body = sep.join(rows)
        for include_header in (False, True):
            material = header + sep + body if include_header else body
            for digest_name in DIGESTS:
                raw_digest = digest(digest_name, material)
                for reduction in ("direct", "mask_xor"):
                    component = (
                        raw_digest if reduction == "direct"
                        else bytes(a ^ b for a, b in zip(raw_digest, mask))
                    )
                    candidates.append((sep_name, include_header, digest_name, reduction,
                                       sha256(component) == target))

    assert len(candidates) == 32
    hits = [candidate for candidate in candidates if candidate[-1]]
    assert not hits, hits
    print(json.dumps({
        "experiment": "L-29/N five-tab set-level digest reproduction",
        "source_sha256": observed_pins,
        "tab_order": list(TAB_ORDER),
        "row_filter": REQUIRED,
        "canonical_serialization": (
            "exact raw CSV data rows in L-29/N binder tab order; optional exact CSV "
            "header; LF or CRLF separators; this script uses no terminal line "
            "ending (the original scratch record did not preserve that choice)"
        ),
        "digest_candidates": list(DIGESTS),
        "reductions": ["direct", "mask_xor"],
        "candidate_count": len(candidates),
        "commitment_hits": len(hits),
        "result": "NO_K04_HIT",
        "reproduction_status": "RECONSTRUCTED_FAMILY_NOT_BITWISE_REPLAY",
        "scope": "No additional row subsets, encodings, hash families, terminal-newline variants, or transformations are tested.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
