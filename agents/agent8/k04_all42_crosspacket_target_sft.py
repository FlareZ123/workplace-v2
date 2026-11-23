#!/usr/bin/env python3
"""K04 immediate cross-record MT predecessor observability under all42 source stages.

Requires the existing source-pinned Agent1 witness extractor. Does not decode
the selected row129 payload or load the K04 acceptance commitment. The direct
MT recurrence is tested only for two antecedents spanning r lane3 -> r+1 lane0.
Run from the workplace-v2 repository: python agents/agent8/k04_all42_crosspacket_target_sft.py
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_all42_fresh_four_output_sft import (  # noqa: E402
    find_all42, retained_native_words, twist, untemper,
)

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
INF = 10_000_000


def closure(witnesses, states):
    n = len(states)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0

    def bound(i, j, low, high):
        d[i][j] = min(d[i][j], high)
        d[j][i] = min(d[j][i], -low)

    for r in range(n - 1):
        bound(r, r + 1, 4 if states[r] == b"ACK" else 0, 100)
    for r, k, l, p, i, q in witnesses:
        bound(r, k, 396 + p - i, 396 + p - i)
        bound(r, l, 623 + p - q, 623 + p - q)

    for k in range(n):
        middle = d[k]
        for i in range(n):
            first = d[i][k]
            if first >= INF:
                continue
            line = d[i]
            for j in range(n):
                via = first + middle[j]
                if via < line[j]:
                    line[j] = via
    assert all(d[i][i] >= 0 for i in range(n))
    return d


def joint_possible(d, r, k, q, i, target=129):
    """Exact four-anchor test: base closure plus three added equalities."""
    anchors = (r, r + 1, k, target)
    a = [[d[x][y] for y in anchors] for x in anchors]
    for x, y, delta in ((0, 1, 4), (0, 2, 400 - i), (0, 3, 627 - q)):
        a[x][y] = min(a[x][y], delta)
        a[y][x] = min(a[y][x], -delta)
    for z in range(4):
        middle = a[z]
        for x in range(4):
            first = a[x][z]
            for y in range(4):
                via = first + middle[y]
                if via < a[x][y]:
                    a[x][y] = via
    return all(a[z][z] >= 0 for z in range(4))


def target_donors(d, native):
    intervals = 0
    matches = []
    for r in range(128):
        if native[r + 1] is None:
            continue
        if d[r][r + 1] < 4 or d[r + 1][r] < -4:
            continue
        for k in range(r + 2, 129):
            if native[k] is None:
                continue
            for i in range(4):
                if d[r][k] < 400 - i or d[k][r] < -(400 - i):
                    continue
                for q in range(4):
                    if d[r][129] < 627 - q or d[129][r] < -(627 - q):
                        continue
                    intervals += 1
                    if joint_possible(d, r, k, q, i):
                        word = native[k][i] ^ twist(native[r][3], native[r + 1][0])
                        matches.append((r, k, q, i, f"{temper(word):08X}"))
    return intervals, matches


def temper(word):
    word ^= word >> 11
    word ^= (word << 7) & 0x9D2C5680
    word ^= (word << 15) & 0xEFC60000
    word ^= word >> 18
    return word & 0xFFFFFFFF


def planted_mt_control():
    """A genuinely seeded stream predicts a withheld complete 32-bit target."""
    gaps = [7] * 132
    gaps[40] = 4
    gaps[45] = 8
    for r in range(97, 103):
        gaps[r] = 8
    starts = [0]
    for gap in gaps:
        starts.append(starts[-1] + gap)
    assert (starts[41] - starts[40],
            starts[97] - starts[40],
            starts[129] - starts[40]) == (4, 397, 627)
    rng = random.Random(0x417A11)
    words = [untemper(rng.getrandbits(32)) for _ in range(starts[-1] + 4)]
    predicted = words[starts[97] + 3] ^ twist(
        words[starts[40] + 3], words[starts[41]]
    )
    assert predicted == words[starts[129]]
    assert temper(predicted) == temper(words[starts[129]])
    return f"{temper(predicted):08X}"



def stage_interval_possible(d, r, target, delta):
    return d[r][target] >= delta and d[target][r] >= -delta


def three_root_joint_possible(d, a, v, u):
    """All three source stage roots must share ONE selected stage S129."""
    starts = (129, a[0], v[0], u[0])
    table = [[d[x][y] for y in starts] for x in starts]
    for i, (_, _, distance) in enumerate((a, v, u), 1):
        table[i][0] = min(table[i][0], distance)
        table[0][i] = min(table[0][i], -distance)
    for mid in range(4):
        via = table[mid]
        for i in range(4):
            first = table[i][mid]
            for j in range(4):
                length = first + via[j]
                if length < table[i][j]:
                    table[i][j] = length
    return all(table[i][i] >= 0 for i in range(4))


def twohop_donors(d, native):
    """Expand X[t-227] once more using X[t-454] and a second MT twist.

    X[t] = X[t-454] XOR twist(X[t-851], X[t-850])
                    XOR twist(X[t-624], X[t-623]).
    Both twists are contiguous WORD PAIRS within intact source packets.
    """
    result = []
    for q in range(4):
        a = [(r, p, 624 + p - q)
             for r in range(129) if native[r] is not None
             for p in range(3) if stage_interval_possible(d, r, 129, 624 + p - q)]
        v = [(r, p, 851 + p - q)
             for r in range(129) if native[r] is not None
             for p in range(3) if stage_interval_possible(d, r, 129, 851 + p - q)]
        u = [(r, i, 454 + i - q)
             for r in range(129) if native[r] is not None
             for i in range(4) if stage_interval_possible(d, r, 129, 454 + i - q)]
        lane = []
        for first in a:
            for second in v:
                for last in u:
                    if not three_root_joint_possible(d, first, second, last):
                        continue
                    ar, ap, _ = first
                    vr, vp, _ = second
                    ur, ui, _ = last
                    native_word = (
                        native[ur][ui]
                        ^ twist(native[vr][vp], native[vr][vp + 1])
                        ^ twist(native[ar][ap], native[ar][ap + 1])
                    )
                    lane.append((ar, ap, vr, vp, ur, ui, f"{temper(native_word):08X}"))
        result.append(lane)
    return result


def planted_twohop_control():
    # Seven native draws per event, except one five-draw packet:
    # S129-S40=623, S129-S7=852, S129-S64=455.
    gaps = [7] * 132
    gaps[8] = 5
    starts = [0]
    for gap in gaps:
        starts.append(starts[-1] + gap)
    assert (starts[129] - starts[40],
            starts[129] - starts[7],
            starts[129] - starts[64]) == (623, 852, 455)
    rng = random.Random(0x417A11)
    words = [untemper(rng.getrandbits(32)) for _ in range(starts[-1] + 4)]
    predicted = (
        words[starts[64] + 2]
        ^ twist(words[starts[7] + 2], words[starts[7] + 3])
        ^ twist(words[starts[40]], words[starts[40] + 1])
    )
    assert predicted == words[starts[129] + 1]
    return f"{temper(predicted):08X}"


def assert_joint_fourlane_excluded(weak):
    # All 25-witness two-hop possibilities share source rows (43,12,66).
    # With a single S129, the three stage distances must coincide across
    # all q=0..3. For top pair positions p=0..2, p-q cannot be constant
    # over four target lanes, a structural obstruction.
    for lane in weak:
        assert len(lane) == 9
        assert all((r1, r2, r3) == (43, 12, 66)
                   for r1, _, r2, _, r3, _, _ in lane)
    assert not any(
        p0 + 3 <= 2 for p0 in range(3)
    )

def main():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    states = re.findall(rb" STATE=(\w+) ", raw)
    assert len(states) == 133
    assert states[129] == b"ACK"
    native = retained_native_words()
    assert len(native) == 133 and native[129] is None

    witnesses = find_all42(native)
    assert len(witnesses) == 42
    weak = closure(witnesses[:25], states)
    strong = closure(witnesses, states)
    weak_intervals, weak_matches = target_donors(weak, native)
    full_intervals, full_matches = target_donors(strong, native)
    assert weak_intervals == 28
    assert weak_matches == [(43, 97, 3, 2, "64EC58DA")], weak_matches
    assert full_intervals == 0 and full_matches == []

    # Six actual cross-boundary source equalities verify the word operation.
    controls = (
        (3, 57, 87, 3, 3), (12, 67, 97, 1, 2),
        (13, 68, 98, 1, 3), (33, 86, 116, 2, 3),
        (40, 94, 125, 2, 0), (43, 97, 130, 2, 3),
    )
    weak_ctl, strong_ctl = [], []
    for r, k, l, i, q in controls:
        assert native[l][q] == native[k][i] ^ twist(native[r][3], native[r + 1][0])
        weak_ctl.append(joint_possible(weak, r, k, q, i, l))
        strong_ctl.append(joint_possible(strong, r, k, q, i, l))
    assert weak_ctl == [False, False, False, True, True, True]
    assert strong_ctl == [False, False, False, True, True, False]
    weak_twohop = twohop_donors(weak, native)
    strong_twohop = twohop_donors(strong, native)
    assert_joint_fourlane_excluded(weak_twohop)
    one = [(43, 0, 12, 2, 66, 3, "B12FDB6A")]
    assert strong_twohop == [one, one, [], []], strong_twohop
    print("SEEDED_MT_TWOHOP_CONTROL PASS", planted_twohop_control())
    print("TWOHOP_SOURCE_25_COUNTS", [len(lane) for lane in weak_twohop])
    print("TWOHOP_SOURCE_ALL42_COUNTS", [len(lane) for lane in strong_twohop])
    print("TWOHOP_SOURCE_ALL42_SURVIVORS", strong_twohop)
    print("TWOHOP_25_JOINT_FOUR_WORD_COUPONS", 0)
    print("SEEDED_MT_CROSSPACKET_CONTROL PASS", planted_mt_control())
    print("SOURCE_SHA256", SOURCE_SHA)
    print("WITNESSES", 25, 17)
    print("SOURCE_CONTROL_25", weak_ctl, "SOURCE_CONTROL_42", strong_ctl)
    print("TARGET_INTERVAL_FEASIBLE_25", weak_intervals,
          "TARGET_COMPLETE_GEOMETRIES_25", weak_matches)
    print("TARGET_INTERVAL_FEASIBLE_42", full_intervals,
          "TARGET_COMPLETE_GEOMETRIES_42", full_matches)
    print("SELECTED_ROW129_BYTES_DECODED False")
    print("ORIGINAL_K04_COMMITMENT_EVALUATED False")
    print("STATUS All42 excludes immediate cross-packet target donors in all four lanes")


if __name__ == "__main__":
    main()
