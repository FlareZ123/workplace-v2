"""Source-pinned H-17 per-job metadata-checksum-seeded CPython printer probe.

This complete-coupon producer hypothesis is conditional. The disputed selected
ACK2 buffer never participates in seed derivation or source calibration.
Run from repo root: python agents/agent41/k04_metadata_hash_seed_sft.py
"""
import hashlib
import json
import random
import re
import zlib
from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "resources"
spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
pat = re.compile(r"^(\\S+) JOB=(\\S+) ATTEMPT=(\\d+) STATE=(\\w+) CLASS=(\\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\\w+)$".replace("\\\\", "\\"))
rows = [m.groups() for line in spool.decode().splitlines() if (m := pat.fullmatch(line))]
assert len(rows) == 133
selected = rows[129]
assert selected[:5] == ("2026-10-03T18:02:00Z", "PS-261003-0417", "2", "ACK", "RECOVER")
route = json.loads((root / "evidence/recovery-routing.json").read_text())
accept = json.loads((root / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
wanted = bytes.fromhex(accept["slot_sha256"]["K04"])

def forms(row):
    date, job, attempt, state, klass, _, dest = row
    suffix = job.rsplit("-", 1)[-1]
    stamp = int(datetime.fromisoformat(date.replace("Z", "+00:00")).timestamp())
    return [job, suffix, date, date[:10], str(stamp), str(stamp // 60),
            f"{job}:{attempt}", f"{job}:{klass}:{dest}",
            f"{date}:{klass}:{dest}", f"{job}|{date}",
            f"{job}|{attempt}|{state}|{klass}|{dest}",
            f"{job}|{date}|{attempt}|{state}|{klass}|{dest}"]

def seeds(message):
    buf = message.encode()
    fnv = 2166136261
    for value in buf:
        fnv = ((fnv ^ value) * 16777619) & 0xFFFFFFFF
    digest = hashlib.sha256(buf).digest()
    return (zlib.crc32(buf), zlib.adler32(buf), fnv,
            int.from_bytes(digest[:4], "little"),
            int.from_bytes(digest[:4], "big"),
            int.from_bytes(digest[-4:], "little"))

def packets(seed):
    rng = random.Random(seed)
    words = [rng.getrandbits(32) for _ in range(35)]
    for pos in range(32):
        window = words[pos:pos + 4]
        for reverse in (False, True):
            oriented = window[::-1] if reverse else window
            for order in ("little", "big"):
                yield pos, reverse, order, b"".join(
                    value.to_bytes(4, order) for value in oriented)

source_hits = []
for idx, row in enumerate(rows):
    if idx == 129:
        continue
    actual = bytes.fromhex(row[5])
    for fi, value in enumerate(forms(row)):
        for si, seed in enumerate(seeds(value)):
            for pos, reverse, order, packet in packets(seed):
                if packet == actual:
                    source_hits.append((idx, fi, si, pos, reverse, order))
assert not source_hits

control_row = rows[42]
planted = next(packet for pos, rev, order, packet in packets(
    seeds(forms(control_row)[7])[2]) if (pos, rev, order) == (13, True, "big"))
control_hits = [(fi, si, pos, rev, order)
    for fi, value in enumerate(forms(control_row))
    for si, seed in enumerate(seeds(value))
    for pos, rev, order, packet in packets(seed) if packet == planted]
assert (7, 2, 13, True, "big") in control_hits

hits = []
checks = 0
for fi, value in enumerate(forms(selected)):
    for si, seed in enumerate(seeds(value)):
        for pos, rev, order, coupon in packets(seed):
            checks += 1
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            if hashlib.sha256(component).digest() == wanted:
                hits.append((fi, si, pos, rev, order, coupon.hex().upper()))
assert checks == 9216
print(json.dumps({"source_records_withheld": 1, "original_source_records": 132,
                  "full_source_packet_hits": source_hits,
                  "selected_original_commitment_checks": checks,
                  "original_commitment_hits": hits,
                  "planted_complete_coupon_positive": True}, sort_keys=True))
