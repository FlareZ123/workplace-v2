"""K04 source-only MT twist syndrome for seven-future-donor packet hypotheses.

Recover native X556 from intact printer row73 and cross-check two historical
donor-placement corpora without consulting K04/K08 target commitments.
"""
import hashlib
import itertools
import json
import random
import re
import struct
import zlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'resources'
E = ROOT / 'evidence'
U = 0xffffffff
MAG = 0x9908b0df
PINS = {
    'print/spool-reconstruction.log': '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
    'transfers/transfer-audit.jsonl': '32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
    'telemetry/freeze-export.jsonl': '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f',
    'recorder/trip-recorder.raw': '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba',
}


def untemper(x):
    for k, left, m in ((18, False, U), (15, True, 0xefc60000),
                       (7, True, 0x9d2c5680), (11, False, U)):
        y = x
        for _ in range(6):
            y = x ^ (((y << k) & m) if left else (y >> k))
        x = y & U
    return x


def twist(a, b):
    return (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) ^ (MAG if b & 1 else 0)


def syndrome(d1179, d1348, d1575, x556):
    # X1179=X952^tw(X555,X556); X1575=X1348^tw(X951,X952).
    # The only relevant bits of unknown X555 and X951 are their high bits.
    return [(h555, h951, x952)
            for h555 in (0, 0x80000000)
            for x952 in [d1179 ^ twist(h555, x556)]
            for h951 in (0, 0x80000000)
            if d1575 == (d1348 ^ twist(h951, x952))]


def source_words():
    raw = (E / 'print/spool-reconstruction.log').read_bytes()
    rows = [bytes.fromhex(b.decode()) for b in re.findall(rb'PAYLOAD=([0-9A-F]{32})', raw)]
    assert len(rows) == 133
    # In the existing p951 model, intact routine job 0373 starts native stage556.
    assert b'JOB=PS-261003-0373' in raw
    assert b'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in raw
    # Row129 (selected K04) is never read or used for a state equation.
    return [untemper(int.from_bytes(rows[73][i:i+4], 'little')) for i in (0, 4, 8)]


def groups():
    telemetry = [json.loads(s) for s in (E / 'telemetry/freeze-export.jsonl').read_text().splitlines()]
    best = {}
    lo = datetime.fromisoformat('2026-10-03T21:13:40+00:00')
    hi = datetime.fromisoformat('2026-10-03T21:13:48+00:00')
    for x in telemetry:
        if (x.get('tag') == 'LT-204' and x.get('field') == 'DIAG_WORD'
                and x.get('quality') == 'GOOD' and x.get('state') == 'HOLD'
                and x.get('seq') in range(8)
                and lo <= datetime.fromisoformat(x['ts']) < hi):
            k = x['seq']
            if k not in best or x['revision'] > best[k]['revision']:
                best[k] = x
    assert sorted(best) == list(range(8))
    k02 = b''.join(int(best[i]['value']).to_bytes(2, 'big') for i in range(8))
    assert hashlib.sha256(k02).digest()[:16].hex().upper() == '0D7E3AB56FB75DA3EB0E2E06786D239E'

    seals = [json.loads(s) for s in (E / 'maintenance/seal-receipts.jsonl').read_text().splitlines()]
    best = {}
    for x in seals:
        if (x.get('permit') == 'PTW-417' and x.get('state') == 'CLOSED'
                and x.get('fitment') == 'AS_LEFT' and x.get('signed') is True):
            k = x['bay']
            if k not in best or x['revision'] > best[k]['revision']:
                best[k] = x
    serials = [best[k]['serial'] for k in 'BDAC']
    assert hashlib.sha256('|'.join(serials).encode()).digest()[:16].hex().upper() == '1384AF96E25D6ADA666209CB55E062FA'
    ptw = bytes.fromhex(''.join(s.rsplit('-', 1)[-1] for s in serials))

    transfers = [json.loads(s) for s in (E / 'transfers/transfer-audit.jsonl').read_text().splitlines()]
    best = {}
    for x in transfers:
        if x['kind'] == 'CHUNK' and x['transfer'] == 'AX-7782':
            k = x['seq']
            if k not in best or x['attempt'] > best[k]['attempt']:
                best[k] = x
    assert sorted(best) == list(range(8))
    k07 = b''.join(bytes.fromhex(best[i]['checkpoint']) for i in range(8))
    assert hashlib.sha256(k07).digest()[:16].hex().upper() == '93495F5E425AB8E592123DABAEB68545'
    return {
        'WN14': bytes.fromhex('049AAB2E1CDE7A82CD7C60234303C91A'),
        'K02raw': k02,
        'PTW417': ptw,
        'K05raw': bytes.fromhex('FF8B78200A56E8586DCDA00EF01E4572'),
        'K06raw': bytes.fromhex('5DBF40EE52FAAED9A536D3326CF0D95A'),
        'K07raw': k07,
    }


def decode(block, little, tempered, reverse, choice):
    parts = [block[i:i+4] for i in range(0, 16, 4)]
    if reverse:
        parts.reverse()
    if choice == 'first':
        parts = parts[:3]
    if choice == 'last':
        parts = parts[1:]
    vals = [int.from_bytes(p, 'little' if little else 'big') for p in parts]
    return [untemper(v) if tempered else v for v in vals]


def node50_quartets():
    blob = (E / 'recorder/trip-recorder.raw').read_bytes()
    assert blob[:8] == b'TRP2DUMP'
    assert struct.unpack_from('<HHI', blob, 8) == (2, 24, 88)
    controls = {}
    for n in range(88):
        rec = blob[16 + 24*n:16 + 24*(n+1)]
        if (zlib.crc32(rec[:20]) & U) != struct.unpack_from('<I', rec, 20)[0]:
            continue
        _, node, _, _, seq = struct.unpack_from('<I H B B I', rec)
        if node == 50:
            assert seq not in controls
            controls[seq] = rec[12:16]
    assert sorted(controls) == list(range(72))
    return [(seq, [controls[seq+j] for j in range(4)]) for seq in range(69)]


def native_coupon(d, x556, x557, x558):
    d1179, d1180, d1181, d1347, d1348, d1574, d1575 = d
    result = []
    for h555, h951, x952 in syndrome(d1179, d1348, d1575, x556):
        delta = d1574 ^ d1347
        lowbit = delta >> 31
        core = delta ^ (MAG if lowbit else 0)
        assert core >> 31 == 0
        x951 = h951 | ((core & 0x3fffffff) << 1) | lowbit
        assert twist(((core >> 30) & 1) << 31, x951) == delta
        x953 = d1180 ^ twist(x556, x557)
        x954 = d1181 ^ twist(x557, x558)
        result.append((x951, x952, x953, x954))
    return result


def main():
    for rel, expected in PINS.items():
        assert hashlib.sha256((E / rel).read_bytes()).hexdigest() == expected
    x556, x557, x558 = source_words()
    source = groups()
    assert all(len(b) == 16 for b in source.values())
    checked = 0
    accepted = []
    for first, second in itertools.permutations(source, 2):
        for choice in ('first', 'last'):
            for a, b, c, d, e, f in itertools.product((False, True), repeat=6):
                left = decode(source[first], a, b, c, choice)
                right = decode(source[second], d, e, f, 'all')
                checked += 1
                if native_coupon(left + right, x556, x557, x558):
                    accepted.append((first, second, choice, a, b, c, d, e, f))
    assert checked == 3840 and accepted == [], (checked, accepted)
    print('SIX_SOURCE_GROUPS', checked, 'SOURCE_COMPATIBLE', len(accepted))

    quartets = node50_quartets()
    checked = 0
    accepted = []
    for family, original in source.items():
        for choice in ('first', 'last'):
            for a, b, c in itertools.product((False, True), repeat=3):
                left = decode(original, a, b, c, choice)
                for seq, raw in quartets:
                    for d, e, f in itertools.product((False, True), repeat=3):
                        block = raw[::-1] if f else raw
                        right = [untemper(int.from_bytes(v, 'little' if d else 'big'))
                                 if e else int.from_bytes(v, 'little' if d else 'big')
                                 for v in block]
                        checked += 1
                        if native_coupon(left + right, x556, x557, x558):
                            accepted.append((family, choice, a, b, c, seq, d, e, f))
    assert checked == 52992 and accepted == [], (checked, accepted)
    print('NODE50_PLUS_SOURCE', checked, 'SOURCE_COMPATIBLE', len(accepted))

    for seed in (1, 8, 32, 127, 364, 606, 623):
        rng = random.Random(seed)
        native = [untemper(rng.getrandbits(32)) for _ in range(1580)]
        donors = [native[i] for i in (1179, 1180, 1181, 1347, 1348, 1574, 1575)]
        assert native_coupon(donors, *native[556:559]) == [tuple(native[951:955])]
        mutation = donors.copy()
        mutation[6] ^= 2
        assert native_coupon(mutation, *native[556:559]) == []
    print('SEVEN_GENUINE_SEEDED_FULL_COUPON_POSITIVES_PASS; SEVEN_SINGLE_BIT_NEGATIVES_PASS')
    print('PRINTER_NATIVE556', f'{x556:08X}', 'TARGET_BITS_AUTHENTICATED', 0)

if __name__ == '__main__':
    main()
