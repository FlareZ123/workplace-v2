"""K04 selected-job copy hypotheses: carry arithmetic, bit slippage, and spool parity.

Run in an unmodified workplace-v2 checkout, from any working directory.
All tests use the supplied original source and untouched K04 SHA256 commitment.
"""
from hashlib import sha256
from itertools import combinations, product
from json import loads
from pathlib import Path
from re import findall

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / 'resources/evidence/print/spool-reconstruction.log'
TARGETS = ROOT / 'resources/acceptance.json'
EXPECTED_SPOOL = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
M = (1 << 128) - 1
BIT_REVERSE = bytes(int(f'{i:08b}'[::-1], 2) for i in range(256))


def accepted(coupon, target):
    return sha256(bytes(x ^ y for x, y in zip(coupon, MASK))).hexdigest() == target


def rot(x, n):
    return ((x << n) | (x >> (128 - n))) & M if n else x


def rows_and_target():
    source = SPOOL.read_bytes()
    assert sha256(source).hexdigest() == EXPECTED_SPOOL
    target = loads(TARGETS.read_text('utf-8'))['slot_sha256']['K04']
    assert target == '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
    rows = []
    for line in source.decode().splitlines():
        if 'PAYLOAD=' not in line:
            continue
        row = dict(findall(r'([A-Z]+)=([^ ]+)', line))
        row['time'] = line.split(' ', 1)[0]
        row['bytes'] = bytes.fromhex(row['PAYLOAD'])
        rows.append(row)
    same = [x for x in rows if x['JOB'] == 'PS-261003-0417']
    assert len(rows) == 133 and len(same) == 4
    mapping = {'L': ('2026-10-03T16:45:00+00:00', 'ACK', 'LABEL', '1'),
               'A': ('2026-10-03T18:01:00Z', 'REQUESTED', 'RECOVER', '1'),
               'C': ('2026-10-03T18:02:00Z', 'ACK', 'RECOVER', '2'),
               'B': ('2026-10-03T18:03:00Z', 'REQUESTED', 'RECOVER', '3')}
    selected = {}
    for letter, meta in mapping.items():
        match = [x for x in same if (x['time'], x['STATE'], x['CLASS'], x['ATTEMPT']) == meta]
        assert len(match) == 1
        selected[letter] = match[0]['bytes']
    return rows, selected, target


def arithmetic_coupons(s):
    for width in (1, 2, 4, 8, 16):
        for order in ('little', 'big'):
            lane_values = [{key: int.from_bytes(buf[i:i+width], order) for key, buf in s.items()}
                           for i in range(0, 16, width)]
            options = []
            for v in lane_values:
                a, b, c, l = (v[k] for k in 'ABCL')
                modulus = 1 << (8 * width)
                expr = [a+b-c, a+c-b, b+c-a, a+b-l, a+l-b, b+l-a,
                        a+b+c-l, a+b+l-c, a+c+l-b, b+c+l-a, a+b, a-b, b-a, a^b]
                expr += [2*v[x]-v[y] for x in 'ABCL' for y in 'ABCL' if x != y]
                opt = [[n % modulus] for n in expr]
                total = (a+b) % modulus
                opt.append([total//2, total//2+modulus//2] if total % 2 == 0 else [])
                options.append(opt)
            for operation in range(len(options[0])):
                for values in product(*(lane[operation] for lane in options)):
                    yield b''.join(n.to_bytes(width, order) for n in values)


def bit_slip_coupons(s):
    nonbyte = [i for i in range(1, 128) if i % 8]
    for reverse in (False, True):
        buf = {k: bytes(BIT_REVERSE[b] for b in data) if reverse else data for k, data in s.items()}
        v = {k: int.from_bytes(data, 'big') for k, data in buf.items()}
        c = v['C']
        for n in 'ABL':
            for shift in nonbyte:
                yield (c ^ rot(v[n], shift)).to_bytes(16, 'big')
                yield (rot(c, shift) ^ v[n]).to_bytes(16, 'big')
                yield rot(v[n], shift).to_bytes(16, 'big')
        for a, b in (('A', 'B'), ('A', 'L'), ('B', 'L')):
            for k in nonbyte:
                ak = rot(v[a], k)
                for j in nonbyte:
                    yield (c ^ ak ^ rot(v[b], j)).to_bytes(16, 'big')


def parity_coupons(rows):
    # 133 rows, including suspect selected copied ACK as a possible XOR donor.
    values = [int.from_bytes(row['bytes'], 'big') for row in rows]
    for n in (1, 2, 3):
        for indices in combinations(range(len(values)), n):
            v = 0
            for i in indices:
                v ^= values[i]
            yield v.to_bytes(16, 'big')
    # Coherent full-print cohorts are also possible XOR parity carriers.
    retained = [r for r in rows if r['time'] != '2026-10-03T18:02:00Z']
    groups = [rows[:128], retained, retained[128:]]
    for field in ('CLASS', 'DEST', 'STATE'):
        groups += [[r for r in retained if r[field] == value] for value in sorted({r[field] for r in retained})]
    for n in (4, 8, 16, 32, 64, 128):
        groups += [rows[:n], rows[128-n:128]]
    for group in groups:
        v = 0
        for row in group:
            v ^= int.from_bytes(row['bytes'], 'big')
        yield v.to_bytes(16, 'big')


def screen(factory, args, target):
    seen = set()
    hits = []
    for coupon in factory(*args):
        if coupon in seen:
            continue
        seen.add(coupon)
        if accepted(coupon, target):
            hits.append(coupon.hex().upper())
    return len(seen), hits


def main():
    rows, s, target = rows_and_target()
    planted_arithmetic = next(arithmetic_coupons(s))
    synthetic_target = sha256(bytes(x ^ y for x, y in zip(planted_arithmetic, MASK))).hexdigest()
    assert screen(arithmetic_coupons, (s,), synthetic_target)[1]
    planted_bitslip = (int.from_bytes(s['C'], 'big') ^ rot(int.from_bytes(s['A'], 'big'), 3)
                       ^ rot(int.from_bytes(s['B'], 'big'), 13)).to_bytes(16, 'big')
    synthetic_target = sha256(bytes(x ^ y for x, y in zip(planted_bitslip, MASK))).hexdigest()
    assert screen(bit_slip_coupons, (s,), synthetic_target)[1]
    planted_parity = bytes(a ^ b ^ c for a, b, c in zip(*(x['bytes'] for x in rows[:3])))
    synthetic_target = sha256(bytes(x ^ y for x, y in zip(planted_parity, MASK))).hexdigest()
    assert screen(parity_coupons, (rows,), synthetic_target)[1]
    for name, factory, args in [('arithmetic', arithmetic_coupons, (s,)),
                                ('bit_slippage', bit_slip_coupons, (s,)),
                                ('printer_parity_1_3_and_groups', parity_coupons, (rows,))]:
        count, hits = screen(factory, args, target)
        print(f'{name}: unique={count} original_K04_hits={len(hits)} candidates={hits}')


if __name__ == '__main__':
    main()
