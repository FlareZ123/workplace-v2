"""Original H-17 printer native MT witness calibration against an i.i.d. 32-bit null.

No selected ACK2 payload, K04 acceptance, route mask, or K08 input is read.
Run from repository root with Python standard library.
"""
from __future__ import annotations

import hashlib
import math
import random
import re
from collections import defaultdict
from pathlib import Path

SOURCE = Path('resources/evidence/print/spool-reconstruction.log')
PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def untemper(y: int) -> int:
    x = y
    for direction, shift, mask, iterations in (
        ('r', 18, 0, 2), ('l', 15, 0xEFC60000, 2),
        ('l', 7, 0x9D2C5680, 6), ('r', 11, 0, 4)
    ):
        original = x
        for _ in range(iterations):
            x = original ^ (x >> shift if direction == 'r' else (x << shift) & mask)
        x &= 0xffffffff
    return x


def mix(a: int, b: int) -> int:
    return (((a & 0x80000000 | b & 0x7fffffff) >> 1)
            ^ (0x9908b0df if b & 1 else 0))


def parse_original() -> list[list[int]]:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    lines = [line for line in raw.decode('ascii').splitlines() if 'PAYLOAD=' in line]
    assert len(lines) == 133
    assert 'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in lines[129]
    rows = []
    for index, line in enumerate(lines):
        if index == 129:
            continue
        packet = bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', line).group(1))
        rows.append([untemper(int.from_bytes(packet[offset:offset + 4], 'little'))
                     for offset in range(0, 16, 4)])
    return rows


def count_witnesses(rows: list[list[int]]) -> int:
    assert all(len(row) == 4 for row in rows)
    n = len(rows)
    xors: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for k in range(n - 1):
        for l in range(k + 1, n):
            for i in range(4):
                for j in range(4):
                    xors[rows[k][i] ^ rows[l][j]].append((k, l))
    found = 0
    for row in range(n - 2):
        for j in (1, 2, 3):
            desired = mix(rows[row][j - 1], rows[row][j])
            for k, l in xors.get(desired, ()):
                found += k > row and l > k
    return found


def synthetic_control() -> int:
    rng = random.Random(20261118)
    rows = []
    for i in range(132):
        rows.append([untemper(rng.getrandbits(32)) for _ in range(4)])
        if i != 131:
            for _ in range(3):
                rng.getrandbits(32)
    return count_witnesses(rows)


def main() -> None:
    n = 132
    candidates = math.comb(n, 3) * 3 * 4 * 4
    expected = candidates / (2 ** 32)
    original_count = count_witnesses(parse_original())
    assert candidates == 17983680
    assert abs(expected - .004187151789665222) < 1e-16
    assert original_count == 25
    rng = random.Random(0x17C4A11B)
    null_counts = [count_witnesses([[rng.getrandbits(32) for _ in range(4)]
                                    for _ in range(n)]) for _ in range(64)]
    genuine_count = synthetic_control()
    assert genuine_count > 10
    print('SOURCE_SHA256', PIN)
    print('ORIGINAL_NONSELECTED_ROWS', n)
    print('ORIGINAL_EXACT_WITNESSES', original_count)
    print('IID32_EXACT_TESTED_TUPLES', candidates)
    print('IID32_EXPECTED_WITNESSES', format(expected, '.12f'))
    print('IID32_MARKOV_UPPER_BOUND_P_25_OR_MORE', format(expected / 25, '.12f'))
    print('IID32_NULL_64_TRIAL_COUNTS', null_counts)
    print('GENUINE_SEEDED_MT_POSITIVE_WITNESSES', genuine_count)
    print('AUTHENTICATED_K04_SELECTED_BITS', 0)


if __name__ == '__main__':
    main()
