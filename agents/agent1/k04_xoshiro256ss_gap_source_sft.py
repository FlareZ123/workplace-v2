"""K04: source-holdout test of xoshiro256** across arbitrary packet gaps.

The 64-bit xoshiro256** output rotl(s1*5,7)*9 can be inverted, so
observed full outputs give exact GF(2) constraints on the 256-bit state.
Two successive 64-bit outputs need not be adjacent: test eight strides,
all four endian/word orders, and independently variable interpacket
gaps 0..96. The disputed selected row129 is *never read as an input*.
Two independent intact packet triples are tested, including rows128,
130,131 bracketing/after the missing coupon.

Run: python agents/agent1/k04_xoshiro256ss_gap_source_sft.py resources
A strict original log SHA256 pin and synthetic seeded producer controls
protect orientation and inversion. No original evidence is changed.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import re
import sys
import time

MASK64 = (1 << 64) - 1
MASK256 = (1 << 256) - 1
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
INV5 = pow(5, -1, 1 << 64)
INV9 = pow(9, -1, 1 << 64)


def rotl(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK64


def rotr(x, n):
    return ((x >> n) | (x << (64 - n))) & MASK64


def inverse_output(y):
    return (rotr((y * INV9) & MASK64, 7) * INV5) & MASK64


def output(state):
    return (rotl((state[1] * 5) & MASK64, 7) * 9) & MASK64


def step(state):
    s0, s1, s2, s3 = state
    t = (s1 << 17) & MASK64
    s2 ^= s0
    s3 ^= s1
    s1 ^= s2
    s0 ^= s3
    s2 ^= t
    s3 = rotl(s3, 45)
    return s0, s1, s2, s3


def output_coefficients(steps):
    # Each 64-bit observed s1 is a GF(2)-linear projection of
    # the 256-bit initial state. Coefficient rows are Python bigints.
    coefficients = [[0] * 64 for _ in range(steps)]
    for bit in range(256):
        state = [0, 0, 0, 0]
        state[bit // 64] = 1 << (bit % 64)
        state = tuple(state)
        for i in range(steps):
            word = state[1]
            while word:
                low = word & -word
                coefficients[i][low.bit_length() - 1] |= 1 << bit
                word -= low
            state = step(state)
    return coefficients


def equations(index, value, coefficients):
    return [
        row | (((value >> bit) & 1) << 256)
        for bit, row in enumerate(coefficients[index])
    ]


def fit(rows, parent=None):
    basis = {} if parent is None else dict(parent)
    for row in rows:
        while row:
            low = row & MASK256
            if not low:
                return None
            pivot = low.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return basis


def solve(basis):
    solution = 0
    for pivot in sorted(basis):
        row = basis[pivot]
        bit = ((row >> 256) & 1) ^ ((row & solution).bit_count() & 1)
        solution |= bit << pivot
    return solution


def control(coefficients):
    original = (
        0xA5B6,
        0x1234FEDC01234567,
        0xF00FF00F,
        0xDEADBEEF,
    )
    for stride, gap_a, gap_b in ((1, 0, 0), (4, 13, 46), (8, 96, 96)):
        locations = [
            0, stride,
            stride + 1 + gap_a, stride * 2 + 1 + gap_a,
            stride * 2 + 2 + gap_a + gap_b,
            stride * 3 + 2 + gap_a + gap_b,
        ]
        state = original
        wanted = []
        for i in range(max(locations) + 1):
            if i in locations:
                wanted.append((i, inverse_output(output(state))))
            state = step(state)
        rows = []
        for i, value in wanted:
            rows.extend(equations(i, value, coefficients))
        basis = fit(rows)
        assert basis is not None and len(basis) == 256
        recovered = solve(basis)
        assert recovered == sum(word << (64 * i) for i, word in enumerate(original))
        print(f"POSITIVE stride={stride} gaps={gap_a},{gap_b} exact256=PASS")


def source(path):
    if path.is_file():
        with ZipFile(path) as archive:
            data = archive.read("evidence/print/spool-reconstruction.log")
    else:
        data = (path / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    lines = [line for line in data.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    return [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1)) for line in lines]


def main(path):
    start = time.monotonic()
    limit = 96
    coefficients = output_coefficients(2 * limit + 3 * 9)
    control(coefficients)
    rows = source(path)

    for name, source_indices in (
        ("routine-first-three", (0, 1, 2)),
        ("selected-adjacent-originals", (128, 130, 131)),
    ):
        compatible_first_two = 0
        tested_third_gap = 0
        matches = 0
        for stride in range(1, 9):
            for reversed_order in (False, True):
                for endian in ("big", "little"):
                    word_indices = (1, 0) if reversed_order else (0, 1)
                    words = [
                        [
                            inverse_output(int.from_bytes(
                                rows[idx][j * 8:(j + 1) * 8], endian
                            ))
                            for j in word_indices
                        ]
                        for idx in source_indices
                    ]
                    first = (equations(0, words[0][0], coefficients)
                             + equations(stride, words[0][1], coefficients))
                    for ga in range(limit + 1):
                        second = stride + 1 + ga
                        basis = fit(first
                                    + equations(second, words[1][0], coefficients)
                                    + equations(second + stride, words[1][1], coefficients))
                        if basis is None:
                            continue
                        compatible_first_two += 1
                        for gb in range(limit + 1):
                            third = second + stride + 1 + gb
                            tested_third_gap += 1
                            third_basis = fit(
                                equations(third, words[2][0], coefficients)
                                + equations(third + stride, words[2][1], coefficients),
                                basis,
                            )
                            if third_basis is not None:
                                matches += 1
        print(name, "source-compatible first-two", compatible_first_two,
              "three-packet gap cases", tested_third_gap,
              "three-packet survivors", matches,
              "seconds", round(time.monotonic() - start, 3))
        assert matches == 0
    print("SOURCE NEGATIVE: no shared xoshiro256** original packet generator"
          " within the defined stride, gap and serialization family.")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
