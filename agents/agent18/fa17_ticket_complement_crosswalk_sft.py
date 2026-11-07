#!/usr/bin/env python3
"""Adversarial SFT for the FA-17 417-minus-ticket spool crosswalk.

Run from the repository root:
    python agents/agent18/fa17_ticket_complement_crosswalk_sft.py

The script checks the original resource bytes and distinguishes arithmetic
coincidence from an authenticated ticket-to-job relation. It does not inspect
or use the withdrawn BX25-08 folio.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path

EXPECTED_SHA256 = {
    "h17-supplemental-office-files/supplier-reconciliation-L29.csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "h17-supplemental-office-files/print-fleet-retirement-note.txt": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
}


def locate_evidence() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if (repo_root / "resources" / "evidence").is_dir():
        return repo_root / "resources" / "evidence"
    if (repo_root / "evidence").is_dir():
        return repo_root / "evidence"
    raise FileNotFoundError("expected resources/evidence or evidence beneath repository root")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    evidence = locate_evidence()
    paths = {name: evidence / name for name in EXPECTED_SHA256}
    for name, path in paths.items():
        actual = sha256(path)
        assert actual == EXPECTED_SHA256[name], (name, actual)

    csv_text = paths["h17-supplemental-office-files/supplier-reconciliation-L29.csv"].read_text(encoding="utf-8")
    csv_lines = [line for line in csv_text.splitlines() if line and not line.startswith("#")]
    rows = list(csv.DictReader(io.StringIO("\n".join(csv_lines))))

    fleet_text = paths["h17-supplemental-office-files/print-fleet-retirement-note.txt"].read_text(encoding="utf-8")
    spool_text = paths["print/spool-reconstruction.log"].read_text(encoding="utf-8")
    notes_text = paths["crew/noticeboard-and-desk-notes.txt"].read_text(encoding="utf-8")

    binder_order = re.findall(r"^L-29/N\s+\d+\s+(ST-\d{3})\b", fleet_text, flags=re.MULTILINE)
    assert binder_order == ["ST-094", "ST-081", "ST-106", "ST-099", "ST-112"]

    by_ticket = {}
    for row in rows:
        if row["account"] == "FA-17" and row["posting"] == "POSTED" and row["source"] in {"L28", "L29"}:
            by_ticket[row["line_ref"]] = row
    north = [by_ticket[t] for t in binder_order]
    a2_holdouts = [row for row in rows if row["account"] == "FA-17" and row["source"] == "L28"
                   and row["posting"] == "POSTED" and row["folio_or_jacket"] == "H17-POL-17/A2"]
    assert [row["line_ref"] for row in a2_holdouts] == ["ST-098", "ST-087"]
    selected = north + a2_holdouts
    ticket_suffixes = [int(row["line_ref"].split("-")[1]) for row in selected]
    assert ticket_suffixes == [94, 81, 106, 99, 112, 98, 87]

    spool_rows = []
    pattern = re.compile(
        r"^(?P<ts>\S+)\s+JOB=PS-261003-(?P<job>\d{4})\s+ATTEMPT=(?P<attempt>\d+)\s+"
        r"STATE=(?P<state>\S+)\s+CLASS=(?P<class>\S+)\s+PAYLOAD=(?P<payload>[0-9A-F]{32})\s+DEST=(?P<dest>\S+)"
    )
    for line in spool_text.splitlines():
        match = pattern.search(line)
        if match:
            item = match.groupdict()
            item["job"] = int(item["job"])
            item["attempt"] = int(item["attempt"])
            spool_rows.append(item)
    assert len(spool_rows) == 133, len(spool_rows)
    spool_jobs = {row["job"] for row in spool_rows}
    assert set(range(300, 428)).issubset(spool_jobs)

    note_ids = {int(n) for n in re.findall(r"^N(\d{2})\s*/", notes_text, flags=re.MULTILINE)}
    assert note_ids == set(range(1, 25)), sorted(note_ids)

    target_match = re.search(r"^PS-261003-(\d{4})\s+ESC-N\s+L-29/N\s+FA-17\b", fleet_text, flags=re.MULTILINE)
    assert target_match, "could not resolve K04 job anchor from print-fleet register"
    anchor = int(target_match.group(1))
    assert anchor == 417
    note_base = 300  # the already-reported N01..N24 -> PS0301..PS0324 structural alignment

    mapping = []
    for row, ticket in zip(selected, ticket_suffixes):
        job = anchor - ticket
        note = job - note_base
        candidates = [x for x in spool_rows if x["job"] == job]
        assert len(candidates) == 1, (job, len(candidates))
        spool = candidates[0]
        mapping.append({
            "ticket": row["line_ref"],
            "source": row["source"],
            "run": row["run"],
            "posting": row["posting"],
            "folio": row["folio_or_jacket"],
            "description": row["description"],
            "job": job,
            "note_hypothesis": note,
            "note_present_in_export": note in note_ids,
            "spool_utc": spool["ts"],
            "class": spool["class"],
            "dest": spool["dest"],
        })

    all_job_anchors = [k for k in range(300, 601) if all(k - t in spool_jobs for t in ticket_suffixes)]
    anchor_scores = []
    for k in all_job_anchors:
        note_values = [k - note_base - t for t in ticket_suffixes]
        anchor_scores.append((sum(n in note_ids for n in note_values), k, note_values))
    best_note_hits = max(score[0] for score in anchor_scores)
    best_note_anchors = [score[1] for score in anchor_scores if score[0] == best_note_hits]
    actual_score = next(score for score in anchor_scores if score[1] == anchor)

    # The source files do not contain a common per-ticket/per-job key.
    assert "PS-261003-" not in csv_text
    assert not re.search(r"\bST-\d{3}\b", spool_text)
    assert all(ticket in fleet_text for ticket in binder_order)
    assert "PS-261003-0417" in fleet_text
    assert not any(f"PS-261003-{row['job']:04d}" in fleet_text for row in mapping)

    report = {
        "source_sha256": {name: sha256(path) for name, path in paths.items()},
        "k04_anchor_from_fleet_register": anchor,
        "ticket_suffixes_in_order": ticket_suffixes,
        "mapping_417_minus_ticket": mapping,
        "known_note_ids": sorted(note_ids),
        "all_seven_jobs_exist": all(row["job"] in spool_jobs for row in mapping),
        "anchors_300_to_600_that_map_all_seven_into_existing_spool_jobs": {
            "count": len(all_job_anchors),
            "min": min(all_job_anchors),
            "max": max(all_job_anchors),
        },
        "note_hit_count_at_417": actual_score[0],
        "max_note_hits_over_job_valid_anchors": best_note_hits,
        "anchors_tying_for_max_note_hits": best_note_anchors,
        "missing_note_hypotheses_at_417": [row["note_hypothesis"] for row in mapping if not row["note_present_in_export"]],
        "source_join_gap": {
            "supplier_csv_has_spool_job_ids": "PS-261003-" in csv_text,
            "spool_log_has_supplier_ticket_ids": bool(re.search(r"\bST-\d{3}\b", spool_text)),
            "fleet_note_has_per_ticket_0300_job_pairings": any(
                f"PS-261003-{row['job']:04d}" in fleet_text for row in mapping
            ),
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
