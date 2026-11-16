#!/usr/bin/env python3
"""Test an L-29/N -> PTW -> four-bay serial block as a K04 candidate.

ST-to-PTW +304 is a candidate locator, not an authenticated foreign key.
Only complete 16-byte objects emitted by the retained signed
CLOSED/AS_LEFT permit records and explicit source orders are tested.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import zlib
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("resources"),
                    help="resources directory, or extracted archive root containing evidence/")
    root = ap.parse_args().root
    ev = root / "evidence" if (root / "evidence").is_dir() else root / "resources/evidence"
    accept_path = root / "acceptance.json" if (root / "acceptance.json").exists() else root / "resources/acceptance.json"

    note = (ev / "h17-supplemental-office-files/print-fleet-retirement-note.txt").read_text()
    closeout_mail = (ev / "mail/04.eml").read_text()
    work_order = (ev / "maintenance/work-order-417.html").read_text()
    routing = json.loads((ev / "recovery-routing.json").read_text())
    acceptance = json.loads(accept_path.read_text())
    target = acceptance["slot_sha256"]["K04"]
    mask = bytes.fromhex(routing["K04"]["masked_component"])

    supplier_path = ev / "h17-supplemental-office-files/supplier-reconciliation-L29.csv"
    supplier_lines = [line for line in supplier_path.read_text().splitlines()
                      if line and not line.startswith("#")]
    supplier = list(csv.DictReader(supplier_lines))
    receipts = [json.loads(line) for line in
                (ev / "maintenance/seal-receipts.jsonl").read_text().splitlines() if line.strip()]

    # Read the L-29/N tab order from the return register. The +304 ST->PTW
    # mapping is the hypothesis under test, not a rule stated by the custodian.
    tabs = re.findall(r"L-29/N\s+0(\d)\s+(ST-\d+)", note)
    chosen, missing = [], []
    for tab, ticket in sorted(((int(t), s) for t, s in tabs)):
        matches = [r for r in supplier if r["line_ref"] == ticket and r["source"] == "L29"
                   and r["run"] == "R3" and r["posting"] == "POSTED"
                   and r["account"] == "FA-17" and r["folio_or_jacket"] == "H17-POL-17/A3"]
        if len(matches) != 1:
            missing.append({"tab": tab, "ticket": ticket,
                            "reason": f"expected one R3 POSTED FA-17 row, got {len(matches)}"})
            continue
        permit = f"PTW-{int(ticket.split('-')[1]) + 304}"
        valid = [r for r in receipts if r.get("permit") == permit
                 and r.get("state") == "CLOSED" and r.get("fitment") == "AS_LEFT"
                 and r.get("signed") is True and r.get("serial")]
        if not valid:
            missing.append({"tab": tab, "ticket": ticket, "permit": permit,
                            "reason": "no retained signed CLOSED AS_LEFT serial"})
            continue
        revision = max(int(r.get("revision", 0)) for r in valid)
        latest = [r for r in valid if int(r.get("revision", 0)) == revision]
        if len(latest) != 1:
            missing.append({"tab": tab, "ticket": ticket, "permit": permit,
                            "reason": f"ambiguous latest records: {len(latest)}"})
            continue
        r = latest[0]
        chosen.append({"tab": tab, "ticket": ticket, "permit": permit,
                       "bay": r.get("bay"), "serial": r["serial"], "revision": revision})

    by_bay = {r["bay"]: r for r in chosen}
    if set(by_bay) != set("ABCD") or len(chosen) != 4:
        raise SystemExit(f"Expected one retained serial in each bay A-D; got {chosen}; missing={missing}")

    sketch = re.search(r"witness walk\s+was\s+([A-D]),\s*([A-D]),\s*([A-D]),\s*([A-D])",
                       closeout_mail, re.I)
    if not sketch:
        raise SystemExit("Could not read signed witness-walk order from MAIL-04")
    sketch_order = list(sketch.groups())
    assert "Field sketch supersedes cabinet lettering" in work_order

    orders = {
        "L29_N_tab_order_available": [r["bay"] for r in sorted(chosen, key=lambda x: x["tab"])],
        "PTW417_signed_witness_walk": sketch_order,
        "natural_bay_order": list("ABCD"),
    }
    results = []
    for order_name, order in orders.items():
        block = b"".join(bytes.fromhex(by_bay[bay]["serial"][3:]) for bay in order)
        for mode, component in [
            ("direct_component", block),
            ("payload_then_route_xor", bytes(a ^ b for a, b in zip(block, mask))),
        ]:
            digest = sha(component)
            results.append({"order": order_name, "mode": mode,
                            "component_hex": component.hex().upper(),
                            "sha256": digest, "matches_K04": digest == target})

        # Bounded per-record CRC32 alternatives; shared CRC semantics are not
        # asserted merely because the recorder export also uses CRC32.
        for input_mode in ["serial_bytes", "serial_ascii", "permit_bay_serial_ascii"]:
            values = []
            for bay in order:
                record = by_bay[bay]
                serial = bytes.fromhex(record["serial"][3:])
                if input_mode == "serial_bytes":
                    data = serial
                elif input_mode == "serial_ascii":
                    data = record["serial"][3:].encode("ascii")
                else:
                    data = f'{record["permit"]}|{bay}|{record["serial"][3:]}'.encode("ascii")
                values.append(zlib.crc32(data) & 0xFFFFFFFF)
            for endian in ["big", "little"]:
                crc_block = b"".join(value.to_bytes(4, endian) for value in values)
                for mode, component in [
                    ("crc32_direct", crc_block),
                    ("crc32_then_route_xor", bytes(a ^ b for a, b in zip(crc_block, mask))),
                ]:
                    digest = sha(component)
                    results.append({"order": order_name, "mode": mode, "input": input_mode,
                                    "endian": endian, "component_hex": component.hex().upper(),
                                    "sha256": digest, "matches_K04": digest == target})

    source_files = [
        "h17-supplemental-office-files/print-fleet-retirement-note.txt",
        "h17-supplemental-office-files/supplier-reconciliation-L29.csv",
        "maintenance/seal-receipts.jsonl",
        "maintenance/work-order-417.html",
        "mail/04.eml",
        "archive-labels.ini",
        "recovery-routing.json",
    ]
    source_hashes = {name: sha((ev / name).read_bytes()) for name in source_files}
    print(json.dumps({
        "candidate_mapping": "ST-xxx -> PTW-(xxx+304); unverified locator hypothesis",
        "selected_records": chosen,
        "missing_or_unavailable": missing,
        "orders": orders,
        "K04_target_sha256": target,
        "K04_mask": routing["K04"]["masked_component"],
        "results": results,
        "hits": [r for r in results if r["matches_K04"]],
        "source_sha256": source_hashes,
    }, indent=2))


if __name__ == "__main__":
    main()
