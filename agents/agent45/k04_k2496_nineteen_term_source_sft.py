"""Exact original-source CPython 19-term integer-seed exclusion, p951/k2496.

Read-only original 132 printer records; selected row129 withheld.
Usage: python agents/agent45/k04_k2496_nineteen_term_source_sft.py
The printer chronology and 2496 genuine prior draws are hypothetical.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import hashlib
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent23"))
from k04_cpython_k2496_n3_worddomain_sft import (
    OFFSET, U, mt, words, original_packets, source_rows
)

G = [19650218]
for i in range(1, 624):
    G.append((1812433253 * (G[-1] ^ (G[-1] >> 30)) + i) & U)

EXPECTED = {
    4: 9, 8: 3, 9: 6, 10: 9, 18: 8, 29: 9, 85: 8,
    120: 9, 145: 9, 172: 5, 173: 8, 256: 8,
    314: 6, 315: 9, 458: 7, 569: 7, 575: 7,
    594: 7, 607: 6,
}
PRIOR_SIX_TERM_EXCLUSIONS = {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 19, 20, 21, 25
}


def reduce_source(source):
    basis = {}
    for expression, rhs in source:
        while expression:
            pivot = expression.bit_length() - 1
            prev = basis.get(pivot)
            if prev is None:
                basis[pivot] = (expression, rhs)
                break
            expression ^= prev[0]
            rhs ^= prev[1]
        else:
            assert rhs == 0
    assert len(basis) == 15365, len(basis)
    pivot_mask = sum(1 << pivot for pivot in basis)
    reduced = {}
    for pivot in sorted(basis):
        expression, rhs = basis[pivot]
        lower = expression & pivot_mask & ((1 << pivot) - 1)
        while lower:
            prior_pivot = lower.bit_length() - 1
            prior_bits, prior_rhs = reduced[prior_pivot]
            expression ^= (1 << prior_pivot) ^ prior_bits
            rhs ^= prior_rhs
            lower = expression & pivot_mask & ((1 << pivot) - 1)
        assert expression & (pivot_mask ^ (1 << pivot)) == 1 << pivot
        reduced[pivot] = (expression ^ (1 << pivot), rhs)
    coefficients = [
        reduced[bit][0] if bit in reduced else (1 << bit)
        for bit in range(624 * 32)
    ]
    constants = [
        reduced[bit][1] if bit in reduced else 0
        for bit in range(624 * 32)
    ]
    return coefficients, constants


def source_dimension(vectors):
    basis = {}
    for expression in vectors:
        while expression:
            pivot = expression.bit_length() - 1
            prev = basis.get(pivot)
            if prev is None:
                basis[pivot] = expression
                break
            expression ^= prev
    return len(basis)


def source_group(coefficients, constants, at):
    indices = [32 * i + b for i in (at - 2, at - 1, at)
               for b in range(32)]
    value = sum(constants[index] << bit
                for bit, index in enumerate(indices))
    projection = {}
    for bit, index in enumerate(indices):
        expression = coefficients[index]
        while expression:
            lowbit = expression & -expression
            free_variable = lowbit.bit_length() - 1
            projection[free_variable] = (
                projection.get(free_variable, 0) | (1 << bit)
            )
            expression ^= lowbit
    basis = {}
    for expression in projection.values():
        while expression:
            pivot = expression.bit_length() - 1
            prev = basis.get(pivot)
            if prev is None:
                basis[pivot] = expression
                break
            expression ^= prev
    assert len(basis) == source_dimension(coefficients[i] for i in indices)
    assert len(basis) <= 9, (at, len(basis))
    domains = [value]
    for direction in basis.values():
        domains.extend(old ^ direction for old in list(domains))
    assert len(domains) == len(set(domains))
    return [
        tuple((v >> (32 * lane)) & U for lane in range(3))
        for v in domains
    ]


def key_term(at, triple):
    earlier, previous, current = triple
    a_previous = ((previous + at - 1) & U) ^ (
        1566083941 * (earlier ^ (earlier >> 30)) & U
    )
    a_current = ((current + at) & U) ^ (
        1566083941 * (previous ^ (previous >> 30)) & U
    )
    return (a_current - (
        G[at] ^ (1664525 * (a_previous ^ (a_previous >> 30)) & U)
    )) & U


def termsets_from_source(source, symbolic, identified):
    coefficients, constants = reduce_source(source)
    termsets = {}
    for at in identified:
        groups = source_group(coefficients, constants, at)
        assert len(groups) == 1 << EXPECTED[at]
        values = {key_term(at, group) for group in groups}
        assert len(values) == len(groups), (at, len(groups), len(values))
        termsets[at] = values
    return termsets


def real_python_control(symbolic):
    # 32 original bytes + 64 SHA512 appended bytes -> 24 little-endian
    # uint32 key words in CPython Random(bytes, version=2).
    seed = bytes((13 + 17 * i) & 255 for i in range(32))
    extended = int.from_bytes(seed + hashlib.sha512(seed).digest(), "big")
    assert (extended.bit_length() + 31) // 32 == 24
    generator = random.Random(seed)
    state = generator.getstate()[1][:624]
    assert state == random.Random(extended).getstate()[1][:624]
    draws = [generator.getrandbits(32) for _ in range(OFFSET + 974)]
    packets = [
        b"".join(
            draws[OFFSET + position + lane].to_bytes(4, "little")
            for lane in range(4)
        ) for position in mt.STARTS
    ]
    controls = termsets_from_source(source_rows(packets, symbolic),
                                   symbolic, EXPECTED)
    actual = {
        at: key_term(at, tuple(state[at - 2:at + 1]))
        for at in EXPECTED
    }
    assert all(actual[at] in values for at, values in controls.items())
    assert actual[4] == actual[172]
    assert actual[4] in (controls[4] & controls[172])
    pair_witnesses = 0
    for a, b in combinations(EXPECTED, 2):
        if (b - a) % 24 == 0:
            assert actual[a] == actual[b]
            assert actual[a] in controls[a] & controls[b]
            pair_witnesses += 1
    assert pair_witnesses > 0
    print("GENUINE_CPYTHON_BYTES32_N24_FULL_SELECTED_WITHHELD=PASS")
    print("GENUINE_19_TRIPLE_SOURCE_DOMAIN_WITNESSES=19/19 PASS")
    print("GENUINE_N24_REPEATED_TERM_PAIRS", pair_witnesses)


def original(symbolic):
    source = source_rows(original_packets(), symbolic)
    coefficients, constants = reduce_source(source)
    detected = {
        at: source_dimension(
            coefficients[32 * word + bit]
            for word in (at - 2, at - 1, at)
            for bit in range(32)
        )
        for at in range(4, 624)
    }
    identified = {
        at: free for at, free in detected.items() if free <= 9
    }
    assert identified == EXPECTED, identified
    terms = {}
    for at in EXPECTED:
        groups = source_group(coefficients, constants, at)
        values = {key_term(at, group) for group in groups}
        assert len(groups) == len(values) == 1 << EXPECTED[at]
        terms[at] = values
    all_pairs = list(combinations(EXPECTED, 2))
    assert len(all_pairs) == 171
    nonempty = [(a, b) for a, b in all_pairs if terms[a] & terms[b]]
    assert not nonempty, nonempty
    excluded = {
        n for n in range(1, 624)
        if any((b - a) % n == 0 for a, b in all_pairs)
    }
    assert len(excluded) == 249, len(excluded)
    assert set(range(1, 69)) <= excluded
    assert PRIOR_SIX_TERM_EXCLUSIONS <= excluded
    assert len(excluded - PRIOR_SIX_TERM_EXCLUSIONS) == 233
    print("ORIGINAL_PRINTER_ROW129_EXCLUDED_RANK=15365")
    print("ORIGINAL_19_FIRSTPASS_TERMS", ",".join(
        f"T{at}:{len(terms[at])}" for at in EXPECTED))
    print("ORIGINAL_ALL_171_PAIRWISE_TERM_INTERSECTIONS_EMPTY=PASS")
    print("ORIGINAL_INTEGER_KEY_LENGTHS_1_TO_623_EXCLUDED=249")
    print("NEW_BEYOND_PRIOR_SIX_TERM_SIEVE=233")
    print("CONTIGUOUS_EXCLUDED_INTEGER_KEY_LENGTHS=1..68")
    print("ORIGINAL_T4_T172_EMPTY_DISJOINT_N24_BYTE_SEED=PASS")
    print("K04_PHYSICAL_AND_K08_FINAL_UNRECOVERED")


if __name__ == "__main__":
    symbolic = words(OFFSET)
    real_python_control(symbolic)
    original(symbolic)
