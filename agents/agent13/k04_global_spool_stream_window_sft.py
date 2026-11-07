"""Read-only K04 search for a global spool byte/nibble-stream slip.

Usage: python k04_global_spool_stream_window_sft.py <archive-root>
The root contains evidence/ and acceptance.json, as in the original ZIP.
No original source, routing, acceptance, verifier, or candidate is modified.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA256 = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
SELECTED_ROW = 129
SELECTED_MARKER = "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"


def xor16(left: bytes, right: bytes) -> bytes:
    assert len(left) == len(right) == 16
    return bytes(a ^ b for a, b in zip(left, right))


def matching_offsets(stream: bytes, mask: bytes, target: str) -> list[int]:
    return [offset for offset in range(len(stream) - 15)
            if hashlib.sha256(xor16(stream[offset:offset + 16], mask)).hexdigest() == target]


def matching_hex_offsets(stream: str, mask: bytes, target: str) -> list[int]:
    hits = []
    for offset in range(len(stream) - 31):
        coupon = bytes.fromhex(stream[offset:offset + 32])
        if hashlib.sha256(xor16(coupon, mask)).hexdigest() == target:
            hits.append(offset)
    return hits


def main(root: Path) -> None:
    evidence = root / "evidence"
    spool_raw = (evidence / "print" / "spool-reconstruction.log").read_bytes()
    route_raw = (evidence / "recovery-routing.json").read_bytes()
    acceptance_raw = (root / "acceptance.json").read_bytes()
    assert hashlib.sha256(spool_raw).hexdigest() == SPOOL_SHA256
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA256
    assert hashlib.sha256(acceptance_raw).hexdigest() == ACCEPT_SHA256

    lines = [line for line in spool_raw.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == 133
    assert SELECTED_MARKER in lines[SELECTED_ROW]
    payloads = []
    for row, line in enumerate(lines):
        if row == SELECTED_ROW:
            continue
        match = re.search(r"(?:^|\\s)PAYLOAD=([0-9A-F]{32})(?=\\s|$)", line)
        assert match is not None, row
        payloads.append(bytes.fromhex(match.group(1)))
    assert len(payloads) == 132 and all(len(payload) == 16 for payload in payloads)

    route = json.loads(route_raw)
    acceptance = json.loads(acceptance_raw)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    raw_stream = b"".join(payloads)
    hex_stream = "".join(payload.hex().upper() for payload in payloads)
    assert len(raw_stream) == 2112 and len(hex_stream) == 4224

    byte_hits = matching_offsets(raw_stream, mask, target)
    hex_hits = matching_hex_offsets(hex_stream, mask, target)
    assert len(raw_stream) - 15 == 2097
    assert len(hex_stream) - 31 == 4193
    assert byte_hits == []
    assert hex_hits == []

    planted_byte_offset = 123
    planted_byte = raw_stream[planted_byte_offset:planted_byte_offset + 16]
    planted_byte_target = hashlib.sha256(xor16(planted_byte, mask)).hexdigest()
    assert matching_offsets(raw_stream, mask, planted_byte_target) == [planted_byte_offset]

    planted_hex_offset = 321
    planted_hex = bytes.fromhex(hex_stream[planted_hex_offset:planted_hex_offset + 32])
    planted_hex_target = hashlib.sha256(xor16(planted_hex, mask)).hexdigest()
    assert matching_hex_offsets(hex_stream, mask, planted_hex_target) == [planted_hex_offset]

    print("SOURCE_PINS spool=PASS route=PASS acceptance=PASS")
    print("SELECTED_ROW_EXCLUDED", SELECTED_ROW, SELECTED_MARKER)
    print("INTACT_PACKETS", len(payloads))
    print("BYTE_STREAM_WINDOWS", len(raw_stream) - 15, "ORIGINAL_K04_HITS", len(byte_hits))
    print("HEX_NIBBLE_WINDOWS", len(hex_stream) - 31, "ORIGINAL_K04_HITS", len(hex_hits))
    print("PLANTED_FULL_TARGET_CONTROLS byte=PASS@123 hex_nibble=PASS@321")
    print("TOTAL_ORIGINAL_FULL_K04_COMPARISONS", (len(raw_stream) - 15) + (len(hex_stream) - 31))
    print("K04_RECOVERED", False)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
