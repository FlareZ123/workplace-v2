"""Exact K04->K08 CPython direct phrase-seed n40 source gate (read only).

Hypothesis: Emily's 93..96-byte normalized final caption seeded CPython
Random(bytes, version=2) producing the intact historical printer stream.
Unverified p951 producer chronology; selected PS-0417 is withheld from input.

Run sharded only when testing this distinct as-yet-open source construction.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent25"))

from k04_n35_n39_caption_source_sft import (
    NORMALIZED, OFFSET, PRINTABLE, genuine_control, original_native,
    seed_alphabet_support, source_term_domains, words,
)

N = 40
PHASES = 624
SHARDS = 16


def source_gate(native, symbolic, phase):
    terms = source_term_domains(native, symbolic, phase, N)
    indexed = {}
    for at, (key_index, free, values) in terms.items():
        if key_index in indexed:
            indexed[key_index].intersection_update(values)
        else:
            indexed[key_index] = set(values)
    if any(not domain for domain in indexed.values()):
        return terms, indexed, {}, True
    lengths = {}
    for length in (93, 94, 95, 96):
        lengths[length] = {}
        for name, alphabet in (("normalized", NORMALIZED), ("printable", PRINTABLE)):
            accepted = {
                i: tuple(x for x in values if seed_alphabet_support(
                    x, N, length, i, alphabet
                ))
                for i, values in indexed.items()
            }
            lengths[length][name] = all(accepted.values())
        if lengths[length]["normalized"]:
            witnesses = {
                i: [f"{x:08X}" for x in values if seed_alphabet_support(
                    x, N, length, i, NORMALIZED
                )][:4]
                for i, values in indexed.items()
            }
            print("N40_NORMALIZED_SOURCE_SURVIVOR", json.dumps({
                "phase": phase, "length": length, "known_positions": len(witnesses),
                "partial_source_words": witnesses,
            }, sort_keys=True), flush=True)
    return terms, indexed, lengths, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, choices=range(SHARDS), required=True)
    args = parser.parse_args()
    start = args.shard * (PHASES // SHARDS)
    stop = start + PHASES // SHARDS
    symbolic = words(OFFSET + 623)
    original = original_native()
    genuine_control(symbolic, N, start, 93)
    genuine_control(symbolic, N, start, 96)
    counts = {
        str(length): {"normalized": 0, "printable": 0}
        for length in (93, 94, 95, 96)
    }
    repeated_closed = 0
    for k in range(start, stop):
        terms, indexed, lengths, excluded = source_gate(original, symbolic, k)
        if excluded:
            repeated_closed += 1
        else:
            for length, alphabet_result in lengths.items():
                for alphabet, allowed in alphabet_result.items():
                    counts[str(length)][alphabet] += int(allowed)
        print("N40_PHASE", json.dumps({
            "phase": k, "terms": len(terms), "distinct_key_indices": len(indexed),
            "repeated_index_disjoint": excluded,
            "normalized_open": [
                length for length in lengths if lengths[length]["normalized"]
            ],
            "printable_open": [
                length for length in lengths if lengths[length]["printable"]
            ],
        }, sort_keys=True), flush=True)
    print("N40_SHARD_COMPLETE", json.dumps({
        "shard": args.shard, "start": start, "stop_exclusive": stop,
        "phases": stop - start, "repeated_index_disjoint": repeated_closed,
        "survivors": counts, "genuine_seed_controls": 2,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
