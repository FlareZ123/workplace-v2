"""Original-only H-17 27 matched PTW/PS IDs and four per-bay packet encoders.
No target digest consulted unless a producer predicts every authentic held-out pair.
"""
import collections, hashlib, json, re
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'resources'
SEAL = ROOT / 'evidence/maintenance/seal-receipts.jsonl'
SPOOL = ROOT / 'evidence/print/spool-reconstruction.log'
assert hashlib.sha256(SEAL.read_bytes()).hexdigest() == 'c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
receipts = collections.defaultdict(list)
for line in SEAL.read_text().splitlines():
    r = json.loads(line)
    receipts[int(r['permit'].split('-')[-1])].append(r)
packets = {}
for line in SPOOL.read_text().splitlines():
    m = re.search(r'JOB=PS-261003-(\d{4}).*?PAYLOAD=([0-9A-F]{32})', line)
    if m and 390 <= int(m[1]) <= 416:
        packets[int(m[1])] = bytes.fromhex(m[2])
groups = collections.defaultdict(list)
for n in range(390, 417):
    assert len(receipts[n]) == 1 and n in packets
    rec = receipts[n][0]
    groups[rec['bay']].append((n, bytes.fromhex(rec['serial'][3:]), packets[n]))
assert sorted((b, len(v)) for b, v in groups.items()) == [('A', 8), ('B', 4), ('C', 9), ('D', 6)]
U = 0xFFFFFFFF

def gf_mul(x, y):
    z = 0
    while y:
        if y & 1:
            z ^= x
        y >>= 1
        x = (x << 1) ^ (0x11B if x & 128 else 0)
        x &= 255
    return z

def gf_pow(x, n):
    a = 1
    while n:
        if n & 1:
            a = gf_mul(a, x)
        x = gf_mul(x, x)
        n >>= 1
    return a

def byte_map_fit(x1, y1, x2, y2):
    if any(a == c for a, c in zip(x1, x2)):
        return None
    a = tuple(gf_mul(b ^ d, gf_pow(c ^ e, 254)) for b, d, c, e in zip(y1, y2, x1, x2))
    b = tuple(v ^ gf_mul(u, x) for v, u, x in zip(y1, a, x1))
    return a, b

def byte_map_run(x, fit):
    a, b = fit
    return bytes(gf_mul(u, v) ^ t for u, v, t in zip(a, x, b))

def ring_fit(x1, y1, x2, y2):
    dx, dy = (x2 - x1) & U, (y2 - y1) & U
    tz = (dx & -dx).bit_length() - 1 if dx else 32
    if tz > 12 or dy % (1 << tz):
        return ()
    mod = 1 << (32 - tz)
    a0 = ((dy >> tz) * pow(dx >> tz, -1, mod)) % mod
    return tuple(((a0 + k * mod) & U, (y1 - (a0 + k * mod) * x1) & U) for k in range(1 << tz))

def rot(x, shift):
    return ((x << shift) | (x >> (32 - shift))) & U if shift else x

# Source-independent planted controls for all four issuer families.
x1, x2, x3 = b'\x01\x02\x03\x04', b'\x05\x06\x07\x08', b'\x09\x0A\x0B\x0C'
a, b = (2, 3, 5, 7), (16, 32, 48, 64)
encode = lambda x: bytes(gf_mul(a[i], x[i]) ^ b[i] for i in range(4))
fit = byte_map_fit(x1, encode(x1), x2, encode(x2))
assert fit and byte_map_run(x3, fit) == encode(x3)
assert (5, 7) in ring_fit(1, 12, 2, 17)
assert (5 * 3 + 7) & U == 22
key = 0xCAFEBABE
origin, other = 0x12345678, 0x9ABCDEFF
hidden1, hidden2 = rot(origin, 7) ^ key, rot(other, 7) ^ key
learned_key = hidden1 ^ rot(origin, 7)
assert (rot(other, 7) ^ learned_key) == hidden2
salt = bytes.fromhex('D331F0A1')
observation1 = bytes(x ^ y for x, y in zip(x1, salt))
observation2 = bytes(x ^ y for x, y in zip(x2, salt))
learned_salt = bytes(x ^ y for x, y in zip(x1, observation1))
assert bytes(x ^ y for x, y in zip(x2, learned_salt)) == observation2

holdout_tests = 0
full_matches = []
for bay, rows in sorted(groups.items()):
    earlier, held = sorted(rows)[:2], sorted(rows)[2:]
    for s_endian, p_endian, word, reversed_serial in product(('big', 'little'), ('big', 'little'), range(4), (False, True)):
        pair = lambda row: ((row[1][::-1] if reversed_serial else row[1]), row[2][4*word:4*word+4])
        (x1, y1), (x2, y2) = [pair(r) for r in earlier]
        observations = [pair(r) for r in held]
        fit = byte_map_fit(x1, y1, x2, y2)
        if fit:
            holdout_tests += 1
            if all(byte_map_run(x, fit) == y for x, y in observations):
                full_matches.append((bay, 'gf256', s_endian, p_endian, word, reversed_serial))
        (sx1, sy1), (sx2, sy2) = ((int.from_bytes(x, s_endian), int.from_bytes(y, p_endian)) for x, y in ((x1, y1), (x2, y2)))
        for a, b in ring_fit(sx1, sy1, sx2, sy2):
            holdout_tests += 1
            if all(((a*int.from_bytes(x, s_endian)+b)&U) == int.from_bytes(y, p_endian) for x, y in observations):
                full_matches.append((bay, 'Z32', s_endian, p_endian, word, reversed_serial))
        pad = bytes(a ^ b for a, b in zip(x1, y1))
        holdout_tests += 1
        if all(bytes(a ^ b for a, b in zip(x, pad)) == y for x, y in observations):
            full_matches.append((bay, 'xor', s_endian, p_endian, word, reversed_serial))
        for shift in range(32):
            k = sy1 ^ rot(sx1, shift)
            holdout_tests += 1
            if all((rot(int.from_bytes(x, s_endian), shift) ^ k) == int.from_bytes(y, p_endian) for x, y in observations):
                full_matches.append((bay, 'rot-xor', s_endian, p_endian, word, reversed_serial, shift))
print('CONTROLS', sum(map(len, groups.values())), 'heldout_independent_records', sum(len(v)-2 for v in groups.values()))
print('SOURCE_ENCODER_HOLDOUT_ASSIGNMENTS', holdout_tests, 'ENTIRE_BAY_HOLDOUT_PASSES', len(full_matches))
print('PLANTED_POSITIVES', 'GF256_BYTE RING32 XORPAD ROTATE_XOR PASS')
assert holdout_tests == 4476 and not full_matches
