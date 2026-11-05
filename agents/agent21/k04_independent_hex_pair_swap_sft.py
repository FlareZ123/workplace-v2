"""Original-source K04 test: independent disjoint hex-pair swap flags at three stages.

Python 3, optional argument is path to evidence directory. Read-only.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources/evidence"
SRC = ROOT / "print/spool-reconstruction.log"
SRC_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")


def run() -> None:
    src = SRC.read_bytes()
    assert hashlib.sha256(src).hexdigest() == SRC_SHA
    lines = [line for line in src.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == 133
    selected = [line for line in lines if line.startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"
    )]
    assert len(selected) == 1
    payload = re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1)
    assert payload == "A9A9DC5731A5E2AE879C47215C2559D5"
    mask = MASK.hex().upper()
    baseline_component = "".join(
        f"{a ^ b:02X}" for a, b in zip(bytes.fromhex(payload), MASK)
    )

    # Independently plant a known complete 128-bit coupon using the stage0,
    # nontrivial, disjoint within-byte nibble-swap flags 0xD35F.
    planted_flags = 0xD35F
    original_chars = list(payload)
    for i in range(16):
        if planted_flags & (1 << i):
            original_chars[2 * i], original_chars[2 * i + 1] = (
                original_chars[2 * i + 1], original_chars[2 * i]
            )
    planted_coupon = bytes(
        a ^ b for a, b in zip(bytes.fromhex("".join(original_chars)), MASK)
    )
    planted_target = hashlib.sha256(planted_coupon).digest()

    checks = original = planted = 0
    for stage in range(3):
        inp = payload if stage == 0 else mask if stage == 1 else baseline_component
        for phase in (0, 1):
            for flags in range(1 << 16):
                chars = list(inp)
                for i in range(16):
                    if flags & (1 << i):
                        a = (2 * i + phase) % 32
                        b = (a + 1) % 32
                        chars[a], chars[b] = chars[b], chars[a]
                changed = "".join(chars)
                if stage == 0:
                    component = bytes(
                        a ^ b for a, b in zip(bytes.fromhex(changed), MASK)
                    )
                elif stage == 1:
                    component = bytes(
                        a ^ b for a, b in zip(bytes.fromhex(changed), bytes.fromhex(payload))
                    )
                else:
                    component = bytes.fromhex(changed)
                digest = hashlib.sha256(component).digest()
                checks += 1
                if digest == TARGET:
                    original += 1
                    print("ORIGINAL_K04_HIT", stage, phase, flags, component.hex(), flush=True)
                if digest == planted_target:
                    planted += 1
                    if stage == 0 and phase == 0 and flags == planted_flags:
                        assert component == planted_coupon

    assert checks == 3 * 2 * 65536
    assert planted == 1
    print(f"K04_DISJOINT_HEX_PAIR_SWAPS original={original} checks={checks} planted_hits={planted}")


if __name__ == "__main__":
    run()
