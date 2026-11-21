#!/usr/bin/env python3
"""Reference-only validation for the K04 xoroshiro128++ dual-inverse borrow circuit.

No SAT solver is used. This checks the Boolean/CNF/XOR circuit against planted
states, verifies forward middle/holdout replay, and reports deterministic sizes.
"""
from __future__ import annotations

import random

MASK64 = (1 << 64) - 1
SEED = (0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA)


def rol64(x: int, n: int) -> int:
    n %= 64
    return ((x << n) | (x >> (64 - n))) & MASK64 if n else x & MASK64


def stream(state: tuple[int, int], count: int = 6) -> list[int]:
    a, b = state
    out = []
    for _ in range(count):
        out.append((rol64((a + b) & MASK64, 17) + a) & MASK64)
        t = a ^ b
        a = (rol64(a, 49) ^ t ^ (t << 21)) & MASK64
        b = rol64(t, 28)
    return out


class BorrowCircuit:
    def __init__(self) -> None:
        self.count = 0
        self.clauses: list[list[int]] = []
        self.xors: list[tuple[list[int], bool]] = []
        self.witness: dict[int, bool] = {}

    def variable(self, value: bool | None = None) -> int:
        self.count += 1
        if value is not None:
            self.witness[self.count] = bool(value)
        return self.count

    def word(self, value: int | None = None) -> list[int]:
        return [self.variable(None if value is None else bool((value >> i) & 1))
                for i in range(64)]

    def lit_value(self, lit: int) -> bool:
        value = self.witness[abs(lit)]
        return value if lit > 0 else not value

    def xor_rhs(self, terms: list[int], rhs: int = 0) -> int:
        terms = [v for v in terms if v]
        if not terms:
            if rhs:
                raise ValueError("constant-one XOR output is not used by this circuit")
            return 0
        if len(terms) == 1 and rhs == 0:
            return terms[0]
        known = all(v in self.witness for v in terms)
        value = ((sum(self.witness[v] for v in terms) % 2) ^ bool(rhs)) if known else None
        out = self.variable(value)
        self.xors.append((terms + [out], bool(rhs)))
        return out

    def xor(self, *terms: int) -> int:
        return self.xor_rhs(list(terms), 0)

    def and_lits(self, x: int, y: int) -> int:
        known = abs(x) in self.witness and abs(y) in self.witness
        value = self.lit_value(x) and self.lit_value(y) if known else None
        out = self.variable(value)
        self.clauses.extend(([-x, -y, out], [x, -out], [y, -out]))
        return out

    def or_lits(self, x: int, y: int) -> int:
        known = abs(x) in self.witness and abs(y) in self.witness
        value = self.lit_value(x) or self.lit_value(y) if known else None
        out = self.variable(value)
        self.clauses.extend(([-x, out], [-y, out], [x, y, -out]))
        return out

    def majority_lits(self, x: int, y: int, z: int) -> int:
        known = all(abs(v) in self.witness for v in (x, y, z))
        value = sum(self.lit_value(v) for v in (x, y, z)) >= 2 if known else None
        out = self.variable(value)
        self.clauses.extend((
            [-x, -y, out], [-x, -z, out], [-y, -z, out],
            [x, y, -out], [x, z, -out], [y, z, -out],
        ))
        return out

    def add64(self, a: list[int], b: list[int]) -> list[int]:
        carry = 0
        out = []
        for i in range(64):
            out.append(self.xor(a[i], b[i], carry))
            if i < 63:
                carry = self.and_lits(a[i], b[i]) if i == 0 else self.majority_lits(a[i], b[i], carry)
        return out

    def sub64(self, a: list[int], b: list[int]) -> list[int]:
        borrow = 0
        out = []
        for i in range(64):
            out.append(self.xor(a[i], b[i], borrow))
            if i < 63:
                borrow = self.and_lits(-a[i], b[i]) if i == 0 else self.majority_lits(-a[i], b[i], borrow)
        return out

    def sub_const64(self, c: int, a: list[int]) -> list[int]:
        borrow = 0
        out = []
        for i in range(64):
            ci = (c >> i) & 1
            out.append(self.xor_rhs([a[i], borrow], ci))
            if i < 63:
                if borrow == 0:
                    borrow = a[i] if ci == 0 else 0
                else:
                    borrow = self.or_lits(a[i], borrow) if ci == 0 else self.and_lits(a[i], borrow)
        return out

    @staticmethod
    def rotated(bits: list[int], n: int) -> list[int]:
        return [bits[(i - n) % 64] for i in range(64)]

    def step(self, a: list[int], b: list[int]) -> tuple[list[int], list[int]]:
        t = [self.xor(x, y) for x, y in zip(a, b)]
        ra = self.rotated(a, 49)
        na = [self.xor(ra[i], t[i], t[i - 21] if i >= 21 else 0) for i in range(64)]
        nb = self.rotated(t, 28)
        return na, nb

    def output(self, a: list[int], b: list[int]) -> list[int]:
        return self.add64(self.rotated(self.add64(a, b), 17), a)

    def get_state_from_output(self, a: list[int], y: int) -> list[int]:
        intermediate = self.sub_const64(y, a)
        return self.sub64(self.rotated(intermediate, -17), a)

    def constrain_sub64_equal(self, a: list[int], b: list[int], expected: list[int]) -> None:
        borrow = 0
        for i in range(64):
            terms = [v for v in (a[i], b[i], borrow, expected[i]) if v]
            self.xors.append((terms, False))
            if i < 63:
                borrow = self.and_lits(-a[i], b[i]) if i == 0 else self.majority_lits(-a[i], b[i], borrow)

    def constrain_output(self, a: list[int], b: list[int], y: int) -> None:
        intermediate = self.sub_const64(y, a)
        self.constrain_sub64_equal(self.rotated(intermediate, -17), a, b)

    def build_first_pair(self, y0: int, y1: int, seed: tuple[int, int] | None = None,
                         include_middle: bool = False):
        a0 = self.word(None if seed is None else seed[0])
        b0 = self.get_state_from_output(a0, y0)
        state1 = self.step(a0, b0)
        self.constrain_output(*state1, y1)
        middle = None
        if include_middle:
            state2 = self.step(*state1)
            state3 = self.step(*state2)
            middle = (self.output(*state2), self.output(*state3))
        return (a0, b0), middle

    def validate_witness(self) -> None:
        assert len(self.witness) == self.count
        for clause in self.clauses:
            assert any(self.lit_value(lit) for lit in clause), clause
        for terms, rhs in self.xors:
            assert (sum(self.witness[v] for v in terms) % 2) == int(rhs), (terms, rhs)

    def bits_to_int(self, bits: list[int]) -> int:
        return sum(int(self.witness[v]) << i for i, v in enumerate(bits))


def main() -> None:
    planted = stream(SEED, 6)
    core = BorrowCircuit()
    core.build_first_pair(planted[0], planted[1], include_middle=False)
    full = BorrowCircuit()
    (state_bits, middle) = full.build_first_pair(planted[0], planted[1], seed=SEED, include_middle=True)
    full.validate_witness()
    assert middle is not None
    recovered_state = tuple(full.bits_to_int(w) for w in state_bits)
    replayed = stream(recovered_state, 6)
    assert replayed[:2] == planted[:2]
    assert [full.bits_to_int(w) for w in middle] == planted[2:4]
    assert replayed[2:4] == planted[2:4]
    assert replayed[4:6] == planted[4:6]

    core_counts = (core.count, len(core.clauses), len(core.xors))
    full_counts = (full.count, len(full.clauses), len(full.xors))
    assert core_counts == (632, 1122, 382), core_counts
    assert full_counts == (1396, 2622, 894), full_counts

    rng = random.Random(0xA17E2026)
    for _ in range(100):
        seed = (rng.getrandbits(64), rng.getrandbits(64))
        outputs = stream(seed, 6)
        circuit = BorrowCircuit()
        (state_bits, middle_bits) = circuit.build_first_pair(
            outputs[0], outputs[1], seed=seed, include_middle=True
        )
        circuit.validate_witness()
        recovered_state = tuple(circuit.bits_to_int(w) for w in state_bits)
        assert stream(recovered_state, 6) == outputs
        assert middle_bits is not None
        assert [circuit.bits_to_int(w) for w in middle_bits] == outputs[2:4]

    print("PASS: deterministic 100-state CNF/XOR witness validation")
    print(f"planted core variables/CNF/XOR: {core_counts}")
    print(f"planted full variables/CNF/XOR: {full_counts}")
    print("No SAT solver invoked; this is circuit validation only.")


if __name__ == "__main__":
    main()
