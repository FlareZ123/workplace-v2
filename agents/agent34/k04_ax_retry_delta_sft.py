#!/usr/bin/env python3
"""Source-pinned K04 screen of per-chunk AX checkpoint retry XOR deltas.

Run with either the repository resources directory or an extracted archive root:
    python agents/agent34/k04_ax_retry_delta_sft.py [resources-or-archive-root]
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

EXPECTED = {
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
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

    rows = [json.loads(line) for line in blobs["evidence/transfers/transfer-audit.jsonl"].splitlines()]
    route = json.loads(blobs["evidence/recovery-routing.json"])
    acceptance = json.loads(blobs["acceptance.json"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    k04_target = acceptance["slot_sha256"]["K04"].lower()
    k07_target = acceptance["slot_sha256"]["K07"].lower()

    transfers = sorted({row["transfer"] for row in rows})
    summaries = {row["transfer"]: row for row in rows if row["kind"] != "CHUNK"}
    chunks = {}
    for row in rows:
        if row["kind"] == "CHUNK":
            chunks.setdefault(row["transfer"], {})[(row["seq"], row["attempt"])] = bytes.fromhex(row["checkpoint"])

    assert transfers == ["AX-7778", "AX-7781", "AX-7782", "AX-7783"]
    assert set(summaries) == set(transfers)
    for transfer in transfers:
        assert set(chunks[transfer]) == {
            (seq, attempt) for seq in range(8) for attempt in (1, 2)
        }
        assert all(len(value) == 2 for value in chunks[transfer].values())

    # Positive control: reproduce K07 from AX-7782's greatest attempt per seq.
    selected = b"".join(chunks["AX-7782"][(seq, 2)] for seq in range(8))
    k07_component = hashlib.sha256(selected).digest()[:16]
    assert sha256(k07_component) == k07_target
    assert summaries["AX-7782"]["kind"] == "COMMIT"
    assert summaries["AX-7782"]["dry_run"] is False
    assert summaries["AX-7778"]["kind"] == "COMMIT"
    assert summaries["AX-7778"]["dry_run"] is False
    assert summaries["AX-7781"]["kind"] == "COMMIT"
    assert summaries["AX-7781"]["dry_run"] is True
    assert summaries["AX-7783"]["kind"] == "ABORT"

    trials = []
    for transfer in transfers:
        delta = b"".join(
            bytes(left ^ right for left, right in zip(
                chunks[transfer][(seq, 1)], chunks[transfer][(seq, 2)]
            ))
            for seq in range(8)
        )
        for interpretation, component in (
            ("retry-delta-as-component", delta),
            (
                "retry-delta-as-payload-xor-K04-mask",
                bytes(value ^ mask_byte for value, mask_byte in zip(delta, mask)),
            ),
        ):
            digest = sha256(component)
            trials.append({
                "transfer": transfer,
                "transfer_status": summaries[transfer]["kind"],
                "dry_run": summaries[transfer].get("dry_run"),
                "interpretation": interpretation,
                "delta_hex": delta.hex().upper(),
                "component_hex": component.hex().upper(),
                "component_sha256": digest,
                "matches_K04": digest == k04_target,
            })

    hits = [trial for trial in trials if trial["matches_K04"]]
    assert len(trials) == 8 and not hits
    print(json.dumps({
        "source_sha256": source_hashes,
        "K04_target_sha256": k04_target,
        "K07_positive_control": {
            "AX7782_attempt2_vector_hex": selected.hex().upper(),
            "K07_component_hex": k07_component.hex().upper(),
            "component_sha256": sha256(k07_component),
            "matches_K07": True,
        },
        "transfer_summaries": summaries,
        "candidate_count": len(trials),
        "K04_hits": hits,
        "trials": trials,
        "selected_PS0417_ACK2_read": False,
        "official_inputs_modified": False,
    }, indent=2))

if __name__ == "__main__":
    main()
