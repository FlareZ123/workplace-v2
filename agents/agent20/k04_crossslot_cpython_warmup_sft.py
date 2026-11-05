"""Original-source CPython MT warmup search from authenticated REC8 binary carriers.

Source test deliberately excludes disputed printer attempt2 K04. If a seeded
producer reproduces the intact first printer packet, its seed and phase would
support a heldout second-packet test and eventual full selected coupon check.
No source says these carrier values were printer-generator seeds.
"""
from hashlib import sha256
from pathlib import Path
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2] / 'resources'
SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
ACCEPTANCE_SHA = '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
ROUTE_SHA = 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5'
TELEMETRY_SHA = '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
TRANSFER_SHA = '32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf'
LIMIT = 131072
SIX = {
    'K01': '049AAB2E1CDE7A82CD7C60234303C91A',
    'K02': '0D7E3AB56FB75DA3EB0E2E06786D239E',
    'K03': '1384AF96E25D6ADA666209CB55E062FA',
    'K05': 'FF8B78200A56E8586DCDA00EF01E4572',
    'K06': '5DBF40EE52FAAED9A536D3326CF0D95A',
    'K07': '93495F5E425AB8E592123DABAEB68545',
}
OTHER = {
    'original-route-mask': '8556C8CB6140A7F9A5123AC7571BEE1C',
    'original-desk-nonce': '5F933DA6A1BD03C32DA5CBC25344F497',
    'original-k02-prehash': 'E1A5E474BAD7E853A2E8C71D3317D507',
    'original-k07-prehash': '8947CEDCB9CC73BAB7E87BE63302C5C9',
}


def pinned(relative, expected):
    data = (ROOT / relative).read_bytes()
    assert sha256(data).hexdigest() == expected
    return data


def pack_four(words, endian, reverse):
    selected = words[::-1] if reverse else words
    return b''.join(v.to_bytes(4, endian) for v in selected)


def first_packet_match(words, target):
    """Return matching complete offset/serialization tuples over a whole-word stream."""
    native_first = int.from_bytes(target[:4], 'little')
    swapped_first = int.from_bytes(target[:4], 'big')
    native_last = int.from_bytes(target[-4:], 'little')
    swapped_last = int.from_bytes(target[-4:], 'big')
    matches, first_hits = [], 0
    for offset in range(len(words) - 3):
        first = words[offset]
        last = words[offset + 3]
        if first in (native_first, swapped_first, native_last, swapped_last) or last in (native_first, swapped_first, native_last, swapped_last):
            first_hits += 1
            four = words[offset:offset + 4]
            for endian in ('little', 'big'):
                for reverse in (False, True):
                    if pack_four(four, endian, reverse) == target:
                        matches.append((offset, endian, reverse))
    return matches, first_hits


def stream(seed):
    generator = random.Random(seed)
    return [generator.getrandbits(32) for _ in range(LIMIT + 3)]


def source_carriers():
    accept = json.loads(pinned('acceptance.json', ACCEPTANCE_SHA))
    for slot, value in SIX.items():
        assert sha256(bytes.fromhex(value)).hexdigest() == accept['slot_sha256'][slot]
    route = json.loads(pinned('evidence/recovery-routing.json', ROUTE_SHA))
    assert route['K04']['masked_component'] == OTHER['original-route-mask']
    assert route['K08']['desk_nonce'] == OTHER['original-desk-nonce']
    records = [json.loads(x) for x in pinned('evidence/telemetry/freeze-export.jsonl', TELEMETRY_SHA).splitlines()]
    from datetime import datetime, timezone
    start = datetime.fromisoformat('2026-10-03T21:13:40+00:00')
    stop = datetime.fromisoformat('2026-10-03T21:13:48+00:00')
    selected = {}
    for record in records:
        stamp = datetime.fromisoformat(record['ts']).astimezone(timezone.utc)
        if (record['tag'] == 'LT-204' and record['field'] == 'DIAG_WORD' and
                record['quality'] == 'GOOD' and record['state'] == 'HOLD' and
                start <= stamp < stop):
            seq = record['seq']
            if seq not in selected or record['revision'] > selected[seq]['revision']:
                selected[seq] = record
    assert b''.join(selected[i]['value'].to_bytes(2, 'big') for i in range(8)).hex().upper() == OTHER['original-k02-prehash']
    transfers = [json.loads(x) for x in pinned('evidence/transfers/transfer-audit.jsonl', TRANSFER_SHA).splitlines()]
    checkpoints = {}
    for row in transfers:
        if row['kind'] == 'CHUNK' and row['transfer'] == 'AX-7782':
            seq = row['seq']
            if seq not in checkpoints or row['attempt'] > checkpoints[seq]['attempt']:
                checkpoints[seq] = row
    assert ''.join(checkpoints[i]['checkpoint'] for i in range(8)) == OTHER['original-k07-prehash']
    # The alternative input blocks below are original source prehashes, not
    # the accepted K02/K07 digests. They may carry unrelated generator entropy.
    values = dict(SIX)
    values.update(OTHER)
    inputs = []
    for label, v in values.items():
        data = bytes.fromhex(v)
        inputs += [(label + ':raw', data),
                   (label + ':sha256', sha256(data).digest()),
                   (label + ':sha256-first16', sha256(data).digest()[:16])]
    return inputs


def seed_variants(data):
    return (('bytes', data), ('integer-big', int.from_bytes(data, 'big')),
            ('integer-little', int.from_bytes(data, 'little')),
            ('hex-utf8', data.hex()))


def controls():
    b = bytes.fromhex(SIX['K01'])
    origin = 4099
    sample = stream(b)
    planted = pack_four(sample[origin:origin + 4], 'big', True)
    assert first_packet_match(sample, planted)[0] == [(origin, 'big', True)]
    sample2 = stream(int.from_bytes(b, 'little'))
    planted2 = pack_four(sample2[7011:7015], 'little', False)
    assert first_packet_match(sample2, planted2)[0] == [(7011, 'little', False)]


def main():
    raw = pinned('evidence/print/spool-reconstruction.log', SPOOL_SHA)
    payloads = re.findall(rb'PAYLOAD=([0-9A-F]{32})', raw)
    assert len(payloads) == 133
    # Decoder touches only source-record row0; selected row129 copied bytes are withheld.
    source_packet = bytes.fromhex(payloads[0].decode('ascii'))
    assert source_packet.hex().upper() == 'FBBBC54356483F5864BB3F06794518A5'
    controls()
    results, firstword = [], 0
    families = 0
    for label, data in source_carriers():
        for form, seed in seed_variants(data):
            families += 1
            predictions, first_hits = first_packet_match(stream(seed), source_packet)
            firstword += first_hits
            results.extend((label, form, *match) for match in predictions)
    assert families == 120
    print(json.dumps({'result': 'MATCHES' if results else 'NO_FULL_SOURCE_PACKET_MATCH',
                      'authenticated_input_blocks': 10,
                      'derived_carrier_variants': 30,
                      'CPython_seeding_rules': 4,
                      'source_first_packet_starts_per_seed': LIMIT,
                      'total_complete_packet_opportunities': families * LIMIT * 4,
                      'first_or_last_word_gate_hits': firstword,
                      'complete_source_packet_hits': len(results),
                      'original_source_hits': results,
                      'genuine_seeded_synthetic_controls': 'PASS',
                      'K04_or_K08_genuine_values_recovered': False}, indent=2))


if __name__ == '__main__':
    main()
