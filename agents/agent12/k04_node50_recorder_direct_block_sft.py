#!/usr/bin/env python3
"""Bounded direct 16-byte donor screen over CRC-valid TRP2 node50 records.

Candidate blocks are frozen from source record fields before the K04 route
mask and acceptance commitment are loaded.
"""
from __future__ import annotations
import hashlib, json, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"

def sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def build_candidates(raw: bytes):
    magic, version, record_size, count = struct.unpack_from("<8sHHI", raw, 0)
    assert (magic, version, record_size, count) == (b"TRP2DUMP", 2, 24, 88)
    node50 = []
    for i in range(count):
        rec = raw[16 + i*24 : 16 + (i+1)*24]
        utc, node, event, latch, seq, control, aux, crc = struct.unpack("<I H B B I 4s I I", rec)
        if zlib.crc32(rec[:20]) & 0xffffffff != crc:
            continue
        if node == 50:
            node50.append({
                "seq": seq, "event": event, "latch": latch,
                "control": control, "aux": aux, "utc": utc,
            })
    node50.sort(key=lambda row: row["seq"])
    assert len(node50) == 72
    assert [row["seq"] for row in node50] == list(range(72))

    candidates = []
    def add(kind, rows, block):
        assert len(block) == 16
        candidates.append({
            "kind": kind,
            "seqs": [row["seq"] for row in rows],
            "block": block,
        })

    for i in range(len(node50)-3):
        rows = node50[i:i+4]
        add("four_control_words", rows, b"".join(row["control"] for row in rows))
    for i in range(len(node50)-3):
        rows = node50[i:i+4]
        add("four_aux_words_le", rows, b"".join(struct.pack("<I", row["aux"]) for row in rows))
    for i in range(len(node50)-1):
        rows = node50[i:i+2]
        add("two_records_control_aux", rows, b"".join(
            row["control"] + struct.pack("<I", row["aux"]) for row in rows
        ))
        add("two_records_aux_control", rows, b"".join(
            struct.pack("<I", row["aux"]) + row["control"] for row in rows
        ))

    assert len(candidates) == 280
    return node50, candidates

def matches(candidates, mask: bytes, target_hash: str):
    found = []
    for item in candidates:
        component = bytes(a ^ b for a, b in zip(item["block"], mask))
        if sha(component).hex() == target_hash:
            found.append({
                "kind": item["kind"], "seqs": item["seqs"],
                "payload": item["block"].hex().upper(),
                "component": component.hex().upper(),
            })
    return found

def main():
    recorder_bytes = (EVIDENCE / "recorder" / "trip-recorder.raw").read_bytes()
    assert sha(recorder_bytes).hex() == RECORDER_SHA
    node50, candidates = build_candidates(recorder_bytes)

    route_bytes = (EVIDENCE / "recovery-routing.json").read_bytes()
    acceptance_bytes = (ROOT / "resources" / "acceptance.json").read_bytes()
    assert sha(route_bytes).hex() == ROUTE_SHA
    assert sha(acceptance_bytes).hex() == ACCEPTANCE_SHA
    route = json.loads(route_bytes)
    acceptance = json.loads(acceptance_bytes)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target_hash = acceptance["slot_sha256"]["K04"]

    planted = candidates[0]
    planted_component = bytes(a ^ b for a, b in zip(planted["block"], mask))
    synthetic_hits = matches(candidates, mask, sha(planted_component).hex())
    synthetic_pass = any(
        hit["kind"] == planted["kind"]
        and hit["seqs"] == planted["seqs"]
        and hit["payload"] == planted["block"].hex().upper()
        for hit in synthetic_hits
    )
    assert synthetic_pass

    hits = matches(candidates, mask, target_hash)
    report = {
        "valid_node50_records": len(node50),
        "sequence_range": [node50[0]["seq"], node50[-1]["seq"]],
        "candidate_counts": {
            "four_control_words": 69,
            "four_aux_words_le": 69,
            "two_records_control_aux": 71,
            "two_records_aux_control": 71,
        },
        "candidate_blocks": len(candidates),
        "unique_candidate_blocks": len({item["block"] for item in candidates}),
        "synthetic_positive_control": synthetic_pass,
        "K04_commitment_hits": hits,
        "new_K04_bits_recovered": 0 if not hits else 128,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if hits:
        raise SystemExit(10)

if __name__ == "__main__":
    main()
