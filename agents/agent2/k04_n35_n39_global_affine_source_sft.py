"""Original K04/K08 joint-source affine correlation of literal printer key words.

This examines n35/n39 residual broad-printable raw-caption seed phases under
hypothetical p951 + genuine CPython Random(bytes, version=2). All original
nonselected printer packets are used, selected row129 is excluded, target
commitments are never consulted. Tests whether source-derived printable
constraints on *distinct* seed words share hidden MT-state variables.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent25"))
from k04_n35_n39_caption_source_sft import (
    OFFSET, PRINTABLE, U, mt, words, original_native,
    source_group, key_term, reduce_source, phase_equations, source_dimension,
    seed_alphabet_support,
)


def affine_projection(coefficients: list[int], terms: dict) -> tuple[int, int, int]:
    direction_columns = defaultdict(int)
    local_rank_sum = 0
    for number, (at, (_, free, _)) in enumerate(terms.items()):
        local_rank_sum += free
        for local_bit, index in enumerate(
            32 * word + bit
            for word in (at - 2, at - 1, at)
            for bit in range(32)
        ):
            expression = coefficients[index]
            while expression:
                lowest = expression & -expression
                source_index = lowest.bit_length() - 1
                direction_columns[source_index] |= (
                    1 << (number * 96 + local_bit)
                )
                expression ^= lowest
    rank = source_dimension(direction_columns.values())
    return local_rank_sum, rank, len(direction_columns)


def phase_analysis(native, symbolic, n: int, k: int):
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, OFFSET + k))
    terms = {}
    for at in range(4, 624):
        idx = (at - 1) % n
        if idx < 16:
            continue
        indices = [32 * word + bit
                   for word in (at - 2, at - 1, at)
                   for bit in range(32)]
        free = source_dimension(coefficients[index] for index in indices)
        if free > 9:
            continue
        groups = source_group(coefficients, constants, at)
        assert len(groups) == 1 << free
        values = {((key_term(at, triple) - idx) & U) for triple in groups}
        assert len(values) == len(groups)
        terms[at] = (idx, free, values)
    lengths = range(4 * (n - 1) - 63, 4 * n - 63)
    survives = []
    for length in lengths:
        if all(any(seed_alphabet_support(value, n, length, idx, PRINTABLE)
                   for value in values)
               for idx, _, values in terms.values()):
            survives.append(length)
    if not survives:
        return {"k": k, "term_count": len(terms), "lengths": []}
    localrank, joint, source_variables = affine_projection(coefficients, terms)
    assert joint <= localrank
    return {"k": k, "term_count": len(terms), "lengths": survives,
            "local_dim_sum": localrank, "joint_dim": joint,
            "source_correlation_dim": localrank - joint,
            "global_free_source_variables": source_variables,
            "at_idx": [[at, idx, free] for at, (idx, free, _) in terms.items()]}


def genuine_control(symbolic, n: int, k: int, length: int):
    raw = (b"After the late watch, there is still room by the window for "
           b"one more cup, and a little light across the sea. " * 3)[:length]
    key = int.from_bytes(raw + hashlib.sha512(raw).digest(), "big")
    assert (key.bit_length() + 31) // 32 == n
    rng = random.Random(raw)
    samples = [rng.getrandbits(32)
               for _ in range(OFFSET + k + mt.STARTS[-1] + 4)]
    synthetic = [[mt.untemper(samples[OFFSET + k + pos + lane])
                  for lane in range(4)]
                 for pos in mt.STARTS]
    result = phase_analysis(synthetic, symbolic, n, k)
    assert length in result["lengths"], (n, k, length, result)
    print("GENUINE_AFFINE_RAWSEED_CONTROL_PASS", n, k, length,
          "terms", result["term_count"],
          "local_vs_joint", (result["local_dim_sum"],result["joint_dim"]),
          flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True, choices=(35, 39))
    parser.add_argument("--shard", type=int, required=True, choices=range(8))
    args = parser.parse_args()
    n = args.n
    phases = (tuple(range(504, 624)) if n == 35
              else tuple(range(309, 338)))[args.shard::8]
    symbolic = words(OFFSET + 623)
    genuine_control(symbolic, n, phases[0], 4*n-64)
    genuine_control(symbolic, n, phases[0], 4*(n-1)-63)
    native = original_native()
    results = []
    for k in phases:
        row = phase_analysis(native, symbolic, n, k)
        if row["lengths"]:
            results.append(row)
            print("ORIGINAL_GLOBAL_AFFINE_PRINTABLE", n, row, flush=True)
    print("AFFINE_SHARD_COMPLETE", n, args.shard, "phases", list(phases),
          "survivors", len(results),
          "correlated", sum(x["source_correlation_dim"] > 0 for x in results),
          "all_independent", all(x["source_correlation_dim"] == 0 for x in results),
          flush=True)


if __name__ == "__main__":
    main()
