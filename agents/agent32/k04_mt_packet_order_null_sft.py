"""K04: exact packet-order null for native MT-style printer recurrence.

No speculative stage index, original K04 acceptance, route mask or selected
ACK2 contents are read. All intact source packet values remain fixed.
"""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from math import factorial
from pathlib import Path
from random import Random
import re
import struct
import sys

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MAG = 0x9908B0DF


def temper(x):
    y = x ^ (x >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    return (y ^ (y >> 18)) & 0xFFFFFFFF


def untemper(y):
    x = y
    for _ in range(2):
        x = y ^ (x >> 18)
    y = x
    for _ in range(3):
        x = y ^ ((x << 15) & 0xEFC60000)
    y = x
    for _ in range(6):
        x = y ^ ((x << 7) & 0x9D2C5680)
    y = x
    for _ in range(5):
        x = y ^ (x >> 11)
    return x & 0xFFFFFFFF


def twist(a, b):
    z = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (z >> 1) ^ (MAG if z & 1 else 0)


def fixture(root):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest() == PIN
    lines = [s for s in raw.decode("ascii").splitlines() if s.startswith("2026-")]
    assert len(lines) == 133
    rows = []
    for i, line in enumerate(lines):
        if i == 129:
            rows.append([])  # Selected ACK2 excluded before payload decoding.
            continue
        m = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert m
        rows.append([untemper(v) for v in struct.unpack("<4I", bytes.fromhex(m[1]))])
    assert sum(map(len, rows)) == 528
    return rows


def links(rows):
    words = [(r, j, v) for r, row in enumerate(rows) for j, v in enumerate(row)]
    positions = defaultdict(list)
    for r, j, value in words:
        positions[value].append((r, j))
    result = []
    for a, row in enumerate(rows):
        for j in range(len(row) - 1):
            t = twist(row[j], row[j + 1])
            for c, cj, word in words:
                for d, dj in positions.get(t ^ word, ()):
                    if (c, cj) < (d, dj) and len({a, c, d}) == 3:
                        result.append((a, c, d))
    return result


def exact_order_probability(witnesses):
    triples = set(witnesses)
    edges = {(a, other) for a, c, d in triples for other in (c, d)}
    roots = {v: v for e in edges for v in e}

    def find(v):
        while roots[v] != v:
            v = roots[v]
        return v

    for a, b in edges:
        roots[find(b)] = find(a)
    groups = defaultdict(list)
    for v in roots:
        groups[find(v)].append(v)
    probability = Fraction(1)
    components = []
    for ids in groups.values():
        ids = sorted(ids)
        ix = {v: j for j, v in enumerate(ids)}
        prereq = [0] * len(ids)
        for a, b in edges:
            if a in ix:
                prereq[ix[b]] |= 1 << ix[a]
        dp = [0] * (1 << len(ids))
        dp[0] = 1
        for mask in range(len(dp)):
            for i in range(len(ids)):
                if not mask & (1 << i) and mask & prereq[i] == prereq[i]:
                    dp[mask | (1 << i)] += dp[mask]
        p = Fraction(dp[-1], factorial(len(ids)))
        probability *= p
        components.append((len(ids), str(p)))
    return probability, len(triples), len(edges), sorted(components)


def main(root):
    rng = Random(39117)
    native = [untemper(rng.getrandbits(32)) for _ in range(625)]
    assert native[624] == native[397] ^ twist(native[0], native[1])
    rng = Random(77325)
    for _ in range(10000):
        y = rng.getrandbits(32)
        assert temper(untemper(y)) == y

    rows = fixture(root)
    for label, corpus in (("all_132", rows), ("ordinary_128", rows[:128])):
        witnesses = links(corpus)
        assert len(witnesses) == (25 if label == "all_132" else 23)
        assert all(a < c and a < d for a, c, d in witnesses)
        p, triples, edge_count, groups = exact_order_probability(witnesses)
        expected = (Fraction(16, 2989355625) if label == "all_132"
                    else Fraction(8, 199290375))
        assert p == expected
        print(label, "links", len(witnesses), "triples", triples,
              "edges", edge_count, "components", groups,
              "exact_probability", str(p), "decimal", f"{float(p):.12g}")
    print("PASS: pinned source, selected row omitted, native MT controls, exact DAG calculation")


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
    main(root)
