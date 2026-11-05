"""Reproduce an unindexed native MT19937 printer stage-difference graph.

Read-only. Requires original resources/evidence/print/spool-reconstruction.log or
the original 46-file ZIP as argv[1]. The selected row is excluded before parsing
any 16-byte source data. No K04 hash, mask or precomputed stage map is used.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTOR = "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"
INF = float("inf")


def temper(x: int) -> int:
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF


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


def twist_mix(x: int, y: int) -> int:
    return ((((x & 0x80000000) | (y & 0x7FFFFFFF)) >> 1)
            ^ (0x9908B0DF if y & 1 else 0))


def source_rows(filename: str) -> list[tuple[int, list[int]]]:
    path = Path(filename)
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as z:
            raw = z.read("evidence/print/spool-reconstruction.log")
    else:
        raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    lines = [s for s in raw.decode("utf-8").splitlines() if "PAYLOAD=" in s]
    assert len(lines) == 133 and SELECTOR in lines[129]
    output = []
    for row, line in enumerate(lines):
        if row == 129:
            continue
        matched = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert matched is not None
        packet = bytes.fromhex(matched.group(1))
        output.append((row, [untemper(int.from_bytes(packet[j:j+4], "little"))
                             for j in range(0, 16, 4)]))
    assert len(output) == 132
    return output


def discover(rows: list[tuple[int, list[int]]]):
    flat = [(row, pos, word)
            for row, words in rows for pos, word in enumerate(words)]
    words = [item[2] for item in flat]
    indexed_xors: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for k in range(len(words)):
        for l in range(k + 32, min(k + 251, len(words))):
            indexed_xors[words[k] ^ words[l]].append((k, l))
    evidence = []
    for base in range(0, len(words), 4):
        for j in range(base + 1, base + 4):
            for k, l in indexed_xors.get(twist_mix(words[j - 1], words[j]), ()):
                if k > j and flat[k][0] > flat[j][0] and flat[l][0] > flat[k][0]:
                    evidence.append((j - 1, j, k, l))
    return flat, evidence


class WeightedUnion:
    def __init__(self, keys: list[int]):
        self.parents = {k: k for k in keys}
        self.deltas = {k: 0 for k in keys}
        self.sizes = {k: 1 for k in keys}
        self.unions = 0

    def find(self, key: int) -> tuple[int, int]:
        if self.parents[key] != key:
            root, delta = self.find(self.parents[key])
            self.deltas[key] += delta
            self.parents[key] = root
        return self.parents[key], self.deltas[key]

    def join(self, a: int, b: int, delta: int):
        # delta is s[b]-s[a] in native output stages.
        ra, da = self.find(a)
        rb, db = self.find(b)
        if ra == rb:
            assert db - da == delta
        elif self.sizes[ra] < self.sizes[rb]:
            self.parents[ra] = rb
            self.deltas[ra] = db - da - delta
            self.sizes[rb] += self.sizes[ra]
            self.unions += 1
        else:
            self.parents[rb] = ra
            self.deltas[rb] = da + delta - db
            self.sizes[ra] += self.sizes[rb]
            self.unions += 1


def directed_constraints(flat, relations):
    # Difference-constraint edges u->v of the form s[v] <= s[u]+w.
    edges = []
    for i, j, k, l in relations:
        a, ai, _ = flat[i]
        same, aj, _ = flat[j]
        b, bk, _ = flat[k]
        c, cl, _ = flat[l]
        assert a == same and aj == ai + 1
        for row, stage_offset in ((b, 397 + ai - bk),
                                  (c, 624 + ai - cl)):
            edges.append((a, row, stage_offset))
            edges.append((row, a, -stage_offset))
    # At least four native output draws per complete printer packet,
    # including the omitted selected row.
    for row in range(132):
        edges.append((row + 1, row, -4))
    return edges


def shortest(n: int, edges, start: int) -> list[float]:
    distances = [INF] * n
    distances[start] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                changed = True
        if not changed:
            break
    assert all(distances[u] + w >= distances[v] for u, v, w in edges), \
        "Contradictory source-stage inequalities"
    return distances


def main(filename: str):
    for _ in range(1000):
        original = random.getrandbits(32)
        assert temper(untemper(original)) == original
    rows = source_rows(filename)
    flat, relations = discover(rows)
    assert len(relations) == 25, len(relations)
    graph = WeightedUnion([row for row, _ in rows])
    for i, _, k, l in relations:
        a, ai, _ = flat[i]
        b, bk, _ = flat[k]
        c, cl, _ = flat[l]
        graph.join(a, b, 397 + ai - bk)
        graph.join(a, c, 624 + ai - cl)
    members = defaultdict(list)
    for row, _ in rows:
        root, delta = graph.find(row)
        members[root].append((row, delta))
    counts = dict(sorted(Counter(map(len, members.values())).items()))
    assert (len(members), graph.unions, counts) == \
        (96, 36, {1: 82, 3: 10, 5: 4})
    assert graph.find(128)[0] == 128 and graph.find(130)[0] == 130

    edges = directed_constraints(flat, relations)
    # s[129]-s[0] is bounded above by shortest path 0->129, below
    # by negative shortest path 129->0. Difference constraints
    # with integer coefficients have attainable integer endpoints.
    low = -shortest(133, edges, 129)[0]
    high = shortest(133, edges, 0)[129]
    assert (low, high) == (916, 971), (low, high)
    # A small synthetic stage graph exercises both lower/upper bounds.
    demo = [(0, 2, 15), (2, 0, -15),
            (1, 0, -4), (2, 1, -4)]
    assert (-shortest(3, demo, 1)[0], shortest(3, demo, 0)[1]) == (4, 11)

    print("SOURCE_SHA256", SPOOL_SHA256)
    print("RETAINED_WHOLE_PACKET_ROWS", len(rows))
    print("UNINDEXED_EXACT_NATIVE_TWIST_RELATIONS", len(relations))
    print("GRAPH_COMPONENTS", len(members), "INDEPENDENT_JOIN_EDGES", graph.unions)
    print("COMPONENT_SIZE_DISTRIBUTION", counts)
    print("SELECTED_NEIGHBORS_SINGLETONS", 128, 130)
    print("RELATIVE_SELECTED_STAGE_MIN_MAX", int(low), int(high))
    print("INCLUSIVE_INTEGER_STAGES", int(high - low + 1))
    print("SELECTED_K04_PHYSICAL_BITS_AUTHENTICATED", 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else "resources/evidence/print/spool-reconstruction.log")
