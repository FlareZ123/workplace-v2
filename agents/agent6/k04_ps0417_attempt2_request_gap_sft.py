#!/usr/bin/env python3
"""Verify the PS-0417 attempt-2 REQUESTED-row gap and bounded K04 payload checks."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


HEADER = re.compile(
    r"^(?P<timestamp>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
    r"STATE=(?P<state>\S+) CLASS=(?P<class>\S+)"
)
PAYLOAD = re.compile(r"\bPAYLOAD=([0-9A-F]{32})\b")


def main() -> None:
    root = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) == 2
        else Path(__file__).resolve().parents[2] / "resources"
    )
    if len(sys.argv) > 2:
        raise SystemExit("usage: python k04_ps0417_attempt2_request_gap_sft.py [resource-root]")

    spool = root / "evidence/print/spool-reconstruction.log"
    mail16 = (root / "evidence/mail/16.eml").read_text(encoding="utf-8")
    routing = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))

    rows = []
    for line_number, line in enumerate(spool.read_text(encoding="ascii").splitlines(), 1):
        match = HEADER.match(line)
        if match and match.group("job") == "PS-261003-0417":
            row = match.groupdict()
            row["line_number"] = line_number
            row["line"] = line
            row["attempt"] = int(row["attempt"])
            rows.append(row)

    assert [(r["attempt"], r["state"], r["class"]) for r in rows] == [
        (1, "ACK", "LABEL"),
        (1, "REQUESTED", "RECOVER"),
        (2, "ACK", "RECOVER"),
        (3, "REQUESTED", "RECOVER"),
    ]
    recover_requests = [r for r in rows if r["state"] == "REQUESTED" and r["class"] == "RECOVER"]
    recover_acks = [r for r in rows if r["state"] == "ACK" and r["class"] == "RECOVER"]
    assert [r["attempt"] for r in recover_requests] == [1, 3]
    assert [r["attempt"] for r in recover_acks] == [2]
    selected = max(recover_acks, key=lambda r: r["attempt"])
    assert selected["timestamp"] == "2026-10-03T18:02:00Z"

    mail16_flat = " ".join(mail16.split())
    assert "later REQUESTED entry was a" in mail16_flat
    assert "button press that never returned an acknowledgement" in mail16_flat
    assert "ACK field came from the dispatch log" in mail16_flat
    assert "not be read as a media-integrity flag" in mail16_flat

    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    candidates = [recover_requests[0], selected, recover_requests[1]]

    print("PS-0417 rows selected by header fields before payload parsing:")
    for row in rows:
        print(
            f"line={row['line_number']} time={row['timestamp']} "
            f"attempt={row['attempt']} state={row['state']} class={row['class']}"
        )

    print("RECOVER REQUESTED attempts:", [r["attempt"] for r in recover_requests])
    print("RECOVER ACK attempts:", [r["attempt"] for r in recover_acks])
    print("REQUESTED attempt 2 present: False")

    for row in candidates:
        payload_match = PAYLOAD.search(row["line"])
        assert payload_match is not None
        payload = bytes.fromhex(payload_match.group(1))
        component = bytes(a ^ b for a, b in zip(payload, mask))
        digest = hashlib.sha256(component).hexdigest()
        assert digest != target
        print(
            f"attempt={row['attempt']} state={row['state']} "
            f"payload={payload.hex().upper()} "
            f"candidate={component.hex().upper()} "
            f"sha256={digest} commitment_match=False"
        )

    print("PASS: selected last ACK is attempt 2; its REQUESTED row is absent.")
    print("PASS: attempt 3 remains REQUESTED and is excluded by MAIL-16.")
    print("PASS: attempt-1 request, attempt-2 ACK copy, and attempt-3 request do not hit K04.")
    print("LIMIT: this does not authenticate the media payload or reconstruct the missing request.")


if __name__ == "__main__":
    main()
