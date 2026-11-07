"""Joint raw-caption word exclusion for open n35/n39 CPython source phases.

Original K04 selected row129 is entirely omitted by the pinned Agent45 source
loader. This is a model-conditional necessary test for a CPython version-2
printer seeded directly by a 73..76 or 89..92 byte *printable* raw caption.
It enforces same-key-word equality across all enumerated original source
terms, unlike independent ASCII term checks. No target hashes are read.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent25"))
from k04_n35_n39_caption_source_sft import (
    OFFSET, PRINTABLE, U, mt, original_native, seed_alphabet_support,
    source_term_domains, words,
)


def common_words(terms: dict, n: int, length: int) -> tuple[bool, bool, dict]:
    grouped = defaultdict(list)
    singleton_ok = True
    for at, (idx, free, values) in terms.items():
        allowed = {value for value in values
                   if seed_alphabet_support(value, n, length, idx, PRINTABLE)}
        if not allowed:
            singleton_ok = False
        grouped[idx].append((at, allowed))
    intersections = {}
    for idx, observations in grouped.items():
        common = set(observations[0][1])
        for _, values in observations[1:]:
            common.intersection_update(values)
        intersections[idx] = common
    repeat_ok = singleton_ok and all(intersections.values())
    sizes = {idx: len(values) for idx, values in intersections.items()}
    return singleton_ok, repeat_ok, sizes


def planted_control(symbolic, n: int, k: int, length: int) -> None:
    raw = (b"After the late watch, there is still room by the window for "
           b"one more cup, and a little light across the sea. " * 3)[:length]
    assert len(raw) == length and all(v in PRINTABLE for v in raw)
    value = int.from_bytes(raw + hashlib.sha512(raw).digest(), "big")
    assert (value.bit_length() + 31) // 32 == n
    rng = random.Random(raw)
    draws = [rng.getrandbits(32)
             for _ in range(OFFSET + k + mt.STARTS[-1] + 4)]
    native = [[mt.untemper(draws[OFFSET + k + start + lane])
               for lane in range(4)] for start in mt.STARTS]
    terms = source_term_domains(native, symbolic, k, n)
    assert terms, "positive source generated zero usable constraints"
    singleton, joint, sizes = common_words(terms, n, length)
    assert singleton and joint, (n, k, length, sizes)
    for at, (idx, _, domain) in terms.items():
        true_word = (value >> (32 * idx)) & U
        assert true_word in domain, (n, k, length, at)
        assert true_word in set.intersection(
            *(set(v for v in term_values
                   if seed_alphabet_support(v, n, length, idx, PRINTABLE))
              for _, (key_idx, _, term_values) in terms.items()
              if key_idx == idx)), (n, k, length, at)
    print("GENUINE_JOINT_PRINTABLE_CONTROL=PASS", n, k, length,
          "term_count", len(terms), "distinct_key_indices", len(sizes), flush=True)


def run(n: int, shard: int) -> None:
    open_phases = tuple(range(504, 624)) if n == 35 else tuple(range(309, 338))
    phases = open_phases[shard::8]
    assert phases
    symbolic = words(OFFSET + 623)
    planted_control(symbolic, n, phases[0], 4 * n - 64)
    planted_control(symbolic, n, phases[0], 4 * (n - 1) - 64 + 1)
    native = original_native()
    totals = {length: dict(terms=0, joint=0, extra=0, survivors=[])
              for length in range(4 * (n - 1) - 63, 4 * n - 63)}
    for k in phases:
        terms = source_term_domains(native, symbolic, k, n)
        for length, row in totals.items():
            per_term, joined, sizes = common_words(terms, n, length)
            row["terms"] += int(per_term)
            row["joint"] += int(joined)
            row["extra"] += int(per_term and not joined)
            if joined:
                row["survivors"].append(k)
            if per_term and not joined:
                print("NEW_JOINT_SOURCE_REJECTION", n, k, length,
                      "distinct_key_indices", len(sizes),
                      "empty_indices", [idx for idx, size in sizes.items()
                                       if not size], flush=True)
    print("JOINT_PHASE_SHARD_COMPLETE", n, shard, "phases", list(phases),
          "length_counts", totals, flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", required=True, type=int, choices=(35, 39))
    p.add_argument("--shard", required=True, type=int, choices=range(8))
    args = p.parse_args()
    run(args.n, args.shard)


if __name__ == "__main__":
    main()
