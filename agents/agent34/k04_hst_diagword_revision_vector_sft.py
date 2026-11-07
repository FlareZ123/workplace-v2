#!/usr/bin/env python3
"""Source-pinned cross-slot K04 screen of complete HST-4 DIAG_WORD revisions.

Run from the repository root:
    python agents/agent34/k04_hst_diagword_revision_vector_sft.py

An optional first argument is either the repository resources directory or an
extracted archive root containing evidence/ and acceptance.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_SHA256 = {
    "evidence/telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
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
        raise FileNotFoundError(f"no evidence/ and acceptance.json under {root}")

    repo = Path(__file__).resolve().parents[2]
    if (repo / "resources" / "evidence").is_dir():
        return repo / "resources"
    if (repo / "evidence").is_dir() and (repo / "acceptance.json").is_file():
        return repo
    raise FileNotFoundError("expected resources/evidence or evidence beneath repository root")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    root = source_root()
    blobs = {name: (root / name).read_bytes() for name in EXPECTED_SHA256}
    source_hashes = {name: sha256(data) for name, data in blobs.items()}
    for name, expected in EXPECTED_SHA256.items():
        assert source_hashes[name] == expected, (name, source_hashes[name], expected)

    rows = [json.loads(line) for line in blobs["evidence/telemetry/freeze-export.jsonl"].splitlines()]
    route = json.loads(blobs["evidence/recovery-routing.json"])
    acceptance = json.loads(blobs["acceptance.json"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    k04_target = acceptance["slot_sha256"]["K04"].lower()
    k02_target = acceptance["slot_sha256"]["K02"].lower()

    revisions = {}
    for revision in (1, 2, 3, 4):
        selected = [
            row for row in rows
            if row["tag"] == "LT-204"
            and row["field"] == "DIAG_WORD"
            and row["revision"] == revision
        ]
        assert len(selected) == 8, (revision, len(selected))
        by_seq = {row["seq"]: row for row in selected}
        assert set(by_seq) == set(range(8)), (revision, sorted(by_seq))
        revisions[revision] = [by_seq[seq] for seq in range(8)]

    # Reproduce the official K02 reducer as a positive control.
    start = datetime.fromisoformat(route["K02"]["start_utc"]).astimezone(timezone.utc)
    end = datetime.fromisoformat(route["K02"]["end_utc_exclusive"]).astimezone(timezone.utc)
    eligible = {}
    for row in rows:
        if not (
            row["tag"] == "LT-204"
            and row["field"] == "DIAG_WORD"
            and row["quality"] == "GOOD"
            and row["state"] == "HOLD"
        ):
            continue
        timestamp = datetime.fromisoformat(row["ts"]).astimezone(timezone.utc)
        if not (start <= timestamp < end):
            continue
        prior = eligible.get(row["seq"])
        if prior is None or row["revision"] > prior["revision"]:
            eligible[row["seq"]] = row

    assert set(eligible) == set(range(8))
    k02_rows = [eligible[seq] for seq in range(8)]
    assert [row["revision"] for row in k02_rows] == [2] * 8
    k02_raw = b"".join(int(row["value"]).to_bytes(2, "big") for row in k02_rows)
    k02_component = hashlib.sha256(k02_raw).digest()[:16]
    assert sha256(k02_component) == k02_target

    trials = []
    for revision in (1, 2, 3, 4):
        source_rows = revisions[revision]
        for endian in ("big", "little"):
            raw_block = b"".join(
                int(row["value"]).to_bytes(2, endian) for row in source_rows
            )
            candidates = (
                ("raw-as-component", raw_block),
                (
                    "raw-as-payload-xor-K04-mask",
                    bytes(value ^ mask_byte for value, mask_byte in zip(raw_block, mask)),
                ),
            )
            for interpretation, component in candidates:
                digest = sha256(component)
                trials.append({
                    "revision": revision,
                    "quality": source_rows[0]["quality"],
                    "state": source_rows[0]["state"],
                    "endian": endian,
                    "interpretation": interpretation,
                    "component_hex": component.hex().upper(),
                    "component_sha256": digest,
                    "matches_K04": digest == k04_target,
                })

    hits = [trial for trial in trials if trial["matches_K04"]]
    assert len(trials) == 16
    assert not hits

    print(json.dumps({
        "source_sha256": source_hashes,
        "K04_target_sha256": k04_target,
        "K02_positive_control": {
            "selected_revisions_by_seq": [row["revision"] for row in k02_rows],
            "raw_vector_hex": k02_raw.hex().upper(),
            "component_hex": k02_component.hex().upper(),
            "component_sha256": sha256(k02_component),
            "matches_K02": True,
        },
        "revision_blocks": [
            {
                "revision": revision,
                "quality": revisions[revision][0]["quality"],
                "state": revisions[revision][0]["state"],
                "values_seq_0_to_7": [row["value"] for row in revisions[revision]],
            }
            for revision in (1, 2, 3, 4)
        ],
        "candidate_count": len(trials),
        "K04_hits": hits,
        "trials": trials,
        "selected_PS0417_ACK2_read": False,
        "official_inputs_modified": False,
    }, indent=2))


if __name__ == "__main__":
    main()
