"""Source-only H-17 PCG64 wall-clock-seed/offset gate.

Requires NumPy. Run from any working directory, e.g.
    python agents/agent38/k04_pcg64_calendar_source_sft.py --kind minute12
    python agents/agent38/k04_pcg64_calendar_source_sft.py --kind unix --start 0 --stop 100000

The selected 18:02 ACK2 bytes, K04 mask and acceptance hash are never read.
Source date window: commissioned 2026-09-24 through intact first printer ACK
2026-10-03 07:00 UTC inclusive. All tested offsets are positions of the
first of two consecutive uint64 outputs, 0..8192 inclusive. Standard
NumPy PCG64/SeedSequence integer-seed initialization, NOT arbitrary state.
"""
import argparse
import datetime as dt
import hashlib
import re
from pathlib import Path

import numpy as np

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
UTC = dt.timezone.utc
EPOCH = dt.datetime(2026, 9, 24, tzinfo=UTC)
LAST = dt.datetime(2026, 10, 3, 7, 0, tzinfo=UTC)
SECONDS = int((LAST - EPOCH).total_seconds()) + 1


def views(packet):
    """Four reversible, globally consistent uint64-byte/half orders."""
    for reverse_halves in (False, True):
        for reverse_bytes in (False, True):
            p = packet[8:] + packet[:8] if reverse_halves else packet
            if reverse_bytes:
                p = p[:8][::-1] + p[8:][::-1]
            first, second = np.frombuffer(p, dtype="<u8")
            yield reverse_halves, reverse_bytes, first, second


def matched_indices(raw, packet):
    for half, byte, first, second in views(packet):
        for index in np.flatnonzero(raw[:-1] == first):
            if raw[index + 1] == second:
                yield int(index), half, byte


def seed_for(kind, n):
    instant = EPOCH + dt.timedelta(seconds=n)
    if kind == "unix":
        return int(instant.timestamp())
    if kind == "calendar14":
        return int(instant.strftime("%Y%m%d%H%M%S"))
    if kind == "minute12":
        return int(instant.strftime("%Y%m%d%H%M"))
    return int(instant.strftime("%Y%m%d"))


def run(kind, start, stop, max_offset):
    spool_path = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    spool = spool_path.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    first = next(line for line in spool.splitlines() if b"PAYLOAD=" in line)
    packet = bytes.fromhex(re.search(rb"PAYLOAD=([A-F0-9]{32})", first).group(1).decode())
    assert packet.hex().upper() == "FBBBC54356483F5864BB3F06794518A5"

    # Genuine seeded, nonzero-offset control checks the same matcher,
    # including every globally consistent byte/half-order transform.
    control = np.random.PCG64(42).random_raw(max(max_offset + 2, 4219))
    base = control[4217:4219].tobytes()
    for reverse_halves in (False, True):
        for reverse_bytes in (False, True):
            p = base[8:] + base[:8] if reverse_halves else base
            if reverse_bytes:
                p = p[:8][::-1] + p[8:][::-1]
            assert (4217, reverse_halves, reverse_bytes) in set(matched_indices(control, p))
    print("synthetic nonzero-offset four-orientation positive controls PASS", flush=True)

    total = 0
    first_half_hits = 0
    full_matches = []
    for n in range(start, stop):
        seed = seed_for(kind, n * 60 if kind == "minute12" else n * 86400 if kind == "date8" else n)
        raw = np.random.PCG64(seed).random_raw(max_offset + 2)
        for reverse_halves, reverse_bytes, prefix, suffix in views(packet):
            for offset in np.flatnonzero(raw[:-1] == prefix):
                first_half_hits += 1
                if raw[offset + 1] == suffix:
                    full_matches.append((seed, int(offset), reverse_halves, reverse_bytes))
        total += 1
    print("kind", kind, "seed_count", total, "range", [start, stop],
          "offsets_per_seed", max_offset + 1, "orientations", 4,
          "first_half_hits", first_half_hits, "full_hits", full_matches, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["unix", "calendar14", "minute12", "date8"], default="minute12")
    parser.add_argument("--start", type=int, default=0, help="inclusive relative seed index")
    parser.add_argument("--stop", type=int, default=None, help="exclusive relative seed index")
    parser.add_argument("--max-offset", type=int, default=8192)
    args = parser.parse_args()
    limits = {"unix": SECONDS, "calendar14": SECONDS,
              "minute12": (SECONDS - 1) // 60 + 1,
              "date8": (SECONDS - 1) // 86400 + 1}
    stop = limits[args.kind] if args.stop is None else args.stop
    assert 0 <= args.start < stop <= limits[args.kind]
    assert args.max_offset >= 4217
    run(args.kind, args.start, stop, args.max_offset)
