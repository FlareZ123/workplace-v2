#!/usr/bin/env python3
"""K04: genuine CPython MT startup-offset gap, p951 source-only n1..24 sieve.

Each offset reanchors the actual initialized register. The disputed selected
row129 is withheld before decoding. No candidate/acceptance/route files read.
A surviving hypothetical seed is never claimed to be the historical producer.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt, U
from k04_cpython_initarray_ringphase_source_sft import consistent, term_domains

SOURCE = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED = 129
TARGET = 951


def observed_packets() -> list[bytes]:
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    all_records = raw.decode("ascii").splitlines()
    records = [line for line in all_records if "PAYLOAD=" in line]
    assert len(records) == len(mt.STARTS) == 133
    assert mt.STARTS[SELECTED] == TARGET
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in records[SELECTED]
    assert "2026-10-03T18:02:00Z" in records[SELECTED]
    packets = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rec).group(1))
               if i != SELECTED else b"\0" * 16
               for i, rec in enumerate(records)]
    # The copied selected payload never enters the array used by the source model.
    return packets


def planted_control(offset: int) -> None:
    """True CPython 24-word integer seed with the identical sparse observed schedule."""
    keys = [(0x12A59831 + i * 0x3179D8AB) & U for i in range(24)]
    seed = sum(x << (32*i) for i, x in enumerate(keys))
    rng = random.Random(seed)
    original_register = list(rng.getstate()[1][:624])
    words = [rng.getrandbits(32) for _ in range(offset + max(mt.STARTS) + 4)]
    packets = [
        b"".join(words[offset + s + j].to_bytes(4, "little")
                 for j in range(4))
        for s in mt.STARTS
    ]
    packets[SELECTED] = b"\0" * 16
    observed = source_states(offset, packets)
    assert all((actual & mask) == value
               for (mask, value), actual in zip(observed, original_register))
    assert consistent(term_domains(observed, 0), 24)
    print(f"PLANTED_TRUE_CPYTHON_24WORD_OFFSET_{offset}=PASS", flush=True)


def seed_domains(term_rows: list[tuple[int, set[int]]], n: int):
    buckets: list[set[int] | None] = [None] * n
    for j, allowed in term_rows:
        idx = j % n
        keyvalues = {(x - idx) & U for x in allowed}
        buckets[idx] = keyvalues if buckets[idx] is None else buckets[idx] & keyvalues
        if not buckets[idx]:
            return []
    if any(a is None for a in buckets):
        return []
    return [sorted(a) for a in buckets]


def genuine_full_source_test(offset: int, packets: list[bytes], n: int,
                             term_rows: list[tuple[int, set[int]]]) -> dict:
    """Attempt exact seed recovery only for fully constrained small key domains."""
    domains = seed_domains(term_rows, n)
    if not domains:
        return {"status": "NO_FINITE_FULLY_CONSTRAINED_KEY"}
    population = 1
    for a in domains:
        population *= len(a)
    if population > 4096:
        return {"status": "LARGE_KEY_DOMAIN", "size": population}
    matches = []
    tested = 0
    for keys in product(*domains):
        if keys[-1] == 0:
            continue
        tested += 1
        seed = sum(x << (32*i) for i, x in enumerate(keys))
        generator = random.Random(seed)
        outputs = [generator.getrandbits(32)
                   for _ in range(offset + max(mt.STARTS) + 4)]
        bad = next((i for i, p in enumerate(mt.STARTS)
                    if i != SELECTED and packets[i] != b"".join(
                        outputs[offset + p + j].to_bytes(4,"little")
                        for j in range(4))), None)
        if bad is None:
            matches.append({"n": n, "key_words": [f"{x:08X}" for x in keys],
                            "payload": b"".join(
                                outputs[offset + TARGET + j].to_bytes(4,"little")
                                for j in range(4)).hex().upper()})
    return {"status": "FULL_SOURCE_TEST", "tested": tested, "matches": matches}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--max-words", type=int, default=24)
    parser.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    assert 624 <= args.start < args.stop <= 2496
    assert 1 <= args.max_words <= 24
    packets = observed_packets()
    if args.controls:
        planted_control(args.start)
    started = time.monotonic()
    failures_s0 = 0
    survivors: dict[int, list[int]] = defaultdict(list)
    recovered = []
    for offset in range(args.start, args.stop):
        states = source_states(offset, packets)
        mask, value = states[0]
        if (value ^ 0x80000000) & mask:
            failures_s0 += 1
        else:
            terms = term_domains(states, 0)
            for n in range(1, args.max_words + 1):
                if consistent(terms, n):
                    survivors[n].append(offset)
                    if n <= 4:
                        test = genuine_full_source_test(offset, packets, n, terms)
                        recovered.append({"offset":offset, "seed_words":n, **test})
        if (offset - args.start + 1) % 8 == 0:
            print(f"PROGRESS offset={offset} of {args.stop-1}, "
                  f"elapsed_s={time.monotonic()-started:.1f}",flush=True)
    result = {
        "phase_range": [args.start,args.stop],
        "offsets_checked": args.stop-args.start,
        "source_sha256": SOURCE_SHA,
        "selected_record_withheld": SELECTED,
        "source_mt_rank": 15365,
        "s0_contradictions": failures_s0,
        "surviving_seedlength_to_offsets": {str(n):v for n,v in sorted(survivors.items())},
        "tested_shortseed_candidates": recovered,
        "elapsed_seconds": round(time.monotonic()-started,3),
    }
    out = ROOT / "artifacts" / "agent40"
    out.mkdir(parents=True, exist_ok=True)
    file = out / f"midwarmup_{args.start}_{args.stop}.json"
    file.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result),flush=True)


if __name__ == "__main__":
    main()
