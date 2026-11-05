"""Read-only H-17 original-source complete-coupon byte-affine hypothesis.

Whole-byte modular and GF(256) maps, all coefficients, three copier stages.
All original files read only; known six accepted values unaffected.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
PINS = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def gf256_mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        overflow = a & 0x80
        a = (a << 1) & 0xFF
        if overflow:
            a ^= 0x1B
        b >>= 1
    return result

def main() -> None:
    for path, digest in PINS.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_text()
    rows = [
        line for line in spool.splitlines()
        if all(field in line for field in (
            "2026-10-03T18:02:00Z ", "JOB=PS-261003-0417 ",
            "ATTEMPT=2 ", "STATE=ACK ", "CLASS=RECOVER "
        ))
    ]
    assert len(rows) == 1
    payload = bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", rows[0]).group(1))
    assert payload.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
    mask = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
    expected = bytes.fromhex(json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"])
    assert len(payload) == len(mask) == 16

    def xor(a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

    planted = xor(bytes((5 * x + 131) & 255 for x in payload), mask)
    planted_digest = hashlib.sha256(planted).digest()
    counts = {"original": 0, "planted": 0, "checked": 0}
    direct_component = xor(payload, mask)
    for family in ("mod256", "gf256"):
        for a in range(256):
            table = bytes(((a * x) & 255 if family == "mod256" else gf256_mul(a, x)) for x in range(256))
            for b in range(256):
                def map_bytes(data: bytes) -> bytes:
                    return bytes(((table[x] + b) & 255 if family == "mod256" else table[x] ^ b) for x in data)

                possibilities = (
                    xor(map_bytes(payload), mask),
                    map_bytes(direct_component),
                    xor(payload, map_bytes(mask)),
                )
                for stage, component in enumerate(possibilities):
                    h = hashlib.sha256(component).digest()
                    counts["checked"] += 1
                    if h == expected:
                        counts["original"] += 1
                        print("ORIGINAL_MATCH", family, a, b, stage, component.hex().upper())
                    if h == planted_digest:
                        counts["planted"] += 1
                        print("PLANTED_MATCH", family, a, b, stage)
    assert counts["checked"] == 393216
    assert counts["planted"] >= 1
    assert counts["original"] == 0
    print(json.dumps(counts, sort_keys=True))

if __name__ == "__main__":
    main()
