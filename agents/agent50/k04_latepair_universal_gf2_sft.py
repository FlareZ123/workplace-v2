"""H-17 source-pinned universal GF(2) packet-transition late-pair SFT.

A source-only 18:24 -> 18:25 calibration fixes the 128 unconstrained bits
left after fitting ordinary spool transitions 0->1 .. 126->127. The selected
18:02 physical packet is fully withheld from fit and heldout predictions.
No source says a common GF(2) issuer spans the ordinary and late classes.
"""
import hashlib
import json
import random
import re
import sys
import zipfile
from pathlib import Path

SHA_SPOOL = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK128 = (1 << 128) - 1


def load(path):
    p = Path(path)
    if p.is_file():
        with zipfile.ZipFile(p) as z:
            return (z.read('evidence/print/spool-reconstruction.log'),
                    json.loads(z.read('evidence/recovery-routing.json')),
                    json.loads(z.read('acceptance.json')))
    root = p / 'resources' if (p / 'resources').is_dir() else p
    return ((root / 'evidence/print/spool-reconstruction.log').read_bytes(),
            json.loads((root / 'evidence/recovery-routing.json').read_text()),
            json.loads((root / 'acceptance.json').read_text()))


def echelon_rows(vectors):
    basis = {}
    for i, source in enumerate(vectors):
        r = source
        c = 1 << i
        for pivot, (v, bits) in sorted(basis.items(), reverse=True):
            if (r >> pivot) & 1:
                r ^= v
                c ^= bits
        if r == 0:
            return None
        basis[r.bit_length() - 1] = (r, c)
    return basis


def coordinates(value, basis):
    mask = 0
    for pivot, (row, bits) in sorted(basis.items(), reverse=True):
        if (value >> pivot) & 1:
            value ^= row
            mask ^= bits
    assert value == 0
    return mask


def apply_transition(source, fit):
    vectors, basis, last_image = fit
    coeff = coordinates(source, basis)
    result = last_image if (coeff >> 127) & 1 else 0
    for i in range(127):
        if (coeff >> i) & 1:
            result ^= vectors[i + 1]
    return result


def fit_source(vectors):
    assert len(vectors) == 133 and all(0 <= v <= MASK128 for v in vectors)
    base = vectors[:128]
    basis = echelon_rows(base)
    assert basis is not None and len(basis) == 128
    coord = coordinates(vectors[131], basis)
    if not (coord >> 127) & 1:
        return None
    shifted = 0
    for i in range(127):
        if (coord >> i) & 1:
            shifted ^= base[i + 1]
    fit = (base, basis, vectors[132] ^ shifted)
    assert apply_transition(vectors[131], fit) == vectors[132]
    return fit


def positive_controls():
    rng = random.Random(20261108)
    # A genuine 128-bit unknown-feedback linear issuer, not canned test outputs.
    for _ in range(100):
        feedback = (rng.getrandbits(128) | 1) & MASK128
        value = rng.getrandbits(128)
        original = []
        for i in range(133):
            original.append(value)
            value = ((value << 1) & MASK128) ^ (feedback if value >> 127 else 0)
        if echelon_rows(original[:128]) is not None:
            break
    else:
        raise AssertionError('Synthetic GF(2) producer failed to build rank128')
    data = original.copy()
    data[129] = rng.getrandbits(128)
    fit = fit_source(data)
    assert fit is not None
    assert apply_transition(data[128], fit) == original[129]
    assert apply_transition(apply_transition(data[128], fit), fit) == data[130]
    assert apply_transition(data[127], fit) == data[128]
    assert apply_transition(data[130], fit) == data[131]
    data[130] ^= 1
    assert apply_transition(apply_transition(data[128], fit), fit) != data[130]
    print('SYNTHETIC rank128 hidden selected, matched + independently corrupted holdout: PASS')


def main():
    positive_controls()
    raw, route, acceptance = load(sys.argv[1] if len(sys.argv) > 1 else '.')
    assert hashlib.sha256(raw).hexdigest() == SHA_SPOOL
    expr = re.compile(
        r'^([^ ]+) JOB=([^ ]+) ATTEMPT=(\d+) STATE=([^ ]+) CLASS=([^ ]+) PAYLOAD=([0-9A-F]{32}) DEST=([^ ]+)$'
    )
    rows = []
    for line in raw.decode('ascii').splitlines():
        match = expr.fullmatch(line)
        if match:
            rows.append(match.groups())
    assert len(rows) == 133
    assert rows[129][:5] == ('2026-10-03T18:02:00Z', 'PS-261003-0417', '2', 'ACK', 'RECOVER')
    assert rows[131][:5] == ('2026-10-03T18:24:00Z', 'PS-261003-0448', '1', 'ACK', 'RECOVER')
    assert rows[132][:5] == ('2026-10-03T18:25:00Z', 'PS-261003-0420', '2', 'ACK', 'RECOVER')
    mask = bytes.fromhex(route['K04']['masked_component'])
    assert mask.hex().upper() == '8556C8CB6140A7F9A5123AC7571BEE1C'
    assert acceptance['slot_sha256']['K04'] == '930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0'
    results = []
    for endian in ('little', 'big'):
        vectors = [int.from_bytes(bytes.fromhex(x[5]), endian) if i != 129 else 0
                   for i, x in enumerate(rows)]
        fit = fit_source(vectors)
        assert fit is not None
        checks = []
        for a, b, steps in ((127, 128, 1), (128, 130, 2), (130, 131, 1)):
            y = vectors[a]
            for _ in range(steps):
                y = apply_transition(y, fit)
            checks.append((a, b, steps, y == vectors[b]))
        assert not any(ok for a, b, s, ok in checks)
        selected = apply_transition(vectors[128], fit).to_bytes(16, endian)
        component = bytes(a ^ b for a, b in zip(selected, mask))
        sha = hashlib.sha256(component).hexdigest()
        assert sha != acceptance['slot_sha256']['K04']
        results.append((endian, selected, component, sha))
        print('ORIGINAL', endian, 'source_holdouts', checks,
              'coupon', selected.hex().upper(),
              'K04_candidate', component.hex().upper(), 'slot_PASS', False)
    assert results[0][1:] == results[1][1:]
    print('RESULT 0 original whole-packet holdouts, 0 K04 acceptance, two endian views equivalent')


if __name__ == '__main__':
    main()
