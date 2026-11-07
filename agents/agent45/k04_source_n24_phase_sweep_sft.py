"""Original-source complete 624-phase CPython seed-recurrence screening.

Each shard covers 39 genuine MT startup offsets, total 2496..3119.
The p951 stage geometry is conditional; selected row129 is withheld.
Run: python agents/agent45/k04_source_n24_phase_sweep_sft.py --shard 0
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import hashlib
import random

from k04_k2496_nineteen_term_source_sft import (
    OFFSET, mt, words, original_packets, reduce_source,
    source_dimension, source_group, key_term
)


def original_native():
    packets = original_packets()
    assert len(packets) == len(mt.STARTS) == 133
    return [
        [mt.untemper(int.from_bytes(packet[4 * lane:4 * lane + 4],
                                    "little")) for lane in range(4)]
        for packet in packets
    ]


def phase_equations(native, symbolic, phase):
    rows = []
    for record, position in enumerate(mt.STARTS):
        if record == 129:
            continue
        for lane in range(4):
            word = native[record][lane]
            rows.extend(
                (expression, (word >> bit) & 1)
                for bit, expression in enumerate(
                    symbolic[624 + phase + position + lane]
                )
            )
    assert len(rows) == 16896
    return rows


def phase_scan(native, symbolic, phase):
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, phase)
    )
    identified = {
        at: free for at in range(4, 624)
        if (free := source_dimension(
            coefficients[32 * index + bit]
            for index in (at - 2, at - 1, at)
            for bit in range(32)
        )) <= 9
    }
    sets = {}
    for at, free in identified.items():
        groups = source_group(coefficients, constants, at)
        assert len(groups) == 1 << free
        terms = {key_term(at, group) for group in groups}
        assert len(terms) == len(groups)
        sets[at] = terms
    pairs = list(combinations(identified, 2))
    disjoint = [(a, b) for a, b in pairs
                if not sets[a].intersection(sets[b])]
    excluded = {
        n for n in range(1, 624)
        if any((b - a) % n == 0 for a, b in disjoint)
    }
    return len(identified), len(pairs), len(disjoint), excluded, sets


def genuine_n24_control(symbolic, phase):
    seed = bytes((13 + 17 * i) & 255 for i in range(32))
    key = int.from_bytes(seed + hashlib.sha512(seed).digest(), "big")
    assert (key.bit_length() + 31) // 32 == 24
    rng = random.Random(seed)
    state = rng.getstate()[1][:624]
    assert state == random.Random(key).getstate()[1][:624]
    generated = [rng.getrandbits(32) for _ in range(phase + 974)]
    generated_native = [
        [mt.untemper(generated[phase + position + lane])
         for lane in range(4)]
        for position in mt.STARTS
    ]
    count, pairs, dcount, excluded, sets = phase_scan(
        generated_native, symbolic, phase
    )
    assert 24 not in excluded, (phase, count, dcount)
    matched_pairs = 0
    for a, b in combinations(sets, 2):
        if (b - a) % 24 == 0:
            true_a = key_term(a, tuple(state[a - 2:a + 1]))
            true_b = key_term(b, tuple(state[b - 2:b + 1]))
            assert true_a == true_b
            assert true_a in sets[a] & sets[b]
            matched_pairs += 1
    print("GENUINE_N24_PHASE_CONTROL=PASS", phase,
          "terms", count, "repeated_pairs", matched_pairs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True,
                        choices=range(16))
    args = parser.parse_args()
    begin = args.shard * 39
    end = begin + 39
    symbolic = words(OFFSET + 623)
    native = original_native()
    genuine_n24_control(symbolic, OFFSET + begin)
    outcomes = Counter()
    for k in range(begin, end):
        phase = OFFSET + k
        count, all_pairs, disjoint, excluded, sets = phase_scan(
            native, symbolic, phase
        )
        status = "EXCLUDED" if 24 in excluded else "OPEN"
        outcomes[status] += 1
        print(f"PHASESCAN shard={args.shard} k={k} prior={phase} "
              f"terms={count} pairs={all_pairs} disjoint={disjoint} "
              f"seed_lengths_excluded={len(excluded)} "
              f"n24={status} n32={'EXCLUDED' if 32 in excluded else 'OPEN'}",
              flush=True)
    assert sum(outcomes.values()) == 39
    print(f"SHARD_COMPLETE id={args.shard} covered={begin}..{end - 1} "
          f"n24_excluded={outcomes['EXCLUDED']} "
          f"n24_open={outcomes['OPEN']}")


if __name__ == "__main__":
    main()
