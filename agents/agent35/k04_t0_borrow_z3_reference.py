#!/usr/bin/env python3
"""Small Z3 first-pair xoroshiro128++ direct-borrow integration reference.

Constructs only the output-0/output-1 inverse core. The 18:02 ACK, 18:03
holdout, route mask and original K04 commitment are intentionally absent.
A solved initial state must be replayed by the canonical owner to construct
and hash the full 16-byte middle before any holdout/uniqueness disposition.

Requires z3-solver==4.15.4.0 for the optional seeded regression control.
"""
from __future__ import annotations

import random

MASK64 = (1 << 64) - 1
PLANTED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol64(value: int, n: int) -> int:
    return ((value << n) | (value >> (64 - n))) & MASK64


def stream(initial: tuple[int, int], count: int = 6) -> list[int]:
    a, b = initial
    out: list[int] = []
    for _ in range(count):
        out.append((rol64((a + b) & MASK64, 17) + a) & MASK64)
        t = a ^ b
        a = (rol64(a, 49) ^ t ^ (t << 21)) & MASK64
        b = rol64(t, 28)
    return out


def inverse_first_pair(y0: int, y1: int, variable_name: str = "first_a0"):
    """Return (a0, t0, constraints, (a1,b1)) in Z3 bitvectors.

    y0/y1 are successive 64-bit xoroshiro128++ outputs.
    Fit ONLY those two outputs. No middle or holdout words are built.
    """
    from z3 import BitVec, BitVecVal, Concat, Extract, RotateLeft, RotateRight

    a0 = BitVec(variable_name, 64)
    u0 = RotateRight(BitVecVal(y0, 64) - a0, 17)

    def borrow_next(x, y, prior):
        # One-bit exact subtraction borrow recurrence:
        # borrow' = MAJ(~x, y, prior).
        return (~x & y) | ((~x | y) & prior)

    r0 = BitVecVal(0, 1)
    t_bits = []
    for i in range(64):
        ui, ai = Extract(i, i, u0), Extract(i, i, a0)
        t_bits.append(ui ^ r0)
        if i < 63:
            r0 = borrow_next(ui, ai, r0)
    t0 = Concat(*reversed(t_bits))

    a1 = RotateLeft(a0, 49) ^ t0 ^ (t0 << 21)
    b1 = RotateLeft(t0, 28)

    u1 = RotateRight(BitVecVal(y1, 64) - a1, 17)
    r1 = BitVecVal(0, 1)
    diff_bits = []
    for i in range(64):
        ui, ai = Extract(i, i, u1), Extract(i, i, a1)
        diff_bits.append(ui ^ ai ^ r1)
        if i < 63:
            r1 = borrow_next(ui, ai, r1)
    required_b1 = Concat(*reversed(diff_bits))
    constraints = [required_b1 == b1]
    return a0, t0, constraints, (a1, b1)


def seeded_control() -> None:
    """Seeded full replay and one-bit-mutated negative; not an unseeded solve."""
    from z3 import BitVecVal, SolverFor, sat, unsat

    rng = random.Random(0x35A17E2026)
    seeds = [PLANTED] + [
        (rng.getrandbits(64), rng.getrandbits(64)) for _ in range(9)
    ]
    for index, seed in enumerate(seeds):
        samples = stream(seed)
        a0, t0, constraints, _ = inverse_first_pair(
            samples[0], samples[1], variable_name=f"seeded_{index}"
        )
        s = SolverFor("QF_BV")
        s.set("timeout", 10000)
        s.add(a0 == BitVecVal(seed[0], 64), *constraints)
        assert s.check() == sat, ("positive", index)
        model = s.model()
        assert model.eval(t0).as_long() == seed[0] ^ seed[1]
        assert stream((seed[0], seed[0] ^ model.eval(t0).as_long())) == samples

        # A mutated second output must be impossible with the initial a0
        # fixed and the first output unchanged.
        wrong_a0, _, wrong_constraints, _ = inverse_first_pair(
            samples[0], samples[1] ^ 1, variable_name=f"negative_{index}"
        )
        wrong = SolverFor("QF_BV")
        wrong.set("timeout", 10000)
        wrong.add(wrong_a0 == BitVecVal(seed[0], 64), *wrong_constraints)
        assert wrong.check() == unsat, ("negative", index)

    print("PASS: 10 seeded original+mutated full-output inversions")
    print("Unseeded SAT state-recovery, source hypothesis and K04 status: UNTESTED")


if __name__ == "__main__":
    seeded_control()
