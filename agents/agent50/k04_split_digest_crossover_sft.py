#!/usr/bin/env python3
"""Bounded K04 cross-slot split-SHA256 candidate test.

Hypothesis: the K04 coupon might equal either 16-byte half of SHA256 over
one of the six already-accepted slot source blocks. The K04 route mask is
then applied exactly as specified. This is an exploratory cross-slot
hypothesis, not a source-attested K04 derivation.

Run from the repository root, or override --evidence-root and --acceptance
for an extracted source bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

FIRST = datetime(2026, 10, 3, 21, 13, 40, tzinfo=timezone.utc)
END = datetime(2026, 10, 3, 21, 13, 48, tzinfo=timezone.utc)
TRP_START = int(datetime(2026, 10, 3, 21, 14, 0, tzinfo=timezone.utc).timestamp())


def jsonlines(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def source_blocks(evidence: Path) -> dict[str, bytes]:
    # K01 is the raw WN-14 component reproduced by resources/work/recover_six.py.
    k01 = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")

    # K02: exact eight LT-204 GOOD/HOLD DIAG_WORD samples, latest revision per seq.
    by_seq = {}
    for r in jsonlines(evidence / "telemetry/freeze-export.jsonl"):
        if (r.get("tag"), r.get("field"), r.get("quality"), r.get("state")) != (
            "LT-204", "DIAG_WORD", "GOOD", "HOLD"
        ):
            continue
        ts = datetime.fromisoformat(r["ts"])
        if not FIRST <= ts < END or not 0 <= r["seq"] <= 7:
            continue
        old = by_seq.get(r["seq"])
        if old is None or r["revision"] > old["revision"]:
            by_seq[r["seq"]] = r
    k02 = b"".join(struct.pack(">H", int(by_seq[i]["value"])) for i in range(8))

    # K03: exact PTW-417 CLOSED/AS_LEFT signed serials in B,D,A,C order.
    by_bay = {}
    for r in jsonlines(evidence / "maintenance/seal-receipts.jsonl"):
        if (r.get("permit"), r.get("state"), r.get("fitment"), r.get("signed")) != (
            "PTW-417", "CLOSED", "AS_LEFT", True
        ):
            continue
        old = by_bay.get(r["bay"])
        if old is None or r["revision"] > old["revision"]:
            by_bay[r["bay"]] = r
    k03 = "|".join(by_bay[bay]["serial"] for bay in ("B", "D", "A", "C")).encode("ascii")

    # K05: exact TRP2 node49/event82 words, latest seq per latch in the 8-second window.
    raw = (evidence / "recorder/trip-recorder.raw").read_bytes()
    magic, version, record_size, count = struct.unpack_from("<8sHHI", raw)
    assert magic == b"TRP2DUMP" and version == 2 and record_size == 24
    latches = {}
    for i in range(count):
        record = raw[16 + i * 24:16 + (i + 1) * 24]
        if len(record) != 24 or zlib.crc32(record[:20]) != struct.unpack_from("<I", record, 20)[0]:
            continue
        ts, node, event, latch, seq, word, aux, crc = struct.unpack("<IHBBI4sII", record)
        if node == 49 and event == 82 and TRP_START <= ts < TRP_START + 8:
            if latch not in latches or seq > latches[latch][0]:
                latches[latch] = (seq, word)
    k05 = b"".join(latches[i][1] for i in range(4))

    # K06: raw Rev-C footer strips in DRAIN,ISOLATE,PURGE,VERIFY service order.
    scan = (evidence / "procedures/RC-17-scans.txt").read_text()
    strips = dict(re.findall(
        r"DOCUMENT RC-17 / REV C / SECTION (\w+).*?Footer control strip:\s*([0-9A-F]{8})",
        scan, re.S
    ))
    k06 = bytes.fromhex("".join(strips[p] for p in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")))

    # K07: latest AX-7782 checkpoint for each chunk, seq 0..7.
    transfers = jsonlines(evidence / "transfers/transfer-audit.jsonl")
    assert any(r.get("kind") == "COMMIT" and r.get("transfer") == "AX-7782" and r.get("dry_run") is False for r in transfers)
    chunks = {}
    for r in transfers:
        if r.get("kind") == "CHUNK" and r.get("transfer") == "AX-7782":
            if r["seq"] not in chunks or r["attempt"] > chunks[r["seq"]]["attempt"]:
                chunks[r["seq"]] = r
    k07 = b"".join(bytes.fromhex(chunks[i]["checkpoint"]) for i in range(8))

    return {"K01": k01, "K02": k02, "K03": k03, "K05": k05, "K06": k06, "K07": k07}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, default=Path("resources/evidence"))
    parser.add_argument("--acceptance", type=Path, default=Path("acceptance.json"))
    parser.add_argument("--routing", type=Path, default=Path("resources/evidence/recovery-routing.json"))
    args = parser.parse_args()

    acceptance = json.loads(args.acceptance.read_text())
    routing = json.loads(args.routing.read_text())
    targets = {k: v.lower() for k, v in acceptance["slot_sha256"].items()}
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target_k04 = targets["K04"]
    assert len(mask) == 16

    blocks = source_blocks(args.evidence_root)
    # Positive controls: source reconstructions must reproduce all six accepted slots.
    positive = {}
    for slot, block in blocks.items():
        component = hashlib.sha256(block).digest()[:16] if slot in {"K02", "K03", "K07"} else block
        positive[slot] = hashlib.sha256(component).hexdigest() == targets[slot]
    assert all(positive.values()), positive

    hits = []
    tested = 0
    for slot, block in blocks.items():
        digest = hashlib.sha256(block).digest()
        for half_name, coupon in (("head16", digest[:16]), ("tail16", digest[16:])):
            component = bytes(a ^ b for a, b in zip(coupon, mask))
            tested += 1
            if hashlib.sha256(component).hexdigest() == target_k04:
                hits.append({"source_slot": slot, "digest_half": half_name})

    print(json.dumps({
        "hypothesis": "K04 coupon is either half of SHA256(source block) from one accepted slot; component=coupon XOR route mask",
        "positive_controls": positive,
        "candidate_count": tested,
        "K04_hits": hits,
    }, indent=2))


if __name__ == "__main__":
    main()
