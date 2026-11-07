"""K04-to-K08 ASCII seed carrier crack across the 64 n32-open true MT phases.

The previously genuine-CPython-source-compatible n32 64 starting phases
have at least one source-identifiable T_i term of small full 96-bit domain.
For a 61..64-byte CPython bytes/str seed (64-byte SHA512 appended), the
key word for every key index 16..31 is literally four bytes of the raw
input. This gives a source-first necessary constraint on the complete
candidate phrase as a printer seed.

The real archive does NOT attest the printer used such a seed, or that
Emily's caption was its seed. This is a conditional source-linked hypothesis.
Selected original spool row129, its copied payload, K04 acceptance, K08
acceptance and desk nonce are withheld from inference.
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
    reduce_source, source_dimension, source_group, key_term,
)

OPEN = tuple(range(166, 202)) + tuple(range(310, 338))
U = 0xFFFFFFFF
PRINTABLE = frozenset(range(0x20, 0x7f))
NORMALIZED = frozenset(b"abcdefghijklmnopqrstuvwxyz0123456789 ")


def source_ranks(coefficients: list[int]) -> dict[int, int]:
    return {
        at: source_dimension(coefficients[32 * i + bit]
                             for i in (at - 2, at - 1, at)
                             for bit in range(32))
        for at in range(4, 624)
    }


def smallest_repeated_pair(ranks: dict[int, int]) -> tuple[int, int, int, int]:
    classes: dict[int, list[int]] = defaultdict(list)
    for at in ranks:
        classes[at % 32].append(at)
    pairs = ((max(ranks[a], ranks[b]), ranks[a] + ranks[b], a, b)
             for group in classes.values()
             for ix, a in enumerate(group)
             for b in group[ix + 1:])
    return min(pairs)


def rawkey_allowed(word: int, key_index: int, length: int,
                   alphabet: frozenset[int]) -> bool:
    assert 16 <= key_index <= 31
    assert 61 <= length <= 64
    chunk = word.to_bytes(4, "big")
    if key_index == 31:
        pad = 64 - length
        return chunk[:pad] == bytes(pad) and all(
            char in alphabet for char in chunk[pad:]
        )
    return all(char in alphabet for char in chunk)


def n32_source_term_constraints(native, symbolic, k: int):
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, OFFSET + k)
    )
    ranks = source_ranks(coefficients)
    observed = {}
    for at, free in ranks.items():
        if free > 9:
            continue
        key_index = (at - 1) % 32
        if key_index < 16:
            continue
        groups = source_group(coefficients, constants, at)
        assert len(groups) == 1 << free
        terms = {((key_term(at, triple) - key_index) & U)
                 for triple in groups}
        observed[at] = (key_index, free, terms)
    return observed, smallest_repeated_pair(ranks)


def original_one_phase(native, symbolic, k: int) -> dict:
    observed, best = n32_source_term_constraints(native, symbolic, k)
    assert observed, (k, "no raw-key source triples")
    summary = {}
    for alphabet_name, alphabet in (("printable", PRINTABLE),
                                    ("normalized", NORMALIZED)):
        by_length = {}
        for length in (61, 62, 63, 64):
            rejected = []
            surviving_terms = []
            for at, (idx, free, terms) in observed.items():
                raw_candidates = [word for word in terms
                                  if rawkey_allowed(word, idx, length, alphabet)]
                if not raw_candidates:
                    rejected.append((at, idx, free, len(terms)))
                else:
                    surviving_terms.append((at, idx, free, len(raw_candidates)))
            by_length[str(length)] = {
                "compatible": not rejected,
                "first_zero_rawword_witness": rejected[0] if rejected else None,
                "falsifying_term_count": len(rejected),
                "passing_term_count": len(surviving_terms),
                "example_printable_rawwords": [
                    {"at": at, "key_index": idx, "word_count": size}
                    for at, idx, _, size in surviving_terms[:3]
                ]
            }
        summary[alphabet_name] = by_length
    return {"k": k, "prior_output_phase": OFFSET + k,
            "source_identified_rawkey_terms": len(observed),
            "min_same-key_triple_pair_rank": best,
            "source_ascii_seed_length_gate": summary}


def genuine_control(symbolic, k: int, length: int) -> None:
    seed = (b"the late watch leaves room at the table and the sea beyond "
            b"the windows ")[:length]
    assert len(seed) == length and all(byte in PRINTABLE for byte in seed)
    key = int.from_bytes(seed + hashlib.sha512(seed).digest(), "big")
    assert (key.bit_length() + 31) // 32 == 32
    generator = random.Random(seed)
    state = random.Random(key).getstate()[1][:624]
    assert generator.getstate()[1][:624] == state
    raw = [generator.getrandbits(32)
           for _ in range(OFFSET + k + mt.STARTS[-1] + 4)]
    synthetic_native = [
        [mt.untemper(raw[OFFSET + k + start + lane])
         for lane in range(4)]
        for start in mt.STARTS
    ]
    observed, best = n32_source_term_constraints(synthetic_native, symbolic, k)
    assert observed
    for at, (idx, _, terms) in observed.items():
        true_word = (key >> (32 * idx)) & U
        assert true_word in terms, (k, length, at, idx)
        assert rawkey_allowed(true_word, idx, length, PRINTABLE)
    print("GENUINE_N32_ASCII_SOURCE_CONTROL=PASS", k, length,
          "exact_rawkey_domains", len(observed), "minpair", best,
          flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shard", type=int, required=True, choices=range(8))
    args = p.parse_args()
    selected = OPEN[args.shard * 8:(args.shard + 1) * 8]
    assert len(selected) == 8
    symbolic = words(OFFSET + 623)
    original = original_native()
    genuine_control(symbolic, selected[0], 64)
    genuine_control(symbolic, selected[0], 61)
    viable = {name: {length: [] for length in ("61", "62", "63", "64")}
              for name in ("printable", "normalized")}
    for k in selected:
        result = original_one_phase(original, symbolic, k)
        for alphabet, lengths in viable.items():
            for length, phases in lengths.items():
                if result["source_ascii_seed_length_gate"][alphabet][length]["compatible"]:
                    phases.append(k)
        print("ORIGINAL_N32_ASCII_PHASE", result, flush=True)
    print("SHARD_COMPLETE", args.shard, "phases", list(selected),
          "surviving_source_role_models", viable, flush=True)


if __name__ == "__main__":
    main()
