"""Read-only H17 original 32-bit-field long-linear-complexity source predictor.

Frozen original selected ACK2 never used in source model. An original full-byte
holdout must be reproduced before any selected K04 commitment is attempted.
"""
from __future__ import annotations
import hashlib, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
POLS = (0x8D, 0x04C11DB7)
MASK = (1 << 32) - 1


def mul(a: int, b: int, poly: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & (1 << 32):
            a ^= poly | (1 << 32)
        b >>= 1
    return result & MASK


def inv(a: int, poly: int) -> int:
    assert a
    u, v, g1, g2 = a, (1 << 32) | poly, 1, 0
    while u != 1:
        j = u.bit_length() - v.bit_length()
        if j < 0:
            u, v = v, u
            g1, g2 = g2, g1
            j = -j
        u ^= v << j
        g1 ^= g2 << j
    while g1.bit_length() > 32:
        g1 ^= ((1 << 32) | poly) << (g1.bit_length() - 33)
    assert mul(g1, a, poly) == 1
    return g1


def bm(values: list[int], poly: int) -> tuple[list[int], int]:
    c, b = [1], [1]
    length, shift, old = 0, 1, 1
    for t, sym in enumerate(values):
        d = sym
        for j in range(1, length + 1):
            d ^= mul(c[j], values[t - j], poly)
        if not d:
            shift += 1
            continue
        snapshot = c[:]
        factor = mul(d, inv(old, poly), poly)
        c.extend([0] * max(0, len(b) + shift - len(c)))
        for j, bv in enumerate(b):
            c[j + shift] ^= mul(factor, bv, poly)
        if 2 * length <= t:
            length, b, old, shift = t + 1 - length, snapshot, d, 1
        else:
            shift += 1
    return c[:length + 1], length


def project(prefix: list[int], coeff: list[int], poly: int, length: int) -> list[int]:
    seen = prefix[:]
    for _ in range(length):
        nxt = 0
        for j in range(1, len(coeff)):
            nxt ^= mul(coeff[j], seen[-j], poly)
        seen.append(nxt)
    return seen[-length:]


def parse() -> list[bytes]:
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA
    rows = []
    for line in original.decode().splitlines():
        m = re.search(
            r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) .*? PAYLOAD=([0-9A-F]{32})",
            line,
        )
        if m and 300 <= int(m.group(1)) <= 427 and m.group(2) == "1" and m.group(3) == "ACK":
            rows.append((int(m.group(1)), bytes.fromhex(m.group(4))))
    rows.sort()
    assert len(rows) == 128 and [n for n, _ in rows] == list(range(300, 428))
    return [p for _, p in rows]


def words(packets: list[bytes], endian: str, reverse: bool) -> list[int]:
    seq = []
    for packet in packets:
        parts = [packet[i:i + 4] for i in range(0, 16, 4)]
        if reverse:
            parts.reverse()
        seq.extend(int.from_bytes(part, endian) for part in parts)
    return seq


def synthetic(poly: int) -> None:
    rng = random.Random(poly + 20261104)
    taps = [0, *(rng.getrandbits(32) for _ in range(5))]
    seq = [rng.getrandbits(32) for _ in range(5)]
    for _ in range(300):
        nextword = 0
        for j in range(1, 6):
            nextword ^= mul(taps[j], seq[-j], poly)
        seq.append(nextword)
    coeff, order = bm(seq[:120], poly)
    assert order == 5 and project(seq[:120], coeff, poly, 64) == seq[120:184]
    print(f"SYNTHETIC field={poly:#x} order=5 withheld=64 PASS", flush=True)


def main() -> None:
    originals = parse()
    print("SOURCE pin PASS; 128 routine source packets", flush=True)
    for pol in POLS:
        synthetic(pol)
        for end in ("little", "big"):
            for reverse in (False, True):
                seq = words(originals, end, reverse)
                for train in (128, 256, 384):
                    coeff, order = bm(seq[:train], pol)
                    expected = seq[train:train + 64]
                    guessed = project(seq[:train], coeff, pol, 64)
                    correct = sum(a == b for a, b in zip(guessed, expected))
                    assert correct == 0, (pol, end, reverse, train, correct)
                    print(
                        f"ORIGINAL field={pol:#x} endian={end} reverse={reverse} "
                        f"train={train} order={order} word_matches={correct}/64",
                        flush=True,
                    )
    print("RESULT: no 32bit-field common low-order predictive recurrence on routine source; selected K04 never used", flush=True)


if __name__ == "__main__":
    main()
