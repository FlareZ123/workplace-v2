#!/usr/bin/env python3
"""Audit candidate ST -> PTW/PS numeric offsets without treating any as authoritative.

Reads only the recovered local evidence in resources/evidence. No network access
or writes. Run from any directory:
    python agents/agent12/st_ptw_ps_offset_scan.py
    python agents/agent12/st_ptw_ps_offset_scan.py C:/path/to/workplace-v2
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


NORTH_ORDER = (94, 81, 106, 99, 112)  # print-fleet binder tab order
GAPS = (43, 44, 96)  # p951 high-leverage printer gaps
TARGET_JOB = 417


def evidence_root(repo_root: Path) -> Path:
    for candidate in (repo_root / "resources" / "evidence", repo_root / "evidence"):
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not find resources/evidence or evidence")


def read_sources(root: Path):
    supplier_path = root / "h17-supplemental-office-files" / "supplier-reconciliation-L29.csv"
    ptw_path = root / "maintenance" / "seal-receipts.jsonl"
    spool_path = root / "print" / "spool-reconstruction.log"

    supplier_lines = supplier_path.read_text(encoding="utf-8").splitlines()
    supplier = list(csv.DictReader(supplier_lines[3:]))
    posted = [r for r in supplier if r.get("posting") == "POSTED"]

    ptw = defaultdict(list)
    for line in ptw_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            ptw[int(row["permit"].split("-")[1])].append(row)

    ps_jobs = set()
    for line in spool_path.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\bJOB=PS-261003-(\d{4})\b", line)
        if match:
            ps_jobs.add(int(match.group(1)))

    return posted, ptw, ps_jobs


def ticket_ids(rows, account: str, folio: str) -> list[int]:
    return sorted({
        int(r["line_ref"].split("-")[1])
        for r in rows
        if r.get("account") == account and r.get("folio") == folio
    })


def summarize_offset(offset: int, groups, singleton_bays, ps_jobs):
    summary = {}
    for name, ids in groups.items():
        mapped = [n + offset for n in ids]
        ptw_hits = [n for n in mapped if n in singleton_bays]
        ps_hits = [n for n in mapped if n in ps_jobs]
        bays = [singleton_bays[n] for n in ptw_hits]
        summary[name] = {
            "ptw": len(ptw_hits),
            "unique_bays": len(set(bays)),
            "bays": "".join(bays),
            "ps": len(ps_hits),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    root = evidence_root(args.repo_root.resolve())
    posted, ptw, ps_jobs = read_sources(root)

    singleton_bays = {
        pid: rows[0]["bay"]
        for pid, rows in ptw.items()
        if 390 <= pid <= 416 and len(rows) == 1
    }
    if len(singleton_bays) != 27:
        raise AssertionError(f"Expected 27 singleton PTW-390..416 receipts, found {len(singleton_bays)}")

    exact_ptw_ps = sorted(pid for pid in singleton_bays if pid in ps_jobs)
    print(f"PTW singleton IDs: {len(singleton_bays)}")
    print(f"Same-suffix PS jobs: {len(exact_ptw_ps)}/27")
    print(f"PTW-417 rows (multi-bay special case): {len(ptw.get(417, []))}")

    groups = {
        "L29/N FA-17": ticket_ids(posted, "FA-17", "H17-POL-17/A3"),
        "L28 FA-17": ticket_ids(posted, "FA-17", "H17-POL-17/A2"),
        "L29/S LV-42": ticket_ids(posted, "LV-42", "H17-POL-17/B4"),
        "Watch ST-09": ticket_ids(posted, "ST-09", "H17-POL-17/C1"),
    }
    if set(groups["L29/N FA-17"]) != set(NORTH_ORDER):
        raise AssertionError(f"Unexpected L29/N ticket set: {groups['L29/N FA-17']}")

    scored = []
    for offset in range(200, 401):
        s = summarize_offset(offset, groups, singleton_bays, ps_jobs)
        north = s["L29/N FA-17"]
        old = s["L28 FA-17"]
        scored.append((
            north["ptw"], north["unique_bays"], old["ptw"],
            north["ps"], old["ps"], offset, s
        ))

    scored.sort(key=lambda x: x[:5], reverse=True)
    print("\nTop offsets by North PTW coverage, bay diversity, and L28 holdout:")
    for nptw, bays, oldptw, nps, ops, offset, _ in scored[:12]:
        print(
            f"  +{offset}: North PTW {nptw}/5, bays {bays}/4, "
            f"L28 PTW {oldptw}/2, North PS {nps}/5, L28 PS {ops}/2"
        )

    for offset in (300, 304):
        print(f"\nOFFSET +{offset}")
        for name, ids in groups.items():
            details = []
            for ticket in ids:
                mapped = ticket + offset
                bay = singleton_bays.get(mapped, "-")
                details.append(f"ST-{ticket:03d}-> {mapped} (bay {bay}, PS {'yes' if mapped in ps_jobs else 'no'})")
            print(f"  {name}: " + "; ".join(details))
        print(f"  PS-{TARGET_JOB:04d} maps to ST-{TARGET_JOB - offset:03d}")
        mapped_gaps = [300 + gap - offset for gap in GAPS]
        print(f"  p951 gaps {GAPS} map to ST IDs {tuple(mapped_gaps)}")

    print("\nInterpretation: offsets are hypotheses only. No source in this export explicitly")
    print("pairs an ST ticket ID with a PTW permit or PS job. Retrieve the original")
    print("SEP26 return index or a paired ticket before using inferred ST IDs.")


if __name__ == "__main__":
    main()
