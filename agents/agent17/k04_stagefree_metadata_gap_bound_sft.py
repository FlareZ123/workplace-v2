"""H-17 printer MT: stage-free two-choice metadata-draw bound.

Original selected ACK2 row129 is withheld before interpreting PAYLOAD.
This test does not use the K04 mask, commitment or any chosen p951 stage.
"""
from __future__ import annotations

import hashlib
import itertools
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def untemper(y: int) -> int:
    x = y
    for typ, n, mask, count in (
        ("r", 18, 0, 2), ("l", 15, 0xEFC60000, 2),
        ("l", 7, 0x9D2C5680, 6), ("r", 11, 0, 4),
    ):
        z = x
        for _ in range(count):
            z = x ^ ((z >> n) if typ == "r" else ((z << n) & mask))
        x = z & 0xffffffff
    return x


def mix(a: int, b: int) -> int:
    return ((((a & 0x80000000) | (b & 0x7fffffff)) >> 1)
            ^ (0x9908b0df if b & 1 else 0))


def original(path: Path):
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as z:
            raw = z.read("evidence/print/spool-reconstruction.log")
    else:
        raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    lines = [s for s in raw.decode("ascii").splitlines() if "PAYLOAD=" in s]
    assert len(lines) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    out = []
    for row, line in enumerate(lines):
        if row == 129:
            continue
        packet = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        out.append((row, [untemper(int.from_bytes(packet[i:i+4], "little"))
                          for i in range(0, 16, 4)]))
    return out


def discover(rows):
    flat = [(r, j, v) for r, words in rows for j, v in enumerate(words)]
    lookup = defaultdict(list)
    for k, (_, _, value) in enumerate(flat):
        for l in range(k + 1, len(flat)):
            lookup[value ^ flat[l][2]].append((k, l))
    found = []
    for base in range(0, len(flat), 4):
        for j in range(base + 1, base + 4):
            for k, l in lookup.get(mix(flat[j-1][2], flat[j][2]), ()):
                if k > j and flat[k][0] > flat[j][0] and flat[l][0] > flat[k][0]:
                    found.append((j-1, j, k, l))
    return flat, found


def edges(flat, found, minimum, maximum=None):
    # s[v] <= s[u] + weight.
    graph = []
    for i, _, k, l in found:
        r, offset, _ = flat[i]
        for target, lag in ((k, 397), (l, 624)):
            other, pos, _ = flat[target]
            weight = lag + offset - pos
            graph.extend(((r, other, weight), (other, r, -weight)))
    for row in range(132):
        graph.append((row+1, row, -(4 + (minimum if row < 127 else 0))))
        if maximum is not None and row < 127:
            graph.append((row, row+1, 4 + maximum))
    return graph


def contradictory(graph):
    dist = [0] * 133
    for _ in range(133):
        changed = False
        for u, v, w in graph:
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            return False
    return True


def min_row127(graph):
    d = [float("inf")] * 133
    d[127] = 0
    for _ in range(132):
        changed = False
        for u, v, w in graph:
            if d[v] > d[u] + w:
                d[v] = d[u] + w
                changed = True
        if not changed:
            break
    assert all(d[v] <= d[u] + w for u, v, w in graph)
    return -d[0]


def tail(n: int, minimum: int):
    # Sum of n i.i.d. Geometric(p=3/4), total-draw upper tail.
    failures = minimum-n
    p, q = 0.75, 0.25
    term = math.exp(math.lgamma(n+failures)-math.lgamma(n)
                    -math.lgamma(failures+1) + n*math.log(p)
                    + failures*math.log(q))
    total = 0.0
    for f in range(failures, failures+1000):
        total += term
        term *= (n+f) * q / (f+1)
        if term < total*1e-16:
            break
    return total


def positive_control():
    rng = random.Random(20261117)
    rows, starts = [], []
    clock = 0
    for row in range(133):
        starts.append(clock)
        rows.append((row, [untemper(rng.getrandbits(32)) for _ in range(4)]))
        clock += 4
        if row < 127:
            for _ in range(3):
                rng.getrandbits(32)
                clock += 1
    flat, found = discover([r for r in rows if r[0] != 129])
    assert len(found) >= 4
    for i, _, k, l in found:
        a, ai, _ = flat[i]
        b, bk, _ = flat[k]
        c, cl, _ = flat[l]
        assert starts[b]-starts[a] == 397+ai-bk
        assert starts[c]-starts[a] == 624+ai-cl
    assert not contradictory(edges(flat, found, 3))
    return len(found)


def main(path: Path):
    positive = positive_control()
    flat, relations = discover(original(path))
    assert len(relations) == 25
    graph = edges(flat, relations, 2)
    assert not contradictory(graph)
    assert min_row127(edges(flat, relations, 0)) == 908
    assert min_row127(graph) == 936
    assert contradictory(edges(flat, relations, 3))
    assert contradictory(edges(flat, relations, 2, 5))

    one_min, two_min = 10000, 10000
    for cut in range(25):
        kept = [relation for i, relation in enumerate(relations) if i != cut]
        one_min = min(one_min, min_row127(edges(flat, kept, 2))-508)
        assert contradictory(edges(flat, kept, 3))
    for cut1, cut2 in itertools.combinations(range(25), 2):
        kept = [r for i, r in enumerate(relations) if i not in (cut1, cut2)]
        two_min = min(two_min, min_row127(edges(flat, kept, 2))-508)
        assert contradictory(edges(flat, kept, 3))
    assert one_min == 425 and two_min == 417
    probability = tail(254, 428)
    assert 7e-13 < probability < 8e-13
    print({
        "exact_source_MT_relations": 25,
        "synthetic_MT_three_draws_per_gap_relations": positive,
        "ordinary_gaps": 127,
        "minimum_hidden_draws": 428,
        "minimum_native_start_at_last_ordinary_job": 936,
        "three_hidden_draws_per_gap_feasible": False,
        "all_gaps_at_most_five_hidden_draws_feasible": False,
        "leave_one_out_minimum_hidden": one_min,
        "leave_two_out_minimum_hidden": two_min,
        "two_threeway_CP_RANDOM_issuer_tail_probability": probability,
        "authenticated_K04_coupon_bits_recovered": 0,
    })


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path("resources/evidence/print/spool-reconstruction.log"))
