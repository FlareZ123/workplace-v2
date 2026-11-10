"""H17 SFT: Python rejection-sampled byte printer issuer, source-only.

Test the first undisputed intact 16-byte printer packet. Never read or fit
the selected 18:02 ACK2 coupon, route mask, target digest, or candidate.
Run five non-overlapping positional seed shards:
  python agents/agent2/k04_randbelow256_clock_source_sft.py 0 70000
  python agents/agent2/k04_randbelow256_clock_source_sft.py 70000 140000
  python agents/agent2/k04_randbelow256_clock_source_sft.py 140000 210000
  python agents/agent2/k04_randbelow256_clock_source_sft.py 210000 280000
  python agents/agent2/k04_randbelow256_clock_source_sft.py 280000 359920
Requires NumPy. Defaults cover all 359920 seeds in one run.
"""
import datetime as dt
import hashlib
import itertools
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
TARGET = bytes.fromhex("FBBBC54356483F5864BB3F06794518A5")
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RAW_DRAWS = 18000

def seeds():
    for day in (2, 3, 4):
        first = int(dt.datetime(2026, 10, day, tzinfo=dt.timezone.utc).timestamp())
        yield from range(first, first + 86400)
    yield from range(20260000, 20270000)
    for day in (2, 3, 4):
        for hour in range(24):
            for minute in range(60):
                yield int(f"202610{day:02}{hour:02}{minute:02}")
    for hour in range(24):
        for minute in range(60):
            for second in range(60):
                yield int(f"20261003{hour:02}{minute:02}{second:02}")

def emitted_bytes(seed):
    # randrange(256) asks getrandbits(9); values >=256 consume a rejected draw.
    # Using randbytes here obtains the *same raw MT32 words* in one C call.
    words = np.frombuffer(random.Random(seed).randbytes(RAW_DRAWS * 4), dtype="<u4")
    high9 = words >> 23
    return high9[high9 < 256].astype(np.uint8).tobytes()

def main():
    assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == SHA
    assert TARGET.hex().upper() in SPOOL.read_text().splitlines()[1]
    seed = 1791079160
    rng = random.Random(seed)
    actual = bytes(rng.randrange(256) for _ in range(2050))
    assert emitted_bytes(seed)[:2050] == actual
    corrupted = actual[:2015] + bytes([actual[2015] ^ 1])
    assert corrupted != actual[:2016]
    print("SYNTHETIC_POSITIVE 2050 exact direct randrange bytes PASS", flush=True)

    lower = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    upper = int(sys.argv[2]) if len(sys.argv) > 2 else 359920
    assert 0 <= lower < upper <= 359920
    start = time.monotonic()
    prefix_hits = 0
    full_matches = []
    for index, seed in enumerate(itertools.islice(seeds(), lower, upper), lower + 1):
        packet_stream = emitted_bytes(seed)
        assert len(packet_stream) >= 8192 + 16
        offset = packet_stream.find(TARGET[:4])
        while 0 <= offset < 8192:
            prefix_hits += 1
            if packet_stream[offset:offset + 16] == TARGET:
                full_matches.append((seed, offset))
                print("WHOLE_ORIGINAL_SOURCE_PACKET_MATCH", seed, offset, flush=True)
            offset = packet_stream.find(TARGET[:4], offset + 1)
    assert index == upper
    assert prefix_hits == 0
    assert not full_matches
    print(f"ORIGINAL_SOURCE_GATE shard={lower}:{upper} phases=8192 prefix4={prefix_hits} whole16={len(full_matches)} elapsed={time.monotonic()-start:.3f}", flush=True)

if __name__ == "__main__":
    main()
