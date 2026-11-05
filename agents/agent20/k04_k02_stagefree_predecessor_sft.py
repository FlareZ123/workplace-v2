"""Test the original K02 diagnostic stream as a stage-unindexed printer-MT precursor.

Read-only single-file test, runnable in the original workplace-v2 repository.
Its input source is an independently accepted K02 eight-halfword sequence, and
its output is a source-only diagnosis. K04 copied ACK2 and commitments are omitted.
"""
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations, product
from pathlib import Path
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2] / 'resources' / 'evidence'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
TELEMETRY_SHA = '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
U32 = 0xFFFFFFFF
MAG = 0x9908B0DF


def load(relative, expected):
    data = (ROOT / relative).read_bytes()
    assert sha256(data).hexdigest() == expected
    return data


def untemper(v):
    for n, left, mask in ((18, False, U32), (15, True, 0xEFC60000),
                           (7, True, 0x9D2C5680), (11, False, U32)):
        old = v
        for _ in range(6):
            v = (old ^ (((v << n) & mask) if left else (v >> n))) & U32
    return v


def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9D2C5680
    v ^= (v << 15) & 0xEFC60000
    v ^= v >> 18
    return v & U32


def precursor_options(early, late):
    difference = (early ^ late) & 0xBFFFFFFF
    parity = difference >> 31
    lower31 = (((difference ^ (MAG if parity else 0)) & 0x3FFFFFFF) << 1) | parity
    return temper(lower31), temper(lower31 | 0x80000000)


def build_index(rows):
    index = defaultdict(list)
    for early, late in combinations(sorted(rows), 2):
        for offset in (0, 1):
            options = [precursor_options(rows[early][offset + i], rows[late][offset + i])
                       for i in range(3)]
            for bits in product((0, 1), repeat=3):
                predicted = [options[i][bits[i]] for i in range(3)]
                for view in ('high16', 'low16'):
                    signature = tuple(v >> 16 if view == 'high16' else v & 65535
                                      for v in predicted)
                    index[signature].append((early, late, offset, bits, view))
    assert sum(map(len, index.values())) == 276672
    return index


def source_sequences(telemetry):
    diag = [row for row in telemetry if row['field'] == 'DIAG_WORD']
    assert len(diag) == 33
    start = datetime.fromisoformat('2026-10-03T21:13:40+00:00')
    stop = datetime.fromisoformat('2026-10-03T21:13:48+00:00')
    selected = {}
    for row in diag:
        stamp = datetime.fromisoformat(row['ts']).astimezone(timezone.utc)
        if (row['tag'] == 'LT-204' and row['quality'] == 'GOOD' and
                row['state'] == 'HOLD' and start <= stamp < stop):
            seq = row['seq']
            if seq not in selected or row['revision'] > selected[seq]['revision']:
                selected[seq] = row
    assert [selected[i]['value'] for i in range(8)] == [
        57765, 58484, 47831, 59475, 41704, 50973, 13079, 54535]
    return {
        'selected_k02': [selected[i] for i in range(8)],
        'all_diag_retrieval': diag,
        'all_diag_utc': sorted(diag, key=lambda row: (datetime.fromisoformat(row['ts']),
                                                        row['revision'], row['seq'])),
        'all_diag_seq_rev': sorted(diag, key=lambda row: (row['seq'], row['revision'],
                                                        datetime.fromisoformat(row['ts']))),
    }


def main():
    spool = load('print/spool-reconstruction.log', SPOOL_SHA)
    payloads = re.findall(rb'PAYLOAD=([0-9A-F]{32})', spool)
    assert len(payloads) == 133
    rows = {i: tuple(untemper(int.from_bytes(bytes.fromhex(payload.decode('ascii'))[j:j + 4], 'little'))
                     for j in range(0, 16, 4))
            for i, payload in enumerate(payloads) if i != 129}
    # The original selected ACK2 bytes are never decoded.
    assert len(rows) == 132
    index = build_index(rows)
    rng = random.Random(0x20170417)
    seeded_native = [untemper(rng.getrandbits(32)) for _ in range(900)]
    for j in range(20, 24):
        assert temper(seeded_native[j + 1]) in precursor_options(
            seeded_native[j + 397], seeded_native[j + 624])

    telemetry = [json.loads(line) for line in load('telemetry/freeze-export.jsonl',
                                                  TELEMETRY_SHA).splitlines()]
    tested = {}
    for name, records in source_sequences(telemetry).items():
        values = [record['value'] for record in records]
        hits = []
        for swapped in (False, True):
            ordered = ([int.from_bytes(value.to_bytes(2, 'little'), 'big')
                        for value in values] if swapped else values)
            for offset in range(len(ordered) - 2):
                hits.extend((swapped, offset, match)
                            for match in index.get(tuple(ordered[offset:offset + 3]), ()))
        tested[name] = {'records': len(values), 'window_views': 2 * (len(values) - 2),
                        'triple_matches': len(hits)}
        assert len(hits) == 0, (name, hits)
        for swapped in (False, True):
            other = [int.from_bytes(v.to_bytes(2, 'little'), 'big') if swapped else v
                     for v in values]
            for i, j, k in permutations(range(len(other)), 3):
                assert (other[i], other[j], other[k]) not in index
        tested[name]['ordered_triple_views'] = 2 * len(values) * (len(values) - 1) * (len(values) - 2)
        tested[name]['ordered_triple_matches'] = 0
    assert sum(d['window_views'] for d in tested.values()) == 198
    print(json.dumps({'source_only': 'NO_K02_STAGEFREE_PRECURSOR_TRIPLE',
                      'printer_source_packets': 132, 'printer_triple_hypotheses': 276672,
                      'telemetry': tested, 'real_seeded_MT_positive': 'PASS',
                      'historical_K04_selected_bits_authenticated': 0}, indent=2))


if __name__ == '__main__':
    main()
