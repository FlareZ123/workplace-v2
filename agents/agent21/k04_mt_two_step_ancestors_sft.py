#!/usr/bin/env python3
"""K04: bound one- and two-step native MT ancestors of the selected packet.

Single-file source-pinned read-only SFT; selected ACK2 copied PAYLOAD excluded.
Usage: python agents/agent21/k04_mt_two_step_ancestors_sft.py [resources-or-zip]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MAG = 0x9908B0DF
U32 = (1 << 32) - 1


def untemper(value: int) -> int:
    for shift, left, mask in ((18, False, U32), (15, True, 0xEFC60000),
                              (7, True, 0x9D2C5680), (11, False, U32)):
        old = value
        for _ in range(6):
            value = (old ^ (((value << shift) & mask) if left else (value >> shift))) & U32
    return value


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & U32


def twist(a: int, b: int) -> int:
    joined = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (joined >> 1) ^ (MAG if joined & 1 else 0)


def read_spool(path: Path) -> bytes:
    if path.is_file() and path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            return archive.read("evidence/print/spool-reconstruction.log")
    return (path / "evidence/print/spool-reconstruction.log").read_bytes()


def build_witnesses(native: list[tuple[int, ...] | None]):
    back: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for row, packet in enumerate(native):
        if packet is not None:
            for lane, word in enumerate(packet):
                back[word].append((row, lane))
    relations = []
    full = partial = 0
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r + 1, len(native)):
            if native[k] is None:
                continue
            for lane, word in enumerate(native[k]):
                for p in (1, 2, 3):
                    for later, q in back.get(word ^ twist(packet[p - 1], packet[p]), ()):
                        if later > k:
                            full += 1
                            relations.extend(((r, k, 396 + p - lane),
                                              (r, later, 623 + p - q)))
                for top in (0, 0x80000000):
                    for later, q in back.get(word ^ twist(top, packet[0]), ()):
                        if later > k:
                            partial += 1
                            relations.extend(((r, k, 396 - lane),
                                              (r, later, 623 - q)))
    return full, partial, list(dict.fromkeys(relations))


def upper_bounds(count: int, relations: list[tuple[int, int, int]]):
    inf = 10**8
    distances = [[0 if i == j else inf for j in range(count)] for i in range(count)]
    for i in range(count - 1):
        distances[i][i + 1] = min(distances[i][i + 1], 16)
        distances[i + 1][i] = min(distances[i + 1][i], -4)
    for i, j, distance in relations:
        distances[i][j] = min(distances[i][j], distance)
        distances[j][i] = min(distances[j][i], -distance)
    for k in range(count):
        stage = distances[k]
        for row in distances:
            inherited = row[k]
            if inherited == inf:
                continue
            for j, value in enumerate(stage):
                candidate = inherited + value
                if candidate < row[j]:
                    row[j] = candidate
    assert all(distances[i][i] == 0 for i in range(count))
    return distances


def main() -> None:
    location = (Path(sys.argv[1]) if len(sys.argv) == 2 else
                Path(__file__).resolve().parents[2] / "resources")
    data = read_spool(location)
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        data, re.M
    )
    assert len(rows) == 133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417",
        b"2", b"ACK", b"RECOVER"
    )
    # Do not even parse the disputed selected physical-coupon copy.
    native = [
        None if index == 129 else tuple(
            untemper(int.from_bytes(
                bytes.fromhex(row[5].decode())[4 * lane:4 * lane + 4], "little"
            )) for lane in range(4))
        for index, row in enumerate(rows)
    ]
    assert native[129] is None

    # Independent synthetic full MT recurrence, round-trip and relation positive.
    seed = [((i * 0x9E3779B9) ^ (i << 9) ^ 0xF0101234) & U32 for i in range(624)]
    planted = (seed[397] ^ twist(seed[0], seed[1])) & U32
    assert untemper(temper(planted)) == planted
    planted_triple = [tuple(seed[0:4]), tuple(seed[397:401]),
                      (planted, 0x13572468, 0xABCDEF02, 0x789A3210)]
    synthetic_full, _, _ = build_witnesses(planted_triple)
    assert synthetic_full >= 1

    full, partial, relations = build_witnesses(native)
    assert (full, partial, len(relations)) == (25, 17, 49)
    distances = upper_bounds(len(rows), relations)
    def placements(delta: int) -> list[tuple[int, int, int, int]]:
        found = []
        for p in range(4):
            for row in range(len(native)):
                if native[row] is None:
                    continue
                for lane in range(4):
                    target_distance = delta + lane - p
                    if (-distances[129][row] <= target_distance
                            <= distances[row][129]):
                        found.append((p, row, lane, target_distance))
        return found

    # To produce X[T+p] in one standard native MT step, the parents lie at
    # T+p-624, T+p-623 and T+p-227.
    # To produce missing X[T+p-227] in a second step, its parents lie at
    # T+p-851, T+p-850, T+p-454.
    first = {offset: placements(offset) for offset in (624, 623, 227)}
    second = {offset: placements(offset) for offset in (851, 850, 454)}
    assert first[624] == [(0, 43, 3, 627)]
    assert first[623] == first[227] == []
    assert second == {851: [], 850: [], 454: []}

    # Exact published source-compatible four-fresh schedule is a witness that
    # the temporal graph is consistent, not a claim of printer provenance.
    stages = (0, 10, 14, 23, 32, 43, 47, 54, 67, 80, 84, 92, 99, 110, 119, 124,
              130, 134, 138, 151, 155, 160, 167, 177, 182, 189, 195, 204, 211,
              215, 224, 230, 237, 242, 251, 258, 263, 275, 288, 297, 305,
              311, 318, 328, 337, 345, 350, 360, 366, 370, 378, 385, 389,
              394, 402, 411, 417, 425, 430, 434, 445, 458, 463, 472, 481,
              489, 495, 505, 514, 520, 532, 537, 542, 548, 558, 565, 572,
              581, 592, 596, 604, 613, 617, 624, 632, 641, 645, 652, 662,
              666, 677, 682, 689, 696, 705, 714, 721, 731, 739, 745, 751,
              755, 767, 771, 779, 784, 792, 796, 804, 811, 822, 833, 842,
              846, 853, 861, 871, 877, 885, 891, 903, 909, 914, 921, 927,
              934, 940, 947, 951, 952, 957, 961, 966)
    assert len(stages) == 133
    deltas = {12: 2, 25: -2, 43: 2, 47: -2, 66: 2,
              79: -2, 96: 2, 109: -2, 128: 3, 129: -1}
    gaps = [b - a + deltas.get(i, 0) for i, (a, b) in
            enumerate(zip(stages, stages[1:]))]
    witness = [0]
    for gap in gaps:
        assert 4 <= gap <= 16
        witness.append(witness[-1] + gap)
    assert witness[129] == 955
    assert all(witness[j] - witness[i] == distance
               for i, j, distance in relations)

    print(json.dumps({
        "spool_sha256": SPOOL_SHA,
        "selected_payload_parsed": False,
        "planted_native_MT_recurrence": "PASS",
        "original_full_witnesses": full,
        "original_partial_witnesses": partial,
        "original_unique_stage_equalities": len(relations),
        "four_fresh_positive_graph_schedule": True,
        "selected_stage_in_example": witness[129],
        "one_step_parent_placements": {str(k): v for k, v in first.items()},
        "two_step_parent_placements": {str(k): v for k, v in second.items()},
        "two_step_direct_intact_leaf_reconstruction_possible": False,
        "actual_K04_recovered": False,
        "scope": "one- and two-forward-native-MT-recursion with original intact direct-word leaves"
    }, indent=2))


if __name__ == "__main__":
    main()
