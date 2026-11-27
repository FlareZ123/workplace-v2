#!/usr/bin/env python3
"""Offline, read-only PTW-417 and route-mask sum-coordinate anchor screen.

LOCAL/authorized only: do not run with historical evidence in public CI.
Does not read K04 selected ACK2 payload, K04 acceptance, PDF or private files.
Emits only aggregate SAT/UNSAT/UNKNOWN totals (no source bytes or candidate).
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from k04_xoropp_sumstate_qfbv_synthetic import exact_two_output, synthetic_controls

ROOT = Path(__file__).resolve().parents[2]
SEALS = ROOT / "resources/evidence/maintenance/seal-receipts.jsonl"
ROUTE = ROOT / "resources/evidence/recovery-routing.json"
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"

SEAL_SHA = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"


def read_sources():
    seal_data = SEALS.read_bytes()
    spool_data = SPOOL.read_bytes()
    assert sha256(seal_data).hexdigest() == SEAL_SHA
    assert sha256(spool_data).hexdigest() == SPOOL_SHA
    route_data = ROUTE.read_bytes()
    assert sha256(route_data).hexdigest() == ROUTE_SHA
    mask = bytes.fromhex(json.loads(route_data)["K04"]["masked_component"])
    assert len(mask) == 16
    seals = [json.loads(line) for line in seal_data.splitlines()]
    selected = {}
    for rec in seals:
        if (rec.get("permit") != "PTW-417" or rec.get("state") != "CLOSED"
                or rec.get("fitment") != "AS_LEFT" or rec.get("signed") is not True):
            continue
        bay = rec["bay"]
        if bay not in selected or rec["revision"] > selected[bay]["revision"]:
            selected[bay] = rec
    assert set(selected) == set("ABCD")
    # The untouched attempt-1 REQUESTED is a hypothetical producer witness.
    # Deliberately withhold attempt-2 ACK2 and all acceptance fields.
    lines = [line.decode() for line in spool_data.splitlines()
             if b"JOB=PS-261003-0417" in line
             and b"ATTEMPT=1 " in line and b"STATE=REQUESTED" in line]
    assert len(lines) == 1
    payload = bytes.fromhex(lines[0].split("PAYLOAD=")[1].split()[0])
    assert len(payload) == 16
    return selected, payload, mask


def main():
    print("synthetic controls:", synthetic_controls(16, 20261127))
    selected, payload, mask = read_sources()
    counts = Counter()
    route_counts = Counter()
    for packet_endian in ("big", "little"):
        first = [int.from_bytes(payload[i:i+8], packet_endian) for i in (0, 8)]
        for reversed_halves in (False, True):
            outputs = first[::-1] if reversed_halves else first
            for bay in sorted(selected):
                raw = bytes.fromhex(selected[bay]["serial"][3:])
                assert len(raw) == 4
                for serial_endian in ("big", "little"):
                    anchor = int.from_bytes(raw, serial_endian)
                    for half in ("low", "high"):
                        status, _, _ = exact_two_output(
                            outputs[0], outputs[1],
                            known_sum_half=anchor, half=half, timeout_ms=3500)
                        counts[status] += 1
            # Different hypothesis: K04’s commissioning route-mask word is
            # an initial sum-state half, not a borrowed PTW seal state.
            for offset in (0, 4, 8, 12):
                word = mask[offset:offset+4]
                for word_endian in ("big", "little"):
                    anchor = int.from_bytes(word, word_endian)
                    for half in ("low", "high"):
                        status, _, _ = exact_two_output(
                            outputs[0], outputs[1],
                            known_sum_half=anchor, half=half, timeout_ms=3500)
                        route_counts[status] += 1
    assert sum(counts.values()) == 64
    assert sum(route_counts.values()) == 64
    # Aggregate only: no candidate/state/serial/commitment bytes.
    print("original source test:", json.dumps(
        {"ptw_configurations": 64, "ptw_dispositions": dict(counts),
         "route_mask_configurations": 64,
         "route_mask_dispositions": dict(route_counts),
         "selected_ack2_read": False, "commitment_checked": False,
         "source_join_authenticated": False}, sort_keys=True))


if __name__ == "__main__":
    main()
