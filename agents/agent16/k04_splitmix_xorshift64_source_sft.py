"""Blind H-17 source-origin pilot: SplitMix64 and xorshift64* exact output models.

Run from the repository: python agents/agent16/k04_splitmix_xorshift64_source_sft.py
Original selected 0417 RECOVER ACK attempt 2, routing mask and commitments are excluded.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import re

MASK = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
A = 0xBF58476D1CE4E5B9
B = 0x94D049BB133111EB
C = 2685821657736338717
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def reverse_xor_right(x, n):
    while n < 64:
        x ^= x >> n
        n *= 2
    return x & MASK


def reverse_xor_left(x, n):
    while n < 64:
        x ^= (x << n) & MASK
        n *= 2
    return x & MASK


def splitmix_unmix(x):
    x = reverse_xor_right(x, 31)
    x = x * pow(B, -1, 1 << 64) & MASK
    x = reverse_xor_right(x, 27)
    x = x * pow(A, -1, 1 << 64) & MASK
    return reverse_xor_right(x, 30)


def splitmix_mix(x):
    x ^= x >> 30
    x = x * A & MASK
    x ^= x >> 27
    x = x * B & MASK
    return (x ^ (x >> 31)) & MASK


def xorshift_step(x):
    x ^= x >> 12
    x ^= (x << 25) & MASK
    x ^= x >> 27
    return x & MASK


def xorshift_unmix(x):
    return x * pow(C, -1, 1 << 64) & MASK


def main():
    source = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    payloads = []
    for line in raw.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        if ("JOB=PS-261003-0417 " in line and
                "STATE=ACK CLASS=RECOVER" in line):
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        if match:
            payloads.append(bytes.fromhex(match.group(1)))
    assert len(payloads) == 132
    assert splitmix_unmix(splitmix_mix(0x123456789ABCDEF0)) == 0x123456789ABCDEF0
    for x in (1, 0x123456789ABCDEF0, MASK):
        assert reverse_xor_right(x ^ (x >> 31), 31) == x
        assert reverse_xor_left(x ^ ((x << 25) & MASK), 25) == x
        assert xorshift_unmix(xorshift_step(x) * C & MASK) == xorshift_step(x)
    for name, unmix, step in (
        ("SplitMix64", splitmix_unmix, lambda x: (x + GAMMA) & MASK),
        ("xorshift64*", xorshift_unmix, xorshift_step),
    ):
        for byteorder in ("big", "little"):
            pairs = [
                (int.from_bytes(b[:8], byteorder), int.from_bytes(b[8:], byteorder))
                for b in payloads
            ]
            states = [(unmix(a), unmix(b)) for a, b in pairs]
            direct = sum(step(a) == b for a, b in states)
            observed = defaultdict(list)
            for index, (a, b) in enumerate(states):
                observed[a].append((index, 0))
                observed[b].append((index, 1))
            matches = set()
            for index, (a, b) in enumerate(states):
                for half, original in enumerate((a, b)):
                    state = original
                    for gap in range(1, 257):
                        state = step(state)
                        for index2, half2 in observed.get(state, ()):
                            if index2 != index or half2 != half:
                                matches.add((index, half, index2, half2, gap))
            print(f"{name} {byteorder}: 132 controls, {direct} same-row consecutive "
                  f"matches, {len(matches)} cross-row/within-row gaps 1..256")
    print("Selected coupon excluded; target commitment was not tested.")


if __name__ == "__main__":
    main()
