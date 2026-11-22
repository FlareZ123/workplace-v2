"""K04 original source-stage conditioned MT coupon, selected ACK2 payload withheld.

Run: python agents/agent8/k04_stage_conditioned_target_sft.py
No evidence, verifier, route or candidate writes.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import re

from k04_mt_packet_boundary_sft import find_witnesses, source_words, temper, twist, untemper

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"


def pinned(path: str, digest: str) -> bytes:
    data = (ROOT / path).read_bytes()
    assert sha256(data).hexdigest() == digest
    return data


def closure(rows: list[tuple[bytes, ...]], witnessed: list[tuple[int, ...]]) -> list[list[float]]:
    size = len(rows)
    infinity = float("inf")
    distances = [[infinity] * size for _ in range(size)]
    for j in range(size):
        distances[j][j] = 0

    def upper(start: int, stop: int, value: int) -> None:
        distances[start][stop] = min(distances[start][stop], value)

    def equality(start: int, stop: int, value: int) -> None:
        upper(start, stop, value)
        upper(stop, start, -value)

    # Retained ACKs must consume four native words. A REQUESTED row may
    # consume zero, and every row may consume at most 100 under this model.
    for j in range(size - 1):
        minimum = 0 if rows[j][3] == b"REQUESTED" else 4
        upper(j, j + 1, 100)
        upper(j + 1, j, -minimum)

    # An MT native recurrence at observed source row/lane (r,p), (k,i), (l,q)
    # imposes these *necessary* integer-start equalities.
    for r, k, l, p, i, q in witnessed:
        equality(r, k, 396 + p - i)
        equality(r, l, 623 + p - q)

    for mid in range(size):
        via_mid = distances[mid]
        for left in range(size):
            prefix = distances[left][mid]
            if prefix == infinity:
                continue
            source = distances[left]
            for right in range(size):
                candidate = prefix + via_mid[right]
                if candidate < source[right]:
                    source[right] = candidate
    assert all(distances[j][j] == 0 for j in range(size)), "source stage network inconsistent"
    return distances


def feasible_difference(dist: list[list[float]], start: int, stop: int, delta: int) -> bool:
    return -dist[stop][start] <= delta <= dist[start][stop]


def main() -> None:
    raw = pinned("resources/evidence/print/spool-reconstruction.log", SOURCE_SHA)
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw,
        re.M,
    )
    assert len(rows) == 133
    assert rows[129][1:5] == (b"PS-261003-0417", b"2", b"ACK", b"RECOVER")
    packets = [None if j == 129 else bytes.fromhex(row[5].decode()) for j, row in enumerate(rows)]
    native = source_words(packets, "little", False)
    historical, _ = find_witnesses(native)
    assert len(historical) == 25
    dist = closure(rows, historical)

    possible: list[set[int]] = [set() for _ in range(4)]
    viable_pairs: set[tuple[int, int]] = set()
    geometries = 0
    for r in range(129):
        if not any(feasible_difference(dist, r, 129, delta) for delta in range(620, 627)):
            continue
        for k in range(r + 1, 129):
            if not any(feasible_difference(dist, r, k, delta) for delta in range(393, 400)):
                continue
            for p in range(4):
                for i in range(4):
                    partner_gap = 396 + p - i
                    if not feasible_difference(dist, r, k, partner_gap):
                        continue
                    for q in range(4):
                        target_gap = 623 + p - q
                        if not feasible_difference(dist, r, 129, target_gap):
                            continue
                        # Exact consistency of all three anchored row-start
                        # stages follows from the original shortest-path
                        # differences between every pair of anchors.
                        if not feasible_difference(dist, k, 129, target_gap - partner_gap):
                            continue
                        geometries += 1
                        viable_pairs.add((r, k))
                        for previous_msb in ((0, 0x80000000) if p == 0 else (0,)):
                            predecessor = native[r][p - 1] if p else previous_msb
                            possible[q].add(temper(native[k][i] ^ twist(predecessor, native[r][p])))

    assert viable_pairs == {(43, 96), (43, 97), (44, 97)}
    assert geometries == 73
    assert [len(words) for words in possible] == [20, 22, 23, 25]

    route = json.loads(pinned("resources/evidence/recovery-routing.json", ROUTE_SHA))
    accept = json.loads(pinned("resources/acceptance.json", ACCEPT_SHA))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    original = accept["slot_sha256"]["K04"]
    checks = hits = 0
    for words in product(*(sorted(x) for x in possible)):
        raw_packet = b"".join(word.to_bytes(4, "little") for word in words)
        coupon = bytes(a ^ b for a, b in zip(raw_packet, mask))
        checks += 1
        hits += sha256(coupon).hexdigest() == original
    assert checks == 253000 and hits == 0

    # Source-witness stage-feasible full packet from rows 43,44,96,97.
    # It explicitly uses the row96->row97 native partner boundary.
    anchors = {43: 0, 44: 4, 96: 394, 97: 398, 129: 624}
    for start, stop in product(anchors, repeat=2):
        assert feasible_difference(dist, start, stop, anchors[stop] - anchors[start])
    four = [
        temper(native[96][3] ^ twist(native[43][0], native[43][1])),
        temper(native[97][0] ^ twist(native[43][1], native[43][2])),
        temper(native[97][1] ^ twist(native[43][2], native[43][3])),
        temper(native[97][2] ^ twist(native[43][3], native[44][0])),
    ]
    proposed_raw = b"".join(word.to_bytes(4, "little") for word in four)
    assert proposed_raw.hex().upper() == "F3B81FDE37F0311F5D01E5F9DA58EC64"
    proposed_coupon = bytes(a ^ b for a, b in zip(proposed_raw, mask))
    assert sha256(proposed_coupon).hexdigest() == "0047533c14229e38d820c31a2dbc71c124ed3d327c9287729a3ad3ab0a2b3ba0"
    assert sha256(proposed_coupon).hexdigest() != original

    rng = random.Random(0x17A11CE)
    outputs = [rng.getrandbits(32) for _ in range(1250)]
    native_fixture = [untemper(value) for value in outputs]
    planted = [temper(native_fixture[397 + q] ^ twist(native_fixture[q], native_fixture[q + 1]))
               for q in range(4)]
    assert planted == outputs[624:628]
    expected = b"".join(word.to_bytes(4, "little") for word in planted)
    synthetic_coupon = bytes(a ^ b for a, b in zip(expected, mask))
    assert sha256(synthetic_coupon).digest() == sha256(bytes(a ^ b for a, b in zip(
        b"".join(word.to_bytes(4, "little") for word in outputs[624:628]), mask))).digest()

    print(json.dumps({
        "historical_fullword_witnesses": len(historical),
        "stage_compatible_target_geometries": geometries,
        "source_row_pairs": sorted(viable_pairs),
        "target_lane_distinct_word_counts": [len(x) for x in possible],
        "complete_original_candidates": checks,
        "original_K04_hits": hits,
        "source_stage_feasible_fourrow_raw": proposed_raw.hex().upper(),
        "source_stage_feasible_fourrow_original_hit": False,
        "seeded_full_packet_positive": True,
    }, indent=2))


if __name__ == "__main__":
    main()
