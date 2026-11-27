#!/usr/bin/env python3
"""Source-pinned 128-printer-job K08 component carrier; never reads quarantined PDF."""
from pathlib import Path
import argparse, hashlib, json, re
ap = argparse.ArgumentParser()
ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2] / 'resources')
root = ap.parse_args().root
spool = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(spool).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
route = (root / 'evidence/recovery-routing.json').read_bytes()
assert hashlib.sha256(route).hexdigest() == 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
acc = (root / 'acceptance.json').read_bytes()
assert hashlib.sha256(acc).hexdigest() == '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
nonce = bytes.fromhex(json.loads(route)['K08']['desk_nonce'])
target = bytes.fromhex(json.loads(acc)['slot_sha256']['K08'])
records = []
pat = re.compile(rb'\S+ JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)')
for row in spool.splitlines():
    m = pat.fullmatch(row)
    if m:
        records.append((int(m[1]), int(m[2]), m[3], m[4],
                        bytes.fromhex(m[5].decode()), m[6]))
assert len(records) == 133
ordinary = [x for x in records if 300 <= x[0] <= 427 and x[1] == 1 and x[2] == b'ACK']
assert len(ordinary) == 128 and sorted(x[0] for x in ordinary) == list(range(300, 428))
ordinary.sort(key=lambda x: x[0])
assert all(len(x[4]) == 16 for x in ordinary)

def pack(bits, little_bit_first=False):
    assert len(bits) == 128
    return bytes(sum(bits[j*8+k] << (k if little_bit_first else 7-k)
                     for k in range(8)) for j in range(16))

def check(c):
    global checks, hits
    for stage, data in (('direct', c),
                        ('nonce_xor', bytes(a ^ b for a, b in zip(c, nonce)))):
        checks += 1
        if hashlib.sha256(data).digest() == target:
            # Never emit an accepted secret component into public CI logs.
            hits.append(stage)

# Full one-bit-per-record payload planes, fixed lane and bit, reversible order views.
checks = 0
hits = []
payload_presentations = 0
payload_unique = set()
for lane in range(16):
    for plane in range(8):
        bits = [(x[4][lane] >> plane) & 1 for x in ordinary]
        for revrows in (False, True):
            selected = bits[::-1] if revrows else bits
            for little in (False, True):
                candidate = pack(selected, little)
                for revbytes in (False, True):
                    packet = candidate[::-1] if revbytes else candidate
                    payload_unique.add(packet)
                    check(packet)
                    payload_presentations += 1
assert payload_presentations == 1024

# Arbitrary Boolean map over nine CLASS/DEST pairs; exactly 128 source events.
pairs = sorted(set((x[3], x[5]) for x in ordinary))
assert len(pairs) == 9
codes = {p: i for i, p in enumerate(pairs)}
stream = [codes[(x[3], x[5])] for x in ordinary]
category_presentations = 0
category_unique = set()
for codebook in range(512):
    bits = [(codebook >> c) & 1 for c in stream]
    for shift in range(128):
        selected = bits[shift:] + bits[:shift]
        for little in (False, True):
            candidate = pack(selected, little)
            for revbytes in (False, True):
                packet = candidate[::-1] if revbytes else candidate
                category_unique.add(packet)
                check(packet)
                category_presentations += 1
assert category_presentations == 262144

# Two independent planted *complete* 16-byte component positives.
plant = bytes.fromhex('11223344556677889900AABBCCDDEEFF')
synthetic_target = hashlib.sha256(plant).digest()
plant_bits = [(plant[i//8] >> (7-i%8)) & 1 for i in range(128)]
synthetic_packets = [bytearray(x[4]) for x in ordinary]
for i, bit in enumerate(plant_bits):
    synthetic_packets[i][4] = (synthetic_packets[i][4] & 254) | bit
recovered = pack([p[4] & 1 for p in synthetic_packets])
assert recovered == plant and hashlib.sha256(recovered).digest() == synthetic_target
synthetic_categories = [(b'RECOVER', b'desk') if bit else (b'LABEL', b'bench')
                        for bit in plant_bits]
lookup = {(b'LABEL', b'bench'): 0, (b'RECOVER', b'desk'): 1}
recovered = pack([lookup[x] for x in synthetic_categories])
assert recovered == plant and hashlib.sha256(recovered).digest() == synthetic_target

print(json.dumps({
    'source': 'PS-0300..0427 ordinary ACKs',
    'payload_presentations': payload_presentations,
    'distinct_payload_components': len(payload_unique),
    'category_presentations': category_presentations,
    'distinct_category_components': len(category_unique),
    'K08_full_commitment_checks_with_nonce_xor': checks,
    'K08_hits': len(hits),
    'planted_payload_control': 'PASS',
    'planted_category_control': 'PASS'
}, sort_keys=True))
