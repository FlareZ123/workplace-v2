#!/usr/bin/env python3
"""Verify the N01-N24 / PS-261003-0301..0324 structural crosswalk.

This checks numbering and timing only. It does not establish that the 16-byte
spool payloads are correct or that the note/job association is causal.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def main() -> None:
    if len(sys.argv) > 1:
        archive = Path(sys.argv[1])
    else:
        archive = Path(__file__).resolve().parents[1] / "resources" / "h17-archive-dump.zip"

    with zipfile.ZipFile(archive) as zf:
        notes_text = zf.read("evidence/crew/noticeboard-and-desk-notes.txt").decode("utf-8")
        spool_text = zf.read("evidence/print/spool-reconstruction.log").decode("utf-8")

    notes = {
        int(m.group(1)): {"author": m.group(2).strip(), "text": m.group(3).strip()}
        for m in re.finditer(r"(?m)^N(\d{2}) / ([^\n]+)\n([^\n]+)$", notes_text)
    }
    spool_rows = {}
    row_pattern = re.compile(
        r"(?m)^(\S+) JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\S+) "
        r"CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$"
    )
    for m in row_pattern.finditer(spool_text):
        suffix = int(m.group(2))
        spool_rows.setdefault(suffix, []).append({
            "timestamp": m.group(1),
            "job": f"PS-261003-{suffix:04d}",
            "attempt": int(m.group(3)),
            "state": m.group(4),
            "class": m.group(5),
            "payload": m.group(6),
            "dest": m.group(7),
        })

    assert len(notes) == 24, f"expected 24 notes, found {len(notes)}"
    assert set(notes) == set(range(1, 25)), "note IDs are not exactly N01-N24"

    rows = []
    for note_id in range(1, 25):
        suffix = 300 + note_id
        candidates = spool_rows.get(suffix, [])
        assert len(candidates) == 1, (
            f"job suffix {suffix:04d}: expected one row, found {len(candidates)}"
        )
        row = candidates[0]
        assert row["attempt"] == 1 and row["state"] == "ACK", (
            f"job {row['job']} is not a single attempt-1 ACK"
        )
        rows.append({
            "note": f"N{note_id:02d}",
            "author": notes[note_id]["author"],
            "text": notes[note_id]["text"],
            **row,
        })

    times = [
        datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        for row in rows
    ]
    intervals = [
        (times[i] - times[i - 1]).total_seconds()
        for i in range(1, len(times))
    ]
    assert intervals == [300.0] * 23, f"unexpected intervals: {intervals}"

    print(json.dumps({
        "notes": len(notes),
        "matched_jobs": len(rows),
        "suffix_rule": "job suffix = 300 + note number",
        "attempt_state": "all 24 are ATTEMPT=1 STATE=ACK",
        "interval_seconds": sorted(set(intervals)),
        "rows": rows,
        "interpretation_limit": (
            "Structural numbering/timing alignment only; no proof of causal note/job linkage "
            "or payload correctness."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
