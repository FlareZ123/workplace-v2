#!/usr/bin/env python3
"""Original-source SFT: detect two apparent future-event references under earlier email dates.

Run with repository's resources/ directory as the first argument.
"""
from pathlib import Path
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from datetime import datetime
import configparser
import hashlib
import json
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
E = ROOT / "evidence"
P = {
    "mail13": E / "mail/13.eml",
    "mail16": E / "mail/16.eml",
    "spool": E / "print/spool-reconstruction.log",
    "transfers": E / "transfers/transfer-audit.jsonl",
    "routes": E / "archive-labels.ini",
}
PIN = {
    "mail13": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "mail16": "02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "transfers": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "routes": "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad",
}
for name, path in P.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == PIN[name], name

def mail(name):
    m = BytesParser(policy=policy.default).parsebytes(P[name].read_bytes())
    return parsedate_to_datetime(m["Date"]), m.get_content()

date13, text13 = mail("mail13")
date16, text16 = mail("mail16")
assert "final custodian handoff is AX-7782" in text13
assert "AX-7783, stopped before handoff" in text13
assert "The later REQUESTED entry" in text16

receipts = {
    r["transfer"]: r
    for line in P["transfers"].read_text().splitlines()
    if (r := json.loads(line))["kind"] in ("COMMIT", "ABORT")
}
assert receipts["AX-7782"]["kind"] == "COMMIT" and receipts["AX-7782"]["dry_run"] is False
assert receipts["AX-7783"]["kind"] == "ABORT"
receipt_utc = receipts["AX-7782"]["receipt_utc"]
assert receipts["AX-7783"]["receipt_utc"] == receipt_utc
receipt_time = datetime.fromisoformat(receipt_utc.replace("Z", "+00:00"))
gap13 = int((receipt_time - date13).total_seconds())
assert gap13 == 125950

cfg = configparser.ConfigParser()
cfg.read(P["routes"])
job = cfg["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
rows = []
for line in P["spool"].read_text().splitlines():
    m = re.match(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) ", line)
    if m and m[2] == job and m[5] == "RECOVER":
        rows.append((datetime.fromisoformat(m[1].replace("Z", "+00:00")), int(m[3]), m[4]))
assert sorted((attempt, state) for _, attempt, state in rows) == [
    (1, "REQUESTED"), (2, "ACK"), (3, "REQUESTED")
]
request3_time = next(t for t, attempt, state in rows if attempt == 3)
ack2_time = next(t for t, attempt, state in rows if attempt == 2)
assert request3_time > ack2_time
gap16 = int((request3_time - date16).total_seconds())
assert gap16 == 36840
print("MAIL13 -> AX7782/83 receipt: ", gap13, "seconds ahead")
print("MAIL16 -> ESC-N later request:", gap16, "seconds ahead")
print("PASS: two source-derived timestamp contradictions under literal contemporaneous mail model")
