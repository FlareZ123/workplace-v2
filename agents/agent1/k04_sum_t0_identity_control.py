#!/usr/bin/env python3
"""Deterministic pure-Python identity control for K04 sum/t0 dual-borrow equations.

This validates arithmetic identities only. It does not test Z3 performance, source
pairing, or the hypothesis that the PS-0417 payloads are xoroshiro128++ outputs.
"""
from __future__ import annotations

import random

MASK64 = (1 << 64) - 1
ROT_OUT = 17
ROT_A = 49
ROT_B = 28
SHIFT_A = 21
SAMPLES = 10_000
SEED = 0xA17E8BC05E34DB24


def rotl64(x: int, n: int) -> int:
    n %= 64
    x &= MASK64
    return ((x << n) | (x >> (64 - n))) & MASK64 if n else x


def rotr64(x: int, n: int) -> int:
    n %= 64
    x &= MASK64
    return ((x >> n) | (x << (64 - n))) & MASK64 if n else x


def output(a: int, b: int) -> int:
    return (rotl64((a + b) & MASK64, ROT_OUT) + a) & MASK64


def step_from_t(a: int, t: int) -> tuple[int, int]:
    a1 = (rotl64(a, ROT_A) ^ t ^ ((t << SHIFT_A) & MASK64)) & MASK64
    b1 = rotl64(t, ROT_B)
    return a1, b1


def subtract_with_borrow(x: int, y: int) -> tuple[int, int]:
    """Return x-y mod 2^64 and the final borrow, using the bit recurrence."""
    borrow = 0
    difference = 0
    for i in range(64):
        xi = (x >> i) & 1
        yi = (y >> i) & 1
        difference |= (xi ^ yi ^ borrow) << i
        borrow = ((1 - xi) & yi) | (((1 - xi) | yi) & borrow)
    return difference & MASK64, borrow


def t0_from_sum(x0: int, a0: int) -> int:
    """Given x0=a0+b0, return t0=a0 XOR b0 via borrow for x0-a0."""
    borrow = 0
    t0 = 0
    for i in range(64):
        xi = (x0 >> i) & 1
        ai = (a0 >> i) & 1
        t0 |= (xi ^ borrow) << i
        borrow = ((1 - xi) & ai) | (((1 - xi) | ai) & borrow)
    return t0 & MASK64


def recover_first_sum(y0: int, x0: int) -> tuple[int, int]:
    """For x0=a0+b0, invert y0=ROTL(x0,17)+a0 and derive t0 without b0."""
    a0 = (y0 - rotl64(x0, ROT_OUT)) & MASK64
    return a0, t0_from_sum(x0, a0)


def stream(a: int, b: int, count: int) -> list[int]:
    out: list[int] = []
    for _ in range(count):
        out.append(output(a, b))
        t = a ^ b
        a, b = step_from_t(a, t)
    return out


def main() -> None:
    rng = random.Random(SEED)
    for sample in range(SAMPLES):
        a0 = rng.getrandbits(64)
        b0 = rng.getrandbits(64)
        expected = stream(a0, b0, 6)

        x0 = (a0 + b0) & MASK64
        recovered_a0, recovered_t0 = recover_first_sum(expected[0], x0)
        assert recovered_a0 == a0, (sample, "a0")
        assert recovered_t0 == (a0 ^ b0), (sample, "t0")

        a1, b1 = step_from_t(recovered_a0, recovered_t0)
        y1 = expected[1]
        u1 = rotr64((y1 - a1) & MASK64, ROT_OUT)
        recovered_b1, _ = subtract_with_borrow(u1, a1)
        assert recovered_b1 == b1, (sample, "second-output borrow")
        assert stream(recovered_a0, recovered_a0 ^ recovered_t0, 6) == expected, (sample, "replay")

    print(f"PASS: {SAMPLES} deterministic states; seed=0x{SEED:016X}")
    print("Arithmetic identities only; no source data or solver performance tested.")


if __name__ == "__main__":
    main()
