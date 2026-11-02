"""Source-anchored H17 byte-codec and cross-stage K04 pilot (2026-11-02).

Freezes two low-entropy global byte-codecs: affine Z/256Z and GF(2^8).
Separates target commitment search from a same-job 0420 cross-stage test.
No claim that any such codec was the genuine printer/copier implementation.
"""
import hashlib
import json
import re
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2] / 'resources'
SPOOL_SHA256 = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def gf8_mul(a, b):
    product = 0
    for _ in range(8):
        if b & 1:
            product ^= a
        b >>= 1
        a = ((a << 1) ^ (0x1B if a & 0x80 else 0)) & 255
    return product


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def main():
    raw = (ROOT / 'evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    records = {}
    lines = raw.decode('ascii').splitlines()
    for line in lines:
        m = re.search(r'JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})', line)
        if m:
            job, attempt, status, klass, payload = m.groups()
            records[(job, int(attempt), status, klass)] = bytes.fromhex(payload)
    assert len(records) == 133
    selected = records[('0417', 2, 'ACK', 'RECOVER')]
    assert selected.hex().upper() == 'A9A9DC5731A5E2AE879C47215C2559D5'
    routing = json.loads((ROOT / 'evidence/recovery-routing.json').read_text())
    accept = json.loads((ROOT / 'acceptance.json').read_text())
    mask = bytes.fromhex(routing['K04']['masked_component'])
    target = bytes.fromhex(accept['slot_sha256']['K04'])
    prior0420 = records[('0420', 1, 'ACK', 'STORES')]
    late0420 = records[('0420', 2, 'ACK', 'RECOVER')]
    prior0417 = records[('0417', 1, 'ACK', 'LABEL')]
    requested0417 = (records[('0417', 1, 'REQUESTED', 'RECOVER')],
                     records[('0417', 3, 'REQUESTED', 'RECOVER')])

    start = perf_counter()
    checks = 0
    matches = []
    best_source_agreement = {}
    synthetic_seen = False
    synthetic_component = xor(bytes((23 * x + 94) & 255 for x in selected), mask)
    synthetic_target = hashlib.sha256(synthetic_component).digest()
    for codec in ('integer-mod256', 'gf256'):
        maximal = (0, None)
        for a in range(1, 256):
            if codec == 'integer-mod256' and not a & 1:
                continue
            table = [((a*x) & 255) if codec == 'integer-mod256' else gf8_mul(a,x) for x in range(256)]
            for b in range(256):
                transform = (lambda x: (table[x]+b)&255) if codec == 'integer-mod256' else (lambda x: table[x]^b)
                source_out = bytes(transform(x) for x in prior0420)
                agreement = sum(x == y for x,y in zip(source_out,late0420))
                if agreement > maximal[0]:
                    maximal = (agreement, (a,b))
                for side in ('payload', 'mask'):
                    inp = selected if side == 'payload' else mask
                    transformed = bytes(transform(x) for x in inp)
                    component = xor(transformed, mask) if side == 'payload' else xor(selected, transformed)
                    checks += 1
                    candidate_hash = hashlib.sha256(component).digest()
                    if candidate_hash == target:
                        matches.append((codec,a,b,side,component.hex().upper()))
                    if (codec,a,b,side) == ('integer-mod256',23,94,'payload'):
                        assert candidate_hash == synthetic_target
                        synthetic_seen = True
        best_source_agreement[codec] = {'max_equal_bytes':maximal[0], 'params':maximal[1]}
    assert synthetic_seen and checks == 196096
    pad = xor(prior0420,late0420)
    predicted0417 = xor(prior0417,pad)
    out = {
        'model': 'single global invertible 8bit affine map on one 16-byte source',
        'selected_source_job': 'PS-261003-0417 RECOVER ACK attempt 2',
        'source_0420_pair_complete_codec_match': False,
        'source_0420_best_16byte_agreement': best_source_agreement,
        'crossjob_xorpad_predicted_0417_hex':predicted0417.hex().upper(),
        'crossjob_xorpad_matches_known_request': [predicted0417==r for r in requested0417],
        'complete_original_commitment_checks':checks,
        'synthetic_positive_control': synthetic_seen,
        'original_K04_commitment_matches':matches,
        'elapsed_seconds':round(perf_counter()-start,3),
    }
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    main()
