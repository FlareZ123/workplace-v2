#!/usr/bin/env python3
"""Test whether later TRP2 node49 latch words or raw HST DIAG_WORDs
provide source-indexed later-stage carriers for the conditional p951 MT19937 model.

Run from repository root:
    python agents/agent6/k04_p951_later_carrier_sft.py

This does not assert that printer and recorder data share a generator; it tests
that specific cross-stream hypothesis against the frozen p951 symbolic basis.
"""
import datetime as dt
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent6"))

import k04_node50_15anchors_sft as node50
from k04_p951_symbolic_basis import MAG, ORIGIN, get, source, temper

EXT_LAST = 2500
MIN_FIXED_BITS = 8
K05_START = dt.datetime.fromisoformat("2026-10-03T21:14:00+00:00")
K05_END = dt.datetime.fromisoformat("2026-10-03T21:14:08+00:00")
K02_START = dt.datetime.fromisoformat("2026-10-03T21:13:40+00:00")
K02_END = dt.datetime.fromisoformat("2026-10-03T21:13:48+00:00")


def extend_states(states, last=EXT_LAST):
    for i in range(len(states), last - ORIGIN + 1):
        t = i - 624
        states.append([
            states[t + 397][j]
            ^ (states[t][31] if j == 30 else (states[t + 1][j + 1] if j < 30 else 0))
            ^ (states[t + 1][0] if (MAG >> j) & 1 else 0)
            for j in range(32)
        ])


def predict_stage(basis, states, stage):
    mask = value = 0
    for bit, equation in enumerate(temper(get(states, stage))):
        known = basis.predict(equation)
        if known is not None:
            mask |= 1 << bit
            value |= known << bit
    return mask, value


def selected_k05_words():
    raw = (ROOT / "resources/evidence/recorder/trip-recorder.raw").read_bytes()
    rows = {}
    for i in range(88):
        row = raw[16 + i * 24:16 + (i + 1) * 24]
        ts, node, event, latch, seq = struct.unpack_from("<IHBBI", row)
        control, aux, crc = struct.unpack_from("<III", row, 12)
        stamp = dt.datetime.fromtimestamp(ts, dt.timezone.utc)
        if node != 49 or event != 82 or not K05_START <= stamp < K05_END:
            continue
        if zlib.crc32(row[:20]) != crc:
            continue
        if latch not in rows or seq > rows[latch]["seq"]:
            rows[latch] = {"latch": latch, "seq": seq, "control": control, "aux": aux}
    assert set(rows) == {0, 1, 2, 3}
    return [rows[i] for i in range(4)]


def selected_k02_words():
    rows = {}
    path = ROOT / "resources/evidence/telemetry/freeze-export.jsonl"
    for line in path.read_text().splitlines():
        r = json.loads(line)
        if (r.get("tag"), r.get("field"), r.get("quality"), r.get("state")) != (
            "LT-204", "DIAG_WORD", "GOOD", "HOLD"
        ):
            continue
        stamp = dt.datetime.fromisoformat(r["ts"])
        if not K02_START <= stamp < K02_END or not 0 <= r["seq"] <= 7:
            continue
        if r["seq"] not in rows or r["revision"] > rows[r["seq"]]["revision"]:
            rows[r["seq"]] = r
    assert set(rows) == set(range(8))
    return [rows[i]["value"] for i in range(8)]


def main():
    basis, states = source(ROOT / "resources")
    assert basis.rank == 15365
    extend_states(states)

    # Existing node50 chronology model: reproduce its held-out controls and
    # metadata-only placement result before adding other source families.
    recorder = node50.recorder()
    pred_node50 = node50.predicted(basis, states)
    opts = {
        seq: node50.metadata(pred_node50, recorder, seq, stage)
        for seq, stage in node50.ANCHORS.items()
    }
    assert all(opts.values())
    joint_rank, target_residual = node50.joint_rank(
        basis, states, recorder, node50.EXPECTED, opts
    )
    assert (joint_rank, target_residual) == (15459, 128)

    metadata_only = {}
    for seq in range(72):
        candidates = []
        for stage in range(-950, -250):
            choices = node50.metadata(pred_node50, recorder, seq, stage)
            if choices:
                bits = max(choice[0] for choice in choices)
                if bits >= 20:
                    candidates.append((stage, bits))
        if candidates:
            metadata_only[seq] = candidates
    assert metadata_only == {9: [(-793, 22)], 44: [(-545, 22)]}

    k05 = selected_k05_words()
    k05_matches = {}
    for row in k05:
        hits = []
        for stage in range(951, EXT_LAST + 1):
            mask, value = predict_stage(basis, states, stage)
            fixed = mask.bit_count()
            if fixed >= MIN_FIXED_BITS and ((row["control"] ^ value) & mask) == 0:
                hits.append((stage, fixed))
        k05_matches[row["latch"]] = hits
    assert not any(k05_matches.values())

    k02 = selected_k02_words()
    k02_matches = {}
    for seq, word in enumerate(k02):
        hits = {"getrandbits16_high": [], "raw_u16_low": []}
        for stage in range(951, EXT_LAST + 1):
            mask, value = predict_stage(basis, states, stage)
            high_mask, high_value = (mask >> 16) & 0xFFFF, (value >> 16) & 0xFFFF
            low_mask, low_value = mask & 0xFFFF, value & 0xFFFF
            if high_mask.bit_count() >= MIN_FIXED_BITS and ((word ^ high_value) & high_mask) == 0:
                hits["getrandbits16_high"].append((stage, high_mask.bit_count()))
            if low_mask.bit_count() >= MIN_FIXED_BITS and ((word ^ low_value) & low_mask) == 0:
                hits["raw_u16_low"].append((stage, low_mask.bit_count()))
        k02_matches[seq] = hits

    print(json.dumps({
        "basis_rank": basis.rank,
        "node50_joint_rank": joint_rank,
        "target_stage_951_954_unknown_bits": target_residual,
        "node50_metadata_only_additional_stages": metadata_only,
        "selected_K05_node49_words": [
            {"latch": r["latch"], "seq": r["seq"], "control": f'{r["control"]:08X}'}
            for r in k05
        ],
        "K05_later_stage_matches_ge_8_bits": k05_matches,
        "selected_K02_DIAG_WORDs": k02,
        "K02_later_stage_matches_ge_8_bits": k02_matches,
        "interpretation": "No source-indexed later-stage carrier found; p951 model leaves K04's 128-bit target quotient free."
    }, sort_keys=True))


if __name__ == "__main__":
    main()
