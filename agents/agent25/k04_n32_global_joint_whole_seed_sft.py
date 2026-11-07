"""Full shared-affine-state feasibility for printable 61–64-byte CPython seed.

Novel n32 extension of Agent 2's exact global-source joint feasibility
method. If the original 132 intact printer packets came from a CPython
Random(bytes) stream, this checks whether any single original source
state realizes all raw-seed ASCII chunks together, rather than choosing
a separate source state for each term. It also tests whether the
surviving words assemble enough bytes to construct a full K08 candidate.

The selected ACK2 packet is excluded by original_native() upstream.
No original K04/K08 acceptance values enter source inference.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent2"))
sys.path.insert(0, str(ROOT / "agents/agent25"))
sys.path.insert(0, str(ROOT / "agents/agent45"))
from k04_n35_n39_global_source_joint_feasible_sft import (
    analyze, genuine_control
)
from k04_source_n24_phase_sweep_sft import (
    OFFSET, words, original_native
)

OPEN = tuple(range(166, 202)) + tuple(range(310, 338))
N = 32


def seed_word_coverage(witnesses, length):
    # key16 is the final raw four bytes, key31 is the first raw 1..4.
    assembled = [None] * length
    for idx, rawhex, _ in witnesses:
        pad_start = 4 * (N - 1 - idx)
        raw = bytes.fromhex(rawhex)
        for j, byte in enumerate(raw):
            absolute = pad_start + j - (64 - length)
            if 0 <= absolute < length:
                assert assembled[absolute] in (None, chr(byte))
                assembled[absolute] = chr(byte)
    return "".join(ch if ch is not None else "?" for ch in assembled), sum(ch is not None for ch in assembled)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, choices=range(8), required=True)
    args = parser.parse_args()
    selected = OPEN[args.shard::8]
    assert len(selected) == 8
    symbolic = words(OFFSET + 623)
    # Positive controls are complete real CPython byte-seeded outputs, with
    # the synthetic selected row withheld under identical source geometry.
    genuine_control(symbolic, N, selected[0], 61)
    genuine_control(symbolic, N, selected[0], 64)
    native = original_native()
    totals = {length: {"local": 0, "joint": 0,
                       "complete_seed_strings": 0,
                       "joint_phases": []}
              for length in range(61, 65)}
    for k in selected:
        result = analyze(native, symbolic, N, k)
        for length, item in result["by_length"].items():
            if item["local_feasible"]:
                totals[length]["local"] += 1
            if item["joint_feasible"]:
                totals[length]["joint"] += 1
                totals[length]["joint_phases"].append(k)
                partial, known = seed_word_coverage(item["witness_words"], length)
                if known == length:
                    totals[length]["complete_seed_strings"] += 1
                    # Print complete original-source feasible bytes in UTF8,
                    # so a separate authentic K08 target gate can apply.
                    print("ORIGINAL_WHOLE_ASCII_SEED_CONSTRUCTION", length, k,
                          repr(partial), flush=True)
                else:
                    print("ORIGINAL_PARTIAL_JOINT_SEED_CONSTRUCTION", length, k,
                          "known_bytes", known, "seed", repr(partial),
                          "consistent_assignments", item["joint_assignments"],
                          flush=True)
            elif item["local_feasible"]:
                print("ORIGINAL_JOINT_ONLY_EXCLUSION", length, k,
                      "term_count", result["terms"],
                      "cross_source_relations",
                      result["cross_term_correlations"],
                      "component_counts", item["local_counts"],
                      "syndrome_count", item["dp_state_counts"][-1],
                      flush=True)
    print("N32_JOINT_SOURCE_SHARD_COMPLETE", args.shard,
          "original_phases", list(selected), "totals", totals, flush=True)


if __name__ == "__main__":
    main()
