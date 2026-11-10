"""H17 SFT: intact printer source gate for byte-per-MT-draw clock seeds.

Emits one byte from each CPython MT word, high-8 or low-8 view.
The selected 18:02 ACK2, mask, commitment and candidate are not read.
"""
import datetime as dt
import hashlib
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FIRST = bytes.fromhex("FBBBC54356483F5864BB3F06794518A5")
UTC = dt.timezone.utc
PHASES = 8192
N_WORDS = PHASES + 15

def seeds():
    for day in (2, 3, 4):
        start = int(dt.datetime(2026, 10, day, tzinfo=UTC).timestamp())
        for s in range(start, start + 86400):
            yield s
    yield from range(20260000, 20270000)
    for day in (2, 3, 4):
        for h in range(24):
            for m in range(60):
                yield int(f"202610{day:02}{h:02}{m:02}")
    for h in range(24):
        for m in range(60):
            for sec in range(60):
                yield int(f"20261003{h:02}{m:02}{sec:02}")

def main():
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = [line for line in raw.decode().splitlines() if "PAYLOAD=" in line]
    assert len(rows) == 133
    assert rows[0].split("PAYLOAD=")[1].split()[0] == FIRST.hex().upper()
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK" in rows[129]
    planted = random.Random(1791079160).randbytes((N_WORDS + 8) * 4)
    for lane in (0, 3):
        stream = planted[lane::4]
        sample = stream[2000:2016]
        assert stream.find(sample, 2000) == 2000
        assert stream.find(sample[:-1] + bytes([sample[-1] ^ 1]), 2000) != 2000
    print("SYNTHETIC_POSITIVE high8/low8 and corruption negative PASS", flush=True)

    start = time.monotonic()
    prefix_counts = [0, 0]
    whole = []
    for i, seed in enumerate(seeds(), 1):
        data = random.Random(seed).randbytes(N_WORDS * 4)
        for lane in (0, 3):
            seq = data[lane::4]
            pos = seq.find(FIRST[:4])
            while pos >= 0 and pos < PHASES:
                prefix_counts[0 if lane == 0 else 1] += 1
                if seq[pos:pos + 16] == FIRST:
                    whole.append((seed, lane, pos))
                    print("WHOLE_SOURCE_PACKET_MATCH", seed, lane, pos, flush=True)
                pos = seq.find(FIRST[:4], pos + 1)
        if i % 50000 == 0:
            print(f"PROGRESS seeds={i} prefix4={prefix_counts} full={len(whole)}", flush=True)
    assert i == 359920
    assert prefix_counts == [1, 2]
    assert not whole
    print(f"ORIGINAL_SOURCE_GATE seeds={i} phases={PHASES} lanes=2 prefix4={prefix_counts} whole16={len(whole)} seconds={time.monotonic()-start:.3f}", flush=True)

if __name__ == "__main__":
    main()
