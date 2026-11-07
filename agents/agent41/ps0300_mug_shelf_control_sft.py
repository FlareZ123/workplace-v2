#!/usr/bin/env python3
"""Pinned source-only test of the conditional PS-0300 / PS-0312 mug-shelf-card hypotheses.

Run from the repository root:
    python agents/agent41/ps0300_mug_shelf_control_sft.py
Or pass --source-root to point at the extracted evidence directory.
This test does not inspect the absent mug-stock workbook or infer K08 wording.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


EXPECTED_SHA256 = {
    "mail/12.eml": "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "h17-supplemental-office-files/retired-office-bookmarks.html": "b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096",
}

JOB_ROWS = {
    "PS-261003-0300": ("2026-10-03T07:00:00+00:00", "1", "ACK", "LABEL", "store"),
    "PS-261003-0312": ("2026-10-03T08:00:00+00:00", "1", "ACK", "STORES", "store"),
    "PS-261003-0317": ("2026-10-03T08:25:00+00:00", "1", "ACK", "LABEL", "store"),
    "PS-261003-0318": ("2026-10-03T08:30:00+00:00", "1", "ACK", "RECOVER", "store"),
    "PS-261003-0323": ("2026-10-03T08:55:00+00:00", "1", "ACK", "RECOVER", "store"),
}


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("resources/evidence"),
        help="directory containing the extracted official evidence tree",
    )
    args = parser.parse_args()
    root = args.source_root

    for relative_path, expected in EXPECTED_SHA256.items():
        path = root / relative_path
        actual = normalized_sha256(path)
        assert actual == expected, f"{relative_path}: SHA256 mismatch: {actual}"

    mail = (root / "mail/12.eml").read_text(encoding="utf-8-sig")
    notes = (root / "crew/noticeboard-and-desk-notes.txt").read_text(encoding="utf-8-sig")
    spool = (root / "print/spool-reconstruction.log").read_text(encoding="utf-8-sig")
    bookmarks = (
        root / "h17-supplemental-office-files/retired-office-bookmarks.html"
    ).read_text(encoding="utf-8-sig")

    normalized_mail = re.sub(r"\s+", " ", mail)
    assert "I have put a small card by the shelf." in normalized_mail
    assert "chipped blue mugs" in normalized_mail
    assert "N11 / David" in notes
    assert "Mug shelf: Even the chipped blue one belongs to someone who expects to see it again." in notes
    assert "N12 / Simon" in notes
    assert "Workshop card: The best repair is sometimes remembering who comes on after you." in notes
    assert "R:/Stores/consumables/mug-stock.xls" in bookmarks
    assert spool.startswith("# printer buffer reconstruction; retained fragments, payload integrity unverified")

    parsed_jobs = {}
    for line in spool.splitlines():
        match = re.match(
            r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
            r"PAYLOAD=(\S+) DEST=(\S+)",
            line,
        )
        if match:
            timestamp, job, attempt, state, job_class, payload, destination = match.groups()
            parsed_jobs[job] = (
                timestamp,
                attempt,
                state,
                job_class,
                destination,
                payload,
            )

    for job, expected in JOB_ROWS.items():
        actual = parsed_jobs[job][:5]
        assert actual == expected, f"{job}: expected {expected}, got {actual}"
        payload = parsed_jobs[job][5]
        assert len(payload) == 32, f"{job}: expected 16-byte payload"
        bytes.fromhex(payload)

    assert not (root / "h17-supplemental-office-files/mug-stock.xls").exists()
    assert "PS-261003-0300" not in mail
    assert "PS-261003-0300" not in notes
    assert "PS-261003-0312" not in mail
    assert "PS-261003-0312" not in notes
    header_block = mail.split("\n\n", 1)[0]
    assert not re.search(r"(?im)^(In-Reply-To|References):", header_block)
    assert "MAIL-12" not in spool

    mail_date_line = next(
        line for line in mail.splitlines() if line.lower().startswith("date:")
    )
    mail_date = parsedate_to_datetime(mail_date_line.split(":", 1)[1].strip())
    ps0300_time = datetime.fromisoformat(JOB_ROWS["PS-261003-0300"][0])
    delta_seconds = int((ps0300_time - mail_date.astimezone(timezone.utc)).total_seconds())
    assert delta_seconds == 24 * 60 * 60 + 27 * 60

    print("Pinned source hashes: PASS")
    print("MAIL-12 shelf-card/mug wording and N11 mug-shelf note: PASS")
    print("mug-stock.xls bookmark pointer: PASS")
    print("PS-0300 / PS-0312 / PS-0317 / PS-0318 / PS-0323 spool rows: PASS")
    print("No literal MAIL-12 <-> PS-0300/PS-0312 identifier join or RFC thread headers in preserved MAIL-12: PASS")
    ps0312_time = datetime.fromisoformat(JOB_ROWS["PS-261003-0312"][0])
    delta_0312 = int((ps0312_time - mail_date.astimezone(timezone.utc)).total_seconds())
    assert delta_0312 == 25 * 60 * 60 + 27 * 60
    print(f"Unauthenticated displayed MAIL-12 Date to PS-0300 interval: {delta_seconds // 3600}h {delta_seconds % 3600 // 60}m")
    print(f"Unauthenticated displayed MAIL-12 Date to PS-0312 interval: {delta_0312 // 3600}h {delta_0312 % 3600 // 60}m")
    print("Conclusion: PS-0300 is an orphan LABEL/store candidate; PS-0312 is a conditional N12 workshop-card candidate.")
    print("Neither is directly joined to the MAIL-12 shelf card.")


if __name__ == "__main__":
    main()
