"""Source-only NumPy MT19937 second-cycle pool4 falsifier, 624 phases.
Source-selected printer row129 withheld. No missing slot hash/mask/key is used.
Run: python agents/agent2/k04_numpy_seedpool_truephase_sft.py
Optionally: python agents/agent2/k04_numpy_seedpool_truephase_sft.py 0 190
"""
import collections
import hashlib
import re
import struct
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2] / 'resources'
# Source-established hypothetical p951 chronology; row129=951 is excluded.
STARTS = list(map(int, '''0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963'''.split(',')))
U = (1 << 32) - 1
MAG = 0x9908B0DF
INIT_B = 0x8B51F9DD
MULT_B = 0x58F38DED
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def untemper(x):
    for shift, mask, left in ((18, U, False), (15, 0xEFC60000, True),
                              (7, 0x9D2C5680, True), (11, U, False)):
        y = x
        for _ in range(6):
            x = (y ^ ((x << shift) & mask if left else x >> shift)) & U
    return x


def wordexpr(last):
    words = [[1 << (32 * i + j) for j in range(32)] for i in range(624)]
    for i in range(624, last + 1):
        old, nxt, previous = words[i - 624], words[i - 623], words[i - 227]
        words.append([
            previous[j]
            ^ (old[31] if j == 30 else nxt[j + 1] if j < 30 else 0)
            ^ (nxt[0] if (MAG >> j) & 1 else 0)
            for j in range(32)
        ])
    return words


def source():
    raw = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    fields = re.findall(rb'PAYLOAD=([0-9A-F]{32})', raw)
    assert len(fields) == len(STARTS) == 133
    return [struct.unpack('<4I', bytes.fromhex(h.decode())) for h in fields]


def construct_basis(expressions, payloads, origin):
    rows = {}
    for row, start in enumerate(STARTS):
        if row == 129:
            continue
        for lane in range(4):
            native = untemper(payloads[row][lane])
            for bit, v in enumerate(expressions[start + lane - origin]):
                b = (native >> bit) & 1
                while v:
                    p = v.bit_length() - 1
                    if p not in rows:
                        rows[p] = (v, b)
                        break
                    w, vb = rows[p]
                    v ^= w
                    b ^= vb
                else:
                    assert b == 0, ('incompatible printer source', row, lane, bit)
    assert len(rows) == 15365
    return rows


def fixed_init_words(expressions, rows):
    partials, fixed = [], []
    for i in range(624):
        mask = value = 0
        for bit, v in enumerate(expressions[i]):
            b = 0
            while v:
                p = v.bit_length() - 1
                if p not in rows:
                    break
                w, wb = rows[p]
                v ^= w
                b ^= wb
            else:
                mask |= 1 << bit
                value |= b << bit
        partials.append((value, mask))
        if mask == U:
            fixed.append(i)
    return partials, fixed


def invert_pool(word, i):
    before = (INIT_B * pow(MULT_B, i, 1 << 32)) & U
    factor = (before * MULT_B) & U
    z = word ^ (word >> 16)
    return ((z * pow(factor, -1, 1 << 32)) & U) ^ before


def forward_pool(pool, i):
    before = (INIT_B * pow(MULT_B, i, 1 << 32)) & U
    factor = (before * MULT_B) & U
    z = ((pool ^ before) * factor) & U
    return z ^ (z >> 16)


def gate(partials, fixed):
    value, mask = partials[0]
    if (value ^ 0x80000000) & mask:
        return 'K0'
    pools = [None] * 4
    for i in fixed:
        if i == 0:
            continue
        v = invert_pool(partials[i][0], i)
        j = i % 4
        if pools[j] is None:
            pools[j] = v
        elif pools[j] != v:
            return 'pool_conflict'
    for i in range(1, 624):
        if pools[i % 4] is None:
            continue
        value, mask = partials[i]
        if (forward_pool(pools[i % 4], i) ^ value) & mask:
            return 'pool_partial'
    return 'SURVIVES'


def model_source(seed, phase):
    rng = np.random.MT19937(seed)
    length = 603 + phase + STARTS[-1] + 4
    raw = [int(x) for x in rng.random_raw(length)]
    packets = [tuple(raw[603 + phase + start + j] for j in range(4))
               for start in STARTS]
    return packets, tuple(int(v) for v in np.random.SeedSequence(seed).pool)


def synthetic_controls():
    tests = ((0, 0), (1234, 13), (20261020, 99),
             ((1 << 127) | 0xDEADBEEF, 218), (5, 390), (17, 392),
             (12345, 393), (12345, 500), (12345, 619),
             (12345, 620), (12345, 623))
    for seed, phase in tests:
        packets, truepool = model_source(seed, phase)
        origin = -1226 - phase
        expressions = wordexpr(STARTS[-1] + 3 - origin)
        rows = construct_basis(expressions, packets, origin)
        partials, fixed = fixed_init_words(expressions, rows)
        assert gate(partials, fixed) == 'SURVIVES'
        truekey = [int(x) for x in np.random.MT19937(seed).state['state']['key']]
        assert all(((truekey[i] ^ v) & mask) == 0
                   for i, (v, mask) in enumerate(partials))
        assert all(invert_pool(partials[i][0], i) == truepool[i % 4]
                   for i in fixed if i)
        print('SYNTHETIC_PASS', seed, phase, len(fixed), flush=True)
    print('NUMPY_SYNTHETIC_CONTROLS_PASS', len(tests), flush=True)


def main(start=0, stop=624):
    assert 0 <= start < stop <= 624
    began = time.monotonic()
    if start == 0:
        synthetic_controls()
    packets = source()
    counts = collections.Counter()
    for phase in range(start, stop):
        # Anchor at NumPy's *initialized* K[0], avoiding invalid MT prehistory.
        origin = -1226 - phase
        expressions = wordexpr(STARTS[-1] + 3 - origin)
        rows = construct_basis(expressions, packets, origin)
        partials, fixed = fixed_init_words(expressions, rows)
        verdict = gate(partials, fixed)
        counts[verdict] += 1
        if phase % 25 == 0 or verdict == 'SURVIVES':
            print('ORIGINAL_PHASE', phase, verdict, len(fixed), flush=True)
    print('ORIGINAL_COUNTS', start, stop, dict(counts),
          'seconds', round(time.monotonic() - began, 2), flush=True)
    assert counts['SURVIVES'] == 0, 'Compatible phase needs independent audit'
    if start == 0 and stop == 624:
        assert counts == collections.Counter({'pool_conflict': 549, 'K0': 75})
        print('COMPLETE_NUMPY_SECOND_CYCLE_POOL4_624_PHASES_EXCLUDED')


if __name__ == '__main__':
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    stop = int(sys.argv[2]) if len(sys.argv) > 2 else 624
    main(start, stop)
