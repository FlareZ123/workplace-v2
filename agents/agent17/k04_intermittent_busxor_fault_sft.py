"""H-17 K04 intermittent uniform copier-byte XOR fault, source-pinned SFT.

For every nonzero 8-bit error and every nonempty subset of the sixteen
selected copied bytes, mutate each affected byte by that same XOR error.
Compare the full original SHA256 K04 commitment. Synthetic control checks
that the complete candidate family has been evaluated correctly.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
SELECTED = "A9A9DC5731A5E2AE879C47215C2559D5"
MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
PLANTED_DELTA = 0x93
PLANTED_POSITIONS = 0x4A35


def main() -> None:
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    route_bytes = (ROOT / "evidence/recovery-routing.json").read_bytes()
    acceptance_bytes = (ROOT / "acceptance.json").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(route_bytes).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(acceptance_bytes).hexdigest() == ACCEPT_SHA
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    assert route["K04"]["masked_component"] == MASK
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    matches = re.findall(
        r"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32})",
        spool.decode("utf-8"),
    )
    assert matches == [SELECTED]
    copied = bytes.fromhex(matches[0])
    baseline = bytes(a ^ b for a, b in zip(copied, bytes.fromhex(MASK)))
    target = bytes.fromhex(K04_SHA)
    assert hashlib.sha256(baseline).digest() != target

    planted = bytearray(baseline)
    for byte in range(16):
        if (PLANTED_POSITIONS >> byte) & 1:
            planted[byte] ^= PLANTED_DELTA
    planted_commitment = hashlib.sha256(planted).digest()

    checks = 0
    synthetic_hits = 0
    actual_hits: list[dict[str, object]] = []
    for delta in range(1, 256):
        state = bytearray(baseline)
        previous = 0
        for index in range(1, 1 << 16):
            positions = index ^ (index >> 1)
            flipped = positions ^ previous
            state[flipped.bit_length() - 1] ^= delta
            previous = positions
            digest = hashlib.sha256(state).digest()
            checks += 1
            if digest == target:
                actual_hits.append({
                    "delta": delta,
                    "positions": f"{positions:04X}",
                    "K04": state.hex().upper(),
                })
            if digest == planted_commitment:
                assert (delta, positions) == (PLANTED_DELTA, PLANTED_POSITIONS)
                synthetic_hits += 1
    assert checks == 255 * ((1 << 16) - 1)
    assert synthetic_hits == 1
    print(json.dumps({
        "complete_original_checks": checks,
        "synthetic_control": synthetic_hits,
        "original_K04_matches": actual_hits,
    }, indent=2))


if __name__ == "__main__":
    main()
