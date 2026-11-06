"""Source-pinned pilot for a stateful printer-spool writer hypothesis.

Tests whether a 16-byte payload is a deterministic transition from the previous
spool state plus source metadata. It uses the 128-record pre-tail ACK prefix as
a holdout series and the same-job 0420 RECOVER ACK2 as a whole-object control.
No K04 commitment or target hash is read or used for model selection.

Run:
  python agents/agent5/k04_stateful_writer_chain_sft.py --root resources
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RETIREMENT_SHA256 = "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
ARCHIVE_LABELS_SHA256 = "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad"

TRANSFORMS = (
    "sha-prev-meta",
    "sha-meta-prev",
    "hmac-prev-meta",
    "hmac-meta-prev",
    "md5-prev-meta",
    "blake2s-prev-meta",
    "hmac-asset-prev-meta",
)
GLOBAL_TRANSFORMS = TRANSFORMS[:-1]
GLOBAL_METADATA = ("job-fields", "time-job-fields", "raw-line-no-payload")
SAME_JOB_METADATA = (
    "job-fields",
    "time-job-fields",
    "asset-job-fields",
    "filing-return-job",
)
JOB_417 = "PS-261003-0417"
JOB_420 = "PS-261003-0420"


def parse_sources(root: Path):
    spool_path = root / "evidence/print/spool-reconstruction.log"
    retirement_path = root / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
    labels_path = root / "evidence/archive-labels.ini"
    spool_raw = spool_path.read_bytes()
    retirement_raw = retirement_path.read_bytes()
    labels_raw = labels_path.read_bytes()
    assert hashlib.sha256(spool_raw).hexdigest() == SPOOL_SHA256
    assert hashlib.sha256(retirement_raw).hexdigest() == RETIREMENT_SHA256
    assert hashlib.sha256(labels_raw).hexdigest() == ARCHIVE_LABELS_SHA256

    rows = []
    pattern = re.compile(
        r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
        r"PAYLOAD=([A-F0-9]{32}) DEST=(\S+)$"
    )
    for line_number, line in enumerate(spool_raw.decode("utf-8").splitlines()):
        match = pattern.fullmatch(line)
        if not match:
            continue
        timestamp, job, attempt, state, klass, payload, dest = match.groups()
        rows.append({
            "line_number": line_number,
            "timestamp": timestamp,
            "job": job,
            "attempt": int(attempt),
            "state": state,
            "class": klass,
            "payload": bytes.fromhex(payload),
            "dest": dest,
            "raw_metadata": line.replace(" PAYLOAD=" + payload, ""),
        })
    assert len(rows) == 133
    assert all(row["state"] == "ACK" for row in rows[:128])

    retirement = retirement_raw.decode("utf-8")
    asset_map = {}
    for job in (JOB_417, JOB_420):
        match = re.search(
            rf"(?m)^\s*{re.escape(job)}\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s*$",
            retirement,
        )
        assert match, job
        return_set, account, filing = match.groups()
        asset_map[job] = {
            "return_set": return_set,
            "account": account,
            "filing": filing,
        }
    assert asset_map[JOB_417] == {
        "return_set": "L-29/N", "account": "FA-17", "filing": "H17-POL-17/A3"
    }
    assert asset_map[JOB_420] == {
        "return_set": "L-29/W", "account": "ST-09", "filing": "STORES/FLT"
    }
    labels = labels_raw.decode("utf-8")
    assert "ESC-N=PS-261003-0417" in labels
    assert "WATCH-SPARE=PS-261003-0420" in labels
    return rows, asset_map


def metadata(row, kind: str, asset_map):
    if kind == "job-fields":
        return (
            f'{row["job"]}|{row["attempt"]}|{row["state"]}|'
            f'{row["class"]}|{row["dest"]}'
        ).encode()
    if kind == "time-job-fields":
        return (
            f'{row["timestamp"]}|{row["job"]}|{row["attempt"]}|'
            f'{row["state"]}|{row["class"]}|{row["dest"]}'
        ).encode()
    if kind == "raw-line-no-payload":
        return row["raw_metadata"].encode()
    if kind == "asset-job-fields":
        a = asset_map[row["job"]]
        return (
            f'{a["account"]}|{row["job"]}|{row["attempt"]}|{row["state"]}|'
            f'{row["class"]}|{row["dest"]}'
        ).encode()
    if kind == "filing-return-job":
        a = asset_map[row["job"]]
        return (
            f'{a["filing"]}|{a["return_set"]}|{row["job"]}|{row["attempt"]}|'
            f'{row["class"]}|{row["dest"]}'
        ).encode()
    raise ValueError(kind)


def transition(name: str, previous: bytes, meta: bytes, asset_id: str = "") -> bytes:
    if name == "sha-prev-meta":
        return hashlib.sha256(previous + meta).digest()[:16]
    if name == "sha-meta-prev":
        return hashlib.sha256(meta + previous).digest()[:16]
    if name == "hmac-prev-meta":
        return hmac.new(previous, meta, hashlib.sha256).digest()[:16]
    if name == "hmac-meta-prev":
        return hmac.new(meta, previous, hashlib.sha256).digest()[:16]
    if name == "md5-prev-meta":
        return hashlib.md5(previous + meta).digest()
    if name == "blake2s-prev-meta":
        return hashlib.blake2s(previous + meta, digest_size=16).digest()
    if name == "hmac-asset-prev-meta":
        return hmac.new(asset_id.encode(), previous + meta, hashlib.sha256).digest()[:16]
    raise ValueError(name)


def find_row(rows, job, attempt, state, klass):
    matches = [
        row for row in rows
        if row["job"] == job and row["attempt"] == attempt
        and row["state"] == state and row["class"] == klass
    ]
    assert len(matches) == 1, (job, attempt, state, klass, len(matches))
    return matches[0]


def run(root: Path):
    rows, asset_map = parse_sources(root)
    synthetic_checks = []
    seed = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    synthetic_meta = b"PS-SYNTH-0001|2|ACK|RECOVER|bench"
    for name in TRANSFORMS:
        synthetic_output = transition(name, seed, synthetic_meta, "FA-17")
        assert transition(name, seed, synthetic_meta, "FA-17") == synthetic_output
        synthetic_checks.append({"transform": name, "output": synthetic_output.hex().upper()})

    global_results = []
    for transform_name in GLOBAL_TRANSFORMS:
        for metadata_name in GLOBAL_METADATA:
            exact = 0
            for index in range(1, 128):
                row = rows[index]
                predicted = transition(
                    transform_name,
                    rows[index - 1]["payload"],
                    metadata(row, metadata_name, asset_map),
                )
                exact += predicted == row["payload"]
            global_results.append({
                "transform": transform_name,
                "metadata": metadata_name,
                "exact_pre_tail_transitions": exact,
                "tested_pre_tail_transitions": 127,
            })

    prior_417 = find_row(rows, JOB_417, 1, "ACK", "LABEL")
    target_417 = find_row(rows, JOB_417, 2, "ACK", "RECOVER")
    prior_420 = find_row(rows, JOB_420, 1, "ACK", "STORES")
    control_420 = find_row(rows, JOB_420, 2, "ACK", "RECOVER")

    same_job_results = []
    for transform_name in TRANSFORMS:
        for metadata_name in SAME_JOB_METADATA:
            predictions = {}
            for job, prior, current in (
                (JOB_417, prior_417, target_417),
                (JOB_420, prior_420, control_420),
            ):
                meta = metadata(current, metadata_name, asset_map)
                predictions[job] = transition(
                    transform_name,
                    prior["payload"],
                    meta,
                    asset_map[job]["account"],
                )
            same_job_results.append({
                "transform": transform_name,
                "metadata": metadata_name,
                "predicted_0417_ack2": predictions[JOB_417].hex().upper(),
                "copied_0417_ack2_match": predictions[JOB_417] == target_417["payload"],
                "predicted_0420_ack2": predictions[JOB_420].hex().upper(),
                "0420_whole_object_control_match": predictions[JOB_420] == control_420["payload"],
            })

    control_hits = [
        row for row in same_job_results
        if row["0420_whole_object_control_match"]
    ]
    prefix_best = max(row["exact_pre_tail_transitions"] for row in global_results)
    result = {
        "status": "COMPLETE",
        "sources": {
            "spool_sha256": SPOOL_SHA256,
            "retirement_note_sha256": RETIREMENT_SHA256,
            "archive_labels_sha256": ARCHIVE_LABELS_SHA256,
            "payload_rows": len(rows),
            "pre_tail_ack_rows": 128,
        },
        "asset_join": asset_map,
        "hypothesis": (
            "A 16-byte payload is a deterministic state transition from the prior "
            "spool record or prior same-job ACK plus canonical job metadata."
        ),
        "synthetic_transition_sanity_checks": synthetic_checks,
        "global_previous_record_models": global_results,
        "same_job_previous_ack_models": same_job_results,
        "summary": {
            "global_models": len(global_results),
            "global_best_exact_transitions": prefix_best,
            "global_transitions_tested_per_model": 127,
            "same_job_models": len(same_job_results),
            "same_job_0420_whole_object_control_hits": len(control_hits),
            "same_job_0417_copy_matches": sum(
                row["copied_0417_ack2_match"] for row in same_job_results
            ),
            "promoted_candidate": None,
            "k04_commitment_contacted": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd() / "resources")
    args = parser.parse_args()
    run(args.root)


if __name__ == "__main__":
    main()
