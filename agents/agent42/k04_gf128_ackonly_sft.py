"""Original H-17 ACK-only full-packet GF(2^128) source interpolation, read-only.

An alternative to the existing five-exceptional-entry model: only ACK records
consume output positions. Only unmodified original 128 regular ACK packets fit.
"""
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import zipfile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ZIP_SHA = "e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK128 = (1 << 128) - 1


def mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a >> 128:
            a = (a & MASK128) ^ 0x87
    return result


def exp(a, n):
    result = 1
    while n:
        if n & 1:
            result = mul(result, a)
        a = mul(a, a)
        n >>= 1
    return result


def all_inverse(values):
    """Batch inverse, one exponentiation, no zero field operands."""
    prefix = [1]
    for value in values:
        assert value
        prefix.append(mul(prefix[-1], value))
    rest = exp(prefix[-1], (1 << 128) - 2)
    output = [0] * len(values)
    for i in range(len(values) - 1, -1, -1):
        output[i] = mul(rest, prefix[i])
        rest = mul(rest, values[i])
    assert rest == 1
    return output


def target_weights(coords, target, inv_denoms):
    differences = [target ^ x for x in coords]
    inv_diffs = all_inverse(differences)
    total = 1
    for difference in differences:
        total = mul(total, difference)
    return [mul(total, mul(inverse_difference, denominator))
            for inverse_difference, denominator in zip(inv_diffs, inv_denoms)]


def weights_for_grid(coords, targets):
    assert len(set(coords)) == len(coords) == 128
    denoms = []
    for i, xi in enumerate(coords):
        denominator = 1
        for j, xj in enumerate(coords):
            if i != j:
                denominator = mul(denominator, xi ^ xj)
        denoms.append(denominator)
    inverses = all_inverse(denoms)
    return [target_weights(coords, target, inverses) for target in targets]


def evaluate(values, weights):
    result = 0
    for value, weight in zip(values, weights):
        result ^= mul(value, weight)
    return result


def source(path):
    if path.is_file():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == ZIP_SHA
        with zipfile.ZipFile(path) as z:
            return z.read('evidence/print/spool-reconstruction.log'), z.read('evidence/recovery-routing.json'), z.read('acceptance.json')
    return ((path / 'evidence/print/spool-reconstruction.log').read_bytes(),
            (path / 'evidence/recovery-routing.json').read_bytes(),
            (path / 'acceptance.json').read_bytes())


def main(path):
    spool, routing, acceptance = source(path)
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [r for r in spool.splitlines() if r.startswith(b'2026-')]
    assert len(rows) == 133
    assert b'ATTEMPT=1 STATE=REQUESTED' in rows[128]
    assert b'ATTEMPT=2 STATE=ACK CLASS=RECOVER' in rows[129]
    assert b'ATTEMPT=3 STATE=REQUESTED' in rows[130]
    assert b'ATTEMPT=1 STATE=ACK CLASS=RECOVER' in rows[131]
    assert b'ATTEMPT=2 STATE=ACK CLASS=RECOVER' in rows[132]
    packet = [bytes.fromhex(re.search(rb'PAYLOAD=([0-9A-F]{32})', r).group(1).decode()) for r in rows]
    assert bytes.fromhex(json.loads(routing)['K04']['masked_component']) == MASK
    assert json.loads(acceptance)['slot_sha256']['K04'] == K04_SHA
    rng = random.Random(20261109)
    models = 0
    source_controls = 0
    matches = []
    synthetic_checks = 0
    for grid in ('ordinal', 'minute'):
        x = list(range(128)) if grid == 'ordinal' else list(range(0,640,5))
        q = (128,129,130) if grid == 'ordinal' else (662,684,685)
        w = weights_for_grid(x,q)
        assert all(len(row)==128 for row in w)
        coeffs = [rng.getrandbits(128) for _ in range(9)]
        def poly(v):
            acc = 0
            for coeff in reversed(coeffs):
                acc = mul(acc,v)^coeff
            return acc
        original = [poly(v) for v in x]
        for j,v in enumerate(q):
            assert evaluate(original,w[j]) == poly(v)
            synthetic_checks += 1
        for endian in ('big','little'):
            for direction in ('forward','reverse'):
                raw = packet[:128] if direction=='forward' else packet[:128][::-1]
                original = [int.from_bytes(data,endian) for data in raw]
                produced = [evaluate(original,weights) for weights in w]
                for j, observed_index in ((1,131),(2,132)):
                    source_controls += produced[j].to_bytes(16,endian)==packet[observed_index]
                printed = produced[0].to_bytes(16,endian)
                reduced = bytes(a^b for a,b in zip(printed,MASK))
                if hashlib.sha256(reduced).hexdigest() == K04_SHA:
                    matches.append((grid,endian,direction,reduced.hex().upper()))
                models+=1
    assert (models,source_controls,len(matches),synthetic_checks) == (8,0,0,6)
    print('Original source SHA256:',SPOOL_SHA)
    print('Original ACK-only 128+3 GF(2^128) models:',models)
    print('Full genuine late ACK holdouts:',source_controls,'/ 16')
    print('K04 original complete commitment matches:',len(matches))
    print('Independently planted source-to-ACK positives:',synthetic_checks,'/ 6 PASS')
    for m in matches: print('ORIGINAL_K04_HIT',m)


if __name__=='__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'resources')
