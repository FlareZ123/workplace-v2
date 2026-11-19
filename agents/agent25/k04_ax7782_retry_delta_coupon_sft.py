#!/usr/bin/env python3
"""One finite AX-7782 retry-delta candidate for the K04 coupon.

Run from the workplace-v2 repository root:
    python agents/agent25/k04_ax7782_retry_delta_coupon_sft.py

The candidate is the bytewise XOR of attempt 1 and attempt 2 for each of
AX-7782's eight chunks, concatenated in seq 0..7 order. It is a hypothesis,
not an authenticated K04 source rule. The selected K07 chain is used as a
positive control for transfer selection and serialization.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
TRANSFER = ROOT / "evidence" / "transfers" / "transfer-audit.jsonl"
QUEUE = ROOT / "evidence" / "transfers" / "queue-note.txt"
ROUTING = ROOT / "evidence" / "recovery-routing.json"
ACCEPTANCE = ROOT / "acceptance.json"

EXPECTED_SHA256 = {
    "transfer": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "queue": "2040af92096bd270352a7c5e4a587ae3a0a26485c2c2a10240ce8504465c788f",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
EXPECTED_DELTA = "EB6383274A74B987AF6089CC0EB242A0"
EXPECTED_COMPONENT = "6E354BEC2B341E7E0A72B30B59A9ACBC"
EXPECTED_K04_COMMIT = (
    "006f8bd6a6e8ccad3920baa9a9c7cfef04a4ab03c6b3c4f47c6ff2d9d7470b79"
)
EXPECTED_K07_COMMIT = (
    "b8884f0ba97f1e3432ddc0e7f14f7ac516ff24430e7c42321af16aad59302680"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    transfer_raw = TRANSFER.read_bytes()
    queue_raw = QUEUE.read_bytes()
    routing_raw = ROUTING.read_bytes()
    acceptance_raw = ACCEPTANCE.read_bytes()

    assert sha256(transfer_raw) == EXPECTED_SHA256["transfer"]
    assert sha256(queue_raw) == EXPECTED_SHA256["queue"]
    assert sha256(routing_raw) == EXPECTED_SHA256["routing"]
    assert sha256(acceptance_raw) == EXPECTED_SHA256["acceptance"]

    rows = [json.loads(line) for line in transfer_raw.splitlines()]
    routing = json.loads(routing_raw)
    acceptance = json.loads(acceptance_raw)

    commits = [
        row for row in rows
        if row.get("kind") == "COMMIT"
        and row.get("transfer") == "AX-7782"
        and row.get("dry_run") is False
        and row.get("chunks") == 8
        and row.get("object") == "IR-261003-H17"
    ]
    assert len(commits) == 1

    by_seq: dict[int, dict[int, bytes]] = {}
    for row in rows:
        if row.get("kind") != "CHUNK" or row.get("transfer") != "AX-7782":
            continue
        by_seq.setdefault(row["seq"], {})[row["attempt"]] = bytes.fromhex(
            row["checkpoint"]
        )
    assert sorted(by_seq) == list(range(8))
    assert all(sorted(attempts) == [1, 2] for attempts in by_seq.values())
    assert all(len(value) == 2 for attempts in by_seq.values()
               for value in attempts.values())

    # Freeze the one retry-delta operation: attempt1 XOR attempt2 per seq.
    deltas = [
        bytes(a ^ b for a, b in zip(by_seq[seq][1], by_seq[seq][2]))
        for seq in range(8)
    ]
    coupon_candidate = b"".join(deltas)
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    assert len(coupon_candidate) == len(mask) == 16
    component_candidate = bytes(
        left ^ right for left, right in zip(coupon_candidate, mask)
    )
    k04_commit = sha256(component_candidate)
    expected_k04 = acceptance["slot_sha256"]["K04"]

    # Positive control: the same transfer's greatest-attempt checkpoint chain
    # must reproduce the accepted K07 commitment exactly.
    selected_k07_input = b"".join(by_seq[seq][2] for seq in range(8))
    k07_component = hashlib.sha256(selected_k07_input).digest()[:16]
    k07_commit = sha256(k07_component)
    expected_k07 = acceptance["slot_sha256"]["K07"]
    assert k07_commit == expected_k07 == EXPECTED_K07_COMMIT

    assert coupon_candidate.hex().upper() == EXPECTED_DELTA
    assert component_candidate.hex().upper() == EXPECTED_COMPONENT
    assert k04_commit == EXPECTED_K04_COMMIT
    assert k04_commit != expected_k04

    print("TRANSFER=AX-7782; COMMIT dry_run=false; chunks=8")
    for seq in range(8):
        print(
            f"SEQ{seq}: A1={by_seq[seq][1].hex().upper()} "
            f"A2={by_seq[seq][2].hex().upper()} "
            f"DELTA={deltas[seq].hex().upper()}"
        )
    print("COUPON_CANDIDATE=" + coupon_candidate.hex().upper())
    print("K04_MASK=" + mask.hex().upper())
    print("K04_COMPONENT_CANDIDATE=" + component_candidate.hex().upper())
    print("K04_CANDIDATE_SHA256=" + k04_commit)
    print("K04_EXPECTED_SHA256=" + expected_k04)
    print("K04_MATCH=NO")
    print("K07_SELECTED_INPUT=" + selected_k07_input.hex().upper())
    print("K07_COMPONENT=" + k07_component.hex().upper())
    print("K07_COMMIT=" + k07_commit)
    print("K07_POSITIVE_CONTROL=PASS")
    print("PASS: one source-pinned retry-delta candidate rejected")


if __name__ == "__main__":
    main()
