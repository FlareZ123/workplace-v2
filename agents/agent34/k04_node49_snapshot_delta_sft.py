#!/usr/bin/env python3
"""Source-pinned K04 screen of the valid node49/event82 snapshot delta.

Run with either the repository resources directory or an extracted archive root:
    python agents/agent34/k04_node49_snapshot_delta_sft.py [resources-or-archive-root]
"""
from __future__ import annotations
import hashlib, json, struct, sys, zlib
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = {
    "evidence/recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    "evidence/recorder/format-note.txt": "78ff213040de20f81bc582cdfc25a4d0930ceb2d3956dbcc944b775b88fd7b22",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def source_root() -> Path:
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
        if (root / "resources" / "evidence").is_dir():
            return root / "resources"
        if (root / "evidence").is_dir() and (root / "acceptance.json").is_file():
            return root
        raise FileNotFoundError(root)
    repo = Path(__file__).resolve().parents[2]
    if (repo / "resources" / "evidence").is_dir():
        return repo / "resources"
    if (repo / "evidence").is_dir() and (repo / "acceptance.json").is_file():
        return repo
    raise FileNotFoundError("expected resources/evidence or evidence under repository root")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    root = source_root()
    blobs = {name: (root / name).read_bytes() for name in EXPECTED}
    source_hashes = {name: sha256(data) for name, data in blobs.items()}
    for name, expected in EXPECTED.items():
        assert source_hashes[name] == expected, (name, source_hashes[name])

    route = json.loads(blobs["evidence/recovery-routing.json"])
    acceptance = json.loads(blobs["acceptance.json"])
    raw = blobs["evidence/recorder/trip-recorder.raw"]
    rule = route["K05"]
    # TRP2 header is 16 bytes; each 24-byte record has LE timestamp/node/event/
    # latch/seq, raw control[4], LE AUX u32 and LE stored CRC32.
    assert raw[:4] == b"TRP2" and len(raw) == 16 + 88 * 24
    start = int(datetime.fromisoformat(rule["start_utc"]).astimezone(timezone.utc).timestamp())
    end = int(datetime.fromisoformat(rule["end_utc_exclusive"]).astimezone(timezone.utc).timestamp())

    records = []
    for index in range(88):
        record = raw[16 + index * 24:16 + (index + 1) * 24]
        ts, node, event, latch, seq = struct.unpack_from("<I H B B I", record, 0)
        stored_crc = struct.unpack_from("<I", record, 20)[0]
        records.append({
            "index": index,
            "ts": ts,
            "node": node,
            "event": event,
            "latch": latch,
            "seq": seq,
            "control": record[12:16],
            "aux": struct.unpack_from("<I", record, 16)[0],
            "crc_good": (zlib.crc32(record[:20]) & 0xFFFFFFFF) == stored_crc,
        })

    eligible = [
        record for record in records
        if record["node"] == rule["node"]
        and record["event"] == rule["event"]
        and start <= record["ts"] < end
        and record["crc_good"]
    ]
    selected = {}
    for record in eligible:
        prior = selected.get(record["latch"])
        if prior is None or record["seq"] > prior["seq"]:
            selected[record["latch"]] = record
    assert set(selected) == {0, 1, 2, 3}
    assert [selected[latch]["seq"] for latch in range(4)] == [300, 301, 302, 303]
    selected_block = b"".join(selected[latch]["control"] for latch in range(4))
    assert sha256(selected_block) == acceptance["slot_sha256"]["K05"]

    previous = {}
    for latch in range(4):
        matches = [
            record for record in eligible
            if record["latch"] == latch and record["seq"] == 200 + latch
        ]
        assert len(matches) == 1
        previous[latch] = matches[0]
    previous_block = b"".join(previous[latch]["control"] for latch in range(4))
    assert [previous[latch]["seq"] for latch in range(4)] == [200, 201, 202, 203]

    # Natural per-latch state change from the earlier complete snapshot to the
    # K05-selected complete snapshot, preserving each opaque 4-byte word.
    delta = bytes(left ^ right for left, right in zip(previous_block, selected_block))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    candidates = (
        ("old200-xor-selected300-as-component", delta),
        (
            "old200-xor-selected300-as-payload-xor-K04-mask",
            bytes(value ^ mask_byte for value, mask_byte in zip(delta, mask)),
        ),
    )
    trials = []
    for interpretation, component in candidates:
        digest = sha256(component)
        trials.append({
            "interpretation": interpretation,
            "component_hex": component.hex().upper(),
            "component_sha256": digest,
            "matches_K04": digest == acceptance["slot_sha256"]["K04"],
        })
    hits = [trial for trial in trials if trial["matches_K04"]]
    assert len(trials) == 2 and not hits

    print(json.dumps({
        "source_sha256": source_hashes,
        "K04_target_sha256": acceptance["slot_sha256"]["K04"],
        "K05_positive_control": {
            "selected_seq_by_latch": [selected[latch]["seq"] for latch in range(4)],
            "selected_control_block_hex": selected_block.hex().upper(),
            "component_sha256": sha256(selected_block),
            "matches_K05": True,
        },
        "previous_snapshot": {
            "seq_by_latch": [previous[latch]["seq"] for latch in range(4)],
            "control_block_hex": previous_block.hex().upper(),
            "aux_by_latch": [previous[latch]["aux"] for latch in range(4)],
        },
        "selected_aux_by_latch": [selected[latch]["aux"] for latch in range(4)],
        "revision_delta_hex": delta.hex().upper(),
        "candidate_count": len(trials),
        "K04_hits": hits,
        "trials": trials,
        "selected_PS0417_ACK2_read": False,
        "official_inputs_modified": False,
    }, indent=2))

if __name__ == "__main__":
    main()
