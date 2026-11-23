"""Exact modular inverse / divisor sieve for all CPython MT integer seed lengths.

Original K04 selected printer payload is excluded; no acceptance digests consulted.
Run: python agents/agent1/k04_all42_cpython_divisor_sft.py
"""
from __future__ import annotations

import collections
import json
import time
from k04_all42_cpython_n98_extended_sft import (
    U, G, projection, source, planted, keyterm, terms,
)

INV1 = pow(1664525, -1, 1 << 32)
INV2 = pow(1566083941, -1, 1 << 32)
DIVISORS = [0] * 624
for delta in range(1, 624):
    for n in range(1, delta + 1):
        if delta % n == 0:
            DIVISORS[delta] |= 1 << (n - 1)


def f1(w):
    return 1664525 * (w ^ (w >> 30)) & U


def f2(w):
    return 1566083941 * (w ^ (w >> 30)) & U


def inverse_last(x, y, term, i):
    """Return the only possible S[i] given S[i-2], S[i-1], key term."""
    a = ((y + i - 1) & U) ^ f2(x)
    c = G[i] ^ f1(a)
    b = (term + c) & U
    return ((b ^ f2(y)) - i) & U


def inverse_first(y, z, term, i):
    """Return the only possible S[i-2] given S[i-1], S[i], key term."""
    b = ((z + i) & U) ^ f2(y)
    c = (b - term) & U
    intermediate = ((c ^ G[i]) * INV1) & U
    a = intermediate ^ (intermediate >> 30)
    intermediate = ((a ^ ((y + i - 1) & U)) * INV2) & U
    return intermediate ^ (intermediate >> 30)


def incompatible_lengths(states):
    """Necessary source contradictions as a 623-bit forbidden-seed-length set.

    Two exact terms with differing value cannot have a common residue modulo n.
    A term determined at one triple also forces any trailing or leading
    partially-known word at another triple with the same key residue.
    The shared-residue condition holds iff n divides their index distance.
    """
    anchors = []
    partial = []
    for i in range(4, 624):
        (mx, x), (my, y), (mz, z) = states[i-2:i+1]
        if mx == my == mz == U:
            anchors.append((i, keyterm(x, y, z, i)))
        elif mx == my == U:
            partial.append((i, 'last', x, y, z, mz))
        elif mz == my == U:
            partial.append((i, 'first', y, z, x, mx))
    incompatible = 0
    for a, (i, term) in enumerate(anchors):
        for j, other in anchors[a+1:]:
            if term != other:
                incompatible |= DIVISORS[j-i]
        for j, position, value1, value2, known_value, mask in partial:
            predicted = (inverse_last(value1, value2, term, j) if position == 'last'
                         else inverse_first(value1, value2, term, j))
            if predicted & mask != known_value:
                incompatible |= DIVISORS[abs(j-i)]
    return incompatible, len(anchors), len(partial)


def cheap_compatible(term_rows, n):
    domains = {}
    for i, free_bits, possible_terms in term_rows:
        residue = (i-1) % n
        if residue in domains:
            domains[residue].intersection_update(possible_terms)
            if not domains[residue]:
                return False
        else:
            domains[residue] = set(possible_terms)
    return True


def seeded_controls():
    for n, offset in ((98, 0), (98, 616), (109, 616), (128, 0),
                      (257, 616), (623, 0)):
        _, true, packets = planted(n, offset)
        states = projection(offset, packets)
        assert all((true[i] & mask) == value
                   for i, (mask, value) in enumerate(states))
        for i in range(4, 624):
            x, y, z = true[i-2:i+1]
            term = keyterm(x, y, z, i)
            assert inverse_first(y, z, term, i) == x
            assert inverse_last(x, y, term, i) == z
        forbidden, exact_count, partial_count = incompatible_lengths(states)
        assert not (forbidden & (1 << (n-1)))
        assert cheap_compatible(list(terms(states, 1)), n)
        print('GENUINE_SEEDED_CONTROL', n, offset, 'PASS',
              exact_count, partial_count, flush=True)


def main():
    seeded_controls()
    selected_withheld = source()
    start = time.monotonic()
    survivors = {n: [] for n in range(1, 624)}
    compatible_s0_origins = 0
    for offset in range(624):
        states = projection(offset, selected_withheld)
        if (states[0][1] ^ 0x80000000) & states[0][0]:
            continue
        compatible_s0_origins += 1
        forbidden, _, _ = incompatible_lengths(states)
        direct_domains = list(terms(states, 1))
        for n in range(1, 624):
            if forbidden & (1 << (n-1)):
                continue
            if cheap_compatible(direct_domains, n):
                survivors[n].append(offset)
        if offset % 100 == 0:
            print('ORIGINAL_SOURCE_PROGRESS', offset,
                  round(time.monotonic()-start, 2), flush=True)
    counts = {n: len(offsets) for n, offsets in survivors.items() if offsets}
    assert compatible_s0_origins == 499
    assert min(counts) == 230
    assert all(not survivors[n] for n in range(1, 230))
    assert {n: len(survivors[n]) for n in (230, 231, 251, 282, 293, 294)} == {
        230: 21, 231: 20, 251: 26, 282: 4, 293: 1, 294: 63,
    }
    print('ORIGINAL_RESULT', json.dumps({
        'source_sha256': '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
        'selected_K04_payload_used': False,
        'tested_prior_output_offsets': 624,
        'tested_seed_lengths': '1..623',
        'compatible_S0_origins': compatible_s0_origins,
        'excluded_seed_lengths': '1..229',
        'first_necessary_compatible_length': min(counts),
        'first_survivor_counts': list(counts.items())[:20],
        'recovered_K04': False,
    }, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
