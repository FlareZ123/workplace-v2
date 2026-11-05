"""Rank two-source-witness MT stage edges for K04 event-index identifiability.

Original-source p951-conditional graph geometry only. Hypothetical donor stage
edges are not original observations; no selected ACK2, K04 digest/mask used.

Run: python agents/agent17/k04_stagegraph_edge_synergy_sft.py
"""
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent13"))
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_stagefree_31bit_hidden_predecessor_graph_sft as source_graph
import k04_p951_symbolic_basis as mt
import k04_crossarchive_stagegraph_sft as joint

N = 133
INF = 10**16


def source_distance():
    flat, printer_words = joint.original_printer()
    relations = source_graph.discover(flat)
    assert len(relations) == 42
    controls = joint.external_stage_edges(printer_words)
    ax = joint.ax_bridge(printer_words)
    given_edges = [ax] + controls
    assert joint.stagegraph(relations, given_edges) == (940, 971, 79)

    arcs = [(i + 1, i, -4) for i in range(N - 1)]
    for r, j, s, k, d, l, _ in relations:
        for other, delta in ((s, 396 + j - k), (d, 623 + j - l)):
            arcs.extend(((r, other, delta), (other, r, -delta)))
    for a, b, offset in given_edges:
        arcs.extend(((a, b, offset), (b, a, -offset)))

    distances = [[INF] * N for _ in range(N)]
    for i in range(N):
        distances[i][i] = 0
    for a, b, offset in arcs:
        distances[a][b] = min(distances[a][b], offset)
    for k in range(N):
        dk = distances[k]
        for i in range(N):
            via_k = distances[i][k]
            if via_k >= INF:
                continue
            di = distances[i]
            for j in range(N):
                distance = via_k + dk[j]
                if distance < di[j]:
                    di[j] = distance
    assert all(distances[i][i] == 0 for i in range(N))
    assert (-distances[129][0], distances[0][129]) == (940, 971)
    return distances, relations, given_edges


def after_first(d, a, b, offset):
    assert offset <= d[a][b] and -offset <= d[b][a]
    return [
        [
            min(
                d[i][j],
                d[i][a] + offset + d[b][j],
                d[i][b] - offset + d[a][j],
            )
            for j in range(N)
        ]
        for i in range(N)
    ]


def second_stage_interval(d, a, b, offset):
    hi = min(
        d[0][129],
        d[0][a] + offset + d[b][129],
        d[0][b] - offset + d[a][129],
    )
    lo = -min(
        d[129][0],
        d[129][a] + offset + d[b][0],
        d[129][b] - offset + d[a][0],
    )
    assert lo <= hi
    return lo, hi


def main():
    d, relations, observed = source_distance()
    starts = mt.STARTS
    assert len(starts) == N
    # The p951 vector is a hypothesis, used only to select future source
    # donor placements, never to fit original spool nor select ACK2 bytes.
    proposed = [
        (a, b, starts[b] - starts[a])
        for a in range(N)
        for b in range(a + 1, N)
        if 224 <= starts[b] - starts[a] <= 230
        and 4 * (b - a) <= starts[b] - starts[a]
    ]
    assert len(proposed) == 102
    for a, b, offset in proposed:
        assert offset <= d[a][b] and -offset <= d[b][a]

    single_hist = Counter()
    pair_hist = Counter()
    ranked = []
    for index, (a, b, offset) in enumerate(proposed):
        lo, hi = second_stage_interval(d, a, b, offset)
        single_hist[32 - (hi - lo + 1)] += 1
        updated = after_first(d, a, b, offset)
        for c, e, suffix in proposed[index + 1:]:
            low, high = second_stage_interval(updated, c, e, suffix)
            gain = 32 - (high - low + 1)
            pair_hist[gain] += 1
            ranked.append((gain, (a, b, offset), (c, e, suffix), (low, high)))

    assert single_hist == {0: 99, 1: 3}, single_hist
    assert pair_hist == {0: 4815, 1: 302, 2: 27, 3: 3, 17: 1, 18: 1, 20: 2}, pair_hist
    winners = [r for r in ranked if r[0] == 20]
    assert len(winners) == 2
    for gain, first, second, interval in winners:
        assert interval == (940, 951)
        assert joint.stagegraph(relations, observed + [first, second])[:2] == interval
        print("TWO_EDGE_20_INDEX_GAIN", first, second, interval)
    print("ORIGINAL_GRAPH_BOUND", (940, 971))
    print("P951_POTENTIAL_SINGLE_EDGES", len(proposed), "single_hist", sorted(single_hist.items()))
    print("P951_POTENTIAL_EDGE_PAIRS", len(ranked), "pair_hist", sorted(pair_hist.items()))
    print("STATUS no original donor matched, no selected physical bits inferred")


if __name__ == "__main__":
    main()
