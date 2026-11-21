#!/usr/bin/env python3
"""Bounded K04 test: PTW-417 signed serial quartet as xoroshiro128++ state.

The only source-selected serial order is MAIL-04's B,D,A,C witness walk.
This tests a raw 128-bit seed/state relation to the selected PS-0417 ACK2
payload; it does not assert that the shared numeric suffix proves a common
printer/maintenance issuer. No candidate or verifier file is modified.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

MASK64 = (1 << 64) - 1
BAY_ORDER = ("B", "D", "A", "C")


def rotl64(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK64


def xoroshiro128pp(state: tuple[int, int]) -> tuple[int, int]:
    """Return the first two xoroshiro128++ 1.0 64-bit outputs."""
    s0, s1 = state
    out = []
    for _ in range(2):
        out.append((rotl64((s0 + s1) & MASK64, 17) + s0) & MASK64)
        s1 ^= s0
        s0 = (rotl64(s0, 49) ^ s1 ^ ((s1 << 21) & MASK64)) & MASK64
        s1 = rotl64(s1, 28)
    return out[0], out[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    evidence = root / "resources" / "evidence"
    acceptance = root / "resources" / "acceptance.json"
    receipts_path = evidence / "maintenance" / "seal-receipts.jsonl"
    spool_path = evidence / "print" / "spool-reconstruction.log"
    route_path = evidence / "recovery-routing.json"

    receipts = [
        json.loads(line)
        for line in receipts_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    latest: dict[str, dict] = {}
    for row in receipts:
        if (
            row.get("permit") != "PTW-417"
            or row.get("state") != "CLOSED"
            or row.get("fitment") != "AS_LEFT"
            or row.get("signed") is not True
            or row.get("bay") not in {"A", "B", "C", "D"}
        ):
            continue
        bay = row["bay"]
        if bay not in latest or row["revision"] > latest[bay]["revision"]:
            latest[bay] = row
    if set(latest) != {"A", "B", "C", "D"}:
        raise ValueError(f"expected one latest signed CLOSED/AS_LEFT row per bay: {sorted(latest)}")

    serials = []
    for bay in BAY_ORDER:
        suffix = latest[bay]["serial"].split("-", 1)[1]
        raw = bytes.fromhex(suffix)
        if len(raw) != 4:
            raise ValueError(f"PTW-417 {bay}: expected four-byte serial, got {len(raw)}")
        serials.append(raw)
    source_block = b"".join(serials)

    # The route says last ACK for this exact job; later REQUESTED attempt 3 is
    # not an ACK. Keep this selection explicit rather than taking the last row.
    ack_rows = []
    for line in spool_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        timestamp_text, rest = line.split(" ", 1)
        fields = dict(
            token.split("=", 1)
            for token in rest.split()
            if "=" in token
        )
        if fields.get("JOB") != "PS-261003-0417" or fields.get("STATE") != "ACK":
            continue
        ack_rows.append((datetime.fromisoformat(timestamp_text.replace("Z", "+00:00")), fields))
    if not ack_rows:
        raise ValueError("no ACK rows for PS-261003-0417")
    selected_time, selected = max(ack_rows, key=lambda item: item[0])
    if (selected.get("ATTEMPT"), selected.get("CLASS"), selected.get("DEST")) != ("2", "RECOVER", "bench"):
        raise ValueError(f"unexpected last ACK selection: {selected}")
    observed_payload = bytes.fromhex(selected["PAYLOAD"])
    if len(observed_payload) != 16:
        raise ValueError("selected PS-0417 payload is not 16 bytes")

    route = json.loads(route_path.read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    if len(mask) != 16:
        raise ValueError("K04 mask is not 16 bytes")
    target = json.loads(acceptance.read_text(encoding="utf-8"))["slot_sha256"]["K04"]

    rows = []
    for serial_endian in ("as_recorded", "reversed_per_serial"):
        block = (
            source_block
            if serial_endian == "as_recorded"
            else b"".join(serial[::-1] for serial in serials)
        )
        for swap_state_halves in (False, True):
            state_block = block if not swap_state_halves else block[8:] + block[:8]
            for state_word_endian in ("big", "little"):
                state = (
                    int.from_bytes(state_block[:8], state_word_endian),
                    int.from_bytes(state_block[8:], state_word_endian),
                )
                outputs = xoroshiro128pp(state)
                for output_endian in ("big", "little"):
                    for swap_outputs in (False, True):
                        ordered = outputs if not swap_outputs else outputs[::-1]
                        candidate = b"".join(
                            word.to_bytes(8, output_endian) for word in ordered
                        )
                        masked = bytes(a ^ b for a, b in zip(candidate, mask))
                        rows.append({
                            "serial_endian": serial_endian,
                            "swap_state_halves": swap_state_halves,
                            "state_word_endian": state_word_endian,
                            "output_endian": output_endian,
                            "swap_outputs": swap_outputs,
                            "candidate_hex": candidate.hex().upper(),
                            "equals_selected_ack_payload": candidate == observed_payload,
                            "direct_commitment_hit": sha256(candidate) == target,
                            "masked_commitment_hit": sha256(masked) == target,
                        })

    # A small deterministic self-check protects the output serializer.
    synthetic = xoroshiro128pp((0x0123456789ABCDEF, 0xFEDCBA9876543210))
    assert len(synthetic) == 2 and all(0 <= word <= MASK64 for word in synthetic)

    result = {
        "experiment": "PTW-417 raw signed serial quartet -> xoroshiro128++ state -> PS-0417 K04",
        "source_order": "".join(BAY_ORDER),
        "selected_serials": {bay: latest[bay]["serial"] for bay in BAY_ORDER},
        "selected_serial_block": source_block.hex().upper(),
        "selected_ps0417_ack": {
            "timestamp": selected_time.isoformat(),
            "attempt": selected["ATTEMPT"],
            "class": selected["CLASS"],
            "destination": selected["DEST"],
            "payload": observed_payload.hex().upper(),
        },
        "k04_mask": mask.hex().upper(),
        "k04_commitment": target,
        "configurations": len(rows),
        "exact_ack_payload_matches": sum(row["equals_selected_ack_payload"] for row in rows),
        "direct_commitment_hits": sum(row["direct_commitment_hit"] for row in rows),
        "masked_commitment_hits": sum(row["masked_commitment_hit"] for row in rows),
        "source_sha256": {
            "seal_receipts": sha256(receipts_path.read_bytes()),
            "spool_reconstruction": sha256(spool_path.read_bytes()),
            "recovery_routing": sha256(route_path.read_bytes()),
            "acceptance": sha256(acceptance.read_bytes()),
        },
        "configurations_detail": rows,
        "limitations": [
            "The PTW-417 / PS-0417 shared suffix is a candidate join, not proof of a common issuer or PRNG seed.",
            "Only the source-selected B,D,A,C quartet and the first two xoroshiro128++ outputs are tested.",
            "No warm-up offsets or alternative PRNG families are tested.",
            "A match to the copied ACK payload would not independently authenticate physical media.",
        ],
    }
    assert result["configurations"] == 32
    assert result["exact_ack_payload_matches"] == 0
    assert result["direct_commitment_hits"] == 0
    assert result["masked_commitment_hits"] == 0
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
