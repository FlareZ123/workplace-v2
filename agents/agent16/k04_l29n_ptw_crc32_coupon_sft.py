#!/usr/bin/env python3
"""Bounded four-lane CRC32 coupon hypothesis for the ESC-N / L-29/N return.

The +304 ticket->PTW mapping is an empirical source-supported inference, not
an authenticated foreign key. This script tests only a small, source-selected
candidate family: four signed AS_LEFT PTW receipts reached from the L-29/N
binder order, serialized as four IEEE/zlib CRC32 values (plus direct 32-bit
permit-ID representations). It never prints candidate bytes.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import zlib
from pathlib import Path

if "H17_SOURCE_ROOT" in os.environ:
    ROOT = Path(os.environ["H17_SOURCE_ROOT"])
else:
    HERE = Path(__file__).resolve().parents[2]
    if (HERE / "resources" / "evidence").is_dir():
        ROOT = HERE / "resources"
    elif (HERE / "evidence").is_dir():
        ROOT = HERE
    else:
        raise SystemExit("Set H17_SOURCE_ROOT to the extracted H-17 source root")

SUPPLIER = ROOT / "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
FLEET = ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
SEALS = ROOT / "evidence/maintenance/seal-receipts.jsonl"
FORMAT = ROOT / "evidence/recorder/format-note.txt"
ROUTING = ROOT / "evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "acceptance.json"

EXPECTED = {
    SUPPLIER.name: "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    FLEET.name: "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    SEALS.name: "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    FORMAT.name: "78ff213040de20f81bc582cdfc25a4d0930ceb2d3956dbcc944b775b88fd7b22",
    ROUTING.name: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE.name: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

for path in (SUPPLIER, FLEET, SEALS, FORMAT, ROUTING, ACCEPTANCE):
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    assert got == EXPECTED[path.name], (path, got)

fleet_text = FLEET.read_text(encoding="utf-8")
assert "PS-261003-0417   ESC-N           L-29/N        FA-17       H17-POL-17/A3" in fleet_text
binder_order = re.findall(r"^L-29/N\\s+\\d\\d\\s+(ST-\\d{3})\\s+", fleet_text, re.M)
assert binder_order == ["ST-094", "ST-081", "ST-106", "ST-099", "ST-112"]

supplier_lines = SUPPLIER.read_bytes().splitlines()

def posted_a3_line(ticket: str) -> bytes:
    matches = []
    for line in supplier_lines:
        if not line.startswith(ticket.encode("ascii") + b","):
            continue
        fields = line.decode("utf-8").split(",")
        if (len(fields) >= 8 and fields[2] == "R3" and fields[3] == "POSTED"
                and fields[4] == "FA-17" and fields[5] == "H17-POL-17/A3"):
            matches.append(line)
    assert len(matches) == 1, (ticket, len(matches))
    return matches[0]

# Retain the source-authored binder order. The +304 ticket->PTW association is
# an inference from the independent North/L28 holdout result, not a foreign key.
receipt_lines = SEALS.read_bytes().splitlines()
receipt_rows = [(line, json.loads(line)) for line in receipt_lines if line.strip()]
selected = []
missing = []
for ticket in binder_order:
    ticket_no = int(ticket.split("-")[1])
    permit_no = ticket_no + 304
    permit = f"PTW-{permit_no:03d}"
    rows = [
        (line, row) for line, row in receipt_rows
        if row.get("permit") == permit
        and row.get("state") == "CLOSED"
        and row.get("fitment") == "AS_LEFT"
        and row.get("signed") is True
    ]
    if not rows:
        missing.append((ticket, permit))
        continue
    line, row = max(rows, key=lambda item: item[1].get("revision", 0))
    selected.append({
        "ticket": ticket,
        "ticket_no": ticket_no,
        "permit": permit,
        "permit_no": permit_no,
        "bay": row["bay"],
        "serial": row["serial"],
        "receipt_line": line,
        "supplier_line": posted_a3_line(ticket),
    })

assert missing == [("ST-081", "PTW-385")], missing
assert [x["permit"] for x in selected] == ["PTW-398", "PTW-410", "PTW-403", "PTW-416"]
assert [x["bay"] for x in selected] == ["A", "B", "C", "D"]
assert all(x["serial"].startswith("SG-") for x in selected)

format_text = FORMAT.read_text(encoding="utf-8")
assert "CRC32 of the preceding 20 record bytes, zlib/IEEE variant" in format_text
assert zlib.crc32(b"123456789") == 0xCBF43926

routing = json.loads(ROUTING.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"].lower()
assert len(mask) == 16 and len(target) == 64

serials = [x["serial"] for x in selected]
permits = [x["permit"] for x in selected]
tickets = [x["ticket"] for x in selected]
permit_numbers = [x["permit_no"] for x in selected]
ticket_numbers = [x["ticket_no"] for x in selected]

crc_inputs = {
    "serial_raw_hex": [bytes.fromhex(s.split("-", 1)[1]) for s in serials],
    "serial_ascii_hex": [s.split("-", 1)[1].encode("ascii") for s in serials],
    "serial_full_label": [s.encode("ascii") for s in serials],
    "receipt_jsonl_record": [x["receipt_line"] for x in selected],
    "permit_full_label": [p.encode("ascii") for p in permits],
    "permit_u32_be_input": [n.to_bytes(4, "big") for n in permit_numbers],
    "ticket_full_label": [t.encode("ascii") for t in tickets],
    "ticket_u32_be_input": [n.to_bytes(4, "big") for n in ticket_numbers],
    "supplier_csv_a3_record": [x["supplier_line"] for x in selected],
}

candidates: dict[str, bytes] = {}
for family, inputs in crc_inputs.items():
    for endian in ("big", "little"):
        raw = b"".join((zlib.crc32(item) & 0xFFFFFFFF).to_bytes(4, endian) for item in inputs)
        candidates[f"crc32_{family}_{endian}"] = raw

# Direct four-reference serializations are included as a bounded baseline.
candidates["permit_u32_be"] = b"".join(n.to_bytes(4, "big") for n in permit_numbers)
candidates["permit_u32_le"] = b"".join(n.to_bytes(4, "little") for n in permit_numbers)
candidates["permit_ascii_4digit"] = b"".join(f"{n:04d}".encode("ascii") for n in permit_numbers)

assert all(len(v) == 16 for v in candidates.values())

def xor16(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

direct_hits = [name for name, raw in candidates.items() if hashlib.sha256(raw).hexdigest() == target]
masked_hits = [name for name, raw in candidates.items() if hashlib.sha256(xor16(raw, mask)).hexdigest() == target]
assert not direct_hits and not masked_hits

candidate_set_sha256 = hashlib.sha256(
    "\\n".join(sorted(hashlib.sha256(v).hexdigest() for v in candidates.values())).encode("ascii")
).hexdigest()

print(f"binder_tickets={','.join(binder_order)}")
print(f"inferred_signed_receipt_permits={','.join(permits)}")
print(f"inferred_signed_receipt_bays={','.join(x['bay'] for x in selected)}")
print(f"missing_signed_receipt={missing[0][0]}->{missing[0][1]}")
print(f"candidate_vectors={len(candidates)}")
print(f"direct_component_hits={len(direct_hits)}")
print(f"masked_coupon_hits={len(masked_hits)}")
print(f"candidate_set_sha256={candidate_set_sha256}")
