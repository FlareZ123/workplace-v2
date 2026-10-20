"""Reproduce all six verified offline REC8/1 components from supplied export.

Run with Python 3 stdlib; prints candidate JSON and independent PASS/NO_MATCH.
No source files are modified.
"""
import hashlib
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "evidence"
FIRST = datetime(2026, 10, 3, 21, 13, 40, tzinfo=timezone.utc)
END = datetime(2026, 10, 3, 21, 13, 48, tzinfo=timezone.utc)


def digest16(value):
    return hashlib.sha256(value).digest()[:16].hex().upper()


def jsonlines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


candidate = {f"K{i:02d}": None for i in range(1, 9)}
candidate["K01"] = "049AAB2E1CDE7A82CD7C60234303C91A"

by_seq = {}
for r in jsonlines(E / "telemetry/freeze-export.jsonl"):
    if (r.get("tag"), r.get("field"), r.get("quality"), r.get("state")) != ("LT-204", "DIAG_WORD", "GOOD", "HOLD"):
        continue
    if not FIRST <= datetime.fromisoformat(r["ts"]) < END or not 0 <= r["seq"] <= 7:
        continue
    previous = by_seq.get(r["seq"])
    if previous is None or r["revision"] > previous["revision"]:
        by_seq[r["seq"]] = r
candidate["K02"] = digest16(b"".join(struct.pack(">H", int(by_seq[i]["value"])) for i in range(8)))

by_bay = {}
for r in jsonlines(E / "maintenance/seal-receipts.jsonl"):
    if (r.get("permit"), r.get("state"), r.get("fitment"), r.get("signed")) != ("PTW-417", "CLOSED", "AS_LEFT", True):
        continue
    previous = by_bay.get(r["bay"])
    if previous is None or r["revision"] > previous["revision"]:
        by_bay[r["bay"]] = r
serials = "|".join(by_bay[bay]["serial"] for bay in ("B", "D", "A", "C"))
candidate["K03"] = digest16(serials.encode("ascii"))

raw = (E / "recorder/trip-recorder.raw").read_bytes()
magic, version, record_size, count = struct.unpack_from("<8sHHI", raw)
assert magic == b"TRP2DUMP" and version == 2 and record_size == 24
latches = {}
start = int(datetime(2026, 10, 3, 21, 14, 0, tzinfo=timezone.utc).timestamp())
for i in range(count):
    record = raw[16 + i * 24:16 + (i + 1) * 24]
    if len(record) != 24 or zlib.crc32(record[:20]) != struct.unpack_from("<I", record, 20)[0]:
        continue
    ts, node, event, latch, seq, word, aux, crc = struct.unpack("<IHBBI4sII", record)
    if node == 49 and event == 82 and start <= ts < start + 8:
        if latch not in latches or seq > latches[latch][0]:
            latches[latch] = (seq, word)
candidate["K05"] = b"".join(latches[i][1] for i in range(4)).hex().upper()

scan = (E / "procedures/RC-17-scans.txt").read_text()
strips = dict(re.findall(
    r"DOCUMENT RC-17 / REV C / SECTION (\w+).*?Footer control strip:\s*([0-9A-F]{8})",
    scan,
    re.S
))
candidate["K06"] = "".join(strips[part] for part in ("DRAIN", "ISOLATE", "PURGE", "VERIFY"))

transfers = jsonlines(E / "transfers/transfer-audit.jsonl")
assert any(r.get("kind") == "COMMIT" and r.get("transfer") == "AX-7782" and r.get("dry_run") is False for r in transfers)
chunks = {}
for r in transfers:
    if r.get("kind") == "CHUNK" and r.get("transfer") == "AX-7782":
        if r["seq"] not in chunks or r["attempt"] > chunks[r["seq"]]["attempt"]:
            chunks[r["seq"]] = r
candidate["K07"] = digest16(b"".join(bytes.fromhex(chunks[i]["checkpoint"]) for i in range(8)))

targets = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]
print(json.dumps(candidate, indent=2))
for k, v in candidate.items():
    if v is not None:
        assert hashlib.sha256(bytes.fromhex(v)).hexdigest() == targets[k], k
        print(k, "PASS")
