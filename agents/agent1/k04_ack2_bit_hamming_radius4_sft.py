#!/usr/bin/env python3
"""Bounded Hamming-radius screen around the selected PS-0417 ACK2 K04 candidate.

The route specifies component = selected RECOVER ACK payload XOR K04 mask.
MAIL-16 warns that the retained printer payload has no independent checksum.
This tests whether a small number (one through four) of bit errors in that
selected 16-byte payload could explain the K04 component commitment.

Run from the repository root:
    python agents/agent1/k04_ack2_bit_hamming_radius4_sft.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTING_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
JOB = "PS-261003-0417"
MAX_BITS = 4


def selected_ack_payload(resources: Path) -> bytes:
    raw = (resources / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    matches = []
    for line in raw.decode("ascii").splitlines():
        if f"JOB={JOB}" not in line:
            continue
        fields = dict(re.findall(r"(\w+)=([^\s]+)", line))
        if (fields.get("ATTEMPT") == "2" and fields.get("STATE") == "ACK"
                and fields.get("CLASS") == "RECOVER"):
            matches.append(bytes.fromhex(fields["PAYLOAD"]))
    assert len(matches) == 1, len(matches)
    assert len(matches[0]) == 16
    return matches[0]


def main() -> None:
    resources = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "resources"
    routing_path = resources / "evidence" / "recovery-routing.json"
    acceptance_path = resources / "acceptance.json"
    routing_raw = routing_path.read_bytes()
    acceptance_raw = acceptance_path.read_bytes()
    assert hashlib.sha256(routing_raw).hexdigest() == ROUTING_SHA
    assert hashlib.sha256(acceptance_raw).hexdigest() == ACCEPTANCE_SHA

    routing = json.loads(routing_raw)
    acceptance = json.loads(acceptance_raw)
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    payload = selected_ack_payload(resources)
    base = bytes(a ^ b for a, b in zip(payload, mask))
    assert len(mask) == len(payload) == len(base) == 16

    print("SOURCE_JOB", JOB, "attempt=2 state=ACK class=RECOVER")
    print("SELECTED_PAYLOAD", payload.hex().upper())
    print("MASK", mask.hex().upper())
    print("DIRECT_COMPONENT", base.hex().upper())
    print("TARGET_SHA256", target.hex())
    direct_hit = hashlib.sha256(base).digest() == target
    print("DIRECT_MATCH", int(direct_hit))
    assert not direct_hit

    # Flipping bits before or after XOR with a fixed mask is equivalent.
    base_int = int.from_bytes(base, "little")
    tested = 0
    start = time.monotonic()
    hits = []
    for radius in range(1, MAX_BITS + 1):
        radius_count = 0
        for positions in itertools.combinations(range(128), radius):
            candidate_int = base_int
            for bit in positions:
                candidate_int ^= 1 << bit
            candidate = candidate_int.to_bytes(16, "little")
            tested += 1
            radius_count += 1
            if hashlib.sha256(candidate).digest() == target:
                hits.append((radius, positions, candidate.hex().upper()))
        print("RADIUS", radius, "TESTED", radius_count,
              "ELAPSED_SECONDS", round(time.monotonic() - start, 2),
              "HITS", len(hits), flush=True)

    assert tested == 11_017_632, tested
    assert not hits, hits
    print("TOTAL_TESTED", tested)
    print("TOTAL_ELAPSED_SECONDS", round(time.monotonic() - start, 2))
    print("NO_MATCH_WITHIN_HAMMING_RADIUS", MAX_BITS)
    print("K04_BITS_RECOVERED 0; K08_WORDS_RECOVERED 0")


if __name__ == "__main__":
    main()
