"""K04 source-only CPython init_by_array key-term sieve over all register rotations.

This tests hypothetical *cyclic initial-register* orientations, not arbitrary
output offsets or actual historical printer firmware. Original selected ACK
row129, K04 mask, acceptance commitments and verifier are never consulted.
"""
from __future__ import annotations

from collections import Counter
import importlib.util
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = Path(__file__).resolve().parents[1] / "agent39" / "k04_scalar_seed_rotation_sft.py"
spec = importlib.util.spec_from_file_location("agent39_mt_source", SOURCE)
assert spec is not None and spec.loader is not None
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)

U = 0xFFFFFFFF
G = [19650218]
for i in range(1, 624):
    G.append((1812433253 * (G[-1] ^ (G[-1] >> 30)) + i) & U)


def f(c: int, x: int) -> int:
    return c * (x ^ (x >> 30)) & U


def keyterm(x: int, y: int, z: int, i: int) -> int:
    """CPython one-visit necessary term key[(i-1)%n]+(i-1)%n, i>=4."""
    prev = (((y + i - 1) & U) ^ f(1566083941, x))
    curr = (((z + i) & U) ^ f(1566083941, y))
    return (curr - (G[i] ^ f(1664525, prev))) & U


def possible(mask: int, value: int) -> tuple[int, ...]:
    if mask == U:
        return (value,)
    if mask.bit_count() == 31:
        return (value, value | ((~mask) & U))
    return ()


def term_domains(states: list[tuple[int, int]], phase: int):
    result = []
    for i in range(4, 624):
        a, b, c = (possible(*states[(phase + i - j) % 624])
                   for j in (2, 1, 0))
        if not a or not b or not c:
            continue
        vals = {keyterm(x, y, z, i) for x in a for y in b for z in c}
        result.append((i - 1, vals))
    return result


def consistent(term_rows, seed_words: int) -> bool:
    residue_domains = {}
    for j, allowed in term_rows:
        r = j % seed_words
        if r in residue_domains:
            residue_domains[r].intersection_update(allowed)
            if not residue_domains[r]:
                return False
        else:
            residue_domains[r] = set(allowed)
    return True


def synthetic_controls() -> None:
    count = 0
    for n in (1, 2, 4, 8, 16, 32, 64, 128, 213, 249, 365, 623):
        seed = sum(((0x12345678 + j * 0x30158DA) & U) << (32 * j)
                   for j in range(n))
        original = list(random.Random(seed).getstate()[1][:624])
        assert original[0] == 0x80000000
        for offset in (0, 17, 201, 390, 623):
            rotated = original[offset:] + original[:offset]
            state = [(U if j % 4 in (0, 2) else 0x7FFFFFFF,
                      v & (U if j % 4 in (0, 2) else 0x7FFFFFFF))
                     for j, v in enumerate(rotated)]
            assert consistent(term_domains(state, (-offset) % 624), n)
            count += 1
    assert count == 60
    print("SYNTHETIC seeded CPython masked-state controls: 60/60 PASS")


def main() -> None:
    synthetic_controls()
    words = mt.symbolic_mt()
    basis = mt.source_basis(words, ROOT)
    assert len(basis) == 15365

    state = []
    for i in range(624):
        mask = value = 0
        for bit, expr in enumerate(words[i]):
            residual = mt.reduce(expr << 1, basis)
            if residual in (0, 1):
                mask |= 1 << bit
                value |= residual << bit
        state.append((mask, value))
    assert all(state[i] == (U, v) for i, v in
               {2: 0xE32E1557, 3: 0x3152E7CB,
                4: 0xBBDD46A0, 622: 0xBBD5A4AB}.items())

    phases = {
        p: term_domains(state, p)
        for p in range(624)
        if not ((state[p][1] ^ 0x80000000) & state[p][0])
    }
    assert len(phases) == 225
    assert Counter(len(rows) for rows in phases.values()) == {96: 204, 95: 21}

    survivors = {n: sum(consistent(rows, n) for rows in phases.values())
                 for n in range(1, 624)}
    assert sum(v == 0 for v in survivors.values()) == 471
    assert min(n for n, count in survivors.items() if count) == 374
    assert survivors[374] == 35 and survivors[373] == 0
    assert survivors[623] == 225 and sum(survivors.values()) == 12558

    print("ORIGINAL intact 132 printer rows; symbolic MT source rank:", len(basis))
    print("S[0] forced 0x80000000: 399/624 rotations excluded")
    print("96 source-derived >=31-bit triple domains at 204 retained phases;",
          "95 at 21 retained phases")
    print("Original source: 388752 phase x key-length pairs tested;",
          "12558 pass necessary checks")
    print("All 624 cyclic-register phases reject every CPython integer",
          "key-array length 1..373 except no exceptions")
    print("Lengths 1..623 rejected completely:", sum(v == 0 for v in survivors.values()))
    print("Earliest necessary survivor: n=374 at 35 cyclic phases")
    print("No true seeded original source or target K04 coupon recovered")


if __name__ == "__main__":
    main()
