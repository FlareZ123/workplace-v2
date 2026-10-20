"""SFT: K04 dispatch ACK selector must not depend on spool payload integrity.

Use from a workplace-v2 checkout. No changes to original resources are made.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "work"))
from h17_witness_intake import last_escrow_ack  # noqa: E402

ORIGINAL = ROOT / "resources" / "evidence"
JOB = "PS-261003-0417"
EXPECTED = (JOB, 2, datetime(2026, 10, 3, 18, 2, tzinfo=timezone.utc))
ACK_PAYLOAD = b" PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench"
ACK_SELECTOR = b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"

CASES = (
    ("unchanged historical export", None),
    ("ACK present but 16-byte payload corrupted", b" PAYLOAD=CORRUPT DEST=bench"),
    ("ACK present but payload and destination missing", b""),
)


def run_case(name: str, replacement: bytes | None) -> None:
    with tempfile.TemporaryDirectory(prefix="h17-ack-selector-") as dirname:
        evidence = Path(dirname)
        (evidence / "print").mkdir()
        shutil.copy2(ORIGINAL / "archive-labels.ini", evidence / "archive-labels.ini")
        source = (ORIGINAL / "print" / "spool-reconstruction.log").read_bytes()
        selected_rows = [
            line for line in source.splitlines()
            if ACK_SELECTOR in line
        ]
        assert len(selected_rows) == 1, "Expected one source-selected ACK row"
        assert ACK_PAYLOAD in selected_rows[0], "Historical source payload differs"
        if replacement is not None:
            original_row = selected_rows[0]
            changed_row = original_row.replace(ACK_PAYLOAD, replacement)
            assert changed_row != original_row
            source = source.replace(original_row, changed_row)
        (evidence / "print" / "spool-reconstruction.log").write_bytes(source)
        observed = last_escrow_ack(evidence)
        print(f"case={name!r}; observed={observed!r}; expected={EXPECTED!r}", flush=True)
        assert observed == EXPECTED, f"Selector incorrectly depends on spool integrity: {name}"
        print(f"PASS: {name}", flush=True)


if __name__ == "__main__":
    for title, altered in CASES:
        run_case(title, altered)
    print("SFT PASS: valid ACK dispatch selector survives damaged/missing payload", flush=True)
