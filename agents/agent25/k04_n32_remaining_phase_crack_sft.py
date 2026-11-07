"""N32 CPython true-startup crack at the 64 phases left open by Agent45.

Source-conditioned exact repeated-key term intersections. Selected printer
record 129 and all K04/K08 acceptance commitments are omitted. The original
printer source and candidate are read-only.

The 32-word CPython integer key length is also the expansion length for
64-byte bytes input under Random(bytes, version=2). This seed type is a
hypothesis and not an established printer/keeper link.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent45"))
from k04_source_n24_phase_sweep_sft import (
    OFFSET, mt, words, original_native, phase_equations,
    reduce_source, source_dimension, key_term,
)

OPEN = tuple(range(166, 202)) + tuple(range(310, 338))
MAX_FREE = 17
N = 32


def candidate_ranks(coefficients: list[int]) -> dict[int, int]:
    ranks = {}
    for at in range(4, 624):
        ranks[at] = source_dimension(
            coefficients[32 * index + bit]
            for index in (at - 2, at - 1, at)
            for bit in range(32)
        )
    return ranks


def all_pairs(ranks: dict[int, int]):
    classes: dict[int, list[int]] = defaultdict(list)
    for at in ranks:
        classes[at % N].append(at)
    items = []
    for cls in classes.values():
        for i, a in enumerate(cls):
            for b in cls[i + 1:]:
                x, y = ranks[a], ranks[b]
                items.append((max(x, y), x + y, a, b))
    return sorted(items)


def exact_term_set(coefficients: list[int], constants: list[int], at: int,
                   expected_free: int) -> set[int]:
    assert expected_free <= MAX_FREE
    indices = [32 * index + bit
               for index in (at - 2, at - 1, at)
               for bit in range(32)]
    value = sum(constants[index] << bit for bit, index in enumerate(indices))
    projection: dict[int, int] = {}
    for bit, index in enumerate(indices):
        expr = coefficients[index]
        while expr:
            lowbit = expr & -expr
            free = lowbit.bit_length() - 1
            projection[free] = projection.get(free, 0) | (1 << bit)
            expr ^= lowbit
    basis: dict[int, int] = {}
    for expr in projection.values():
        while expr:
            pivot = expr.bit_length() - 1
            old = basis.get(pivot)
            if old is None:
                basis[pivot] = expr
                break
            expr ^= old
    assert len(basis) == expected_free
    domains = [value]
    for direction in basis.values():
        domains += [old ^ direction for old in domains]
    assert len(domains) == 1 << expected_free
    terms = set()
    for blob in domains:
        triple = tuple((blob >> (lane * 32)) & 0xFFFFFFFF
                       for lane in range(3))
        terms.add(key_term(at, triple))
    return terms


def examine(native, symbolic, k: int, is_control: bool):
    phase = OFFSET + k
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, phase)
    )
    ranks = candidate_ranks(coefficients)
    pairs = all_pairs(ranks)
    assert pairs
    best = pairs[0]
    term_cache: dict[int, set[int]] = {}
    inspected = 0
    exhausted = True
    witness = None
    for max_free, sum_free, a, b in pairs:
        if max_free > MAX_FREE:
            exhausted = False
            break
        # Repeated term labels for positions a and b are necessary for n32.
        if a not in term_cache:
            term_cache[a] = exact_term_set(coefficients, constants, a, ranks[a])
        if b not in term_cache:
            term_cache[b] = exact_term_set(coefficients, constants, b, ranks[b])
        inspected += 1
        intersection = term_cache[a] & term_cache[b]
        if is_control:
            # Exact true seeded CPython register term must survive.
            if not intersection:
                raise AssertionError(("true seeded control disjoint", k, a, b))
            if inspected >= 12:
                break
        elif not intersection:
            witness = (a, b, ranks[a], ranks[b],
                       len(term_cache[a]), len(term_cache[b]))
            break
    if is_control:
        assert inspected > 0, ("no inexpensive positive pairs", k, best)
        return {"control": "PASS", "phase": k, "pairs": inspected,
                "best_pair": best, "terms_computed": len(term_cache)}
    return {"phase": k, "best_pair": best,
            "n32": "EXCLUDED" if witness else "OPEN",
            "witness": witness, "pairs_checked": inspected,
            "pair_scan_exhausted_under_cap": exhausted,
            "terms_computed": len(term_cache)}


def planted_native(phase: int):
    seed = bytes((11 + 19 * i) & 255 for i in range(64))
    extended = int.from_bytes(seed + hashlib.sha512(seed).digest(), "big")
    assert (extended.bit_length() + 31) // 32 == 32
    generator = random.Random(seed)
    assert generator.getstate()[1][:624] == random.Random(extended).getstate()[1][:624]
    output = [generator.getrandbits(32)
              for _ in range(phase + mt.STARTS[-1] + 4)]
    return [[mt.untemper(output[phase + pos + lane])
             for lane in range(4)]
            for pos in mt.STARTS]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shard", type=int, choices=range(8), required=True)
    args = p.parse_args()
    selected = OPEN[args.shard * 8:(args.shard + 1) * 8]
    assert len(selected) == 8
    symbolic = words(OFFSET + 623)
    raw_native = original_native()
    print("GENUINE_N32_POSITIVE", examine(
        planted_native(OFFSET + selected[0]), symbolic, selected[0], True
    ), flush=True)
    statuses = []
    for k in selected:
        result = examine(raw_native, symbolic, k, False)
        statuses.append(result["n32"])
        print("ORIGINAL_N32_PHASE", result, flush=True)
    print("SHARD_COMPLETE", args.shard, "phases", list(selected),
          "excluded", statuses.count("EXCLUDED"),
          "open", statuses.count("OPEN"), flush=True)


if __name__ == "__main__":
    main()
