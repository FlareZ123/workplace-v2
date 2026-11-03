"""Source-only long-phase clock-seed test for original H17 ordinary spool.

Single-file runnable test (SFT) from repository root:
    python agents/agent20/k04_global_clockseed_longphase_sft.py

This tests a single CPython Random(integer) generator whose ordinary spool
row 0300 appears at any aligned word offset 0..8191, rather than seeding
only the disputed selected job. It never reads selected ACK, mask, acceptance
commitments, K08, candidate or verifier. Original spool source is read-only.
"""
import datetime
import hashlib
import random
import re
import time
from itertools import chain
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NWORDS = 8192
EXPECTED_SEEDS = 359920


def source_target():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256
    ordinary = [line for line in raw.splitlines()
                if b"JOB=PS-261003-0300 " in line]
    assert len(ordinary) == 1
    match = re.search(rb"PAYLOAD=([0-9A-F]{32})", ordinary[0])
    assert match
    packet = bytes.fromhex(match.group(1).decode("ascii"))
    assert packet.hex().upper() == "FBBBC54356483F5864BB3F06794518A5"
    return packet


def seed_candidates():
    utc = datetime.timezone.utc
    lo = int(datetime.datetime(2026, 10, 2, tzinfo=utc).timestamp())
    hi = int(datetime.datetime(2026, 10, 5, tzinfo=utc).timestamp())
    yield from range(lo, hi)
    yield from range(20260000, 20270000)
    for day in (2, 3, 4):
        for hour in range(24):
            for minute in range(60):
                yield 202610000000 + day * 10000 + hour * 100 + minute
    for hour in range(24):
        for minute in range(60):
            for second in range(60):
                yield 20261003000000 + hour * 10000 + minute * 100 + second


def inspect_seeds(seeds, packet, progress=False):
    prefix, count, prefix_hits, complete_hits = packet[:4], 0, 0, []
    start = time.perf_counter()
    for seed in seeds:
        count += 1
        output = random.Random(seed).randbytes(NWORDS * 4)
        offset = output.find(prefix)
        while offset != -1:
            if offset % 4 == 0:
                prefix_hits += 1
                if output[offset:offset + len(packet)] == packet:
                    complete_hits.append((seed, offset // 4))
            offset = output.find(prefix, offset + 1)
        if progress and count % 100000 == 0:
            print("original search", count, "seeds,", prefix_hits,
                  "aligned firstword hits, elapsed_sec",
                  round(time.perf_counter() - start, 1), flush=True)
    return count, prefix_hits, complete_hits


def main():
    observed = source_target()
    synthetic_seed = 1791079160
    synthetic_phase = 2000
    synthetic_stream = random.Random(synthetic_seed).randbytes(NWORDS * 4)
    planted = synthetic_stream[synthetic_phase * 4:(synthetic_phase + 4) * 4]
    assert inspect_seeds((synthetic_seed - 1, synthetic_seed,
                          synthetic_seed + 1), planted) == (
                              3, 1, [(synthetic_seed, synthetic_phase)])
    print("synthetic real CPython MT seed at word phase 2000: PASS")

    count, prefix_hits, complete_hits = inspect_seeds(seed_candidates(),
                                                      observed, progress=True)
    assert count == EXPECTED_SEEDS, count
    assert prefix_hits == 0, prefix_hits
    assert not complete_hits, complete_hits
    print("original source row0300: scanned", count, "integer seeds,",
          NWORDS, "possible aligned word starts/seed")
    print("aligned firstword hits", prefix_hits,
          "complete 16-byte packet matches", len(complete_hits))
    print("selected ACK untouched; K04/K08 not recovered")


if __name__ == "__main__":
    main()
