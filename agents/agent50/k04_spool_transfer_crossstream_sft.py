#!/usr/bin/env python3
"""Source-pinned, read-only K04 spool/transfer cross-stream candidate test.

Only aggregate counts are printed. Candidate bytes, the K04 mask, component
hashes and acceptance digests are never emitted.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "spool": ROOT / "resources/evidence/print/spool-reconstruction.log",
    "transfer": ROOT / "resources/evidence/transfers/transfer-audit.jsonl",
    "routing": ROOT / "resources/evidence/recovery-routing.json",
    "acceptance": ROOT / "resources/acceptance.json",
}
EXPECTED = {
    "spool": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "transfer": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
ROW = re.compile(
    r"(?P<ts>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
    r"STATE=(?P<state>\S+) CLASS=(?P<class>\S+) "
    r"PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)"
)


def load_pinned():
    for name, path in FILES.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED[name]:
            raise SystemExit(f"source pin mismatch: {name}")

    packets = []
    for line in FILES["spool"].read_text(encoding="utf-8").splitlines():
        match = ROW.search(line)
        if match:
            row = match.groupdict()
            row["payload"] = bytes.fromhex(row["payload"])
            packets.append(row)
    if len(packets) != 133:
        raise SystemExit("unexpected printer packet count")

    transfer_rows = [
        json.loads(line)
        for line in FILES["transfer"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    groups = {}
    for row in transfer_rows:
        if row.get("kind") == "CHUNK":
            groups.setdefault((row["transfer"], row["attempt"]), []).append(row)
    chains = {}
    for key, group in groups.items():
        group = sorted(group, key=lambda x: x["seq"])
        if len(group) != 8 or [x["seq"] for x in group] != list(range(8)):
            raise SystemExit("unexpected transfer chain shape")
        chains[key] = b"".join(bytes.fromhex(x["checkpoint"]) for x in group)
    if len(chains) != 8:
        raise SystemExit("unexpected transfer chain count")

    routing = json.loads(FILES["routing"].read_text(encoding="utf-8"))
    acceptance = json.loads(FILES["acceptance"].read_text(encoding="utf-8"))
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"].lower()
    if len(mask) != 16:
        raise SystemExit("unexpected K04 mask length")
    return packets, chains, mask, target


def matches(coupon: bytes, mask: bytes, target: str) -> bool:
    if len(coupon) != 16:
        return False
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    return hashlib.sha256(component).hexdigest() == target


def algebraic_candidates(a: bytes, b: bytes):
    yield bytes(x ^ y for x, y in zip(a, b))
    yield bytes((x + y) & 0xFF for x, y in zip(a, b))
    yield bytes((x - y) & 0xFF for x, y in zip(a, b))
    yield bytes((y - x) & 0xFF for x, y in zip(a, b))
    for endian in ("big", "little"):
        aa = [int.from_bytes(a[i:i + 2], endian) for i in range(0, 16, 2)]
        bb = [int.from_bytes(b[i:i + 2], endian) for i in range(0, 16, 2)]
        for fn in (
            lambda x, y: (x + y) & 0xFFFF,
            lambda x, y: (x - y) & 0xFFFF,
            lambda x, y: (y - x) & 0xFFFF,
        ):
            yield b"".join(fn(x, y).to_bytes(2, endian) for x, y in zip(aa, bb))
        ai = int.from_bytes(a, endian)
        bi = int.from_bytes(b, endian)
        for value in (
            (ai + bi) % (1 << 128),
            (ai - bi) % (1 << 128),
            (bi - ai) % (1 << 128),
        ):
            yield value.to_bytes(16, endian)


def main():
    packets, chains, mask, target = load_pinned()
    selected = [
        row for row in packets
        if row["job"] == "PS-261003-0417"
        and row["attempt"] == "2"
        and row["state"] == "ACK"
        and row["class"] == "RECOVER"
        and row["dest"] == "bench"
    ]
    if len(selected) != 1:
        raise SystemExit("selected ESC-N record is not unique")
    selected_payload = selected[0]["payload"]
    selected_chain = chains[("AX-7782", 2)]

    # All retained packet/transfer-chain pairs; forward/reversed sequence,
    # native/per-checkpoint byte order, and 16 aligned arithmetic functions.
    pairwise_tests = 0
    original_hits = 0
    for packet in packets:
        for chain in chains.values():
            for reverse in (False, True):
                oriented = chain[::-1] if reverse else chain
                for swap in (False, True):
                    candidate_chain = (
                        b"".join(oriented[i:i + 2][::-1] for i in range(0, 16, 2))
                        if swap else oriented
                    )
                    for coupon in algebraic_candidates(packet["payload"], candidate_chain):
                        pairwise_tests += 1
                        original_hits += int(matches(coupon, mask, target))

    # One aligned 2-byte chunk per position, chosen from either source.
    pchunks = [selected_payload[i:i + 2] for i in range(0, 16, 2)]
    cchunks = [selected_chain[i:i + 2] for i in range(0, 16, 2)]
    chunk_tests = 0
    for selector in range(1 << 8):
        coupon = b"".join(
            cchunks[i] if (selector >> i) & 1 else pchunks[i]
            for i in range(8)
        )
        chunk_tests += 1
        original_hits += int(matches(coupon, mask, target))

    # One byte from each 2-byte pair of each source, interleaved P/C or C/P.
    byte_tests = 0
    for p_selector in range(1 << 8):
        pbytes = [bytes([pchunks[i][(p_selector >> i) & 1]]) for i in range(8)]
        for c_selector in range(1 << 8):
            cbytes = [bytes([cchunks[i][(c_selector >> i) & 1]]) for i in range(8)]
            for order in (0, 1):
                coupon = b"".join(
                    pbytes[i] + cbytes[i] if order == 0
                    else cbytes[i] + pbytes[i]
                    for i in range(8)
                )
                byte_tests += 1
                original_hits += int(matches(coupon, mask, target))

    # Synthetic end-to-end positive and negative controls for the exact reducer.
    planted_coupon = bytes(range(16))
    planted_mask = bytes((17 * i + 3) & 0xFF for i in range(16))
    planted_component = bytes(a ^ b for a, b in zip(planted_coupon, planted_mask))
    planted_target = hashlib.sha256(planted_component).hexdigest()
    positive = matches(planted_coupon, planted_mask, planted_target)
    negative = not matches(bytes(reversed(planted_coupon)), planted_mask, planted_target)
    if not (positive and negative):
        raise SystemExit("synthetic reducer control failed")

    print(json.dumps({
        "source_pins": "PASS",
        "printer_packets": len(packets),
        "transfer_chains": len(chains),
        "selected_pair": "PS-261003-0417/ACK2 + AX-7782/attempt2",
        "pairwise_algebraic_tests": pairwise_tests,
        "selected_chunk_selector_tests": chunk_tests,
        "selected_byte_interleave_tests": byte_tests,
        "total_complete_candidates": pairwise_tests + chunk_tests + byte_tests,
        "original_K04_commitment_matches": original_hits,
        "synthetic_positive_and_negative_controls": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
