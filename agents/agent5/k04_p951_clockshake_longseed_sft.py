"""Source-only clock-derived SHAKE128/256 -> long binary seed B check.

Conditional model: the printer is CPython Random(bytes, version=2), with
p951 chronology and first output at source row0. The selected ACK2 and all
official commitments are excluded. A success is only a source-seed hypothesis.
Run from repository checkout with Python 3; DAY_LO/HI are UTC YYYY-MM-DD.
"""
import datetime as dt
import hashlib
import os
from pathlib import Path
import time

SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
KEY22 = bytes.fromhex("FD6A4CF7")
KEY23 = bytes.fromhex("06EDCDAD")
MIN_LEN, MAX_LEN = 2357, 2428
assert MAX_LEN - MIN_LEN == 71
synth = bytearray(MAX_LEN)
synth[MIN_LEN - 32:MIN_LEN - 24] = KEY23 + KEY22
assert (KEY23 + KEY22) in synth[MIN_LEN - 32:MAX_LEN - 24]

def utc_epoch(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp())

def inputs(ts):
    d = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
    yield "epoch_decimal", str(ts).encode("ascii")
    yield "epoch_uint32_le", ts.to_bytes(4, "little")
    yield "epoch_uint32_be", ts.to_bytes(4, "big")
    yield "epoch_uint64_le", ts.to_bytes(8, "little")
    yield "epoch_uint64_be", ts.to_bytes(8, "big")
    yield "iso_utc", d.strftime("%Y-%m-%dT%H:%M:%SZ").encode("ascii")
    yield "iso_space", d.strftime("%Y-%m-%d %H:%M:%S").encode("ascii")

start = utc_epoch(os.getenv("DAY_LO", "2026-09-24"))
end = utc_epoch(os.getenv("DAY_HI", "2026-10-05"))
assert start < end
count = 0
first4, both8 = [], []
t0 = time.time()
for ts in range(start, end):
    for encoding, seed in inputs(ts):
        for algo in ("shake_128", "shake_256"):
            b = hashlib.new(algo, seed).digest(MAX_LEN - 24)
            pos = b.find(KEY22, MIN_LEN - 28, MAX_LEN - 24)
            while pos >= 0:
                found = (ts, encoding, algo, pos + 28)
                first4.append(found)
                if b[pos - 4:pos] == KEY23:
                    both8.append(found)
                pos = b.find(KEY22, pos + 1, MAX_LEN - 24)
            count += 1
    if (ts + 1 - start) % 86400 == 0:
        print("DAY", dt.datetime.fromtimestamp(ts, dt.timezone.utc).date(),
              "trials", count, "first4", len(first4),
              "both8", len(both8), "elapsed_sec", round(time.time() - t0, 1), flush=True)
print("FINISHED", "trials", count, "first4", first4, "both8", both8)
assert count == (end - start) * 14
