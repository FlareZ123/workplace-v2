#!/usr/bin/env python3
"""Source-blind null benchmark for K01 A1-cell validity and K05 M10 convergence.

This reads source records only; it never reads acceptance.json or a K08 hash.
Run from the repository root:
    python agents/agent1/k08_workbook_coordinate_null_sft.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import struct
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

EXPECTED = {
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "recorder": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
    "mail03": "3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889",
    "mail06": "6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3",
}
TARGET_NIBBLES = (0xA, 0x0, 0xD, 0x4)  # row 10, column M=77
LOW_IF_EVEN_MASK = 0b1010  # low/high/low/high


def read_pinned(path: Path, name: str) -> bytes:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED[name], (name, path)
    return raw


def low_nibble(word: bytes) -> int:
    return sum((word[j] & 1) << j for j in range(4))


def load_actual(resources: Path):
    routing = json.loads(read_pinned(resources / "evidence/recovery-routing.json", "routing"))
    recorder = read_pinned(resources / "evidence/recorder/trip-recorder.raw", "recorder")
    mail03 = read_pinned(resources / "evidence/mail/03.eml", "mail03").decode("ascii")
    mail06 = read_pinned(resources / "evidence/mail/06.eml", "mail06").decode("ascii")

    groups = {}
    for text in (mail03, mail06):
        for group, value in re.findall(r"WN-14 / group ([A-D]) / ([0-9A-F]{8})", text):
            groups[group] = bytes.fromhex(value)
    k01 = b"".join(groups[g] for g in "ABCD")
    assert k01.hex().upper() == "049AAB2E1CDE7A82CD7C60234303C91A"

    route = routing["K05"]
    start = datetime.fromisoformat(route["start_utc"])
    end = datetime.fromisoformat(route["end_utc_exclusive"])
    magic, version, record_size, count = struct.unpack_from("<8sHHI", recorder, 0)
    assert (magic, version, record_size, count) == (b"TRP2DUMP", 2, 24, 88)
    by_latch = {i: [] for i in range(4)}
    for i in range(count):
        row = recorder[16 + i * record_size:16 + (i + 1) * record_size]
        if zlib.crc32(row[:20]) & 0xFFFFFFFF != struct.unpack_from("<I", row, 20)[0]:
            continue
        ts, node, event, latch, seq = struct.unpack_from("<IHBBI", row, 0)
        when = datetime.fromtimestamp(ts, timezone.utc)
        if (node == route["node"] and event == route["event"]
                and start <= when < end and latch in by_latch):
            by_latch[latch].append((seq, row[12:16]))

    expected = {
        0: [(200, bytes.fromhex("42BFD053")), (300, bytes.fromhex("FF8B7820"))],
        1: [(201, bytes.fromhex("8052760C")), (301, bytes.fromhex("0A56E858"))],
        2: [(202, bytes.fromhex("6FC2B743")), (302, bytes.fromhex("6DCDA00E"))],
        3: [(203, bytes.fromhex("BFB00270")), (303, bytes.fromhex("F01E4572"))],
    }
    assert {k: sorted(v) for k, v in by_latch.items()} == expected
    pairs = [[low_nibble(sorted(by_latch[l])[0][1]),
              low_nibble(sorted(by_latch[l])[1][1])] for l in range(4)]
    selected = [pairs[l][(LOW_IF_EVEN_MASK >> l) & 1] for l in range(4)]
    assert selected == list(TARGET_NIBBLES), (pairs, selected)
    outputs = {}
    for mask in range(16):
        output = tuple(pairs[l][(mask >> l) & 1] for l in range(4))
        outputs.setdefault(output, []).append(mask)
    assert len(outputs) == 8
    assert outputs[TARGET_NIBBLES] == [8, 10]
    return k01, pairs, outputs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resources", type=Path,
                    default=Path(__file__).resolve().parents[2] / "resources")
    ap.add_argument("--trials", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=20261121)
    args = ap.parse_args()

    k01, actual_pairs, actual_outputs = load_actual(args.resources)
    all_cells_valid = all(k01[i] != 0 and k01[i + 1] != 0 for i in range(0, 16, 2))

    # Under uniform random bytes, a row/column pair is valid iff both bytes
    # are nonzero. Byte-valued columns 1..255 are within BIFF8's 256 columns.
    p_k01 = (255 / 256) ** 16
    p_fixed = 1 / (16 ** 4)
    # For any of 16 masks to produce fixed M10, each latch's pair must
    # contain its target nibble at least once.
    p_any = (31 / 256) ** 4
    # Exactly two masks produce M10 iff one latch has both target nibbles
    # and the other three each have exactly one target nibble.
    p_two = 4 * (1 / 256) * (30 / 256) ** 3
    p_unique8 = 4 * (1 / 16) * (15 / 16) ** 3

    print("K01_HEX", k01.hex().upper())
    print("K01_ALL_EIGHT_A1_CELLS_VALID", int(all_cells_valid))
    print("K01_RANDOM_ALL_EIGHT_VALID_EXACT", f"{p_k01:.10f}")
    print("K05_ACTUAL_LATCH_NIBBLES", actual_pairs)
    print("K05_LOW_IF_EVEN_MASK", f"{LOW_IF_EVEN_MASK:04b}")
    print("K05_LOW_IF_EVEN_OUTPUT", actual_pairs[0][0], actual_pairs[1][1],
          actual_pairs[2][0], actual_pairs[3][1], "=> M10")
    print("K05_UNIQUE_OUTPUTS", len(actual_outputs))
    print("K05_M10_MASKS", actual_outputs[TARGET_NIBBLES])
    print("FIXED_MASK_M10_PROB_EXACT", f"{p_fixed:.10f}")
    print("ANY_OF_16_MASKS_M10_PROB_EXACT", f"{p_any:.10f}")
    print("M10_EXACTLY_TWO_MASKS_PROB_EXACT", f"{p_two:.10f}")
    print("EXACTLY_EIGHT_UNIQUE_OUTPUTS_PROB_EXACT", f"{p_unique8:.10f}")
    print("JOINT_K01_VALID_AND_FIXED_MASK_M10", f"{p_k01 * p_fixed:.12f}")
    print("JOINT_K01_VALID_AND_ANY_MASK_M10", f"{p_k01 * p_any:.12f}")

    rng = random.Random(args.seed)
    counts = {k: 0 for k in (
        "k01_all_valid", "fixed_mask_hit", "any_mask_hit",
        "exactly_two_masks_hit", "unique8", "joint_fixed", "joint_any"
    )}
    start = time.monotonic()
    for _ in range(args.trials):
        raw = [rng.getrandbits(8) for _ in range(16)]
        kvalid = all(raw[i] and raw[i + 1] for i in range(0, 16, 2))
        if kvalid:
            counts["k01_all_valid"] += 1

        pairs = [[rng.getrandbits(4), rng.getrandbits(4)] for _ in range(4)]
        fixed = [pairs[l][(LOW_IF_EVEN_MASK >> l) & 1] for l in range(4)]
        fixed_hit = tuple(fixed) == TARGET_NIBBLES
        any_hit = all(any(v == TARGET_NIBBLES[l] for v in pairs[l])
                      for l in range(4))
        hit_mask_count = 1
        for latch in range(4):
            hit_mask_count *= sum(v == TARGET_NIBBLES[latch] for v in pairs[latch])
        unique_count = 2 ** sum(pairs[l][0] != pairs[l][1] for l in range(4))

        if fixed_hit:
            counts["fixed_mask_hit"] += 1
        if any_hit:
            counts["any_mask_hit"] += 1
        if hit_mask_count == 2:
            counts["exactly_two_masks_hit"] += 1
        if unique_count == 8:
            counts["unique8"] += 1
        if kvalid and fixed_hit:
            counts["joint_fixed"] += 1
        if kvalid and any_hit:
            counts["joint_any"] += 1

    print("MONTE_CARLO_TRIALS", args.trials, "SEED", args.seed,
          "ELAPSED_SECONDS", round(time.monotonic() - start, 2))
    for key, value in counts.items():
        print("MC", key, value, f"{value / args.trials:.8f}")
    print("PASS source-blind coordinate null benchmark")


if __name__ == "__main__":
    main()
