"""H17 K04: source-wide alternate mask object extraction with fixed copied ACK.

The prior all-file audit fixed the published mask and varied a coupon carrier.
This test holds the selected copied ACK fixed and varies a raw/hex mask carrier.
These two reduced-component image sets are compared for true novelty.
Run: python agents/agent41/k04_original_mask_carriers_sft.py [original-export.zip]
Original sources are read only. No recovery claim is implied by a negative.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ORIGINAL_ZIP_SHA256 = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
P = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
M = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")

def source_members():
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ORIGINAL_ZIP_SHA256
        with zipfile.ZipFile(path) as archive:
            out = {name: archive.read(name) for name in archive.namelist()
                   if not name.endswith("/")}
    else:
        root = REPO / "resources"
        out = {str(path.relative_to(root)).replace("\\", "/"): path.read_bytes()
               for path in root.rglob("*") if path.is_file()
               and str(path.relative_to(root)).replace("\\", "/")
               not in ("candidate.json", "work/recover_six.py")}
    assert len(out) == 46, len(out)
    assert hashlib.sha256(out["evidence/print/spool-reconstruction.log"]).hexdigest() == SPOOL_SHA256
    assert P.hex().upper().encode() in out["evidence/print/spool-reconstruction.log"]
    return out

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

members = source_members()
locations = {}
raw_assignments = hex_assignments = 0
for name in sorted(members):
    data = members[name]
    for offset in range(len(data) - 15):
        value = data[offset:offset + 16]
        raw_assignments += 1
        locations.setdefault(value, (name, "raw", offset))
    for match in re.finditer(rb"[A-Fa-f0-9]{32,}", data):
        text = match.group()
        for offset in range(len(text) - 31):
            value = bytes.fromhex(text[offset:offset + 32].decode("ascii"))
            hex_assignments += 1
            locations.setdefault(value, (name, "hex", match.start() + offset))

baseline = {xor(value, M) for value in locations}
alternate = {xor(P, value) for value in locations}
overlap = baseline & alternate
hits = [dict(component=component.hex().upper(),
             mask=xor(P, component).hex().upper(),
             origin=locations[xor(P, component)])
        for component in alternate if hashlib.sha256(component).digest() == TARGET]
synthetic_mask = next(value for value, loc in locations.items()
                      if loc[0] == "evidence/maintenance/inspection-rounds.log")
synthetic_digest = hashlib.sha256(xor(P, synthetic_mask)).digest()
planted_hits = sum(hashlib.sha256(xor(P, value)).digest() == synthetic_digest
                   for value in locations)

assert raw_assignments == 117583, raw_assignments
assert hex_assignments == 892, hex_assignments
assert len(locations) == len(alternate) == len(baseline) == 67470
assert len(overlap) == 2
assert not hits and planted_hits == 1
print(json.dumps({
    "original_members": len(members), "raw16_assignments": raw_assignments,
    "ascii_hex32_assignments": hex_assignments,
    "distinct_candidate_masks": len(locations),
    "prior_fixed_mask_source_carrier_components": len(baseline),
    "alternative_mask_complete_components": len(alternate),
    "old_new_component_overlap": len(overlap),
    "new_reduced_components": len(alternate - overlap),
    "original_k04_matches": hits,
    "planted_control_hits": planted_hits,
}, sort_keys=True))
