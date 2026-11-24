#!/usr/bin/env python3
"""Bounded K04 screen: AX-7782 pre-retry checkpoint block as a four-fresh donor.

Read-only. Uses Agent10's frozen all42/four-fresh model and tests only the
source-ordered attempt-1 AX-7782 checkpoint block (no permutations).
Run from repository root:
  python agents/agent14/k04_ax7782_attempt1_fourfresh_donor_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent10"))

import k04_all42_wholewindow_sft as whole
import k04_all42_fourfresh_countermodel_sft as counter
import k04_fourfresh_future_source_donor_sft as donor

PINS = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "evidence/mail/13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def main() -> int:
    resources = ROOT / "resources"
    for relative, expected in PINS.items():
        actual = hashlib.sha256((resources / relative).read_bytes()).hexdigest()
        assert actual == expected, (relative, actual)

    transfer_rows = [
        json.loads(line)
        for line in (resources / "evidence/transfers/transfer-audit.jsonl").read_text().splitlines()
    ]
    attempt1 = [
        row for row in transfer_rows
        if row.get("kind") == "CHUNK"
        and row.get("transfer") == "AX-7782"
        and row.get("attempt") == 1
    ]
    attempt1.sort(key=lambda row: row["seq"])
    assert [row["seq"] for row in attempt1] == list(range(8))
    assert all(row["object"] == "IR-261003-H17" and row["bytes"] == 1048576 for row in attempt1)
    donor_block = b"".join(bytes.fromhex(row["checkpoint"]) for row in attempt1)
    assert len(donor_block) == 16

    mail13 = (resources / "evidence/mail/13.eml").read_text()
    assert "Each chunk was retried once" in mail13
    assert "second attempt has the checkpoint used in the committed chain" in mail13

    spool = (resources / "evidence/print/spool-reconstruction.log").read_text()
    pattern = re.compile(
        r"^(\\S+) JOB=(\\S+) ATTEMPT=(\\d+) STATE=(\\w+) "
        r"CLASS=(\\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\\w+)$",
        re.MULTILINE,
    )
    rows = list(pattern.finditer(spool))
    assert len(rows) == 133
    fields = [match.groups() for match in rows]
    assert fields[129][1:5] == ("PS-261003-0417", "2", "ACK", "RECOVER")

    # Keep the selected ACK2 packet withheld exactly as in the frozen model.
    native = [
        None if index == 129 else tuple(
            whole.untemper(
                int.from_bytes(bytes.fromhex(row[5])[4 * lane:4 * lane + 4], "little")
            )
            for lane in range(4)
        )
        for index, row in enumerate(fields)
    ]

    gaps = [
        later - earlier
        for earlier, later in zip(whole.ALT_STAGES, whole.ALT_STAGES[1:])
    ]
    for index, delta in counter.GAP_DELTAS.items():
        gaps[index] += delta
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[129] == 955

    symbols = whole.symbolic_words(0, max(max(stages) + 4, 1863 + 4))
    basis = whole.build_basis(native, tuple(stages), symbols, 0)
    assert len(basis) == 15434

    target_forms = [
        symbols[stages[129] + lane][bit]
        for lane in range(4)
        for bit in range(32)
    ]
    donor_maps = {
        start: donor.donor_mapping(start, basis, symbols, target_forms)
        for start in (1409, 1863)
    }

    routing = json.loads((resources / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((resources / "acceptance.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()

    components = []
    hits = []
    for start, mapping in donor_maps.items():
        for endian in ("big", "little"):
            for already_native in (True, False):
                donor_bits = donor.donor_bits_from_block(
                    donor_block, tuple(range(4)), endian, already_native
                )
                target_bits = donor.map_native(donor_bits, mapping)
                coupon = donor.coupon_from_native_bits(target_bits)
                component = bytes(a ^ b for a, b in zip(coupon, mask))
                components.append(component)
                if hashlib.sha256(component).hexdigest() == target:
                    hits.append({
                        "donor_start": start,
                        "word_endian": endian,
                        "already_native": already_native,
                    })

    assert len(components) == 8
    assert len(set(components)) == 8
    print(json.dumps({
        "hypothesis": "AX-7782 attempt-1 checkpoints are a future four-word donor for the printer MT model",
        "source_order": "transfer AX-7782, attempt 1, seq 0..7; pair adjacent 16-bit checkpoints into four 32-bit words",
        "attempt1_is_committed_K07_input": False,
        "printer_target_stage": stages[129],
        "hypothetical_donor_starts": sorted(donor_maps),
        "presentations_checked": len(components),
        "distinct_components": len(set(components)),
        "K04_commitment_hits": len(hits),
        "matching_presentations": hits,
        "synthetic_control": "inherited four-fresh algebraic control; not evidence of a historical shared generator",
        "source_files_unchanged": True,
        "candidate_bytes_emitted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
