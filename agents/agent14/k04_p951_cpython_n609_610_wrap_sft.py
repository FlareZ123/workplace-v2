"""Original p951 source conditional CPython seed lengths 609/610 exclusion.

Uses Agent14's exact source-safe n611 substrate and Agent39's GF(2) printer
source only. A jointly source-consistent early-register word domain is
enumerated before nonlinear repeated-key inversion; selected row129 excluded.
Usage: python agents/agent14/k04_p951_cpython_n609_610_wrap_sft.py
"""
from __future__ import annotations

import importlib.util
import random
from pathlib import Path

SELF = Path(__file__).resolve().with_name("k04_p951_cpython_n611_wrap_sft.py")
spec = importlib.util.spec_from_file_location("n611_source", SELF)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
gf = prior.gf
U = prior.U


def canonical(expr: int, basis: dict[int, int]) -> int:
    """Fully project a GF(2) equation through ALL basis pivots."""
    remainder = 0
    while expr > 1:
        p = expr.bit_length() - 1
        if p in basis:
            expr ^= basis[p]
        else:
            remainder ^= 1 << p
            expr ^= 1 << p
    return remainder | expr


def joint_domain(indices: list[int], basis: dict, expressions: list) -> tuple[list, list]:
    pivots, chosen = {}, []
    for idx in indices:
        for bit, expr in enumerate(expressions[idx]):
            value = canonical(expr << 1, basis) >> 1
            while value:
                p = value.bit_length() - 1
                if p in pivots:
                    value ^= pivots[p]
                else:
                    pivots[p] = value
                    chosen.append((idx, bit))
                    break
    assert len(chosen) <= 4
    possibilities = []
    for selection in range(1 << len(chosen)):
        augmented = basis.copy()
        for pick, (idx, bit) in enumerate(chosen):
            row = gf.reduce(
                (expressions[idx][bit] << 1) | ((selection >> pick) & 1),
                augmented,
            )
            assert row != 1
            if row > 1:
                augmented[row.bit_length() - 1] = row
        assignment = {}
        for idx in indices:
            val = 0
            for bit, expr in enumerate(expressions[idx]):
                result = gf.reduce(expr << 1, augmented)
                assert result in (0, 1)
                val |= result << bit
            assignment[idx] = val
        possibilities.append(assignment)
    assert len(set(tuple(x.values()) for x in possibilities)) == len(possibilities)
    return chosen, possibilities


def invert_repeat(n: int, original: list[int]) -> dict[int, int]:
    """Repeat key j%n at first pass j=622 down to n+3, recovering S[n+2..621]."""
    s = original.copy()
    a_next = prior.state_a(s, 623)
    recovered = {623: s[623], 622: s[622]}
    for j in range(622, n + 2, -1):
        residue = j % n
        assert residue >= 3
        key = (
            prior.state_a(s, residue + 1)
            - (prior.BASE[residue + 1] ^ prior.mix(prior.state_a(s, residue), prior.A))
            - residue
        ) & U
        previous = prior.unmix(
            prior.BASE[j + 1] ^ ((a_next - key - residue) & U), prior.INV_A
        )
        s[j - 1] = prior.unmix(previous ^ ((s[j] + j) & U), prior.INV_B)
        recovered[j - 1] = s[j - 1]
        a_next = previous
    return recovered


def controls() -> None:
    rng = random.Random(0x609610)
    for n in (609, 610):
        for trial in range(16):
            seed_words = [rng.getrandbits(32) for _ in range(n)]
            seed_words[-1] |= 0x80000000
            seed = sum(word << (32 * j) for j, word in enumerate(seed_words))
            real = list(random.Random(seed).getstate()[1][:624])
            recovered = invert_repeat(n, real)
            assert all(real[i] == x for i, x in recovered.items()), (n, trial)
    print("32/32 genuine CPython 609/610-word repeated-key controls PASS")


def main() -> None:
    controls()
    original, masks, basis, expressions = prior.source_constraints()
    for n, indexes, expected, low_fail, high_fail in (
        (609, [7, 13, 14], 16, 8, 24),
        (610, [7, 13], 8, 4, 12),
    ):
        pivots, options = joint_domain(indexes, basis, expressions)
        assert len(options) == expected
        contradiction_counts = {612: 0, 621: 0}
        for values in options:
            for high in (0, 0x80000000):
                s = original.copy()
                s[623] |= high
                for i, word in values.items():
                    s[i] = word
                predicted = invert_repeat(n, s)
                if (predicted[621] ^ original[621]) & masks[621]:
                    contradiction_counts[621] += 1
                else:
                    assert (predicted[612] ^ original[612]) & masks[612], (
                        n, values, high, predicted[612]
                    )
                    contradiction_counts[612] += 1
        assert contradiction_counts == {612: low_fail, 621: high_fail}
        print(
            f"ORIGINAL p951 CPython n{n}: initial quotient rank {len(pivots)}, "
            f"{expected*2} exhaustive complete boundary assignments, "
            f"S621 contradictions {high_fail}, S612 contradictions {low_fail}, "
            "survivors ZERO"
        )
    print("Selected original K04 and final K08 words still unresolved")


if __name__ == "__main__":
    main()
