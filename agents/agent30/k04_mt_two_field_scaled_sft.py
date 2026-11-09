"""H17 K04 source-only two independent scaled-uint32 three-way printer metadata issuers.

Use as sibling to k04_mt_joint_float_sft.py. The original copied selected ACK2 is
withheld; only intact spool label source and native MT chronology are fitted.
Synthetic calibration asserts complete held-out category recovery.
"""
import itertools
import random
import k04_mt_joint_float_sft as m


def scaled3_options(v, b):
    n = 0
    mask = 0
    for j in range(32):
        t = b.bit(v[j])
        if t is None:
            mask |= 1 << j
        elif t:
            n |= 1 << j
    return frozenset(range((3*n) >> 32, (3*(n+mask) >> 32)+1))


def run_geometry(rows, source_words, b, geometry):
    outputs = [m.temper(w) for w in source_words]
    projected = [scaled3_options(w, b) for w in outputs]
    classcats = tuple(sorted({x[0] for x in rows[:128]}))
    destcats = tuple(sorted({x[1] for x in rows[:128]}))
    assert len(classcats) == len(destcats) == 3
    codebooks = [
        (dict(zip(classcats, cc)), dict(zip(destcats, dd)))
        for cc in itertools.permutations(range(3))
        for dd in itertools.permutations(range(3))
    ]
    rejections = 0
    for position in ('first', 'last', 'any'):
        for labelbind in ('previous', 'following'):
            for order in ('class_first', 'dest_first'):
                observations = []
                for i in range(127):
                    start = m.STAGES[i] + 4
                    end = m.STAGES[i+1]
                    assert end-start >= 2
                    if position == 'first':
                        pairs = [(start, start+1)]
                    elif position == 'last':
                        pairs = [(end-2, end-1)]
                    else:
                        pairs = list(itertools.combinations(range(start, end), 2))
                    possible = set()
                    for first, second in pairs:
                        for x in projected[first]:
                            for y in projected[second]:
                                possible.add((x, y) if order == 'class_first' else (y, x))
                    c, d = rows[i+(labelbind == 'following')][:2]
                    observations.append((c, d, possible))
                trained = []
                for cm, dm in codebooks:
                    if all((cm[c], dm[d]) in p for c, d, p in observations[:95]):
                        hold = sum((cm[c], dm[d]) in p for c, d, p in observations[95:])
                        trained.append((hold, cm, dm))
                best = max((x[0] for x in trained), default=-1)
                full = sum(x[0] == 32 for x in trained)
                print('MODEL', geometry, position, labelbind, order,
                      'train_maps', len(trained), 'best_holdout', best,
                      'full_maps', full, flush=True)
                rejections += int(full == 0 and best < 32)
    return rejections


def synthetic_controls():
    rng = random.Random(20261109)
    for _ in range(128):
        a, b = rng.getrandbits(32), rng.getrandbits(32)
        base = m.Basis()
        symbolic = [[1 << j for j in range(32)], [1 << (32+j) for j in range(32)]]
        for lane, word in enumerate((a, b)):
            for bit in range(32):
                base.add(symbolic[lane][bit], (word >> bit) & 1)
        assert scaled3_options(symbolic[0], base) == frozenset(((3*a) >> 32,))
        assert scaled3_options(symbolic[1], base) == frozenset(((3*b) >> 32,))
    cats = tuple(sorted(("LABEL", "STORES", "RECOVER")))
    dests = tuple(sorted(("desk", "bench", "store")))
    perm_class = (2, 0, 1)
    perm_dest = (1, 2, 0)
    rows = [(cats[rng.randrange(3)], dests[rng.randrange(3)]) for _ in range(127)]
    symbols = [(perm_class[cats.index(c)], perm_dest[dests.index(d)]) for c, d in rows]
    mappings = [
        (dict(zip(cats, x)), dict(zip(dests, y)))
        for x in itertools.permutations(range(3))
        for y in itertools.permutations(range(3))
    ]
    matches = [
        (cm, dm) for cm, dm in mappings
        if all((cm[c], dm[d]) == symbol
               for (c, d), symbol in zip(rows[:95], symbols[:95]))
    ]
    assert len(matches) == 1
    cm, dm = matches[0]
    assert all((cm[c], dm[d]) == symbol
               for (c, d), symbol in zip(rows[95:], symbols[95:]))
    print("SYNTHETIC_PASS 128 exact scaled3 source projections + 32 complete label holdouts")


def main():
    synthetic_controls()
    rows = m.load()
    base_stages = m.STAGES[:]
    rejected = 0
    for geom in ('950', '951', '952', '953', '954', '955'):
        delta = m.DIFFERENCES.get(geom)
        m.STAGES[:] = [
            s + m.ALPHABET.index(x)-13 for s, x in zip(base_stages, delta)
        ] if delta else base_stages[:]
        source, b = m.basis(rows)
        print('ORIGINAL_GEOMETRY', geom, 'rank', len(b.rows), flush=True)
        rejected += run_geometry(rows, source, b, geom)
    assert rejected == 72, rejected
    print("ORIGINAL_FINAL 72/72 separate 3-way scaled-draw metadata issuers rejected; no K04 source bits")


if __name__ == '__main__':
    main()
