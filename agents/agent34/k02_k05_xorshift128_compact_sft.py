"""Original K02→K05 xorshift128 producer falsifier; no K04/K08 commitment read."""
import hashlib
import itertools
from pathlib import Path

RES = Path(__file__).resolve().parents[2] / 'resources' / 'evidence'
assert hashlib.sha256((RES/'telemetry/freeze-export.jsonl').read_bytes()).hexdigest() == '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
assert hashlib.sha256((RES/'recorder/trip-recorder.raw').read_bytes()).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
# Official selector: K02 GOOD/HOLD, highest revision per seq 0..7, 21:13:40..48.
K02 = bytes.fromhex('E1A5E474BAD7E853A2E8C71D3317D507')
# Official selector: K05 node49/event82/CRC-good highest seq300..303, latch 0..3.
K05 = bytes.fromhex('FF8B78200A56E8586DCDA00EF01E4572')
U = (1 << 32) - 1


def step(state):
    a, b, c, d = state
    t = (a ^ ((a << 11) & U)) & U
    return (b, c, d, ((d ^ (d >> 19)) ^ t ^ (t >> 8)) & U)


def expressions(count):
    s = tuple(tuple(1 << (32 * i + j) for j in range(32)) for i in range(4))
    out = []
    for _ in range(count):
        a, b, c, d = s
        t = tuple(a[j] ^ (a[j-11] if j >= 11 else 0) for j in range(32))
        w = tuple(d[j] ^ (d[j+19] if j < 13 else 0) ^ t[j] ^
                  (t[j+8] if j < 24 else 0) for j in range(32))
        s = (b, c, d, w)
        out.append(w)
    return out


def solve(rows):
    pivots = {}
    for v, bit in rows:
        while v:
            p = v.bit_length()-1
            if p not in pivots:
                pivots[p] = (v, bit)
                break
            eq, value = pivots[p]
            v ^= eq
            bit ^= value
        if not v and bit:
            return None
    return pivots


def predict(pivots, eq):
    bit = 0
    while eq:
        p = eq.bit_length()-1
        if p not in pivots:
            return None
        row, value = pivots[p]
        eq ^= row
        bit ^= value
    return bit


def models(expr):
    for endian, reverse, high in itertools.product(('big', 'little'), (False, True), (False, True)):
        blocks = [K02[i:i+2] for i in range(0, 16, 2)]
        if reverse: blocks.reverse()
        words = [int.from_bytes(b, endian) for b in blocks]
        yield 'eight_cropped', (endian, reverse, high), 8, [
            (expr[i][j + 16*high], (word >> j) & 1)
            for i, word in enumerate(words) for j in range(16)]
    for endian, reverse, swap in itertools.product(('big', 'little'), (False, True), (False, True)):
        blocks = [K02[i:i+4] for i in range(0, 16, 4)]
        if swap: blocks = [b[2:]+b[:2] for b in blocks]
        if reverse: blocks.reverse()
        words = [int.from_bytes(b, endian) for b in blocks]
        yield 'four_full', (endian, reverse, swap), 4, [
            (expr[i][j], (word >> j) & 1)
            for i, word in enumerate(words) for j in range(32)]


def run():
    expr = expressions(108)
    st = (0x13579bdf, 0x2468ace0, 0x31415926, 0x27182818)
    generated = []
    for output in expr:
        st = step(st)
        generated.append(st[3])
    for count, width, expected_rank, expected_known in ((4, 32, 128, 128), (8, 16, 125, 59)):
        rows = [(expr[i][j], (generated[i] >> j) & 1)
                for i in range(count) for j in range(width)]
        fit = solve(rows)
        assert fit is not None and len(fit) == expected_rank
        p = count + 13
        known = 0
        for i in range(4):
            for bit, equation in enumerate(expr[p+i]):
                v = predict(fit, equation)
                if v is not None:
                    known += 1
                    assert v == (generated[p+i] >> bit) & 1
        assert known == expected_known
        print('PLANTED', count, 'outputs:', known, 'correct heldout bits')
    counts = {}
    for name, mode, start, rows in models(expr):
        d = counts.setdefault(name, {'modes':0, 'inconsistent_K02':0, 'rank':0,
                                      'K05_predictions':0, 'K05_matches':0, 'min_errors':129})
        d['modes'] += 1
        fit = solve(rows)
        if fit is None:
            d['inconsistent_K02'] += 1
            continue
        d['rank'] = max(d['rank'], len(fit))
        for gap, endian, reverse in itertools.product(range(97), ('big','little'), (False, True)):
            blocks = [K05[i:i+4] for i in range(0, 16, 4)]
            if reverse: blocks.reverse()
            words = [int.from_bytes(b, endian) for b in blocks]
            known = errors = 0
            for i, word in enumerate(words):
                for bit, equation in enumerate(expr[start+gap+i]):
                    v = predict(fit, equation)
                    if v is not None:
                        known += 1
                        errors += v != (word >> bit) & 1
            if known >= 16:
                d['K05_predictions'] += 1
                d['K05_matches'] += errors == 0
                d['min_errors'] = min(d['min_errors'], errors)
    assert counts == {
        'eight_cropped': {'modes':8, 'inconsistent_K02':8, 'rank':0,
                          'K05_predictions':0,'K05_matches':0,'min_errors':129},
        'four_full': {'modes':8, 'inconsistent_K02':0, 'rank':128,
                      'K05_predictions':3104,'K05_matches':0,'min_errors':44}}
    print('ORIGINAL', counts)
    print('PASS compact xorshift128 source-only heldout, K04/K08 unresolved')

if __name__ == '__main__': run()
