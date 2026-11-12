#!/usr/bin/env python3
"""Bounded K04 source-copy corruption test (one/two arbitrary byte edits).

This tests whether the selected retained-fragment ACK2 payload can be turned
into the accepted physical coupon by changing at most two of its 16 bytes.
The repeated A9A9 prefix is recorded as an anomaly, not assumed to be a marker.
The selected ACK payload is an unverified copy and is used only as a candidate
base; no historical integrity claim is made.

Standard library only. Read-only against original resources.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCE_ROOT = ROOT / "resources" if (ROOT / "resources").is_dir() else ROOT
SPOOL_PATH = RESOURCE_ROOT / "evidence/print/spool-reconstruction.log"
ROUTE_PATH = RESOURCE_ROOT / "evidence/recovery-routing.json"
ACCEPT_PATH = RESOURCE_ROOT / "acceptance.json"

EXPECTED_SHA = {
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xor_bytes(a: bytes, b: bytes) -> bytes:
    assert len(a) == len(b) == 16
    return bytes(x ^ y for x, y in zip(a, b))


def load_source():
    spool = SPOOL_PATH.read_bytes()
    route_raw = ROUTE_PATH.read_bytes()
    acceptance_raw = ACCEPT_PATH.read_bytes()
    assert sha256(spool) == EXPECTED_SHA["spool"]
    assert sha256(route_raw) == EXPECTED_SHA["routing"]
    assert sha256(acceptance_raw) == EXPECTED_SHA["acceptance"]

    route = json.loads(route_raw)
    acceptance = json.loads(acceptance_raw)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    assert len(mask) == 16 and len(target) == 64

    selected = []
    payloads = []
    for line in spool.splitlines():
        match = re.search(rb"PAYLOAD=([0-9A-F]{32})", line)
        if match:
            payloads.append(bytes.fromhex(match.group(1).decode("ascii")))
        if b"JOB=PS-261003-0417 " in line and b"ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line:
            selected.append(line)
    assert len(payloads) == 133
    assert len(selected) == 1
    selected_match = re.search(rb"PAYLOAD=([0-9A-F]{32})", selected[0])
    assert selected_match
    copied = bytes.fromhex(selected_match.group(1).decode("ascii"))
    assert copied.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    return copied, payloads, mask, target


def accepted(payload: bytes, mask: bytes, target: str) -> bool:
    return sha256(xor_bytes(payload, mask)) == target


def run_original(copied: bytes, payloads: list[bytes], mask: bytes, target: str):
    repeated = bytes.fromhex("A9A9")
    prefix_count = sum(p.startswith(repeated) for p in payloads)
    any_adjacent_count = sum(any(p[i:i + 2] == repeated for i in range(15)) for p in payloads)
    assert prefix_count == 1 and any_adjacent_count == 1

    prefix_hits = []
    for value in range(1 << 16):
        candidate = value.to_bytes(2, "big") + copied[2:]
        if accepted(candidate, mask, target):
            prefix_hits.append(candidate)
    assert not prefix_hits

    # Each pair contributes 2^16 assignments; overlaps occur when one edited
    # byte is restored to its copied value, so report assignments, not uniques.
    hits = []
    assignments = 0
    work = bytearray(copied)
    for i, j in itertools.combinations(range(16), 2):
        original_i, original_j = work[i], work[j]
        for a in range(256):
            work[i] = a
            for b in range(256):
                work[j] = b
                if accepted(bytes(work), mask, target):
                    hits.append((i, j, a, b, bytes(work)))
        work[i], work[j] = original_i, original_j
        assignments += 1 << 16
    assert assignments == 7_864_320
    assert not hits
    return {
        "payload_count": len(payloads),
        "unique_A9A9_prefixes": prefix_count,
        "unique_A9A9_adjacent_occurrences": any_adjacent_count,
        "prefix_replacements_checked": 65_536,
        "prefix_hits": len(prefix_hits),
        "two_byte_position_assignments": assignments,
        "two_byte_hits": len(hits),
        "conclusion": "No accepted physical coupon is at Hamming distance 0, 1, or 2 from the retained ACK2 payload.",
    }


def synthetic_positive(mask: bytes):
    # A planted two-byte repair must be found uniquely by the same acceptance path.
    base = bytearray.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    base[3], base[14] = 0x12, 0x34
    planted = bytes(base)
    planted_target = sha256(xor_bytes(planted, mask))
    hits = []
    original = bytearray.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    for a in range(256):
        original[3] = a
        for b in range(256):
            original[14] = b
            candidate = bytes(original)
            if sha256(xor_bytes(candidate, mask)) == planted_target:
                hits.append((a, b, candidate))
    assert hits == [(0x12, 0x34, planted)]
    return {"positions": [3, 14], "planted_bytes": "1234", "unique_hits": 1}


def main():
    copied, payloads, mask, target = load_source()
    result = run_original(copied, payloads, mask, target)
    result["synthetic_positive"] = synthetic_positive(mask)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
