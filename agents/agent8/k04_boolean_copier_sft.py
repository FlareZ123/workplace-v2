"""One-file H-17 K04 same-job Boolean-gate copier experiment (read-only).

Usage: python k04_boolean_copier_sft.py PATH_TO_H17_RESOURCES
"""
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / 'resources'
raw = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
rows = [s for s in raw.decode('ascii').splitlines() if 'JOB=PS-261003-0417 ' in s]
assert len(rows) == 4
selectors = [('16:45:00', 'LABEL', 'ACK', 1), ('18:01:00', 'RECOVER', 'REQUESTED', 1),
             ('18:02:00', 'RECOVER', 'ACK', 2), ('18:03:00', 'RECOVER', 'REQUESTED', 3)]
donors = []
for time, klass, state, attempt in selectors:
    selected = [s for s in rows if time in s and f'CLASS={klass}' in s
                and f'STATE={state}' in s and f'ATTEMPT={attempt}' in s]
    assert len(selected) == 1
    donors.append(bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', selected[0]).group(1)))
assert donors[2].hex().upper() == 'A9A9DC5731A5E2AE879C47215C2559D5'
mask = bytes.fromhex(json.loads((root / 'evidence/recovery-routing.json').read_text())['K04']['masked_component'])
target = bytes.fromhex(json.loads((root / 'acceptance.json').read_text())['slot_sha256']['K04'])


def profiles(sources):
    return [sum(((d[byte] >> bit) & 1) << j for j, d in enumerate(sources))
            for byte in range(16) for bit in range(8)]


def packet(profile, truth_table):
    output = bytearray(16)
    for i, value in enumerate(profile):
        output[i // 8] |= ((truth_table >> value) & 1) << (i % 8)
    return bytes(output)


for name, source_indices, expected_overlap, planted in [
    ('three_earlier_or_later', [0, 1, 3], 3, 0x96),
    ('four_including_ack_copy', [0, 1, 2, 3], 4, 0x6996),
]:
    inputs = [donors[i] for i in source_indices]
    p = profiles(inputs)
    assert set(p) == set(range(1 << len(inputs)))
    total = 1 << (1 << len(inputs))
    planted_digest = hashlib.sha256(bytes(a ^ b for a, b in zip(packet(p, planted), mask))).digest()
    seen = set()
    hits = []; direct_hits = []; plant_hits = 0; mosaic = 0
    for truth in range(total):
        coupon = packet(p, truth)
        assert coupon not in seen
        seen.add(coupon)
        mosaic += all(coupon[i] in {d[i] for d in donors} for i in range(16))
        component = bytes(a ^ b for a, b in zip(coupon, mask))
        actual_digest = hashlib.sha256(component).digest()
        if actual_digest == target:
            hits.append((truth, component.hex().upper()))
        if hashlib.sha256(coupon).digest() == target:
            direct_hits.append(truth)
        plant_hits += actual_digest == planted_digest
    assert len(seen) == total and mosaic == expected_overlap and plant_hits == 1
    print(json.dumps({'model': name, 'fully_observed_profiles': len(set(p)),
          'distinct_coupons': total, 'outside_prior_same_offset_byte_mosaic': total - mosaic,
          'original_masked_hits': hits, 'original_direct_hits': direct_hits,
          'synthetic_positive_hits': plant_hits}, sort_keys=True))
    assert not hits and not direct_hits
