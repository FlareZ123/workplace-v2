#!/usr/bin/env python3
"""Reproduce the North tab-05 ST-to-PS offset discriminator.

Run from the repository root:
    python agents/agent38/st_ps_offset_discriminator_sft.py
"""
from __future__ import annotations

import configparser
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIREMENT = ROOT / "resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
LABELS = ROOT / "resources/evidence/archive-labels.ini"
ROUTING = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"

retirement = RETIREMENT.read_text(encoding="utf-8")
north = re.search(r"(?ms)^L-29/N.*?\n(.*?)(?=^L-29/[SW]\b|\Z)", retirement)
if not north:
    raise SystemExit("Could not locate the L-29/N binder block")
tab5 = re.search(r"(?m)^\s*05\s+(ST-\d{3})\b", north.group(1))
if not tab5:
    raise SystemExit("Could not locate L-29/N tab 05")
ticket = tab5.group(1)

labels = configparser.ConfigParser()
labels.read(LABELS, encoding="utf-8")
target_job = labels["printer_routes_2026-09-01_to_2026-10-03"]["esc-n"]
target_suffix = int(target_job.rsplit("-", 1)[1])

routing = json.loads(ROUTING.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
target_digest = acceptance["slot_sha256"]["K04"]

rows: dict[str, list[dict[str, object]]] = {}
pattern = re.compile(
    r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
    r"PAYLOAD=([0-9A-Fa-f]{32})"
)
for line in SPOOL.read_text(encoding="utf-8").splitlines():
    match = pattern.search(line)
    if not match:
        continue
    job, attempt, state, job_class, payload_hex = match.groups()
    rows.setdefault(job, []).append(
        {
            "attempt": int(attempt),
            "state": state,
            "class": job_class,
            "payload": bytes.fromhex(payload_hex),
        }
    )

def last_ack(job: str) -> dict[str, object]:
    acks = [row for row in rows.get(job, []) if row["state"] == "ACK"]
    if not acks:
        raise SystemExit(f"No ACK found for {job}")
    return max(acks, key=lambda row: int(row["attempt"]))

target_ack = last_ack(target_job)
print(f"North final binder tab: {ticket}")
print(f"Selected ESC-N job: {target_job}")
print(
    "Selected job last ACK: "
    f"attempt={target_ack['attempt']} class={target_ack['class']}"
)
print("Offset comparison:")
for offset in (300, 304):
    mapped_suffix = int(ticket[3:]) + offset
    mapped_job = f"PS-261003-{mapped_suffix:04d}"
    ack = last_ack(mapped_job)
    payload = ack["payload"]
    assert isinstance(payload, bytes)
    candidate = bytes(a ^ b for a, b in zip(payload, mask))
    digest = hashlib.sha256(candidate).hexdigest()
    print(
        f"  +{offset}: {ticket} -> {mapped_job}; "
        f"gap_to_selected={target_suffix - mapped_suffix}; "
        f"last_ACK_attempt={ack['attempt']}; class={ack['class']}; "
        f"K04_commitment_match={digest == target_digest}"
    )
