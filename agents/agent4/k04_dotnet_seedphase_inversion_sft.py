"""Source-pinned conditional .NET Framework Random(int seed) phase inversion.

For each q in --start..--end, invert source bytes at 3 empirically
affine output coordinates, then independently check each surviving full
16-byte packet against the exact legacy generator implementation.

Requires sibling k04_dotnet_seedbyte_inversion_sft.py and NumPy.
No historical source establishes that the H-17 printer used .NET.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
from pathlib import Path

import numpy as np

from k04_dotnet_seedbyte_inversion_sft import M, SOURCE_SHA256, samples


def find_seeds(packet: bytes, phase: int, slopes, bases, affine):
    coords = [i for i in range(phase, phase + 16) if affine[i]]
    if len(coords) < 3:
        raise ValueError((phase, coords))
    i0, i1, i2 = coords[:3]
    y0 = packet[i0 - phase]
    inv = pow(slopes[i0], -1, M)
    count = (M - 1 - y0) // 256 + 1
    found = []
    survivors = 0
    for start in range(0, count, 1_000_000):
        vals = y0 + 256 * np.arange(start, min(count, start + 1_000_000), dtype=np.int64)
        seeds = ((vals - bases[i0]) * inv) % M
        for t in (i1, i2):
            seeds = seeds[(((bases[t] + slopes[t] * seeds) % M) & 255) == packet[t - phase]]
        survivors += len(seeds)
        for s in seeds:
            s = int(s)
            if bytes(x & 255 for x in samples(s, phase + 16)[phase:]) == packet:
                found.append(s)
    if bytes(x & 255 for x in samples(M, phase + 16)[phase:]) == packet:
        found.append(M)
    return survivors, sorted(set(found)), (i0, i1, i2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spool", type=Path, required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=64)
    ap.add_argument("--orientation", choices=["forward", "reversed"], default="forward")
    args = ap.parse_args()
    assert 0 <= args.start <= args.end <= 64
    raw = args.spool.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    records = [bytes.fromhex(m.group(1)) for line in raw.decode().splitlines()
               if "+00:00" in line
               if (m := re.search(r"PAYLOAD=([0-9A-F]{32})", line))]
    assert len(records) == 128
    packet = records[0][::-1] if args.orientation == "reversed" else records[0]

    count = args.end + 16
    bases = samples(0, count)
    one = samples(1, count)
    slopes = [(x - y) % M for x, y in zip(one, bases)]
    rng = random.Random(20261105)
    affine = [True] * count
    for _ in range(20000):
        seed = rng.randrange(M)
        actual = samples(seed, count)
        for t in range(count):
            affine[t] &= actual[t] == (bases[t] + slopes[t] * seed) % M
    print("EMPIRICAL affine coords", sum(affine), "of", count, flush=True)

    for seed, phase in ((42, 0), (1234567, 11), (1000000000, 31), (2000000000, 64)):
        if phase > args.end:
            continue
        planted = bytes(x & 255 for x in samples(seed, phase + 16)[phase:])
        count_survived, found, _ = find_seeds(planted, phase, slopes, bases, affine)
        assert seed in found, (seed, phase, count_survived, found)
        print("PLANTED PASS", seed, phase, flush=True)

    for phase in range(args.start, args.end + 1):
        survivors, hits, indices = find_seeds(packet, phase, slopes, bases, affine)
        print("ORIGINAL", args.orientation, phase, indices, survivors, hits, flush=True)


if __name__ == "__main__":
    main()
