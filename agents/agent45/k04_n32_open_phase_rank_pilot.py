"""Conditional p951 genuine CPython n32 open-phase source-rank pilot.

Use original 132 intact printer records, exclude selected row129, and examine
the smallest-rank repeated-key n32 initialized-state term pair. If tractable,
test complete independent term-set intersection. The K04 commitment and
selected copied ACK are not used.
Run: python agents/agent45/k04_n32_open_phase_rank_pilot.py
"""
from __future__ import annotations
from itertools import combinations
import hashlib
import random

from k04_source_n24_phase_sweep_sft import (
    OFFSET, mt, words, original_native, phase_equations,
    reduce_source, source_dimension, source_group, key_term
)

PHASES = (OFFSET + 166, OFFSET + 180, OFFSET + 201,
          OFFSET + 310, OFFSET + 337)
U = 0xffffffff


def pilot(symbolic):
    packets = original_native()
    for phase in PHASES:
        coefficients, constants = reduce_source(
            phase_equations(packets, symbolic, phase)
        )
        dimension = {
            at: source_dimension(
                coefficients[32 * index + bit]
                for index in (at - 2, at - 1, at)
                for bit in range(32)
            ) for at in range(4, 624)
        }
        pairs = sorted(
            ((dimension[a] + dimension[b], max(dimension[a], dimension[b]),
              dimension[a], dimension[b], a, b)
             for a, b in combinations(dimension, 2)
             if (b - a) % 32 == 0)
        )
        assert pairs
        best = pairs[0]
        feasible = [p for p in pairs if p[1] <= 13]
        print(f"N32_ORIGINAL_PHASE prior={phase} "
              f"min_sum={best[0]} max_dimension={best[1]} "
              f"dimensions={best[2]},{best[3]} term_pair={best[4]},{best[5]} "
              f"tractable_pairs_both_max13={len(feasible)}",
              flush=True)
        if feasible:
            hit = 0
            witness = None
            for _, _, da, db, a, b in feasible:
                vals_a = {key_term(a, row) for row in
                          source_group(coefficients, constants, a)}
                vals_b = {key_term(b, row) for row in
                          source_group(coefficients, constants, b)}
                assert len(vals_a) == 1 << da
                assert len(vals_b) == 1 << db
                if not vals_a.intersection(vals_b):
                    hit += 1
                    witness = (a, b)
                    break
            print(f"N32_ORIGINAL_PHASE_PAIRWISE_DISJOINT "
                  f"prior={phase} found={hit} witness={witness}",
                  flush=True)


def seeded_true_term_control():
    payload = bytes((i * 19 + 37) & 255 for i in range(64))
    expanded = int.from_bytes(payload + hashlib.sha512(payload).digest(), "big")
    assert (expanded.bit_length() + 31) // 32 == 32
    gen = random.Random(payload)
    assert gen.getstate() == random.Random(expanded).getstate()
    state = gen.getstate()[1][:624]
    candidate_pairs = 0
    for a in range(4, 624):
        b = a + 32
        if b >= 624:
            break
        assert key_term(a, tuple(state[a-2:a+1])) == key_term(
            b, tuple(state[b-2:b+1]))
        candidate_pairs += 1
    assert candidate_pairs >= 500
    print("GENUINE_CPYTHON_BYTES64_N32_REPEATED_KEY_TERMS=PASS",
          candidate_pairs)


if __name__ == "__main__":
    seeded_true_term_control()
    pilot(words(OFFSET + 337))
