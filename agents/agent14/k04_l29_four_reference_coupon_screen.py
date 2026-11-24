#!/usr/bin/env python3
"""Bounded, read-only K04 screen for two L-29/N four-reference hypotheses.

Run from repository root:
  python agents/agent14/k04_l29_four_reference_coupon_screen.py

For the supplied ZIP extraction:
  python agents/agent14/k04_l29_four_reference_coupon_screen.py --root /path/to/extracted-export

Never prints candidate bytes and never edits source or acceptance files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
import struct
import zlib
from decimal import Decimal
from pathlib import Path


def load_inputs(root: Path):
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    routing = json.loads((root / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    fleet_path = root / "evidence" / "h17-supplemental-office-files" / "print-fleet-retirement-note.txt"
    csv_path = root / "evidence" / "h17-supplemental-office-files" / "supplier-reconciliation-L29.csv"
    fleet_text = fleet_path.read_text(encoding="utf-8")
    fleet_fields = next(line for line in fleet_text.splitlines() if line.startswith("PS-261003-0417")).split()
    assert fleet_fields == ["PS-261003-0417", "ESC-N", "L-29/N", "FA-17", "H17-POL-17/A3"]
    refs = fleet_fields[1:]

    binder = []
    for line in fleet_text.splitlines():
        m = re.match(r"^L-29/N\s+(\d{2})\s+(ST-\d{3})\s+(.+)$", line)
        if m:
            binder.append((m.group(1), m.group(2), m.group(3)))
    assert binder == [
        ("01", "ST-094", "lid plate, return"),
        ("02", "ST-081", "edge guide, exchange"),
        ("03", "ST-106", "separator, refit"),
        ("04", "ST-099", "hinge, retain"),
        ("05", "ST-112", "catch, clean"),
    ]

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        data_lines = [line for line in f if not line.startswith("#")]
    all_rows = list(csv.DictReader(data_lines))
    selected = {}
    south_credit = None
    for row in all_rows:
        if row["source"] == "L29" and row["run"] == "R3" and row["posting"] == "POSTED":
            if row["account"] == "FA-17" and row["folio_or_jacket"] == "H17-POL-17/A3":
                selected[row["line_ref"]] = row
            elif row["line_ref"] == "ST-151" and row["account"] == "LV-42" and row["folio_or_jacket"] == "CS-18/5":
                south_credit = row
    expected = {
        "ST-094": ("18.40", "lid-plate labour"),
        "ST-081": ("4.20", "guide rail"),
        "ST-106": ("12.50", "separator fitting"),
        "ST-099": ("0.00", "hinge realignment"),
        "ST-112": ("0.00", "catch cleaning"),
    }
    for ticket, (amount, description) in expected.items():
        assert (selected[ticket]["amount_eur"], selected[ticket]["description"]) == (amount, description)
    assert south_credit is not None
    assert (south_credit["amount_eur"], south_credit["description"]) == ("0.00", "guide shim credit")
    return acceptance, routing, refs, binder, selected, south_credit


def build_candidates(refs, rows, ticket_numbers, amounts_cents, five_refs):
    candidates = []

    def add(label, coupon):
        if len(coupon) == 16:
            candidates.append((label, coupon))

    for t_endian, a_endian in itertools.product(("big", "little"), repeat=2):
        add(f"ticket16+amount16:{t_endian}/{a_endian}", b"".join(
            t.to_bytes(2, t_endian) + a.to_bytes(2, a_endian)
            for t, a in zip(ticket_numbers, amounts_cents)
        ))
        add(f"amount16+ticket16:{a_endian}/{t_endian}", b"".join(
            a.to_bytes(2, a_endian) + t.to_bytes(2, t_endian)
            for t, a in zip(ticket_numbers, amounts_cents)
        ))
    for endian in ("big", "little"):
        add(f"ticket_u32_{endian}", b"".join(t.to_bytes(4, endian) for t in ticket_numbers))
        add(f"amount_cents_u32_{endian}", b"".join(a.to_bytes(4, endian) for a in amounts_cents))

    for delim in ("", "\n", "\r\n"):
        for endian in ("big", "little"):
            add(f"fullrow_crc32:{delim!r}:{endian}", b"".join(
                zlib.crc32((",".join(r[k] for k in r.keys()) + delim).encode()).to_bytes(4, endian)
                for r in rows
            ))
    for delimiter in ("", "|", ","):
        for endian in ("big", "little"):
            add(f"ref_cents_crc32:{delimiter!r}:{endian}", b"".join(
                zlib.crc32((r["line_ref"] + delimiter + str(a)).encode()).to_bytes(4, endian)
                for r, a in zip(rows, amounts_cents)
            ))

    hash_fns = {
        "crc32": lambda b: zlib.crc32(b).to_bytes(4, "big"),
        "md5_first4": lambda b: hashlib.md5(b).digest()[:4],
        "md5_last4": lambda b: hashlib.md5(b).digest()[-4:],
        "sha1_first4": lambda b: hashlib.sha1(b).digest()[:4],
        "sha256_first4": lambda b: hashlib.sha256(b).digest()[:4],
        "sha256_last4": lambda b: hashlib.sha256(b).digest()[-4:],
        "blake2s4": lambda b: hashlib.blake2s(b, digest_size=4).digest(),
    }
    value_sets = {
        "ticket": [r["line_ref"].encode() for r in rows],
        "ticket_suffix": [f"{n:03d}".encode() for n in ticket_numbers],
        "ticket_amount_text": [f"{r['line_ref']}|{r['amount_eur']}".encode() for r in rows],
        "ticket_amount_cents": [f"{r['line_ref']}|{a}".encode() for r, a in zip(rows, amounts_cents)],
    }
    for source, values in value_sets.items():
        for hname, fn in hash_fns.items():
            add(f"{source}:{hname}", b"".join(fn(v) for v in values))

    ascii_values = {
        "four_zero_padded_ticket_ids": "".join(f"{n:04d}" for n in ticket_numbers),
        "four_ticket_ids_space_pad": "".join(f"{n:03d}" for n in ticket_numbers).ljust(16, " "),
        "four_ticket_ids_zero_pad": "".join(f"{n:03d}" for n in ticket_numbers).ljust(16, "0"),
        "four_part_abbreviations": "LIDPGUIDSEPAHING",
        "four_part_abbreviations_dash": "LIDP-GUID-SEPA-HING"[:16],
    }
    for label, value in ascii_values.items():
        add(label, value.encode())
    for endian in (">", "<"):
        add(f"float32_amounts_{endian}", b"".join(struct.pack(endian + "f", a / 100) for a in amounts_cents))
        add(f"float32_amounts_reverse_{endian}", b"".join(struct.pack(endian + "f", a / 100) for a in amounts_cents[::-1]))

    selected_refs = [r["line_ref"] for r in rows]
    input_values = {
        "four_ids_nodiv": "".join(selected_refs).encode(),
        "four_ids_comma": ",".join(selected_refs).encode(),
        "four_ids_pipe": "|".join(selected_refs).encode(),
        "four_ids_lf": "\n".join(selected_refs).encode(),
        "five_ids_nodiv": "".join(five_refs).encode(),
        "five_ids_comma": ",".join(five_refs).encode(),
        "five_ids_pipe": "|".join(five_refs).encode(),
        "five_ids_lf": "\n".join(five_refs).encode(),
        "four_rows_lf": "\n".join(",".join(r[k] for k in r.keys()) for r in rows).encode(),
        "four_rows_pipe": "|".join(",".join(r[k] for k in r.keys()) for r in rows).encode(),
    }
    hash128 = {
        "md5": lambda b: hashlib.md5(b).digest(),
        "sha1_first16": lambda b: hashlib.sha1(b).digest()[:16],
        "sha256_first16": lambda b: hashlib.sha256(b).digest()[:16],
        "sha3_256_first16": lambda b: hashlib.sha3_256(b).digest()[:16],
        "blake2b16": lambda b: hashlib.blake2b(b, digest_size=16).digest(),
        "blake2s16": lambda b: hashlib.blake2s(b, digest_size=16).digest(),
    }
    for input_name, payload in input_values.items():
        for hname, fn in hash128.items():
            add(f"{input_name}:{hname}", fn(payload))

    ref_hashes = {
        "crc32": lambda b: zlib.crc32(b).to_bytes(4, "big"),
        "md5_first4": lambda b: hashlib.md5(b).digest()[:4],
        "sha1_first4": lambda b: hashlib.sha1(b).digest()[:4],
        "sha256_first4": lambda b: hashlib.sha256(b).digest()[:4],
        "blake2s4": lambda b: hashlib.blake2s(b, digest_size=4).digest(),
    }
    for hname, fn in ref_hashes.items():
        add(f"route_refs:{hname}", b"".join(fn(x.encode()) for x in refs))
    cleaned = [re.sub(r"[^A-Za-z0-9]", "", x) for x in refs]
    for pad in (" ", "0", "\x00"):
        add(f"route_refs_compact_pad_{ord(pad)}", b"".join(x.upper()[:4].ljust(4, pad).encode() for x in cleaned))
    for sep in ("", "|", ",", "\n", "/"):
        payload = sep.join(refs).encode()
        for hname, fn in hash128.items():
            add(f"route_refs_join:{sep!r}:{hname}", fn(payload))
    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("resources"),
                        help="resource root containing evidence/ and acceptance.json")
    args = parser.parse_args()
    acceptance, routing, refs, binder, selected, south_credit = load_inputs(args.root)
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    selectors = {
        "tabs_01_04_four_repair_items": ["ST-094", "ST-081", "ST-106", "ST-099"],
        "tabs_01_02_03_05_conditional_three_plus_tab05": ["ST-094", "ST-081", "ST-106", "ST-112"],
        "three_positive_north_plus_explicit_l29s_credit": ["ST-094", "ST-081", "ST-106", "ST-151"],
    }
    all_values = set()
    results = []
    for name, tickets in selectors.items():
        rows = [selected[t] if t in selected else south_credit for t in tickets]
        numbers = [int(t.split("-")[1]) for t in tickets]
        amounts = [int(Decimal(r["amount_eur"]) * 100) for r in rows]
        candidates = build_candidates(refs, rows, numbers, amounts, [t for _, t, _ in binder])
        matches = []
        for label, coupon in candidates:
            all_values.add(coupon)
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            if hashlib.sha256(component).hexdigest() == target:
                matches.append(label)
        results.append({
            "selector": name,
            "tickets_in_order": tickets,
            "candidate_transformations": len(candidates),
            "unique_coupon_values": len({coupon for _, coupon in candidates}),
            "commitment_matches": len(matches),
            "matching_transformations": matches,
        })
    assert [r["candidate_transformations"] for r in results] == [159, 159, 159]
    assert [r["unique_coupon_values"] for r in results] == [156, 156, 156]
    assert len(all_values) == 332
    print(json.dumps({
        "hypothesis": "K04 coupon is a four-reference object derived from the ESC-N / L-29/N binder trail",
        "results": results,
        "total_candidate_transformations": sum(r["candidate_transformations"] for r in results),
        "total_unique_coupon_values": len(all_values),
        "total_commitment_matches": sum(r["commitment_matches"] for r in results),
        "source_files_unchanged": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
