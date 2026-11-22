"""Original 42 MT printer witness necessary short-gap counts (no original writes).

Run: python agents/agent8/k04_mt_all42_shortgap_sft.py
The selected ACK2 PAYLOAD is excluded before hexadecimal parsing.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import re

from k04_mt_packet_boundary_sft import find_witnesses, source_words, twist

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REGION = tuple(range(12, 32)) + (65,) + tuple(range(115, 126))
assert len(REGION) == 32


def stage_edges(rows: list[tuple[bytes, ...]], witnesses: list[tuple[int, ...]],
                short: tuple[int, ...]) -> list[tuple[int, int, int]]:
    short_set = set(short)
    edges: list[tuple[int, int, int]] = []
    for j, row in enumerate(rows[:-1]):
        minimum = 0 if row[3] == b"REQUESTED" else 4
        maximum = 100
        if j in REGION:
            minimum, maximum = ((4, 6) if j in short_set else (7, 100))
        edges.append((j, j + 1, maximum))
        edges.append((j + 1, j, -minimum))
    for r, k, l, p, i, q in witnesses:
        for other, delta in ((k, 396 + p - i), (l, 623 + p - q)):
            edges.append((r, other, delta))
            edges.append((other, r, -delta))
    return edges


def integer_feasible(nodes: int, edges: list[tuple[int, int, int]]) -> tuple[bool, list[int] | None]:
    """Integral difference constraints are feasible iff no negative cycle."""
    distances = [0] * nodes
    for _ in range(nodes):
        changed = False
        for source, dest, bound in edges:
            candidate = distances[source] + bound
            if candidate < distances[dest]:
                distances[dest] = candidate
                changed = True
        if not changed:
            return True, [v - distances[0] for v in distances]
    return False, None


def firstword_witnesses(native: list[list[int] | None]) -> list[tuple[int, int, int, int, int, int]]:
    inverted: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for l, packet in enumerate(native):
        if packet is not None:
            for q, word in enumerate(packet):
                inverted[word].append((l, q))
    first = []
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r + 1, len(native)):
            partner = native[k]
            if partner is None:
                continue
            for i, word in enumerate(partner):
                for predecessor_msb in (0, 0x80000000):
                    for l, q in inverted.get(word ^ twist(predecessor_msb, packet[0]), ()):
                        if l > k:
                            first.append((r, k, l, 0, i, q))
    return first


def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133
    assert rows[129][1:5] == (b"PS-261003-0417", b"2", b"ACK", b"RECOVER")
    native = source_words(
        [None if j == 129 else bytes.fromhex(row[5].decode()) for j, row in enumerate(rows)],
        "little", False,
    )
    full, _ = find_witnesses(native)
    partial = firstword_witnesses(native)
    assert len(full) == 25 and len(partial) == 17

    def feasible(witnesses: list[tuple[int, ...]], short: tuple[int, ...]):
        return integer_feasible(len(rows), stage_edges(rows, witnesses, short))

    assert not feasible(full, ())[0]
    assert feasible(full, (12,))[0]
    stronger = full + partial
    assert not feasible(stronger, ())[0]
    single = [row for row in REGION if feasible(stronger, (row,))[0]]
    assert single == [], single
    pairs = [pair for pair in combinations(REGION, 2) if feasible(stronger, pair)[0]]
    allowed = tuple(j for j in REGION if j not in (12, 13))
    assert pairs == list(combinations(allowed, 2)) and len(pairs) == 435

    ok, stages = feasible(stronger, (65, 118))
    assert ok and stages is not None
    steps = [stages[j + 1] - stages[j] for j in range(132)]
    assert sum(step < 7 for j, step in enumerate(steps) if j in REGION) == 2
    assert steps[65] in (4, 5, 6) and steps[118] in (4, 5, 6)
    assert all(
        stages[k] - stages[r] == 396 + p - i and
        stages[l] - stages[r] == 623 + p - q
        for r, k, l, p, i, q in stronger
    )

    print(json.dumps({
        "historical_fullword_witnesses": len(full),
        "historical_partial_firstword_witnesses": len(partial),
        "source_region_rows": list(REGION),
        "source25_minimum_short_events": 1,
        "source42_single_short_event_feasible": len(single),
        "source42_minimum_short_events": 2,
        "two_short_event_pairs_feasible": len(pairs),
        "two_short_event_pairs_excluded_rows": [12, 13],
        "two_short_event_example": [65, 118],
        "example_draw_counts": [steps[65], steps[118]],
        "ack2_payload_withheld": True,
        "original_K04_accepted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
