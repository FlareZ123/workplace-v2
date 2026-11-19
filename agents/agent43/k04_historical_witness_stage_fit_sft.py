#!/usr/bin/env python3
"""Source-pinned historical MT-witness stage-fit and holdout SFT.

Run from repository root:
    python agents/agent43/k04_historical_witness_stage_fit_sft.py

The selected PS-261003-0417 attempt-2 ACK at source row 129 is metadata-checked
and skipped before its PAYLOAD field is extracted or decoded. This test uses
only the 132 other packets. It does not read K04 mask/commitment or candidate.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import random
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
N_ROWS = 133
MISSING_ROW = 129
INF = 10**18
TRIALS = 96


def untemper(y: int) -> int:
    x = y
    for _ in range(2):
        x = y ^ (x >> 18)
    z = x
    for _ in range(2):
        z = x ^ ((z << 15) & 0xEFC60000)
    x = z
    for _ in range(6):
        z = x ^ ((z << 7) & 0x9D2C5680)
    x = z
    for _ in range(4):
        z = x ^ (z >> 11)
    return z & 0xFFFFFFFF


def load_source(path: Path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == SOURCE_SHA256, digest
    lines = [line for line in raw.decode("ascii").splitlines()
             if "PAYLOAD=" in line]
    assert len(lines) == N_ROWS, len(lines)

    packets = {}
    metadata = {}
    for row, line in enumerate(lines):
        marker = line.find(" PAYLOAD=")
        assert marker >= 0
        prefix = line[:marker]
        fields = dict(re.findall(r"([A-Z_]+)=([^\s]+)", prefix))
        metadata[row] = fields
        if row == MISSING_ROW:
            assert fields.get("JOB") == "PS-261003-0417"
            assert fields.get("ATTEMPT") == "2"
            assert fields.get("STATE") == "ACK"
            assert fields.get("CLASS") == "RECOVER"
            # Continue before slicing, matching or decoding the selected payload.
            continue
        payload_tail = line[marker + len(" PAYLOAD="):]
        match = re.match(r"([0-9A-F]{32})(?:\s|$)", payload_tail)
        assert match is not None, row
        # Some trailing metadata (notably DEST) follows the payload field.
        fields.update(dict(re.findall(r"([A-Z_]+)=([^\s]+)",
                                      payload_tail[match.end():])))
        packet = bytes.fromhex(match.group(1))
        packets[row] = [
            untemper(int.from_bytes(packet[4*j:4*j+4], "little"))
            for j in range(4)
        ]
    assert len(packets) == 132
    assert len({tuple(v) for v in packets.values()}) == 132
    assert len({word for packet in packets.values() for word in packet}) == 528
    return packets, metadata


def discover_chronological_links(packets):
    """Find exact MT twist witnesses with source-row order r < k < l."""
    flat = [(row, j, value)
            for row, packet in packets.items()
            for j, value in enumerate(packet)]
    by_value = defaultdict(list)
    for row, j, value in flat:
        by_value[value].append((row, j))

    found = []
    for row, packet in packets.items():
        for j in range(3):
            first, second = packet[j:j+2]
            z = (first & 0x80000000) | (second & 0x7FFFFFFF)
            mix = (z >> 1) ^ (0x9908B0DF if z & 1 else 0)
            for middle_row, middle_j, middle in flat:
                if middle_row <= row:
                    continue
                for final_row, final_j in by_value.get(mix ^ middle, ()):
                    if final_row > middle_row:
                        found.append((row, j, middle_row, middle_j,
                                      final_row, final_j))
    return sorted(set(found))


def stage_edges(relations):
    """Difference constraints for S_(i+1)-S_i >= 4 and exact MT lags."""
    edges = []
    for row, j, middle_row, middle_j, final_row, final_j in relations:
        for target, position, lag in (
            (middle_row, middle_j, 397),
            (final_row, final_j, 624),
        ):
            step = lag + j - position
            # S_target - S_row == step
            edges.append((row, target, step))
            edges.append((target, row, -step))
    for row in range(N_ROWS - 1):
        # S_row - S_(row+1) <= -4
        edges.append((row + 1, row, -4))
    return edges


def shortest(edges, source):
    distance = [INF] * N_ROWS
    distance[source] = 0
    for _ in range(N_ROWS - 1):
        changed = False
        for u, v, weight in edges:
            if distance[u] < INF and distance[v] > distance[u] + weight:
                distance[v] = distance[u] + weight
                changed = True
        if not changed:
            break
    return distance


def graph_stats(relations):
    edges = stage_edges(relations)
    distance = [0] * N_ROWS
    feasible = True
    for iteration in range(N_ROWS):
        changed = False
        for u, v, weight in edges:
            if distance[v] > distance[u] + weight:
                distance[v] = distance[u] + weight
                changed = True
        if not changed:
            break
        if iteration == N_ROWS - 1:
            feasible = False

    parent = list(range(N_ROWS))
    rank = [0] * N_ROWS

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        else:
            parent[rb] = ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1

    for row, j, middle_row, middle_j, final_row, final_j in relations:
        union(row, middle_row)
        union(row, final_row)

    components_excluding_selected = len({
        find(row) for row in range(N_ROWS) if row != MISSING_ROW
    })
    bounds = None
    if feasible:
        from_zero = shortest(edges, 0)
        from_target = shortest(edges, MISSING_ROW)
        lo = -from_target[0]
        hi = from_zero[MISSING_ROW]
        bounds = (lo, hi)
    return {
        "feasible": feasible,
        "components_excluding_selected": components_excluding_selected,
        "selected_bounds": bounds,
        "edges": edges,
    }


def bounds_for(edges, target):
    from_zero = shortest(edges, 0)
    from_target = shortest(edges, target)
    lo = -from_target[0]
    hi = from_zero[target]
    return lo, hi


def holdout_analysis(packets):
    rows = sorted(packets)
    results = []
    for heldout in rows:
        if heldout == 0:
            # Row zero is the stage-coordinate origin, not a predictive holdout.
            continue
        training = {row: packet for row, packet in packets.items()
                    if row != heldout}
        relations = discover_chronological_links(training)
        stats = graph_stats(relations)
        assert stats["feasible"]
        lo, hi = bounds_for(stats["edges"], heldout)
        results.append((heldout, len(relations), lo, hi))
    widths = [hi-lo for _, _, lo, hi in results
              if lo > -INF and hi < INF]
    unbounded = [row for row, _, lo, hi in results
                 if lo <= -INF or hi >= INF]
    unique = sum(lo == hi for _, _, lo, hi in results)
    return {
        "holdouts": len(results),
        "unique_stage": unique,
        "finite_intervals": len(widths),
        "unbounded_rows": unbounded,
        "width_min": min(widths),
        "width_median": statistics.median(widths),
        "width_mean": statistics.mean(widths),
        "width_max": max(widths),
        "feasible": len(results),
    }


def shuffled_packets(packets, metadata, rng, strata):
    row_ids = sorted(packets)
    output = {row: list(packet) for row, packet in packets.items()}
    if strata is None:
        values = [list(packets[row]) for row in row_ids]
        rng.shuffle(values)
        return {row: value for row, value in zip(row_ids, values)}

    groups = defaultdict(list)
    for row in row_ids:
        fields = metadata[row]
        key = tuple(fields[name] for name in strata)
        groups[key].append(row)
    for group in groups.values():
        values = [list(packets[row]) for row in group]
        rng.shuffle(values)
        for row, value in zip(group, values):
            output[row] = value
    return output


def run_controls(name, packets, metadata, strata, seed):
    rng = random.Random(seed)
    counts = []
    feasible = 0
    selected_finite = 0
    for _ in range(TRIALS):
        trial = shuffled_packets(packets, metadata, rng, strata)
        relations = discover_chronological_links(trial)
        stats = graph_stats(relations)
        counts.append(len(relations))
        if stats["feasible"]:
            feasible += 1
            lo, hi = stats["selected_bounds"]
            if lo > -INF and hi < INF:
                selected_finite += 1
    return {
        "name": name,
        "mean": statistics.mean(counts),
        "median": statistics.median(counts),
        "min": min(counts),
        "max": max(counts),
        "at_least_25": sum(value >= 25 for value in counts),
        "stage_feasible": feasible,
        "selected_finite_if_feasible": selected_finite,
    }


def main():
    packets, metadata = load_source(SOURCE)
    relations = discover_chronological_links(packets)
    stats = graph_stats(relations)
    assert len(relations) == 25
    assert stats["feasible"]
    assert stats["components_excluding_selected"] == 96
    assert stats["selected_bounds"] == (916, 971)

    # Since the full 25-edge graph is feasible, every single-edge deletion is
    # feasible too; the consistency gate cannot identify a unique decoy edge.
    one_edge_deletions = sum(
        graph_stats(relations[:i] + relations[i+1:])["feasible"]
        for i in range(len(relations))
    )
    assert one_edge_deletions == 25

    holdouts = holdout_analysis(packets)
    assert holdouts == {
        "holdouts": 131,
        "unique_stage": 0,
        "finite_intervals": 128,
        "unbounded_rows": [53, 83, 132],
        "width_min": 55,
        "width_median": 62,
        "width_mean": 69.8671875,
        "width_max": 141,
        "feasible": 131,
    }, holdouts

    controls = [
        run_controls("whole-row", packets, metadata, None, 20261119043),
        run_controls("class-dest", packets, metadata, ("CLASS", "DEST"),
                     20261119044),
        run_controls("class-dest-state", packets, metadata,
                     ("CLASS", "DEST", "STATE"), 20261119045),
    ]
    expected = [
        ("whole-row", 8.833333333333334, 8, 2, 18, 0, 3, 0),
        ("class-dest", 10.65625, 11, 5, 18, 0, 0, 0),
        ("class-dest-state", 9.90625, 10, 2, 18, 0, 2, 0),
    ]
    for actual, want in zip(controls, expected):
        assert (actual["name"], actual["mean"], actual["median"],
                actual["min"], actual["max"], actual["at_least_25"],
                actual["stage_feasible"],
                actual["selected_finite_if_feasible"]) == want, actual

    print("SOURCE_SHA256", SOURCE_SHA256)
    print("SELECTED_ROW", MISSING_ROW, "metadata-checked; payload not decoded")
    print("ORIGINAL_WITNESSES", len(relations),
          "STAGE_FEASIBLE", stats["feasible"],
          "COMPONENTS_EXCLUDING_SELECTED",
          stats["components_excluding_selected"],
          "SELECTED_STAGE_INTERVAL", stats["selected_bounds"],
          "SINGLE_EDGE_DELETIONS_FEASIBLE", one_edge_deletions)
    print("WHOLE_PACKET_HOLDOUTS", holdouts)
    for control in controls:
        print("NULL", control)
    print("BOUNDARY: exact recurrence signal is chronology-enriched but does not "
          "identify unique stages; no K04 bytes recovered.")


if __name__ == "__main__":
    main()
