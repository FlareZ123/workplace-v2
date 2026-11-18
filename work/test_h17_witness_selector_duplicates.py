"""SFT: last ESC-N ACK must fail closed on contradictory source records.

The historical source is read, then each mutation occurs in a temporary copy.
No original evidence or acceptance commitment is written.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work"))
from h17_witness_intake import last_escrow_ack

SOURCE = ROOT / "resources" / "evidence"
JOB = "PS-261003-0417"
SELECTOR = "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"
EXPECTED = (JOB, 2, datetime(2026, 10, 3, 18, 2, tzinfo=timezone.utc))
ORIGINAL_PAYLOAD = "A9A9DC5731A5E2AE879C47215C2559D5"

def run() -> None:
    spool = (SOURCE / "print" / "spool-reconstruction.log").read_text(encoding="utf-8")
    selected = [line for line in spool.splitlines() if SELECTOR in line]
    assert len(selected) == 1
    row = selected[0]
    assert ORIGINAL_PAYLOAD in row

    scenarios = [
        ("original", "", False),
        ("identical duplicate", row, False),
        ("conflicting complete copied payload", row.replace(ORIGINAL_PAYLOAD,
            "F9A9DC5731A5E2AE879C47215C2559D5"), True),
        ("conflicting timestamp", row.replace("18:02:00Z", "18:12:00Z"), True),
        ("conflicting ACK class", row.replace("CLASS=RECOVER", "CLASS=LABEL"), True),
        ("higher ACK attempt with different class", row.replace(
            "ATTEMPT=2", "ATTEMPT=3").replace("CLASS=RECOVER", "CLASS=LABEL"), True),
        ("duplicate with missing payload", row.split(" PAYLOAD=")[0], False),
        ("later REQUESTED does not supersede ACK", row.replace(
            "STATE=ACK", "STATE=REQUESTED").replace("ATTEMPT=2", "ATTEMPT=3"), False),
    ]
    with tempfile.TemporaryDirectory(prefix="h17-ack-conflict-") as tempdir:
        evidence = Path(tempdir)
        (evidence / "print").mkdir()
        shutil.copyfile(SOURCE / "archive-labels.ini", evidence / "archive-labels.ini")
        for title, addition, rejects in scenarios:
            (evidence / "print" / "spool-reconstruction.log").write_text(
                spool + ("\n" + addition if addition else ""), encoding="utf-8"
            )
            try:
                observed = last_escrow_ack(evidence)
            except ValueError as error:
                if not rejects:
                    raise AssertionError(f"{title}: unexpected rejection {error}") from error
                print(f"PASS rejected: {title}: {error}", flush=True)
            else:
                assert not rejects, f"{title}: accepted inconsistent ACK records"
                assert observed == EXPECTED, (title, observed)
                print(f"PASS accepted: {title}: {observed}", flush=True)

if __name__ == "__main__":
    run()
    print("SFT PASS: eight original/contradictory selector scenarios", flush=True)
