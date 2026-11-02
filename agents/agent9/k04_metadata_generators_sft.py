"""K04 independent per-record generator controls, selected coupon withheld.

Two alternative complete-packet mechanisms:
1. CPython Random(int) seeded anew from each job/time metadata row.
2. Public metadata digest with reusable unknown XOR or modular-additive pad.
A source-only 128-bit fit of at least two intact rows is required before
predicting the disputed selected ACK. Tests do not modify any evidence.
Run: python agents/agent9/k04_metadata_generators_sft.py
"""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import hashlib
import random
import re

root = Path(__file__).resolve().parents[2] / "resources"
raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
expr = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)")
rows = []
for line in raw.decode().splitlines():
    match = expr.fullmatch(line)
    if match:
        date, job, attempt, state, cls, payload, dest = match.groups()
        rows.append((date, job, int(attempt), state, cls, bytes.fromhex(payload), dest))
assert len(rows) == 133
normal = rows[:128]
assert all(r[3] == "ACK" for r in normal)

def numeric_seeds(r):
    date, job, attempt, *_ = r
    t = datetime.fromisoformat(date.replace("Z", "+00:00"))
    epoch = int(t.timestamp())
    suffix = int(job.rsplit("-", 1)[-1])
    return {
        "epoch": epoch, "minute": epoch // 60, "five_minute": epoch // 300,
        "hhmm": t.hour * 100 + t.minute, "job_suffix": suffix,
        "full_job_digits": int(job.replace("PS-", "").replace("-", "")),
        "date_hhmm": int(t.strftime("%Y%m%d%H%M")),
        "day": int(t.strftime("%Y%m%d")),
        "suffix_attempt": (suffix << 8) | attempt,
    }

seed_checks = 0
seed_hits = []
for i, row in enumerate(normal):
    for name, seed in numeric_seeds(row).items():
        rng = random.Random(seed)
        words = [rng.getrandbits(32) for _ in range(36)]
        for order in ("big", "little"):
            for offset in range(33):
                seed_checks += 1
                predicted = b"".join(w.to_bytes(4, order) for w in words[offset:offset + 4])
                if predicted == row[5]:
                    seed_hits.append((i, name, order, offset))
assert seed_checks == 76032

def forms(r):
    date, job, attempt, state, cls, payload, dest = r
    t = datetime.fromisoformat(date.replace("Z", "+00:00"))
    suffix = job.rsplit("-", 1)[-1]
    return {
        "job": job, "suffix": suffix, "timestamp": date,
        "dateonly": date[:10], "isoUTC": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "minute": t.strftime("%H:%M"), "job|ts": job + "|" + date,
        "ts|job": date + "|" + job, "job:class": job + ":" + cls,
        "job:dest": job + ":" + dest, "job:class:dest": job + ":" + cls + ":" + dest,
        "ts:class:dest": date + ":" + cls + ":" + dest,
        "job-epoch": suffix + str(int(t.timestamp())),
        "yyyymmddhhmm": t.strftime("%Y%m%d%H%M"),
        "job_prefix": job.rsplit("-", 1)[0],
    }

def digest(name, value):
    if name == "md5":
        return hashlib.md5(value).digest()
    if name == "blake2s-16":
        return hashlib.blake2s(value, digest_size=16).digest()
    if name == "blake2b-16":
        return hashlib.blake2b(value, digest_size=16).digest()
    return hashlib.new(name, value).digest()

def group(r, mode):
    if mode == "global":
        return "*"
    if mode == "class":
        return r[4]
    if mode == "dest":
        return r[6]
    return r[4] + "|" + r[6]

def fitted_pad(y, x, operation):
    if operation == "xor":
        return bytes(a ^ b for a, b in zip(y, x))
    order = "big" if operation == "addBE" else "little"
    return (int.from_bytes(y, order) - int.from_bytes(x, order)) % (1 << 128)

hashes = ("md5", "sha1", "sha256", "sha512", "sha3_256", "blake2s-16", "blake2b-16")
checks = 0
pad_hits = []
for formula in forms(normal[0]):
    for algorithm in hashes:
        for view in ("first", "last"):
            digests = []
            for r in normal:
                d = digest(algorithm, forms(r)[formula].encode())
                digests.append(d[:16] if view == "first" else d[-16:])
            for partition in ("global", "class", "dest", "class_dest"):
                groups = defaultdict(list)
                for i, r in enumerate(normal):
                    groups[group(r, partition)].append(i)
                for operation in ("xor", "addBE", "addLE"):
                    for g, indices in groups.items():
                        if len(indices) < 2:
                            continue
                        value = fitted_pad(normal[indices[0]][5], digests[indices[0]], operation)
                        checks += 1
                        matching = sum(fitted_pad(normal[i][5], digests[i], operation) == value
                                       for i in indices)
                        if matching >= 2:
                            pad_hits.append((formula, algorithm, view, partition, operation, g, matching))
assert checks == 10080

# Synthetic controls for both numeric and digested-pad layouts.
s = 173
assert random.Random(s).getrandbits(32) == random.Random(s).getrandbits(32)
x0 = bytes(range(16))
x1 = bytes(range(16, 32))
pad = bytes.fromhex("0123456789ABCDEF0011223344556677")
assert fitted_pad(bytes(a ^ b for a, b in zip(x0, pad)), x0, "xor") == pad
assert fitted_pad(bytes(a ^ b for a, b in zip(x1, pad)), x1, "xor") == pad
delta = 0x12345678
for x in (x0, x1):
    y = ((int.from_bytes(x, "big") + delta) % (1 << 128)).to_bytes(16, "big")
    assert fitted_pad(y, x, "addBE") == delta

print("normal_rows", len(normal), "selected_held_out", 1)
print("numeric_seed_full128_comparisons", seed_checks, "source_hits", seed_hits)
print("metadata_hash_group_calibrations", checks, "source_hits", pad_hits)
print("synthetic_controls", "PASS")
if not seed_hits and not pad_hits:
    print("NO_SOURCE_MODEL: original K04 selected coupon not predicted")
