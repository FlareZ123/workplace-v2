"""Original source .NET Framework System.Random.NextBytes producer sieve.

Tests 8 contiguous ordinary print packets with 0..16 unobserved generator bytes
between packets, any unobserved prelude. Uses a necessary seed-free 55/34-byte
subtractive recurrence. No K04 missing packet or acceptance commitment opened.
Microsoft reference implementation: github.com/microsoft/referencesource, random.cs.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import re
from pathlib import Path

CHECKOUT = Path(__file__).resolve().parents[2] / 'resources'
ROOT = CHECKOUT if CHECKOUT.exists() else Path(__file__).resolve().parent
SPOOL_HASH = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MBIG = (1 << 31) - 1


def framework_nextbytes(seed: int, length: int) -> bytes:
    assert 0 <= seed <= MBIG
    state = [0] * 56
    mj = 161803398 - seed
    state[55] = mj
    mk = 1
    for i in range(1, 55):
        ii = (21 * i) % 55
        state[ii] = mk
        mk = mj - mk
        if mk < 0:
            mk += MBIG
        mj = state[ii]
    for _ in range(4):
        for i in range(1, 56):
            state[i] -= state[1 + (i + 30) % 55]
            if state[i] < 0:
                state[i] += MBIG
    ii, jj = 0, 21
    output = bytearray()
    for _ in range(length):
        ii = ii + 1 if ii < 55 else 1
        jj = jj + 1 if jj < 55 else 1
        value = state[ii] - state[jj]
        if value == MBIG:
            value -= 1
        if value < 0:
            value += MBIG
        state[ii] = value
        output.append(value & 255)
    return bytes(output)


def source_rows():
    data = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_HASH
    lines = [line for line in data.decode('ascii').splitlines() if '+00:00 JOB=' in line]
    assert len(lines) == 128
    assert all(re.search(r'PAYLOAD=[0-9A-F]{32}', line) for line in lines)
    return [bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', line).group(1)) for line in lines]


def valid_triple(word, first, second):
    d = (first - second) & 255
    return word == d or word == ((d - 1) & 255)


def candidate_paths(packets, max_gap=16):
    assert all(len(packet) == 16 for packet in packets)
    known = {}
    visits, leaves = 0, []

    def add_packet(start, packet):
        added = []
        for ix, word in enumerate(packet):
            t = start + ix
            if t >= 55 and t - 55 in known and t - 34 in known:
                if not valid_triple(word, known[t - 55], known[t - 34]):
                    for k in added:
                        del known[k]
                    return False
            known[t] = word
            added.append(t)
        return True

    def go(row, start, history):
        nonlocal visits
        visits += 1
        if not add_packet(start, packets[row]):
            return
        if row + 1 == len(packets):
            leaves.append(history)
        else:
            for gap in range(max_gap + 1):
                go(row + 1, start + 16 + gap, history + (gap,))
        for t in range(start, start + 16):
            del known[t]

    go(0, 0, ())
    return visits, leaves


def main():
    for seed in (0, 1, 42, MBIG):
        output = framework_nextbytes(seed, 1000)
        assert all(valid_triple(output[t], output[t - 55], output[t - 34])
                   for t in range(55, 1000))
    assert framework_nextbytes(1, 16).hex() == '46d086824097e4a395cfff46699c73c4'

    # Positive planted 8-packet producer with seven fixed hidden draw gaps.
    gaps = (2, 0, 3, 1, 4, 2, 1)
    original = framework_nextbytes(124523, 8 * 16 + sum(gaps))
    first = 0
    synthetic = []
    for i in range(8):
        synthetic.append(original[first:first + 16])
        first += 16 + (gaps[i] if i < 7 else 0)
    pos_visits, pos_leaves = candidate_paths(synthetic)
    assert gaps in pos_leaves
    source = source_rows()[:8]
    source_visits, source_leaves = candidate_paths(source)
    print(json.dumps({
        'original_spool_sha256': SPOOL_HASH,
        'packet_count': 8,
        'hidden_byte_gap_range': [0,16],
        'total_possible_hidden_gap_vectors': 17**7,
        'source_nodes_visited': source_visits,
        'source_compatible_gap_vectors': len(source_leaves),
        'synthetic_source_nodes_visited': pos_visits,
        'synthetic_compatible_gap_vectors': len(pos_leaves),
        'actual_planted_gaps_recovered': gaps in pos_leaves,
        'framework_reference_control': 'PASS',
    }, indent=2))
    assert not source_leaves


if __name__ == '__main__':
    main()
