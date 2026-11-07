"""K04 printer-to-K08 literal-seed crib, generalized to untested CPython n35/n39.

Do not run against phase sets already rejected by Agent45's separate repeated
T-term disjointness test. This checker reads original printer payloads only
from the 132 intact rows; disputes selected row129 before source inference.

Usage:
    python agents/agent25/k04_n35_n39_caption_source_sft.py --n 31 --phases 1,2,3

Phase k means exactly 2496+k genuinely prior CPython outputs. For a byte seed
length L, n=ceil((L+64)/4), using integer seed bytes || SHA512(bytes). Key
word index>=16 is an exact four-byte raw-input carrier. Source-identified
firstpass T_i domains are exact and exhaustive only if the 96-bit source
triple dimension <=9. Missing terms add no exclusions.

Historical printer engine, p951 geometry, actual seed and selected coupon
remain unproven and no K04/K08 target hash is read.
"""
from __future__ import annotations

import argparse
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

NORMALIZED = frozenset(b"abcdefghijklmnopqrstuvwxyz0123456789 ")
PRINTABLE = frozenset(range(0x20, 0x7f))
U = 0xffffffff


def seed_alphabet_support(raw_word: int, n: int, length: int, key_index: int,
                          alphabet: frozenset[int]) -> bool:
    assert 16 <= key_index < n
    assert 4 * (n - 1) - 64 < length <= 4 * n - 64
    pad = 4 * n - 64 - length if key_index == n - 1 else 0
    data = raw_word.to_bytes(4, "big")
    return data[:pad] == bytes(pad) and all(char in alphabet for char in data[pad:])


def source_term_domains(native, symbolic, k: int, n: int):
    coefficients, constants = reduce_source(
        phase_equations(native, symbolic, OFFSET + k)
    )
    found = {}
    for at in range(4, 624):
        key_index = (at - 1) % n
        if key_index < 16:
            continue
        free = source_dimension(coefficients[32 * index + bit]
                                for index in (at - 2, at - 1, at)
                                for bit in range(32))
        if free > 9:
            continue
        groups = source_group(coefficients, constants, at)
        assert len(groups) == 1 << free
        values = {((key_term(at, triple) - key_index) & U)
                  for triple in groups}
        found[at] = (key_index, free, values)
    return found


def genuine_control(symbolic, n: int, k: int, length: int):
    words_seed = b"the late watch leaves room at the table and the sea beyond the windows "
    seed = (words_seed * ((length + len(words_seed)) // len(words_seed)))[:length]
    assert len(seed) == length and all(c in NORMALIZED for c in seed)
    expanded = int.from_bytes(seed + hashlib.sha512(seed).digest(), "big")
    assert (expanded.bit_length() + 31) // 32 == n
    rng = random.Random(seed)
    assert rng.getstate()[1][:624] == random.Random(expanded).getstate()[1][:624]
    out = [rng.getrandbits(32) for _ in range(OFFSET + k + mt.STARTS[-1] + 4)]
    native = [[mt.untemper(out[OFFSET + k + start + lane])
               for lane in range(4)]
              for start in mt.STARTS]
    observed = source_term_domains(native, symbolic, k, n)
    assert observed, ("synthetic test has zero source terms", n, k)
    for at, (idx, free, values) in observed.items():
        trueword = (expanded >> (32 * idx)) & U
        assert trueword in values, (n, k, length, at, idx, free)
        assert seed_alphabet_support(trueword, n, length, idx, NORMALIZED)
    print("GENUINE_CPYTHON_N_SOURCE_ASCII_CONTROL=PASS", n, k, length,
          "observed_raw_words", len(observed), flush=True)


def source_phase(original, symbolic, n: int, k: int):
    terms = source_term_domains(original, symbolic, k, n)
    result = {}
    for length in range(4 * (n - 1) - 64 + 1, 4 * n - 64 + 1):
        length_result = {}
        for tag, alphabet in (("normalized", NORMALIZED),
                              ("printable", PRINTABLE)):
            failures = []
            compatible_terms = 0
            for at, (key_index, free, domain) in terms.items():
                passing = sum(seed_alphabet_support(
                    x, n, length, key_index, alphabet
                ) for x in domain)
                if passing == 0:
                    failures.append((at, key_index, free))
                else:
                    compatible_terms += 1
            length_result[tag] = {
                "necessary_source_compatible": not failures,
                "source_falsifying_term_count": len(failures),
                "first_falsifying_term": failures[0] if failures else None,
                "source_compatible_term_count": compatible_terms
            }
        result[str(length)] = length_result
    return {"n": n, "k": k, "prior_draws": OFFSET + k,
            "identified_rawkey_source_terms": len(terms),
            "lengths": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True, choices=(35, 39))
    parser.add_argument("--phases", required=False,
                        help="comma-separated known n-specific OPEN k from Agent45")
    parser.add_argument("--shard", type=int, choices=range(8))
    args = parser.parse_args()
    if args.phases:
        phases = tuple(int(s) for s in args.phases.split(",") if s.strip())
    else:
        assert args.shard is not None
        prior_open = tuple(range(504, 624)) if args.n == 35 else tuple(range(309, 338))
        phases = prior_open[args.shard::8]
    assert phases and len(set(phases)) == len(phases)
    assert all(0 <= k < 624 for k in phases)
    n = args.n
    symbolic = words(OFFSET + 623)
    genuine_control(symbolic, n, phases[0], 4 * n - 64)
    genuine_control(symbolic, n, phases[0], 4 * (n - 1) - 64 + 1)
    original = original_native()
    summary = {str(length): {"normalized": [], "printable": []}
               for length in range(4 * (n - 1) - 64 + 1, 4 * n - 64 + 1)}
    for k in phases:
        result = source_phase(original, symbolic, n, k)
        print("ORIGINAL_N_ASCII_SOURCE", result, flush=True)
        for length, tags in result["lengths"].items():
            for tag, value in tags.items():
                if value["necessary_source_compatible"]:
                    summary[length][tag].append(k)
    print("PHASE_SET_COMPLETE", n, "tested", len(phases),
          "phase_ids", phases, "source_surviving_phases", summary, flush=True)


if __name__ == "__main__":
    main()
