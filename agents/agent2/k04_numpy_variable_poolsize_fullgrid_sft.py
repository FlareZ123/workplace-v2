"""NumPy SeedSequence variable pool-size source gate: 624 phases x 620 sizes.
Original selected printer row129 and all target commitments are withheld.
Requires NumPy and the neighboring pool4 exact source model.
"""
import collections
import sys
import time
import numpy as np
from k04_numpy_secondcycle_pool4_fullphase_sft import (
    STARTS, construct_basis, fixed_init_words, forward_pool,
    invert_pool, source, wordexpr,
)


def test_model(partials, fixed, size):
    value, mask = partials[0]
    if (value ^ 0x80000000) & mask:
        return 'K0', 0
    pool = {}
    for i in fixed:
        if i == 0:
            continue
        predicted = invert_pool(partials[i][0], i)
        residue = i % size
        if residue in pool and pool[residue] != predicted:
            return 'fixed_conflict', len(pool)
        pool[residue] = predicted
    for i in range(1, 624):
        value, mask = partials[i]
        residue = i % size
        if residue in pool and ((forward_pool(pool[residue], i) ^ value) & mask):
            return 'partial_conflict', len(pool)
    return 'SURVIVES', len(pool)


def synthetic_controls():
    samples = ((4, 0), (5, 123), (8, 623), (16, 78),
               (32, 207), (64, 440), (128, 29), (256, 508),
               (512, 610), (19, 323), (37, 5), (61, 413),
               (101, 469), (127, 287), (301, 125),
               (511, 575), (523, 155), (601, 233), (623, 607))
    for size, phase in samples:
        seed = 12345 + size
        seq = np.random.SeedSequence(seed, pool_size=size)
        rng = np.random.MT19937(seq)
        nraw = 603 + phase + STARTS[-1] + 4
        raw = [int(x) for x in rng.random_raw(nraw)]
        packets = [tuple(raw[603 + phase + start + j] for j in range(4))
                   for start in STARTS]
        origin = -1226 - phase
        expressions = wordexpr(STARTS[-1] + 3 - origin)
        rows = construct_basis(expressions, packets, origin)
        partials, fixed = fixed_init_words(expressions, rows)
        verdict = test_model(partials, fixed, size)
        assert verdict[0] == 'SURVIVES', (size, phase, verdict)
        assert all(invert_pool(partials[i][0], i) == int(seq.pool[i % size])
                   for i in fixed if i)
    print('TRUE_NUMPY_VARIABLE_POOL_POSITIVES', len(samples), 'PASS', flush=True)


def main(start=0, stop=624):
    assert 0 <= start < stop <= 624
    began = time.monotonic()
    if start == 0:
        synthetic_controls()
    packets = source()
    counts = collections.Counter()
    smallest = 624
    for phase in range(start, stop):
        origin = -1226 - phase
        expressions = wordexpr(STARTS[-1] + 3 - origin)
        rows = construct_basis(expressions, packets, origin)
        partials, fixed = fixed_init_words(expressions, rows)
        survivors = 0
        for size in range(4, 624):
            verdict, known_pool_words = test_model(partials, fixed, size)
            counts[verdict] += 1
            if verdict == 'SURVIVES':
                smallest = min(smallest, size)
                survivors += 1
                if size < 554:
                    raise AssertionError(('short-pool survivor', phase, size))
        if phase % 25 == 0:
            print('ORIGINAL_PHASE', phase, 'surviving_sizes', survivors,
                  'seconds', round(time.monotonic() - began, 2), flush=True)
    print('ORIGINAL_SOURCE_POOLSIZE_GRID', start, stop, dict(counts),
          'minimum_surviving_poolsize', smallest,
          'seconds', round(time.monotonic() - began, 2), flush=True)
    if start == 0 and stop == 624:
        expected = collections.Counter({
            'fixed_conflict': 301039,
            'K0': 46500,
            'partial_conflict': 33556,
            'SURVIVES': 5785,
        })
        assert counts == expected, (counts, expected)
        assert smallest == 554
        assert sum(counts.values()) == 624 * 620
        print('PASS_NUMPY_VARIABLE_POOL_4_THROUGH_553_EXCLUDED', flush=True)


if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    stop = int(sys.argv[2]) if len(sys.argv) > 2 else 624
    main(start, stop)
