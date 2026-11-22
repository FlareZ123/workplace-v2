#!/usr/bin/env python3
"""Original ZIP packaging-subsecond CPython MT source-only printer holdout.

Two explicit seed families at the ZIP's first extended-UTC second:
* Random(float(epoch_seconds) + microseconds / 1e6)
* Random(epoch_seconds * 1e6 + microseconds)

Do not fit the disputed PS-0417 buffer or examine K04/K08 commitments.
Reject a producer family unless it can emit a complete undisputed ACK packet
in the first 8192 32-bit outputs, allowing all four-lane permutations and
per-lane byte reversals.

Original full 1e6-sample runs on 22 Nov 2026:
float 0 hits, 172.306s; integer 0 hits, 169.124s.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOURCE_PACKET = bytes.fromhex("FBBBC54356483F5864BB3F06794518A5")
ZIP_FIRST_UT_SECOND = 1792469534
STAGES = 8192


def compatible_starts(outputs: bytes, packet: bytes) -> list[int]:
    """Find any complete 4word view without enumerating all 384 at every offset."""
    target = [packet[j:j+4] for j in range(0, 16, 4)]
    tokens = set(target) | {w[::-1] for w in target}
    offsets = set()
    for word in tokens:
        cursor = 0
        while (found := outputs.find(word, cursor)) != -1:
            cursor = found + 1
            if found % 4:
                continue
            index = found // 4
            for start in range(max(0, index-3), min(index+1, STAGES-3)):
                blob = outputs[4*start:4*start+16]
                if any(all(blob[4*j:4*j+4] in
                           (target[p[j]], target[p[j]][::-1])
                           for j in range(4))
                       for p in itertools.permutations(range(4))):
                    offsets.add(start)
    return sorted(offsets)


def seeded_control(model: str) -> None:
    us = 123456
    seed = (ZIP_FIRST_UT_SECOND + us/1_000_000 if model == "float"
            else ZIP_FIRST_UT_SECOND*1_000_000+us)
    data = random.Random(seed).randbytes(STAGES*4)
    true = data[16*4:20*4]
    lanes = [true[j:j+4] for j in range(0, 16, 4)]
    shuffled = b"".join(lanes[j][::-1] if j & 1 else lanes[j]
                        for j in (3, 1, 0, 2))
    assert 16 in compatible_starts(data, shuffled)
    corrupted = bytearray(shuffled)
    corrupted[7] ^= 1
    assert 16 not in compatible_starts(data, bytes(corrupted))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=("float", "integer"), required=True)
    p.add_argument("--start-us", type=int, default=0)
    p.add_argument("--end-us", type=int, default=1_000_000)
    p.add_argument("--spool", type=Path, default=ROOT/"resources/evidence/print/spool-reconstruction.log")
    args = p.parse_args()
    assert 0 <= args.start_us <= args.end_us <= 1_000_000
    assert hashlib.sha256(args.spool.read_bytes()).hexdigest() == SOURCE_SHA256
    seeded_control(args.model)
    start = time.monotonic()
    hits = []
    for us in range(args.start_us, args.end_us):
        seed = (ZIP_FIRST_UT_SECOND + us/1_000_000 if args.model == "float"
                else ZIP_FIRST_UT_SECOND*1_000_000+us)
        data = random.Random(seed).randbytes(STAGES*4)
        positions = compatible_starts(data, SOURCE_PACKET)
        if positions:
            hits.append([us, positions])
            print(json.dumps({"microsecond": us, "full_source_positions": positions}), flush=True)
    print(json.dumps({
        "model": args.model, "source_utc_second": ZIP_FIRST_UT_SECOND,
        "range": [args.start_us, args.end_us],
        "tested": args.end_us-args.start_us,
        "source_packet_matches": len(hits), "hits": hits,
        "first_native_word_phases": [0, STAGES-4],
        "allowed_serializers": "all 24 four-word orders and 16 independent byte reversals",
        "seeded_full_packet_control": "PASS",
        "elapsed_seconds": round(time.monotonic()-start, 3),
        "K04_commitment": "NOT_EVALUATED",
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
