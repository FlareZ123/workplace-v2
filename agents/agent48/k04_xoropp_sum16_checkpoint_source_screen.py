#!/usr/bin/env python3
"""Read-only, redacted original-source test of the conditional xoroshiro128++ gap inverse.

Only prints aggregate SAT/UNSAT/UNKNOWN counts and whether a complete
historical K04 commitment passes. Does not report or publish original
packet bytes, decoded candidates, source checkpoints or slot digests.
No interpretation of an opaque transfer checkpoint as a printer state
field is authenticated by the source; this is an explicit hypothesis.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from k04_xoropp_sum16_gap_erasure_synthetic import gap16_erasure_inverse

ROOT = Path(__file__).resolve().parents[2] / "resources"
PINS = {
    "evidence/print/spool-reconstruction.log":
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/transfers/transfer-audit.jsonl":
        "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def read_sources():
    for path, sha in PINS.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha, path
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_text()
    packets = {}
    for row in spool.splitlines():
        if "JOB=PS-261003-0417 " not in row or "CLASS=RECOVER" not in row:
            continue
        m = re.search(r"ATTEMPT=(\d+) STATE=(\w+) .*PAYLOAD=([0-9A-F]{32}) ", row)
        if m is None:
            continue
        # Deliberately do not decode or use the disputed middle ACK2.
        if (int(m.group(1)), m.group(2)) in ((1, "REQUESTED"), (3, "REQUESTED")):
            packets[(int(m.group(1)), m.group(2))] = bytes.fromhex(m.group(3))
    assert set(packets) == {(1, "REQUESTED"), (3, "REQUESTED")}
    audit = [json.loads(s) for s in
             (ROOT / "evidence/transfers/transfer-audit.jsonl").read_text().splitlines()]
    checkpoints = {x["seq"]:bytes.fromhex(x["checkpoint"]) for x in audit
                   if x["kind"] == "CHUNK" and x["transfer"] == "AX-7782"
                   and x["attempt"] == 2}
    assert set(checkpoints) == set(range(8))
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    targets = json.loads((ROOT / "acceptance.json").read_text())
    return packets[(1, "REQUESTED")], packets[(3, "REQUESTED")], checkpoints, bytes.fromhex(
        routing["K04"]["masked_component"]), targets["slot_sha256"]["K04"]

def words(packet, end, reversed_words):
    pair = [int.from_bytes(packet[i:i+8], end) for i in (0,8)]
    return pair[::-1] if reversed_words else pair

def run(timeout_ms=7000):
    prior, later, cps, route_mask, commitment = read_sources()
    counts = {"SAT":0, "UNSAT":0, "UNKNOWN":0}
    complete = 0
    passed = False
    for seq in range(8):
        for cp_end in ("big", "little"):
            anchor = int.from_bytes(cps[seq], cp_end)
            for word_end in ("big", "little"):
                for reverse in (False, True):
                    y0,y1 = words(prior, word_end, reverse)
                    y4,y5 = words(later, word_end, reverse)
                    for offset in (0, 48):
                        status, _, middle = gap16_erasure_inverse(
                            y0, y1, y4, y5, anchor, offset=offset, timeout_ms=timeout_ms)
                        assert status in counts
                        counts[status] += 1
                        complete += 1
                        if middle is None:
                            continue
                        predicted_words = middle[::-1] if reverse else middle
                        packet = b"".join(w.to_bytes(8, word_end) for w in predicted_words)
                        candidate = bytes(a ^ b for a,b in zip(packet, route_mask))
                        passed |= hashlib.sha256(candidate).hexdigest() == commitment
    assert complete == 128
    print(json.dumps({"cases":complete,"status_counts":counts,
                      "verified_historical_k04":passed},sort_keys=True))

if __name__ == "__main__":
    run()
