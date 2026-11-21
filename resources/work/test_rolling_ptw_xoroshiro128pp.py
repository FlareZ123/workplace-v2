#!/usr/bin/env python3
"""Bounded target-blind test: rolling PTW bay state -> xoroshiro128++ packet."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

MASK64 = (1 << 64) - 1
BAY_ORDERS = (("A", "B", "C", "D"), ("B", "D", "A", "C"))


def rotl64(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK64


def packet_from_state(state: tuple[int, int], output_view: int) -> bytes:
    s0, s1 = state
    outputs = []
    for _ in range(2):
        out = (rotl64((s0 + s1) & MASK64, 17) + s0) & MASK64
        s1 ^= s0
        s0 = (rotl64(s0, 49) ^ s1 ^ ((s1 << 21) & MASK64)) & MASK64
        s1 = rotl64(s1, 28)
        outputs.append(out)
    endian = "little" if output_view & 1 else "big"
    if output_view & 2:
        outputs.reverse()
    return b"".join(word.to_bytes(8, endian) for word in outputs)


def load_receipts(path: Path) -> dict[int, tuple[str, bytes]]:
    by_permit: dict[int, list[dict]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        m = re.fullmatch(r"PTW-(\d+)", row.get("permit", ""))
        if not m:
            continue
        if row.get("state") == "CLOSED" and row.get("fitment") == "AS_LEFT" and row.get("signed") is True:
            by_permit[int(m.group(1))].append(row)
    selected = {}
    for n in range(390, 417):
        candidates = by_permit.get(n, [])
        if len(candidates) != 1:
            raise ValueError(f"PTW-{n}: expected one signed CLOSED/AS_LEFT row, got {len(candidates)}")
        row = candidates[0]
        raw = bytes.fromhex(row["serial"].split("-", 1)[1])
        if len(raw) != 4:
            raise ValueError(f"PTW-{n}: expected four-byte serial")
        selected[n] = (row["bay"], raw)
    return selected


def load_packets(path: Path) -> dict[int, bytes]:
    by_job: dict[int, list[bytes]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        fields = dict(re.findall(r"([A-Z_]+)=([^\s]+)", line))
        if fields.get("STATE") != "ACK":
            continue
        m = re.fullmatch(r"PS-261003-(\d{4})", fields.get("JOB", ""))
        if not m:
            continue
        n = int(m.group(1))
        if 390 <= n <= 416:
            payload = bytes.fromhex(fields["PAYLOAD"])
            if len(payload) != 16:
                raise ValueError(f"PS-{n}: expected 16-byte ACK payload")
            by_job[n].append(payload)
    packets = {}
    for n in range(395, 417):
        candidates = by_job.get(n, [])
        if len(candidates) != 1:
            raise ValueError(f"PS-{n}: expected one ACK packet, got {len(candidates)}")
        packets[n] = candidates[0]
    return packets


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--evidence", type=Path, default=None,
                    help="optional direct path to the evidence directory")
    args = ap.parse_args()
    if args.evidence is not None:
        evidence = args.evidence
    else:
        root = args.root if args.root is not None else Path(__file__).resolve().parents[2]
        evidence = root / "resources" / "evidence"

    receipts = load_receipts(evidence / "maintenance" / "seal-receipts.jsonl")
    packets = load_packets(evidence / "print" / "spool-reconstruction.log")

    rolling: dict[str, bytes] = {}
    states: dict[int, dict[str, bytes]] = {}
    for n in range(390, 417):
        bay, serial = receipts[n]
        rolling[bay] = serial
        if len(rolling) == 4 and n in packets:
            states[n] = dict(rolling)
    if set(states) != set(range(395, 417)):
        raise ValueError(f"expected complete rolling states 0395..0416; got {sorted(states)}")

    rows = [(n, states[n], packets[n]) for n in range(395, 417)]
    results = []
    for bay_order in BAY_ORDERS:
        for serial_endian in ("big", "little"):
            for state_endian in ("big", "little"):
                for swap_state_words in (False, True):
                    for output_view in range(4):
                        matches = 0
                        for _, state_by_bay, observed in rows:
                            state_bytes = b"".join(
                                state_by_bay[bay] if serial_endian == "big" else state_by_bay[bay][::-1]
                                for bay in bay_order
                            )
                            words = [
                                int.from_bytes(state_bytes[:8], state_endian),
                                int.from_bytes(state_bytes[8:], state_endian),
                            ]
                            if swap_state_words:
                                words.reverse()
                            if packet_from_state(tuple(words), output_view) == observed:
                                matches += 1
                        results.append({
                            "bay_order": "".join(bay_order),
                            "serial_word_endian": serial_endian,
                            "state_word_endian": state_endian,
                            "swap_64bit_state_words": swap_state_words,
                            "output_view": output_view,
                            "exact_packet_matches_of_22": matches,
                        })

    print(json.dumps({
        "experiment": "rolling-PTW-state-as-xoroshiro128pp-state",
        "target_blind": True,
        "training_pairs": [f"{n:04d}" for n, _, _ in rows],
        "pair_count": len(rows),
        "state_configurations": 16,
        "output_serializers_per_state": 4,
        "total_configurations": len(results),
        "best_exact_packet_matches_of_22": max(x["exact_packet_matches_of_22"] for x in results),
        "configurations": results,
        "limitations": [
            "PTW/PS same-suffix join is not source-authenticated",
            "no warm-up offsets tested",
            "no alternative PRNGs tested",
            "no target PS-0417 data used",
        ],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
