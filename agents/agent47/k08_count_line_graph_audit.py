#!/usr/bin/env python3
"""Source-local, no-commitment graph audit for the K08 COUNT LINE / LOW IF EVEN rule.

Prints identifiers and graph structure only, never source text or key candidates.
No PDF, protected original, verifier or commitment is loaded.
"""
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/crew/noticeboard-and-desk-notes.txt"

def build_edges(source):
    records = re.findall(r"^N(\\d{2}) / [^\\n]+\\n([^\\n]+)", source, re.M)
    assert len(records) == 24
    edges = {}
    for label, line in records:
        body = line.partition(": ")[2] if ": " in line else line
        count = len(body.split())
        edges[int(label)] = count + (count % 2 == 0)
    assert set(edges) == set(range(1, 25))
    return edges

def traverse(edges, origin):
    path, first_at = [], {}
    node = origin
    while node in edges and node not in first_at:
        first_at[node] = len(path)
        path.append(node)
        node = edges[node]
    if node not in edges:
        return "EXIT", tuple(path), node
    return "CYCLE", tuple(path), tuple(path[first_at[node]:])

def audit(source):
    edges = build_edges(source)
    found = traverse(edges, 9)
    assert found == ("CYCLE", (9, 13, 23, 21, 11, 15), (9, 13, 23, 21, 11, 15))
    assert {n for n in edges.values() if n not in edges} == {25, 31}
    results = [traverse(edges, i) for i in sorted(edges)]
    cycles = set()
    for outcome, _, final in results:
        if outcome == "CYCLE":
            cycle = list(final)
            cycles.add(min(tuple(cycle[j:] + cycle[:j]) for j in range(len(cycle))))
    assert cycles == {(9, 13, 23, 21, 11, 15)}
    return edges, results

if __name__ == "__main__":
    edges, results = audit(SOURCE.read_text(encoding="utf-8"))
    print("N09 traversal:", traverse(edges, 9)[0], traverse(edges, 9)[1])
    print("Distinct cycles:", 1)
    print("Off-graph destinations:", sorted({v for v in edges.values() if v not in edges}))
    print("Start counts:", {kind: sum(r[0] == kind for r in results) for kind in ("CYCLE", "EXIT")})
