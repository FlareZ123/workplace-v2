#!/usr/bin/env python3
"""Bounded K04 candidate test: digest the source-indexed North L-29/N ticket set.

Reads original evidence only. No canonical candidate, verifier, acceptance or
routing file is modified. Run from any directory with Python 3.11+:
    python agents/agent3/k04_north_ticket_row_digest_sft.py
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLEET = ROOT / "resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
CSV_PATH = ROOT / "resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
ROUTE = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"

PINS = {
    FLEET: "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    CSV_PATH: "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    ROUTE: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
for path, expected in PINS.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, (path, actual, expected)

import json

fleet = FLEET.read_text(encoding="utf-8")
csv_text = CSV_PATH.read_text(encoding="utf-8")
routing = json.loads(ROUTE.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
assert len(mask) == 16 and len(target) == 32

# The fleet note supplies the five-ticket binder order and the selected ESC-N
# / L-29/N / FA-17 / H17-POL-17/A3 association.
binder_ids = re.findall(r"^L-29/N\s+\d+\s+(ST-\d+)\s+", fleet, re.M)
assert binder_ids == ["ST-094", "ST-081", "ST-106", "ST-099", "ST-112"]
assert re.search(
    r"^PS-261003-0417\s+ESC-N\s+L-29/N\s+FA-17\s+H17-POL-17/A3$",
    fleet, re.M
)

# Preserve each exact CSV row line while selecting only the five R3/POSTED
# entries for the North account/folio. This excludes the R2/VOID ST-099 row
# and the R4/HELD duplicate ST-112 row.
data_lines = [line for line in csv_text.splitlines() if not line.startswith("#")]
reader = csv.DictReader(data_lines)
selected = []
for row in reader:
    raw_line = data_lines[reader.line_num - 1]
    if (
        row["line_ref"] in binder_ids
        and row["run"] == "R3"
        and row["posting"] == "POSTED"
        and row["account"] == "FA-17"
        and row["folio_or_jacket"] == "H17-POL-17/A3"
    ):
        selected.append((row["line_ref"], raw_line))
assert len(selected) == 5
by_id = dict(selected)
assert set(by_id) == set(binder_ids)
csv_order = [ticket for ticket, _ in selected]
assert csv_order == ["ST-094", "ST-106", "ST-112", "ST-081", "ST-099"]

orders = {
    "binder": binder_ids,
    "csv": csv_order,
}
header = next(line for line in data_lines if line.startswith("line_ref,"))
hashers = {
    "MD5": lambda b: hashlib.md5(b).digest(),
    "SHA256-first16": lambda b: hashlib.sha256(b).digest()[:16],
    "SHA512-first16": lambda b: hashlib.sha512(b).digest()[:16],
    "BLAKE2s-16": lambda b: hashlib.blake2s(b, digest_size=16).digest(),
    "BLAKE2b-16": lambda b: hashlib.blake2b(b, digest_size=16).digest(),
    "SHA3-256-first16": lambda b: hashlib.sha3_256(b).digest()[:16],
}

candidates: list[tuple[str, bytes]] = []
for order_name, ids in orders.items():
    row_lines = [by_id[ticket] for ticket in ids]
    forms = {
        "rows-LF": "\n".join(row_lines).encode("utf-8"),
        "rows-LF-final": ("\n".join(row_lines) + "\n").encode("utf-8"),
        "header-rows-LF": ("\n".join([header] + row_lines)).encode("utf-8"),
        "header-rows-LF-final": ("\n".join([header] + row_lines) + "\n").encode("utf-8"),
    }
    for form_name, body in forms.items():
        for hash_name, hasher in hashers.items():
            digest = hasher(body)
            candidates.append((f"{order_name}/{form_name}/{hash_name}/component", digest))
            candidates.append((
                f"{order_name}/{form_name}/{hash_name}/payload",
                bytes(a ^ b for a, b in zip(digest, mask)),
            ))

assert len(candidates) == 96
values = [value for _, value in candidates]
assert len(set(values)) == 96

# Exercise the identical complete-candidate SHA256 comparison with one
# independently planted in-family candidate; it must be found exactly once.
synthetic_target = hashlib.sha256(values[0]).digest()
synthetic_hits = sum(hashlib.sha256(value).digest() == synthetic_target for value in values)
assert synthetic_hits == 1

hits = [
    label for label, value in candidates
    if hashlib.sha256(value).digest() == target
]
print(f"binder_order={','.join(binder_ids)}")
print(f"csv_order={','.join(csv_order)}")
print(f"distinct_complete_candidates={len(candidates)}")
print(f"original_K04_hits={len(hits)}")
print(f"synthetic_positive_hits={synthetic_hits}")
print("RESULT=NO_MATCH" if not hits else "RESULT=MATCH")
assert not hits
