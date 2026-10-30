"""H-17 K04: 62 selected starts with all 130 observed ACK starts fixed.

This is a conditional necessary-source-equation certificate, not an authentic MT
source, a selected coupon, or a recovery key. Selected r129 payload is omitted.
"""
from collections import defaultdict
import re
from random import Random

import k04_ack_chronology_sliding_certificate_sft as source

ACK_ROWS = (*range(128), 129, 131, 132)
BOUNDARY_MASK = 0xBFFFFFFF


def boundary_hits() -> list[tuple[int, int, int, int, int]]:
    rows = {}
    lines = [ln for ln in source.SPOOL.read_text('ascii').splitlines() if ' PAYLOAD=' in ln]
    for row, line in enumerate(lines):
        if row in (128, 129, 130):
            continue
        assert 'STATE=ACK' in line
        payload = bytes.fromhex(re.search(r'PAYLOAD=([A-F0-9]{32})', line).group(1))
        rows[row] = tuple(source.untemper(int.from_bytes(payload[12-4*k:16-4*k], 'little'))
                          for k in range(4))
    indexed = defaultdict(list)
    for row, words in rows.items():
        for word, value in enumerate(words):
            indexed[value & BOUNDARY_MASK].append((row, word))
    hits = []
    for a in range(128):
        signature = source.twist(0, rows[a][0]) & BOUNDARY_MASK
        for b in range(a+1, 128):
            for bw, val in enumerate(rows[b]):
                for c, cw in indexed.get((signature ^ val) & BOUNDARY_MASK, ()):
                    if c > b:
                        hits.append((a, b, bw, c, cw))
    assert hits == [(21, 74, 2, 105, 1), (22, 75, 2, 106, 2), (39, 93, 3, 123, 1)]
    return hits


def make_edges(hits, boundaries) -> list[tuple[int,int,int]]:
    edges = []
    for a,aw,b,bw,c,cw in hits:
        for first,last,delta in ((a,b,397+aw-bw),(a,c,624+aw-cw)):
            edges.extend(((first,last,delta),(last,first,-delta)))
    for a,b,bw,c,cw in boundaries:
        for first,last,delta in ((a,b,396-bw),(a,c,623-cw)):
            edges.extend(((first,last,delta),(last,first,-delta)))
    edges.extend((a,b,4) for a,b in zip(ACK_ROWS,ACK_ROWS[1:]))
    return edges


def add_eq(a,b,d):
    return [(a,b,d),(b,a,-d)]


def solve(edges: list[tuple[int,int,int]], origin: int = 0) -> dict[int,int]:
    starts = {r:None for r in ACK_ROWS}
    starts[origin] = 0
    for _ in ACK_ROWS:
        changed = False
        for a,b,gap in edges:
            if starts[a] is None:
                continue
            proposed = starts[a] + gap
            if starts[b] is None or starts[b] < proposed:
                starts[b] = proposed
                changed = True
        if not changed:
            assert all(v is not None for v in starts.values())
            return starts
    raise ValueError('infeasible source difference constraints')


def main() -> None:
    generator = Random(7123)
    stream = [source.untemper(generator.getrandbits(32)) for _ in range(625)]
    assert stream[624] == stream[397] ^ source.twist(stream[0], stream[1])
    assert (stream[624] ^ stream[397]) & BOUNDARY_MASK == source.twist(0,stream[1]) & BOUNDARY_MASK
    hits = source.original_hits()  # verifies source SHA without ever reading r129 payload
    boundaries = boundary_hits()
    bare_edges = make_edges(hits, boundaries)
    from_first = solve(bare_edges, origin=0)
    from_target = solve(bare_edges, origin=129)
    from_last = solve(bare_edges, origin=132)
    unconditional = (from_first[132], -from_last[0],
                     from_first[129], -from_target[0])
    assert unconditional == (930, 991, 919, 980)
    print('SOURCE-ONLY ABSOLUTE BOUNDS: final ACK 930..991, missing ACK 919..980')
    edges = (bare_edges + add_eq(0,132,991) +
             add_eq(0,127,915) + add_eq(0,131,984))
    baseline = solve(edges + add_eq(0,129,919))
    assert (baseline[0],baseline[127],baseline[129],baseline[131],baseline[132]) == (0,915,919,984,991)
    observed = {r:baseline[r] for r in ACK_ROWS if r != 129}
    for target_start in range(919,981):
        witness = {**observed,129:target_start}
        for a,b,gap in edges:
            assert witness[b] >= witness[a] + gap
        for a,aw,b,bw,c,cw in hits:
            assert witness[b]+bw == witness[a]+aw+397
            assert witness[c]+cw == witness[a]+aw+624
        for a,b,bw,c,cw in boundaries:
            assert witness[b]+bw == witness[a]+396
            assert witness[c]+cw == witness[a]+623
        assert all(witness[b]-witness[a]>=4 for a,b in zip(ACK_ROWS,ACK_ROWS[1:]))
        assert all(witness[r] == observed[r] for r in observed)
    # Synthetic true seeded MT stream: identical observed 130 ACK outputs in
    # all 62 histories, but 62 distinct missing-event four-word coupons.
    generator = Random(7123)
    stream_words = [generator.getrandbits(32) for _ in range(1000)]
    fixed_original_positions = tuple((row, observed[row]) for row in observed)
    fixed_observed_data = tuple(tuple(stream_words[observed[row]+i] for i in range(4))
                                for row, _ in fixed_original_positions)
    synthetic_targets = set()
    for target_start in range(919, 981):
        regenerated = tuple(tuple(stream_words[observed[row]+i] for i in range(4))
                            for row, _ in fixed_original_positions)
        assert regenerated == fixed_observed_data
        synthetic_targets.add(tuple(stream_words[target_start:target_start+4]))
    assert len(synthetic_targets) == 62
    print('TRUE-STREAM CONTROL: fixed entire MT state and 130 known outputs; 62 distinct missing-event coupons')
    print('AUGMENTED: original 21 fullword + 3 masked 31-bit constraints PASS')
    print('FIXED 130 OBSERVED ACK starts; only selected r129 changes')
    print('Selected start 919..980: 62/62 feasible; bounding ACK r127=915, r131=984')
    print('No source-to-selected producer/copy bridge and no target coupon bits recovered')


if __name__ == '__main__':
    main()
