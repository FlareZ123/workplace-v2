#!/usr/bin/env python3
"""Bounded SFC32/JSF32 state test for the TRP2/PS0300-0303 suffix join.

Run from the repository root:
    python agents/agent18/k05_sfc32_jsf32_suffix_sft.py

Tests only direct four-word-state interpretations; no arbitrary seed or skip
search is performed.
"""
from __future__ import annotations
import hashlib, json, re, struct, zlib
from datetime import datetime, timezone
from pathlib import Path

MASK = 0xFFFFFFFF
TRP2_SHA256 = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def source_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    if (root / "resources" / "evidence").is_dir():
        return root
    if (root / "evidence").is_dir():
        return root
    raise FileNotFoundError("resources/evidence not found")


def rotl32(x: int, n: int) -> int:
    x &= MASK
    return ((x << n) | (x >> (32 - n))) & MASK


def sfc32_step(state: list[int]) -> tuple[list[int], int]:
    a, b, c, d = state
    out = (a + b + d) & MASK
    d = (d + 1) & MASK
    a = (b ^ (b >> 9)) & MASK
    b = (c + (c << 3)) & MASK
    c = (rotl32(c, 21) + out) & MASK
    return [a, b, c, d], out


def jsf32_step(state: list[int]) -> tuple[list[int], int]:
    a, b, c, d = state
    t = (a - rotl32(b, 27)) & MASK
    a = (b ^ rotl32(c, 17)) & MASK
    b = (c + d) & MASK
    c = (d + t) & MASK
    d = (a + t) & MASK
    return [a, b, c, d], d


def generate(step, state: list[int], count: int) -> list[int]:
    state = list(state)
    output = []
    for _ in range(count):
        state, value = step(state)
        output.append(value & MASK)
    return output


def advance_state(step, state: list[int]) -> list[int]:
    return step(list(state))[0]


def words(payload: bytes, endian: str, reverse: bool = False) -> list[int]:
    result = [int.from_bytes(payload[i:i + 4], endian) for i in range(0, len(payload), 4)]
    return result[::-1] if reverse else result


def load_k05(evidence: Path) -> list[dict]:
    raw = (evidence / "recorder" / "trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRP2_SHA256
    magic, version, record_size, count = struct.unpack_from("<8sHHI", raw)
    assert (magic, version, record_size, count) == (b"TRP2DUMP", 2, 24, 88)
    start = int(datetime(2026, 10, 3, 21, 14, 0, tzinfo=timezone.utc).timestamp())
    selected = {}
    for i in range(count):
        rec = raw[16 + i * 24:16 + (i + 1) * 24]
        if zlib.crc32(rec[:20]) != struct.unpack_from("<I", rec, 20)[0]:
            continue
        ts, node, event, latch, seq, control, aux, crc = struct.unpack("<IHBBI4sII", rec)
        if node == 49 and event == 82 and start <= ts < start + 8 and latch in range(4):
            if latch not in selected or seq > selected[latch]["seq"]:
                selected[latch] = {"ts": ts, "latch": latch, "seq": seq, "control": control, "aux": aux}
    assert set(selected) == {0, 1, 2, 3}
    return [selected[i] for i in range(4)]


def load_spool(evidence: Path) -> dict[int, dict]:
    raw = (evidence / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    result = {}
    pattern = re.compile(r"^(\S+)\s+JOB=PS-261003-(\d{4}).*?PAYLOAD=([0-9A-F]{32})")
    for line in raw.decode("utf-8").splitlines():
        match = pattern.search(line)
        if match:
            stamp, suffix, payload = match.groups()
            suffix = int(suffix)
            if suffix in range(300, 304):
                result[suffix] = {"timestamp": stamp, "payload": bytes.fromhex(payload)}
    assert set(result) == {300, 301, 302, 303}
    assert all(len(row["payload"]) == 16 for row in result.values())
    return result


def main() -> None:
    root = source_root()
    evidence = root / "resources" / "evidence"
    if not evidence.is_dir():
        evidence = root / "evidence"
    records = load_k05(evidence)
    jobs = load_spool(evidence)
    controls = b"".join(row["control"] for row in records)
    assert [row["seq"] for row in records] == [300, 301, 302, 303]
    assert [row["latch"] for row in records] == [0, 1, 2, 3]
    assert len({row["ts"] for row in records}) == 1
    assert len({row["aux"] for row in records}) == 1 and records[0]["aux"] == 4318

    # Published reference-vector controls for the two implementations.
    sfc_vector = generate(sfc32_step, [1, 2, 3, 4], 5)
    assert sfc_vector == [0x00000007, 0x00000022, 0x03600060, 0x0B421D78, 0xCC849C75]
    jsf_seed = [0xF1EA5EED, 0, 0, 0]
    for _ in range(20):
        jsf_seed = advance_state(jsf32_step, jsf_seed)
    jsf_vector = generate(jsf32_step, jsf_seed, 10)
    assert jsf_vector == [0x1A9B6C07, 0x9A550895, 0xF12BE876, 0x0902BA19, 0x20F1A244,
                          0x832BC5D2, 0x0BFDB9A1, 0x7384175A, 0x96A0F7E5, 0x470AD8F6]

    algorithms = {"SFC32": sfc32_step, "JSF32": jsf32_step}
    target_words = {
        endian: [word for job in range(300, 304) for word in words(jobs[job]["payload"], endian)]
        for endian in ("big", "little")
    }
    control_words = {endian: words(controls, endian) for endian in ("big", "little")}

    direct_scores = []
    for name, step in algorithms.items():
        for input_endian in ("big", "little"):
            for input_reverse in (False, True):
                state = words(controls, input_endian, input_reverse)
                generated = generate(step, state, 16)
                for output_endian, expected in target_words.items():
                    for output_reverse in (False, True):
                        candidate = generated[::-1] if output_reverse else generated
                        direct_scores.append((sum(a != b for a, b in zip(candidate, expected)), name,
                                              input_endian, input_reverse, output_endian, output_reverse))

    reverse_scores = []
    for name, step in algorithms.items():
        for input_endian in ("big", "little"):
            for input_reverse in (False, True):
                state = words(jobs[300]["payload"], input_endian, input_reverse)
                generated = generate(step, state, 4)
                for output_endian, expected in control_words.items():
                    for output_reverse in (False, True):
                        candidate = generated[::-1] if output_reverse else generated
                        reverse_scores.append((sum(a != b for a, b in zip(candidate, expected)), name,
                                               input_endian, input_reverse, output_endian, output_reverse))

    pairwise_scores = []
    for name, step in algorithms.items():
        for input_endian in ("big", "little"):
            for input_reverse in (False, True):
                for output_endian in ("big", "little"):
                    mismatches = 0
                    for latch, job in enumerate(range(300, 304)):
                        state = words(jobs[job]["payload"], input_endian, input_reverse)
                        generated = generate(step, state, 1)[0]
                        expected = int.from_bytes(records[latch]["control"], output_endian)
                        mismatches += generated != expected
                    pairwise_scores.append((mismatches, name, input_endian, input_reverse, output_endian))

    direct_min = min(row[0] for row in direct_scores)
    reverse_min = min(row[0] for row in reverse_scores)
    pairwise_min = min(row[0] for row in pairwise_scores)
    assert direct_min == 16 and reverse_min == 4 and pairwise_min == 4
    assert not any(row[0] == 0 for row in direct_scores + reverse_scores + pairwise_scores)

    print(json.dumps({
        "selected_k05": [{"seq": r["seq"], "latch": r["latch"], "control": r["control"].hex().upper(),
                          "aux": r["aux"], "timestamp_utc": datetime.fromtimestamp(r["ts"], timezone.utc).isoformat()}
                         for r in records],
        "spool_jobs": [{"job": j, "timestamp_utc": jobs[j]["timestamp"],
                        "payload": jobs[j]["payload"].hex().upper()} for j in range(300, 304)],
        "positive_controls": {"SFC32_state_1_2_3_4": [f"{x:08X}" for x in sfc_vector],
                              "JSF32_seed_0_after_20_warmups": [f"{x:08X}" for x in jsf_vector]},
        "direct_K05_state_to_4_spool_jobs": {"interpretations": len(direct_scores), "minimum_word_mismatches": direct_min},
        "PS0300_state_to_K05_control_block": {"interpretations": len(reverse_scores), "minimum_word_mismatches": reverse_min},
        "per_job_payload_state_to_corresponding_control": {"interpretations": len(pairwise_scores), "minimum_pair_mismatches": pairwise_min},
        "exact_hits": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
