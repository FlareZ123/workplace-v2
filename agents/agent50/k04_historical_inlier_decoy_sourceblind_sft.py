#!/usr/bin/env python3
"""Source-blind H-17 K04 MT-witness corroboration and packet-shuffle SFT.

The selected PS-0417 attempt-2 row is excluded before PAYLOAD parsing.
No p951 stage vector, K04 mask, acceptance digest, or selected ACK bytes
are read. Run from repository root:
  python agents/agent50/k04_historical_inlier_decoy_sourceblind_sft.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
N = 133
MISSING = 129
INF = 10**15


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


def read_source(path: Path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == SOURCE_SHA256, (digest, SOURCE_SHA256)
    lines = [line for line in raw.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == N
    packets = [None] * N
    metadata = []
    for row, line in enumerate(lines):
        cls = re.search(r"\bCLASS=([A-Z]+)", line).group(1)
        dest = re.search(r"\bDEST=([a-z]+)", line).group(1)
        state = re.search(r"\bSTATE=([A-Z]+)", line).group(1)
        attempt = int(re.search(r"\bATTEMPT=(\d+)", line).group(1))
        metadata.append((cls, dest, state, attempt))
        if row == MISSING:
            # Validate record identity only; do not parse its PAYLOAD field.
            assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        packets[row] = bytes.fromhex(match.group(1))
    assert packets[MISSING] is None
    assert sum(packet is not None for packet in packets) == 132
    return packets, metadata, digest


def flat_words(packets):
    flat = []
    for row, packet in enumerate(packets):
        if packet is None:
            continue
        for lane in range(4):
            value = int.from_bytes(packet[4 * lane:4 * lane + 4], "little")
            flat.append((row, lane, untemper(value)))
    assert len(flat) == 528
    return flat


def discover(flat):
    """Find exact 397/624 recurrence witnesses with one unknown predecessor MSB."""
    byword = defaultdict(list)
    for row, lane, word in flat:
        byword[word].append((row, lane))
    relations = []
    for row, lane, first in flat:
        low_mix = ((first & 0x7FFFFFFF) >> 1) ^ (
            0x9908B0DF if first & 1 else 0
        )
        for middle_row, middle_lane, middle in flat:
            if middle_row <= row:
                continue
            for predecessor_msb in (0, 1):
                predicted = middle ^ low_mix ^ (predecessor_msb << 30)
                for final_row, final_lane in byword.get(predicted, ()):
                    if final_row > middle_row:
                        relations.append((
                            row, lane, middle_row, middle_lane,
                            final_row, final_lane, predecessor_msb
                        ))
    return sorted(relations)


class WeightedUF:
    """Maintain exact constraints stage[b] - stage[a] == delta."""
    def __init__(self):
        self.parent = list(range(N))
        self.offset = [0] * N
        self.bad = False

    def find(self, x):
        if self.parent[x] != x:
            root, delta = self.find(self.parent[x])
            self.offset[x] += delta
            self.parent[x] = root
        return self.parent[x], self.offset[x]

    def join(self, a, b, delta):
        ra, da = self.find(a)
        rb, db = self.find(b)
        if ra == rb:
            if db - da != delta:
                self.bad = True
        else:
            self.parent[rb] = ra
            self.offset[rb] = da + delta - db


def build_uf(relations):
    uf = WeightedUF()
    for row, lane, middle_row, middle_lane, final_row, final_lane, _ in relations:
        uf.join(row, middle_row, 396 + lane - middle_lane)
        uf.join(row, final_row, 623 + lane - final_lane)
    return uf


def graph_edges(relations):
    edges = []
    for row, lane, middle_row, middle_lane, final_row, final_lane, _ in relations:
        for other, gap in (
            (middle_row, 396 + lane - middle_lane),
            (final_row, 623 + lane - final_lane),
        ):
            edges.extend(((row, other, gap), (other, row, -gap)))
    # Packet chronology: each next packet starts at least four outputs later.
    for row in range(N - 1):
        edges.append((row + 1, row, -4))
    return edges


def bellman_ford(edges, origin=None):
    distance = [0] * N if origin is None else [INF] * N
    if origin is not None:
        distance[origin] = 0
    for iteration in range(N):
        changed = False
        for a, b, weight in edges:
            if distance[a] < INF and distance[a] + weight < distance[b]:
                distance[b] = distance[a] + weight
                changed = True
        if not changed:
            return distance, True
        if iteration == N - 1:
            return distance, False
    return distance, True


def graph_summary(relations):
    uf = build_uf(relations)
    edges = graph_edges(relations)
    _, feasible = bellman_ford(edges)
    from_zero, zero_ok = bellman_ford(edges, 0)
    from_target, target_ok = bellman_ford(edges, MISSING)
    assert feasible and zero_ok and target_ok and not uf.bad
    components = len({uf.find(row)[0] for row in range(N) if row != MISSING})
    return {
        "relations": len(relations),
        "components_excluding_missing_row": components,
        "monotone_feasible": feasible,
        "selected_row_129_isolated_in_equality_graph": uf.find(MISSING)[0] == MISSING,
        "selected_start_offset_lower_bound": -from_target[0],
        "selected_start_offset_upper_bound": from_zero[MISSING],
    }, uf


def firstword_support(fullword, firstword, all_relations, flat):
    def support_against(relation, anchors):
        anchor_uf = build_uf(anchors)
        if anchor_uf.bad:
            return None
        row, lane, middle_row, middle_lane, final_row, final_lane, _ = relation
        root, base = anchor_uf.find(row)
        middle_root, middle_base = anchor_uf.find(middle_row)
        final_root, final_base = anchor_uf.find(final_row)
        mid = None if root != middle_root else (
            middle_base - base == 396 + lane - middle_lane
        )
        fin = None if root != final_root else (
            final_base - base == 623 + lane - final_lane
        )
        return mid, fin

    both = one = none = conflict = 0
    single_anchor_robust = single_anchor_fragile = 0
    row_disjoint_both = word_disjoint_both = 0
    fragile_dependencies = []
    for relation in firstword:
        status = support_against(relation, fullword)
        mid, fin = status
        if mid is False or fin is False:
            conflict += 1
        elif mid is True and fin is True:
            both += 1
            failures = []
            for index, anchor in enumerate(fullword):
                reduced = fullword[:index] + fullword[index + 1:]
                if support_against(relation, reduced) != (True, True):
                    failures.append(index)
            if failures:
                single_anchor_fragile += 1
                fragile_dependencies.append({
                    "firstword_relation": list(relation),
                    "necessary_single_deletion_anchor_indices": failures,
                    "necessary_anchors": [list(fullword[index]) for index in failures],
                })
            else:
                single_anchor_robust += 1

            touched_rows = {relation[0], relation[2], relation[4]}
            row_disjoint = [
                anchor for anchor in fullword
                if not touched_rows.intersection({anchor[0], anchor[2], anchor[4]})
            ]
            if support_against(relation, row_disjoint) == (True, True):
                row_disjoint_both += 1

            touched_words = {
                (relation[0], relation[1]),
                (relation[2], relation[3]),
                (relation[4], relation[5]),
            }
            word_disjoint = [
                anchor for anchor in fullword
                if not touched_words.intersection({
                    (anchor[0], anchor[1]),
                    (anchor[2], anchor[3]),
                    (anchor[4], anchor[5]),
                })
            ]
            if support_against(relation, word_disjoint) == (True, True):
                word_disjoint_both += 1
        elif mid is True or fin is True:
            one += 1
        else:
            none += 1

    predecessor_coverage = {}
    for label, relation_set in (("fullword_anchors", fullword),
                                ("all_relations", all_relations)):
        stage_uf = build_uf(relation_set)
        observed = defaultdict(list)
        for row, lane, word in flat:
            root, offset = stage_uf.find(row)
            observed[root].append((offset + lane, word >> 31))
        covered = matching = 0
        for row, lane, middle_row, middle_lane, final_row, final_lane, msb in firstword:
            root, offset = stage_uf.find(row)
            predecessor_stage = offset + lane - 1
            bits = {bit for stage, bit in observed[root] if stage == predecessor_stage}
            if bits:
                covered += 1
                if bits == {msb}:
                    matching += 1
        predecessor_coverage[label] = [covered, matching]

    return {
        "firstword_relations": len(firstword),
        "both_offsets_graph_implied_by_fullword_anchors": both,
        "one_offset_graph_implied": one,
        "neither_offset_graph_implied": none,
        "offset_conflicts": conflict,
        "both_offset_relations_single_anchor_deletion_robust": single_anchor_robust,
        "both_offset_relations_single_anchor_fragile": single_anchor_fragile,
        "both_offset_relations_row_disjoint": row_disjoint_both,
        "both_offset_relations_exact_word_disjoint": word_disjoint_both,
        "fragile_anchor_dependencies": fragile_dependencies,
        "predecessor_msb_coverage": predecessor_coverage,
    }


def potential_relations(flat):
    """All word-value triplets before chronological row-order filtering."""
    byword = defaultdict(list)
    for row, lane, word in flat:
        byword[word].append((row, lane))
    potential = []
    for source_row, source_lane, first in flat:
        low_mix = ((first & 0x7FFFFFFF) >> 1) ^ (
            0x9908B0DF if first & 1 else 0
        )
        for middle_row, middle_lane, middle in flat:
            if middle_row == source_row:
                continue
            for msb in (0, 1):
                predicted = middle ^ low_mix ^ (msb << 30)
                for final_row, final_lane in byword.get(predicted, ()):
                    if len({source_row, middle_row, final_row}) == 3:
                        potential.append((
                            source_row, source_lane, middle_row, middle_lane,
                            final_row, final_lane, msb
                        ))
    assert len(potential) == 84 and len(set(potential)) == 84
    return potential


def relation_stats(potential, position):
    relations = []
    for sr, sj, mr, mj, dr, dj, msb in potential:
        a, b, c = position[sr], position[mr], position[dr]
        if a < b < c:
            relations.append((a, sj, b, mj, c, dj, msb))
    fullword = [r for r in relations if r[1] != 0]
    firstword = [r for r in relations if r[1] == 0]
    uf = build_uf(fullword)
    both = one = none = conflict = 0
    if not uf.bad:
        for row, lane, middle_row, middle_lane, final_row, final_lane, _ in firstword:
            root, base = uf.find(row)
            middle_root, middle_base = uf.find(middle_row)
            final_root, final_base = uf.find(final_row)
            mid = None if root != middle_root else middle_base - base == 396 + lane - middle_lane
            fin = None if root != final_root else final_base - base == 623 + lane - final_lane
            if mid is False or fin is False:
                conflict += 1
            elif mid is True and fin is True:
                both += 1
            elif mid is True or fin is True:
                one += 1
            else:
                none += 1
    return len(fullword), len(firstword), both, one, none, conflict, uf.bad


def run_null(potential, metadata, key_fields, trials, seed):
    slots = [row for row in range(N) if row != MISSING]
    groups = defaultdict(list)
    for row in slots:
        groups[tuple(metadata[row][field] for field in key_fields)].append(row)
    group_slots = list(groups.values())
    rng = random.Random(seed)
    hist = Counter()
    both_hist = Counter()
    for _ in range(trials):
        position = {row: row for row in slots}
        for group in group_slots:
            packet_ids = group[:]
            rng.shuffle(packet_ids)
            for slot, packet_id in zip(group, packet_ids):
                position[packet_id] = slot
        full, first, both, one, none, conflict, bad = relation_stats(potential, position)
        hist[(full, first, bad)] += 1
        if not bad:
            both_hist[both] += 1
    totals = []
    for (full, first, bad), count in hist.items():
        totals.extend([full + first] * count)
    totals.sort()
    quantile = lambda p: totals[int(p * (len(totals) - 1))]
    return {
        "key_fields": list(key_fields),
        "group_sizes": sorted((len(group) for group in group_slots), reverse=True),
        "trials": trials,
        "seed": seed,
        "total_relation_mean": sum(totals) / len(totals),
        "total_relation_median": quantile(0.50),
        "total_relation_p95": quantile(0.95),
        "total_relation_p99": quantile(0.99),
        "total_relation_max": max(totals),
        "trials_with_total_at_least_42": sum(value >= 42 for value in totals),
        "max_fullword_relations": max(full for full, first, bad in hist),
        "max_firstword_relations": max(first for full, first, bad in hist),
        "fullword_graph_inconsistencies": sum(
            count for (full, first, bad), count in hist.items() if bad
        ),
        "firstword_both_supported_histogram": dict(sorted(both_hist.items())),
        "trials_with_both_supported_at_least_10": sum(
            count for value, count in both_hist.items() if value >= 10
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path("resources/evidence/print/spool-reconstruction.log"))
    parser.add_argument("--trials", type=int, default=200000)
    args = parser.parse_args()
    packets, metadata, source_digest = read_source(args.source)
    flat = flat_words(packets)
    relations = discover(flat)
    fullword = [r for r in relations if r[1] != 0]
    firstword = [r for r in relations if r[1] == 0]
    assert (len(relations), len(fullword), len(firstword)) == (42, 25, 17)

    full_summary, _ = graph_summary(fullword)
    all_summary, _ = graph_summary(relations)
    assert full_summary["selected_start_offset_lower_bound"] == 916
    assert all_summary["selected_start_offset_lower_bound"] == 917
    assert all_summary["selected_start_offset_upper_bound"] == 971
    assert all_summary["selected_row_129_isolated_in_equality_graph"]

    support = firstword_support(fullword, firstword, relations, flat)
    assert (
        support["both_offsets_graph_implied_by_fullword_anchors"],
        support["one_offset_graph_implied"],
        support["neither_offset_graph_implied"],
        support["offset_conflicts"],
    ) == (10, 1, 6, 0)
    assert (
        support["both_offset_relations_single_anchor_deletion_robust"],
        support["both_offset_relations_single_anchor_fragile"],
        support["both_offset_relations_row_disjoint"],
        support["both_offset_relations_exact_word_disjoint"],
    ) == (3, 7, 0, 10)
    assert support["predecessor_msb_coverage"] == {
        "fullword_anchors": [0, 0],
        "all_relations": [0, 0],
    }

    potential = potential_relations(flat)
    original = relation_stats(potential, {row: row for row in range(N) if row != MISSING})
    assert original == (25, 17, 10, 1, 6, 0, False)

    cd = run_null(potential, metadata, (0, 1), args.trials, 20261119011)
    fullmeta = run_null(potential, metadata, (0, 1, 2, 3), args.trials, 20261119012)
    if args.trials == 200000:
        assert cd["total_relation_max"] == 37 and cd["trials_with_total_at_least_42"] == 0
        assert fullmeta["total_relation_max"] == 37 and fullmeta["trials_with_total_at_least_42"] == 0
        assert (cd["max_fullword_relations"], cd["max_firstword_relations"]) == (23, 15)
        assert (fullmeta["max_fullword_relations"], fullmeta["max_firstword_relations"]) == (24, 16)

    output = {
        "source_sha256": source_digest,
        "selected_row_129_payload_parsed": False,
        "original_relations": {
            "total": len(relations),
            "fullword_lane_nonzero": len(fullword),
            "firstword_lane_zero_31bit": len(firstword),
        },
        "fullword_only_graph": full_summary,
        "all_relation_graph": all_summary,
        "firstword_support": support,
        "null_class_dest": cd,
        "null_class_dest_state_attempt": fullmeta,
        "zero_exceedance_95pct_upper_bound": 1 - 0.05 ** (1 / args.trials),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
