#!/usr/bin/env python3
"""Source-pinned PTW-417 seal-label digest hypotheses for K04.

The work order explicitly links PTW-417 seal-rack labels to printer job
PS-261003-0417. This SFT tests a bounded family of text serializations of the
four selected signed as-left serials as possible 16-byte K04 coupons/components.
It does not assert that the printer historically used a digest.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
from pathlib import Path

SOURCE_ROOT = (
    Path(os.environ["H17_SOURCE_ROOT"])
    if "H17_SOURCE_ROOT" in os.environ
    else Path(__file__).resolve().parents[2]
)
if (SOURCE_ROOT / "evidence").is_dir():
    EVIDENCE = SOURCE_ROOT / "evidence"
    ACCEPTANCE = SOURCE_ROOT / "acceptance.json"
else:
    EVIDENCE = SOURCE_ROOT / "resources" / "evidence"
    ACCEPTANCE = SOURCE_ROOT / "resources" / "acceptance.json"

WORK_ORDER = EVIDENCE / "maintenance" / "work-order-417.html"
SEAL_RECEIPTS = EVIDENCE / "maintenance" / "seal-receipts.jsonl"
CLOSEOUT_EMAIL = EVIDENCE / "mail" / "04.eml"
SPOOL = EVIDENCE / "print" / "spool-reconstruction.log"
PRINT_FLEET = EVIDENCE / "h17-supplemental-office-files" / "print-fleet-retirement-note.txt"
ROUTING = EVIDENCE / "recovery-routing.json"

EXPECTED_SHA256 = {
    WORK_ORDER.name: "158399fb294a647fc0ba7037af5f9fea9ba980c9034298770c209d13ea0cc88f",
    SEAL_RECEIPTS.name: "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    CLOSEOUT_EMAIL.name: "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
    SPOOL.name: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    PRINT_FLEET.name: "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    ROUTING.name: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE.name: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path in (WORK_ORDER, SEAL_RECEIPTS, CLOSEOUT_EMAIL, SPOOL, PRINT_FLEET, ROUTING, ACCEPTANCE):
    actual = sha256_file(path)
    assert actual == EXPECTED_SHA256[path.name], (path, actual)

work_order = WORK_ORDER.read_text(encoding="utf-8")
print_fleet = PRINT_FLEET.read_text(encoding="utf-8")
spool_text = SPOOL.read_text(encoding="utf-8")
closeout = CLOSEOUT_EMAIL.read_text(encoding="utf-8")
assert "PTW-417" in work_order
assert "PS-261003-0417" in print_fleet and "ESC-N" in print_fleet and "FA-17" in print_fleet
assert "PS-261003-0417" in spool_text
bay_match = re.search(r"The witness walk\s+was ([A-D](?:, [A-D]){3})\.", closeout)
assert bay_match is not None
bay_order = [part.strip() for part in bay_match.group(1).split(",")]
assert bay_order == ["B", "D", "A", "C"]

receipt_rows = [
    json.loads(line)
    for line in SEAL_RECEIPTS.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
selected = {}
for bay in bay_order:
    rows = [
        row for row in receipt_rows
        if row["permit"] == "PTW-417"
        and row["bay"] == bay
        and row["state"] == "CLOSED"
        and row["fitment"] == "AS_LEFT"
        and row["signed"] is True
    ]
    assert rows
    selected[bay] = max(rows, key=lambda row: row["revision"])

serials = [selected[bay]["serial"] for bay in bay_order]
canonical_k03_text = "|".join(serials).encode("ascii")
k03_component = hashlib.sha256(canonical_k03_text).digest()[:16]

routing = json.loads(ROUTING.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
k04_target = acceptance["slot_sha256"]["K04"]
k03_target = acceptance["slot_sha256"]["K03"]
assert hashlib.sha256(k03_component).hexdigest() == k03_target
assert len(mask) == 16 and len(k04_target) == 64

separators = ("", "|", ",", ";", " ", "\n")
metadata = ("", "PTW-417", "PS-261003-0417", "PTW-417|PS-261003-0417")


def digest16_variants(data: bytes) -> dict[str, bytes]:
    sha1 = hashlib.sha1(data).digest()
    sha256 = hashlib.sha256(data).digest()
    sha512 = hashlib.sha512(data).digest()
    sha3 = hashlib.sha3_256(data).digest()
    return {
        "md5": hashlib.md5(data).digest(),
        "sha1-first": sha1[:16],
        "sha1-last": sha1[-16:],
        "sha256-first": sha256[:16],
        "sha256-last": sha256[-16:],
        "sha512-first": sha512[:16],
        "sha512-last": sha512[-16:],
        "blake2s16": hashlib.blake2s(data, digest_size=16).digest(),
        "blake2b16": hashlib.blake2b(data, digest_size=16).digest(),
        "shake256-16": hashlib.shake_256(data).digest(16),
        "sha3-256-first": sha3[:16],
        "sha3-256-last": sha3[-16:],
    }


candidates: set[bytes] = set()
input_count = 0
candidate_assignments = 0
for order in itertools.permutations(serials):
    for separator in separators:
        for include_prefix in (False, True):
            for lowercase in (False, True):
                parts = []
                for serial in order:
                    value = serial if include_prefix else serial.split("-", 1)[1]
                    parts.append(value.lower() if lowercase else value.upper())
                body = separator.join(parts)
                for meta in metadata:
                    for placement in ("prefix", "suffix"):
                        if not meta:
                            text_value = body
                        elif placement == "prefix":
                            text_value = meta + separator + body
                        else:
                            text_value = body + separator + meta
                        input_count += 1
                        for digest in digest16_variants(text_value.encode("ascii")).values():
                            candidate_assignments += 1
                            candidates.add(digest)

masked_hits = [
    candidate.hex().upper()
    for candidate in candidates
    if hashlib.sha256(bytes(a ^ b for a, b in zip(candidate, mask))).hexdigest() == k04_target
]
direct_component_hits = [
    candidate.hex().upper()
    for candidate in candidates
    if hashlib.sha256(candidate).hexdigest() == k04_target
]

# Independently planted complete positives validate both acceptance paths.
planted = min(candidates)
planted_masked_component = bytes(a ^ b for a, b in zip(planted, mask))
planted_masked_target = hashlib.sha256(planted_masked_component).hexdigest()
planted_masked_hits = [
    candidate for candidate in candidates
    if hashlib.sha256(bytes(a ^ b for a, b in zip(candidate, mask))).hexdigest()
    == planted_masked_target
]
planted_direct_target = hashlib.sha256(planted).hexdigest()
planted_direct_hits = [
    candidate for candidate in candidates
    if hashlib.sha256(candidate).hexdigest() == planted_direct_target
]
assert planted_masked_hits == [planted]
assert planted_direct_hits == [planted]
assert masked_hits == []
assert direct_component_hits == []

candidate_set_sha256 = hashlib.sha256(
    b"\n".join(candidate.hex().upper().encode("ascii") for candidate in sorted(candidates))
).hexdigest()

print(f"selected_bay_order={','.join(bay_order)}")
print(f"selected_serials={'|'.join(serials)}")
print(f"canonical_k03_component={k03_component.hex().upper()}")
print(f"serial_text_inputs={input_count}")
print(f"digest_assignments={candidate_assignments}")
print(f"unique_16_byte_candidates={len(candidates)}")
print(f"original_k04_masked_coupon_hits={len(masked_hits)}")
print(f"original_k04_direct_component_hits={len(direct_component_hits)}")
print(f"planted_masked_coupon_positive_hits={len(planted_masked_hits)}")
print(f"planted_direct_component_positive_hits={len(planted_direct_hits)}")
print(f"candidate_set_sha256={candidate_set_sha256}")
