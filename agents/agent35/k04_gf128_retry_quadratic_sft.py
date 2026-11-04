"""H-17 GF128-affine printer retry interpolation: exact original-source SFT."""
import hashlib
import re
import sys
from functools import lru_cache
from pathlib import Path

P = 0xE1000000000000000000000000000000
ONE = 1 << 127
SPOOL = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
TARGET = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'


def mul(a, b):
    ans = 0
    for i in range(127, -1, -1):
        if b >> i & 1:
            ans ^= a
        a = a >> 1 ^ (P if a & 1 else 0)
    return ans


def power(a, n):
    ans = ONE
    while n:
        if n & 1:
            ans = mul(ans, a)
        a = mul(a, a)
        n >>= 1
    return ans


def div(a, b):
    assert b
    return mul(a, power(b, (1 << 128)-2))


@lru_cache(maxsize=1)
def columns():
    return tuple(mul(1 << i, 1 << i) ^ (1 << i) for i in range(128))


def quadratic(a, b, c):
    # Exact polynomial a*x^2 + b*x + c = 0 over the GHASH field.
    if not a:
        return [div(c, b)] if b else []
    if not b:
        return [power(div(c, a), 1 << 127)]
    u = div(b, a)
    v = div(div(c, a), mul(u, u))
    cols = columns()
    rows = [sum(((col >> j) & 1) << i for i, col in enumerate(cols)) |
            (((v >> j) & 1) << 128) for j in range(128)]
    piv = []
    r = 0
    for i in range(128):
        j = next((j for j in range(r, 128) if rows[j] >> i & 1), None)
        if j is None:
            continue
        rows[r], rows[j] = rows[j], rows[r]
        for k in range(128):
            if k != r and rows[k] >> i & 1:
                rows[k] ^= rows[r]
        piv.append(i)
        r += 1
    assert r == 127
    if any(row >> 128 & 1 for row in rows[r:]):
        return []
    z = sum(((rows[k] >> 128) & 1) << i for k, i in enumerate(piv))
    result = [mul(u, z), mul(u, z ^ ONE)]
    assert all(mul(a, mul(h, h)) ^ mul(b, h) ^ c == 0 for h in result)
    return result


def view(x, layout):
    b = x.to_bytes(16, 'big')
    if layout & 4:
        b = bytes(int(f'{v:08b}'[::-1], 2) for v in b)
    blocks = [b[i:i+4] for i in (0, 4, 8, 12)]
    if layout & 2:
        blocks = [v[::-1] for v in blocks]
    if layout & 1:
        blocks.reverse()
    return int.from_bytes(b''.join(blocks), 'big')


def coupon_pass(h, pad, x, layout):
    physical = view(mul(h, x) ^ pad, layout).to_bytes(16, 'big')
    component = bytes(a ^ b for a, b in zip(physical, MASK))
    return hashlib.sha256(component).hexdigest() == TARGET


def original(path):
    data = Path(path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL
    lines = data.decode('ascii').splitlines()
    keys = {
        'A': ('0417', '16:45:00', 'STATE=ACK CLASS=LABEL'),
        'B': ('0417', '18:01:00', 'STATE=REQUESTED CLASS=RECOVER'),
        'C': ('0417', '18:03:00', 'STATE=REQUESTED CLASS=RECOVER'),
        'U': ('0420', '17:00:00', 'STATE=ACK CLASS=STORES'),
        'V': ('0420', '18:25:00', 'STATE=ACK CLASS=RECOVER'),
    }
    selected = {}
    for symbol, (job, time, state) in keys.items():
        matches = [s for s in lines if 'JOB=PS-261003-' + job in s and time in s and state in s]
        assert len(matches) == 1, symbol
        selected[symbol] = int(re.search('PAYLOAD=([0-9A-F]{32})', matches[0]).group(1), 16)
    assert len(selected) == 5  # Deliberately never extract 0417 ACK attempt2.
    return selected


def test(path):
    h0 = 0x76B0F7189BDA0A85778BA0946BE568A2
    pad0 = 0x139ABA9C72719C329472DF449D148051
    a, u = 0x923441459AC822112247786EE1A4ACB3, 0x12450112518BD2410DD0A99FEAFB5C93
    for h in (ONE, 3, h0):
        b = mul(h, a) ^ pad0
        c = mul(h, mul(h, b) ^ pad0) ^ pad0
        v = mul(h, u) ^ pad0
        assert h in quadratic(b ^ u, v ^ u, c ^ v)
        assert div(b ^ v, a ^ u) == h
    print('SYNTHETIC_TWO_JOB_PAIR_AND_QUADRATIC_BRACKET_POSITIVES PASS')
    d = original(path)
    counts = {'two_anchor_heldout': 0, 'bracket_roots': 0,
              'samejob_roots': 0, 'samejob_crossjob_heldout': 0, 'target_hits': 0}
    for layout in range(8):
        A, B, C, U, V = (view(d[k], layout) for k in 'ABCUV')
        assert all(view(view(x, layout), layout) == x for x in d.values())
        # Two genuine original one-step pairs, then predict a complete intermediate.
        h = div(B ^ V, A ^ U)
        p = B ^ mul(h, A)
        predicted = mul(h, B) ^ p
        counts['two_anchor_heldout'] += (mul(h, predicted) ^ p == C)
        counts['target_hits'] += coupon_pass(h, p, B, layout)
        # Independently known 0420 U->V plus 0417 B->missing->C bracket.
        roots = quadratic(B ^ U, V ^ U, C ^ V)
        counts['bracket_roots'] += len(roots)
        for h in roots:
            p = V ^ mul(h, U)
            m = mul(h, B) ^ p
            assert mul(h, m) ^ p == C
            counts['target_hits'] += coupon_pass(h, p, B, layout)
        # Independently known 0417 A->B, bracket B->missing->C.
        roots = quadratic(B ^ A, B ^ A, C ^ B)
        counts['samejob_roots'] += len(roots)
        for h in roots:
            p = B ^ mul(h, A)
            m = mul(h, B) ^ p
            assert mul(h, m) ^ p == C
            counts['samejob_crossjob_heldout'] += (mul(h, U) ^ p == V)
            counts['target_hits'] += coupon_pass(h, p, B, layout)
    print('ORIGINAL_EIGHT_LAYOUTS', counts)
    assert counts == {'two_anchor_heldout':0, 'bracket_roots':12,
                      'samejob_roots':4, 'samejob_crossjob_heldout':0, 'target_hits':0}


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'resources/evidence/print/spool-reconstruction.log'
    test(path)
