#!/usr/bin/env python3
"""Reproduce the HST-4 PV seq ↔ spool-job suffix crosswalk."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"


def load_starts() -> list[int]:
    source = ROOT / "agents" / "agent49" / "k04_p951_symbolic_basis.py"
    spec = importlib.util.spec_from_file_location("k04_p951_symbolic_basis", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load p951 source: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.STARTS


def read_spool_rows() -> list[dict[str, int | str]]:
    pattern = re.compile(
        r"JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+)"
    )
    rows = []
    path = EVIDENCE / "print" / "spool-reconstruction.log"
    for line in path.read_text(encoding="ascii").splitlines():
        match = pattern.search(line)
        if match is None:
            continue
        job, attempt, state, job_class = match.groups()
        rows.append(
            {
                "job": int(job),
                "attempt": int(attempt),
                "state": state,
                "class": job_class,
            }
        )
    return rows


def read_pv_rows() -> dict[int, dict]:
    path = EVIDENCE / "telemetry" / "freeze-export.jsonl"
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    pv_rows = [row for row in rows if row["field"] == "PV"]
    by_seq = {row["seq"]: row for row in pv_rows}
    assert len(pv_rows) == 112
    assert len(by_seq) == len(pv_rows)
    assert sorted(by_seq) == list(range(100, 212))
    return by_seq


def main() -> None:
    starts = load_starts()
    spool = read_spool_rows()
    pv = read_pv_rows()

    assert len(starts) == len(spool) == 133
    assert [row["job"] for row in spool[:128]] == list(range(300, 428))

    for index, seq in enumerate(range(100, 212)):
        assert spool[index]["job"] == seq + 200

    observed_gaps = [
        starts[index + 1] - (starts[index] + 4)
        for index in range(112)
    ]
    missing_gaps = [
        starts[index + 1] - (starts[index] + 4)
        for index in range(112, 128)
    ]
    assert min(observed_gaps) == 2
    assert max(observed_gaps) == 13
    assert sum(observed_gaps) == 389
    assert missing_gaps == [5, 3, 4, 5, 2, 4, 3, 4, 2, 3, 2, 2, 2, 2, 2, 1]

    original_0417 = spool[117]
    selected_0417 = spool[129]
    assert original_0417 == {
        "job": 417,
        "attempt": 1,
        "state": "ACK",
        "class": "LABEL",
    }
    assert selected_0417 == {
        "job": 417,
        "attempt": 2,
        "state": "ACK",
        "class": "RECOVER",
    }
    assert starts[117] == 876
    assert starts[129] == 951

    print("HST PV seq 100..211 maps exactly to spool jobs 300..411 (+200).")
    print("Missing HST seq 212..227 maps to spool jobs 412..427.")
    print("Target PS-0417: original ACK1/LABEL row117 stage876;")
    print("               selected ACK2/RECOVER row129 stage951.")
    print("Missing seq212..227 gap lengths:", missing_gaps)
    print("PASS: source-pinned arithmetic crosswalk reproduced.")


if __name__ == "__main__":
    main()
