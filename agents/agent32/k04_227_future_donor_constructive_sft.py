"""Synthetic MT inverse-twist 227-pair target recovery with original boundary checks.

Run: python agents/agent32/k04_227_future_donor_constructive_sft.py resources

Reconstructs four hidden synthetic 32-bit MT outputs exactly from two
227-separated five-word source runs. The original selected printer row129
is never interpreted; the real future donor words have not been recovered.
"""
import hashlib
import random
import re
import sys
from pathlib import Path

MAG = 0x9908B0DF
MASK = 0xFFFFFFFF
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def untemper(x):
    for shift, left, filt in ((18, False, MASK), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, MASK)):
        y = x
        for _ in range(6):
            y = x ^ (((y << shift) & filt) if left else (y >> shift))
        x = y & MASK
    return x


def twist(mixed):
    return ((mixed >> 1) ^ (MAG if mixed & 1 else 0)) & MASK


def inverse_twist(value):
    parity = value >> 31
    return ((((value ^ (MAG if parity else 0)) << 1) | parity) & MASK)


def reconstruct_pair_donors(future_397, future_624):
    assert len(future_397) == len(future_624) == 5
    mixed = [inverse_twist(a ^ b) for a, b in zip(future_397, future_624)]
    recovered = [((mixed[j - 1] & 0x7FFFFFFF) | (mixed[j] & 0x80000000))
                 for j in range(1, 5)]
    return mixed, recovered


def synthetic_control(seed):
    rng = random.Random(seed)
    states = [untemper(rng.getrandbits(32)) for _ in range(1600)]
    for index in (0, 200, 624, 951):
        mixed = (states[index] & 0x80000000) | (states[index + 1] & 0x7FFFFFFF)
        assert states[index + 624] == states[index + 397] ^ twist(mixed)
        assert inverse_twist(twist(mixed)) == mixed
    first = [states[t + 397] for t in range(950, 955)]
    second = [states[t + 624] for t in range(950, 955)]
    mixed, recovered = reconstruct_pair_donors(first, second)
    assert mixed[0] & 0x80000000 == states[950] & 0x80000000
    assert mixed[4] & 0x7FFFFFFF == states[955] & 0x7FFFFFFF
    assert recovered == states[951:955]


def main(root):
    for seed in (0, 1, 417, 20261003, 20261102, 0xF123456789ABC):
        synthetic_control(seed)
    print("PASS six synthetic CPython MT streams; 4 withheld 32-bit words recovered")

    source = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SPOOL_SHA
    lines = [line for line in source.splitlines() if b"PAYLOAD=" in line]
    assert len(lines) == 133
    row128 = bytes.fromhex(re.search(rb"PAYLOAD=([0-9A-F]{32})", lines[128]).group(1).decode())
    row130 = bytes.fromhex(re.search(rb"PAYLOAD=([0-9A-F]{32})", lines[130]).group(1).decode())
    x950 = untemper(int.from_bytes(row128[12:16], "little"))
    x955 = untemper(int.from_bytes(row130[0:4], "little"))
    assert (x950, x955) == (0xB1E734D0, 0x852D0B6A)
    print("Original p951 boundary states: X950=", f"{x950:08X}",
          "X955=", f"{x955:08X}")
    print("A valid donor pair must match X950 MSB and X955 low31.")
    print("Prospective donor runs: 1347..1351 and 1574..1578 (227 apart)")
    print("No original future donor values or selected coupon recovered.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
