#!/usr/bin/env python3
"""Reproduce the bounded N14 cross-slot selector/source-gate review.

Target-blind: reads candidate values and routing constants, not acceptance
commitments. It does not inspect or decode image content.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def selector(raw: bytes) -> tuple[str, int]:
    if len(raw) != 16:
        raise ValueError(f"expected 16 bytes, got {len(raw)}")
    packed = bytearray(2)
    for i, byte in enumerate(raw):
        packed[i // 8] |= (byte & 1) << (i % 8)
    packed_hex = bytes(packed).hex().upper()
    value = sum((ord(char) & 1) << i for i, char in enumerate(packed_hex))
    return packed_hex, value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=Path("resources/evidence"))
    parser.add_argument("--candidate", type=Path, default=Path("candidate.json"))
    args = parser.parse_args()

    evidence = args.evidence_dir
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    routing = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))

    inputs: list[tuple[str, bytes]] = []
    for slot in ("K01", "K02", "K03", "K05", "K06", "K07"):
        value = candidate.get(slot)
        if value is not None:
            inputs.append((slot, bytes.fromhex(value)))
    inputs.extend([
        ("K04 mask", bytes.fromhex(routing["K04"]["masked_component"])),
        ("K08 nonce", bytes.fromhex(routing["K08"]["desk_nonce"])),
    ])

    print("slot inputs (packed byte-LSB hex -> selector):")
    selectors: dict[int, list[str]] = {}
    for label, raw in inputs:
        packed, value = selector(raw)
        print(f"  {label:9s} {packed} -> {value:2d}")
        selectors.setdefault(value, []).append(label)

    print("\nselector multiplicity:")
    for value, labels in sorted(selectors.items()):
        print(f"  N{value:02d}: {len(labels)}/8 {', '.join(labels)}")

    spool = (evidence / "print" / "spool-reconstruction.log").read_text(encoding="utf-8")
    rows: list[tuple[str, bytes]] = []
    pattern = re.compile(
        r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) "
        r"PAYLOAD=([0-9A-Fa-f]{32})"
    )
    wanted = {"PS-261003-0417", "PS-261003-0448", "PS-261003-0420"}
    for line in spool.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        job, attempt, state, job_class, payload = match.groups()
        if job in wanted:
            rows.append((f"{job} a{attempt} {state} {job_class}", bytes.fromhex(payload)))

    print("\nmatched printer controls (same selector, no image assumption):")
    selected_ack2: bytes | None = None
    for label, raw in rows:
        packed, value = selector(raw)
        print(f"  {label:42s} {packed} -> {value:2d}")
        if label == "PS-261003-0417 a2 ACK RECOVER":
            selected_ack2 = raw

    if selected_ack2 is None:
        raise SystemExit("selected PS-0417 ATTEMPT=2 ACK not found")
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    candidate_coupon = bytes(a ^ b for a, b in zip(selected_ack2, mask))
    packed, value = selector(candidate_coupon)
    print(f"  {'PS-0417 ACK2 xor K04 mask':42s} {packed} -> {value:2d}")

    n14_labels = selectors.get(14, [])
    print("\nN14 slot-input count:", len(n14_labels), "/", len(inputs))
    print("N14 inputs:", ", ".join(n14_labels))
    print("No HMAC/slot commitment is read or tested by this script.")


if __name__ == "__main__":
    main()
