"""Standalone H-17 source-only prime-field coupon producer experiment.

Run as a read-only Python 3 program with an optional ZIP/directory argument.
No accepted original component or verifier is modified.
"""
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import zipfile

SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
K04_SHA = '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
ZIP_SHA = 'e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7'
MASK = bytes.fromhex('8556C8CB6140A7F9A5123AC7571BEE1C')
PRIMES = (2**128 + 51, 2**128 - 159, 2**130 - 5)
MAX_VALUE = 1 << 128


def interpolate(x_data, y_data, x_query, p):
    """Return unique degree <len(data) polynomial evaluation in F_p."""
    assert len(x_data) == len(y_data) == 128
    x_data = [x % p for x in x_data]
    assert len(set(x_data)) == 128
    product = 1
    for x in x_data:
        product = product * (x_query - x) % p
    result = 0
    for i, (x_i, y_i) in enumerate(zip(x_data, y_data)):
        denominator = 1
        for j, x_j in enumerate(x_data):
            if i != j:
                denominator = denominator * (x_i - x_j) % p
        inv_denominator = pow(denominator, p - 2, p)
        quotient = pow((x_query - x_i) % p, p - 2, p)
        result = (result + y_i * inv_denominator * quotient) % p
    return result * product % p


def source(path):
    if path.is_file():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ZIP_SHA
        with zipfile.ZipFile(path) as z:
            return (z.read('evidence/print/spool-reconstruction.log'),
                    z.read('evidence/recovery-routing.json'), z.read('acceptance.json'))
    return ((path/'evidence/print/spool-reconstruction.log').read_bytes(),
            (path/'evidence/recovery-routing.json').read_bytes(),
            (path/'acceptance.json').read_bytes())


def positive_controls():
    rng = random.Random(20261109)
    for p in PRIMES:
        for series in (0, 1):
            x_data = list(range(128)) if series == 0 else list(range(0, 640, 5))
            checks = [128, 129, 130, 131, 132] if series == 0 else [661,662,663,684,685]
            # A true degree-8 prime-field source, with all 16-byte observations in range.
            coeffs = [rng.randrange(1 << 32) for _ in range(9)]
            def poly(x):
                v = 0
                for a in reversed(coeffs):
                    v = v * x + a
                return v % p
            observed = [poly(x) for x in x_data]
            assert all(x < MAX_VALUE for x in observed)
            for x in checks:
                predicted = interpolate(x_data, observed, x, p)
                assert predicted == poly(x), (hex(p), series, x)
                assert predicted < MAX_VALUE
    print('synthetic_true_primefield_polynomial_controls=30/30 PASS')


def main(path):
    positive_controls()
    spool, routing, acceptance = source(path)
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [r for r in spool.splitlines() if r.startswith(b'2026-')]
    assert len(rows) == 133
    assert b'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in rows[129]
    packets = [bytes.fromhex(re.search(rb'PAYLOAD=([0-9A-F]{32})', row).group(1).decode()) for row in rows]
    for i in range(128):
        assert f'JOB=PS-261003-{300+i:04d}'.encode() in rows[i]
    assert b'JOB=PS-261003-0448' in rows[131]
    assert b'JOB=PS-261003-0420' in rows[132]
    assert bytes.fromhex(json.loads(routing)['K04']['masked_component']) == MASK
    target = json.loads(acceptance)['slot_sha256']['K04']
    assert target == K04_SHA
    match = []
    count = 0
    whole_holdout = 0
    printable_predictions = 0
    examples = []
    for p in PRIMES:
        for schedule in ('ordinal', 'minute'):
            x_data = list(range(128)) if schedule == 'ordinal' else list(range(0, 640, 5))
            x_late = [128,129,130,131,132] if schedule == 'ordinal' else [661,662,663,684,685]
            for endian in ('big', 'little'):
                for direction in ('forward', 'reverse'):
                    buf = packets[:128] if direction == 'forward' else packets[:128][::-1]
                    y_data = [int.from_bytes(value, endian) for value in buf]
                    if any(y >= p for y in y_data):
                        raise AssertionError('Original source packet exceeds declared finite field')
                    values = [interpolate(x_data, y_data, x, p) for x in x_late]
                    heldouts = []
                    for pos in (3,4):
                        predicted = values[pos].to_bytes(16, endian) if values[pos] < MAX_VALUE else None
                        heldouts.append(predicted == packets[131 if pos == 3 else 132])
                    whole_holdout += sum(heldouts)
                    if values[1] < MAX_VALUE:
                        printed = values[1].to_bytes(16, endian)
                        component = bytes(a^b for a,b in zip(printed, MASK))
                        hit = hashlib.sha256(component).hexdigest() == target
                        printable_predictions += 1
                    else:
                        hit = False
                    count += 1
                    if hit:
                        match.append((p,schedule,endian,direction,component.hex().upper()))
                    examples.append({'prime':hex(p), 'coordinate':schedule,
                                     'endian':endian, 'direction':direction,
                                     'selected_in_16B':values[1] < MAX_VALUE,
                                     'holdout_whole_matches':sum(heldouts),
                                     'selected_original_hash_match':hit})
    assert count == 24
    print('source_SHA256', SPOOL_SHA)
    print('model_assignments',count)
    print('canonical_16B_selected_predictions',printable_predictions)
    print('genuine_late_ACK_whole_packet_matches',whole_holdout, '/ 48')
    print('full_original_K04_SHA256_matches',len(match))
    print('per_model',json.dumps(examples,separators=(',',':')))
    for entry in match:
        print('ORIGINAL_K04_HIT',entry)


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources')
