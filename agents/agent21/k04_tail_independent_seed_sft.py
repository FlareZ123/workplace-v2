"""Target-blind independent-seed probe for the four intact-looking RECOVER-tail records.

The disputed K04 attempt-2 payload, route mask and commitment are excluded.
Every match must precede prediction of the disputed coupon.
"""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import random
import re

path = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
data = path.read_bytes()
source_hash = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert sha256(data).hexdigest() == source_hash

rows = []
for line in data.decode("ascii").splitlines():
    if line.startswith("2026-10-03T18:"):
        match = re.search(r"ATTEMPT=(\d+).*?STATE=(\S+).*?PAYLOAD=([0-9A-F]{32})", line)
        if match is None:
            continue
        if "JOB=PS-261003-0417" in line and match.group(1) == "2":
            continue
        words = tuple(int(match.group(3)[i:i + 8], 16) for i in range(0, 32, 8))
        rows.append((line[:20], words))
assert len(rows) == 4

seeds = {0, 1, 17, 417, 420, 448, 261003, 20261003, 20261004, 2026, 1003, 1802}
start = datetime(2026, 10, 3, tzinfo=timezone.utc)
for i in range(2 * 24 * 60):
    dt = start + timedelta(minutes=i)
    seeds.update((
        int(dt.strftime("%Y%m%d%H%M")),
        int(dt.strftime("%y%m%d%H%M")),
        int(dt.timestamp()),
        int(dt.strftime("%H%M")),
    ))
for base in (
    datetime(2026, 10, 3, 18, 1, tzinfo=timezone.utc),
    datetime(2026, 10, 3, 18, 24, tzinfo=timezone.utc),
):
    epoch = int(base.timestamp())
    seeds.update(range(epoch - 1800, epoch + 1801))

targets = {}
for timestamp, words in rows:
    targets.setdefault(words[0], []).append((timestamp, words, "big32"))
    reversed_words = tuple(int.from_bytes(w.to_bytes(4, "big"), "little") for w in words)
    targets.setdefault(reversed_words[0], []).append((timestamp, reversed_words, "little32"))


def locate(seed, window, first_words):
    """Search all overlapping four-word windows, preserving start indices on partial hits."""
    generator = random.Random(seed)
    draw = generator.getrandbits
    a, b, c = draw(32), draw(32), draw(32)
    for index in range(3, window + 3):
        d = draw(32)
        if a in first_words:
            for timestamp, words, orientation in first_words[a]:
                if (a, b, c, d) == words:
                    return index - 3, timestamp, orientation
        a, b, c = b, c, d
    return None


control_seed = 202610031802
synthetic = random.Random(control_seed)
for _ in range(725):
    synthetic.getrandbits(32)
control_words = tuple(synthetic.getrandbits(32) for _ in range(4))
assert locate(control_seed, 8192, {
    control_words[0]: [("synthetic-heldout", control_words, "big32")]
}) == (725, "synthetic-heldout", "big32")

hits = []
for seed in sorted(seeds):
    match = locate(seed, 4096, targets)
    if match:
        hits.append((seed, *match))

print("original source SHA-256:", source_hash)
print("withheld selected attempt: PS-261003-0417/2, entirely excluded")
print("test source rows:", len(rows))
for timestamp, words in rows:
    print(" ", timestamp, "".join(f"{w:08X}" for w in words))
print("numeric candidate seeds:", len(seeds))
print("first-output offsets per seed:", 4096)
print("total start offset assignments:", len(seeds) * 4096)
print("orientation variants: big32, little32")
print("synthetic phase-725 positive control: PASS")
print("real intact-tail matches:", hits)
