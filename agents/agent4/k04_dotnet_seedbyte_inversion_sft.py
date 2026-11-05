"""H-17 legacy .NET Framework Random.NextBytes scalar-seed inversion.

Source: https://github.com/microsoft/referencesource/blob/main/mscorlib/system/random.cs
Original spool is read-only. The model is a fresh Random(int seed)
per 16-byte packet; no historical .NET printer implementation is presumed.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
from pathlib import Path

import numpy as np

M = 2147483647
SOURCE_SHA256 = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'


def i32(value: int) -> int:
    return ((value + 2147483648) & 0xFFFFFFFF) - 2147483648


def samples(seed: int, count: int = 16) -> list[int]:
    """Port the reference-source unchecked Int32 subtractive generator."""
    seed = M if seed == -2147483648 else abs(seed)
    a = [0] * 56
    mj = 161803398 - seed
    a[55] = mj
    mk = 1
    for i in range(1, 55):
        j = (21 * i) % 55
        a[j] = mk
        mk = i32(mj - mk)
        if mk < 0:
            mk += M
        mj = a[j]
    for _ in range(4):
        for i in range(1, 56):
            a[i] = i32(a[i] - a[1 + (i + 30) % 55])
            if a[i] < 0:
                a[i] += M
    ii, jj = 0, 21
    out = []
    for _ in range(count):
        ii = ii % 55 + 1
        jj = jj % 55 + 1
        v = i32(a[ii] - a[jj])
        if v == M:
            v -= 1
        if v < 0:
            v += M
        a[ii] = v
        out.append(v)
    return out


def coupon(seed: int) -> bytes:
    return bytes(v & 255 for v in samples(seed))


def recover(payload: bytes) -> tuple[int, list[int]]:
    b = samples(0, 4)
    c = samples(1, 4)
    slopes = [(c[i] - b[i]) % M for i in range(4)]
    inv = pow(slopes[0], -1, M)
    checked = 0
    recovered = set()
    count = (M - 1 - payload[0]) // 256 + 1
    for start in range(0, count, 1_000_000):
        steps = np.arange(start, min(count, start + 1_000_000), dtype=np.int64)
        seeds = ((payload[0] + 256 * steps - b[0]) * inv) % M
        for i in (1, 3):
            matching = (((b[i] + slopes[i] * seeds) % M) & 255) == payload[i]
            seeds = seeds[matching]
        checked += len(seeds)
        for seed in seeds:
            if coupon(int(seed)) == payload:
                recovered.add(int(seed))
    exceptions = {M, 0}
    for i in (0, 1, 3):
        exceptions.add((-b[i] * pow(slopes[i], -1, M)) % M)
    for seed in exceptions:
        if coupon(seed) == payload:
            recovered.add(seed)
    return checked, sorted(recovered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--spool', type=Path, default=Path(__file__).resolve().parents[2] /
                        'resources/evidence/print/spool-reconstruction.log')
    args = parser.parse_args()
    raw = args.spool.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Original spool source pin mismatch')
    records = [bytes.fromhex(match.group(1)) for line in raw.decode('ascii').splitlines()
               if '+00:00' in line
               if (match := re.search(r'PAYLOAD=([0-9A-F]{32})', line))]
    if len(records) != 128:
        raise ValueError('Expected 128 ordinary control coupons')
    b = samples(0, 4)
    c = samples(1, 4)
    slopes = [(c[i] - b[i]) % M for i in range(4)]
    rng = random.Random(20261105)
    for _ in range(20000):
        seed = rng.randrange(M)
        observed = samples(seed, 4)
        assert all(observed[i] == (b[i] + slopes[i] * seed) % M for i in (0, 1, 3))
    print('POSITIVE: affine identities hold on 20,000 seeded histories')
    for seed in (0, 42, 1234567, 777777777, 2000000000, M):
        n, found = recover(coupon(seed))
        assert seed in found, (seed, n, found)
        print('POSITIVE planted seed', seed, 'three-byte survivors', n)
    for idx in (0, 1, 63, 127):
        for direction, packet in (('forward', records[idx]), ('reverse', records[idx][::-1])):
            n, found = recover(packet)
            print(f'ORIGINAL row={idx} direction={direction} three-byte survivors={n} full-seed hits={found}')


if __name__ == '__main__':
    main()
