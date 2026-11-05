"""K04 stage-free MT19937 integer-offset graph and blind packet recovery SFT.

Source only: the disputed row129 buffer and p951 STARTS are never loaded.
Fits exact native MT twist relations to unknown packet-start differences.
"""
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
raw = SPOOL.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
for line in raw.decode().splitlines():
    m = re.search(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})", line)
    if m:
        rows.append((m[1], int(m[2]), m[3], m[4], bytes.fromhex(m[5])))
assert len(rows) == 133 and rows[129][:4] == ("PS-261003-0417", 2, "ACK", "RECOVER")
U32 = (1 << 32) - 1

def untemper(v):
    v ^= v >> 18
    v ^= (v << 15) & 0xefc60000
    x = v
    for _ in range(5):
        v = x ^ ((v << 7) & 0x9d2c5680)
    x = v
    for _ in range(3):
        v = x ^ (v >> 11)
    return v & U32

def temper(v):
    v ^= v >> 11
    v ^= (v << 7) & 0x9d2c5680
    v ^= (v << 15) & 0xefc60000
    v ^= v >> 18
    return v & U32

def mix(a, b):
    y = (a & 0x80000000) | (b & 0x7fffffff)
    return (y >> 1) ^ (0x9908b0df if y & 1 else 0)

def discover(packets):
    native = []
    positions = []
    for row, packet in packets:
        for lane in range(4):
            native.append(untemper(int.from_bytes(packet[4 * lane:4 * lane + 4], "little")))
            positions.append((row, lane))
    table = defaultdict(list)
    for k in range(len(native)):
        for l in range(k + 32, min(len(native), k + 251)):
            table[native[k] ^ native[l]].append((k, l))
    result = []
    for i in range(len(native)):
        if i % 4 == 3:
            continue
        for k, l in table.get(mix(native[i], native[i + 1]), []):
            if i + 1 < k:
                result.append((positions[i], positions[i + 1], positions[k], positions[l]))
    return result, dict(zip(positions, native))

class Displacement:
    def __init__(self, nodes):
        self.parent = {i:i for i in nodes}
        self.offset = {i:0 for i in nodes}

    def find(self, node):
        parent = self.parent[node]
        if parent != node:
            root, shift = self.find(parent)
            self.parent[node] = root
            self.offset[node] += shift
        return self.parent[node], self.offset[node]

    def join(self, a, b, difference):
        # S[b] - S[a] = difference.
        ra, da = self.find(a)
        rb, db = self.find(b)
        if ra == rb:
            assert db - da == difference
        else:
            self.parent[rb] = ra
            self.offset[rb] = difference + da - db

def stage_graph(ids, relations, total):
    ds = Displacement(ids)
    for (ri, i), (rj, j), (rk, k), (rl, l) in relations:
        assert ri == rj and j == i + 1
        ds.join(ri, rk, 397 + i - k)
        ds.join(ri, rl, 624 + i - l)
    connected = defaultdict(list)
    for row in ids:
        root, shift = ds.find(row)
        connected[root].append((row, shift))
    # Entire chronological 133-row (or synthetic 256-row) sequence contributes
    # S[r+1]-S[r]>=4, including placeholders for unobserved complete packets.
    for row in range(total):
        if row not in ds.parent:
            ds.parent[row] = row
            ds.offset[row] = 0
    edges = []
    for row in range(total - 1):
        ra, a = ds.find(row)
        rb, b = ds.find(row + 1)
        weight = 4 + a - b
        if ra == rb:
            assert weight <= 0, ("order contradiction", row)
        else:
            edges.append((ra, rb, weight))
    return ds, connected, edges

def longest(roots, edges, origin):
    # Exact Bellman-Ford longest paths for constraints T[v]>=T[u]+weight.
    distance = {root:None for root in roots}
    distance[origin] = 0
    for _ in range(len(roots)):
        progressed = False
        for u, v, weight in edges:
            if distance[u] is None:
                continue
            candidate = distance[u] + weight
            if distance[v] is None or candidate > distance[v]:
                distance[v] = candidate
                progressed = True
        if not progressed:
            return distance
    raise AssertionError("positive chronology cycle")

def bounds(ds, edges, row1, row2, total):
    roots = {ds.find(r)[0] for r in range(total)}
    ra, a = ds.find(row1)
    rb, b = ds.find(row2)
    fwd = longest(roots, edges, ra)[rb]
    backward = longest(roots, edges, rb)[ra]
    return (None if fwd is None else fwd + b - a,
            None if backward is None else -backward + b - a)

def reconstruct(ds, edges, observed_values, missing, total):
    roots = {ds.find(r)[0] for r in range(total)}
    paths = {root:longest(roots, edges, root) for root in roots}
    rm, om = ds.find(missing)
    fixed = {}
    for (row, lane), value in observed_values.items():
        rr, off = ds.find(row)
        fwd = paths[rm][rr]
        back = paths[rr][rm]
        if fwd is not None and back is not None:
            minimum = fwd + off - om
            maximum = -back + off - om
            if minimum == maximum:
                position = minimum + lane
                if position in fixed:
                    assert fixed[position] == value
                fixed[position] = value
    prediction = []
    for lane in range(4):
        a, b, c = (fixed.get(lane - 624), fixed.get(lane - 623),
                   fixed.get(lane - 227))
        prediction.append(None if any(x is None for x in (a, b, c)) else c ^ mix(a, b))
    return fixed, prediction

original = [(i, packet[4]) for i, packet in enumerate(rows) if i != 129]
relations, values = discover(original)
assert len(relations) == 25
ds, parts, edges = stage_graph([i for i, _ in original], relations, 133)
sizes = sorted((len(x) for x in parts.values()), reverse=True)
assert len(parts) == 96 and sizes[:14] == [5] * 4 + [3] * 10
assert sum(len(x) for x in parts.values() if len(x) > 1) == 50
first = bounds(ds, edges, 128, 129, 133)
second = bounds(ds, edges, 129, 130, 133)
fixed, prediction = reconstruct(ds, edges, values, 129, 133)
assert first == (4, 59) and second == (4, 59)
assert len(fixed) == 0 and all(x is None for x in prediction)
print("ORIGINAL_SOURCE_GRAPH", json.dumps({
    "twist_links":len(relations), "components":len(parts),
    "non_singletons":14, "packets_in_non_singletons":50,
    "selected_delta_from_prior":first, "next_delta_from_selected":second,
    "native_words_fixed_relative_to_selected":len(fixed),
    "selected_complete_words_predicted":0}, sort_keys=True))

# Blind refits on ten distinct whole source packets: do not read withheld
# bytes until after all constraints and stage-conditioned predictions exist.
held = []
for missing in (10, 21, 34, 53, 73, 83, 101, 117, 128, 130):
    intact = [(i, packet) for i, packet in original if i != missing]
    link, observed = discover(intact)
    gd, groups, ce = stage_graph([i for i, _ in intact], link, 133)
    prev = max(i for i, _ in intact if i < missing)
    nxt = min(i for i, _ in intact if i > missing)
    earlier = bounds(gd, ce, prev, missing, 133)
    later = bounds(gd, ce, missing, nxt, 133)
    located, predicted = reconstruct(gd, ce, observed, missing, 133)
    correct = sum(temper(p) == int.from_bytes(rows[missing][4][4*j:4*j+4], "little")
                  for j, p in enumerate(predicted) if p is not None)
    count = sum(p is not None for p in predicted)
    assert count == correct == 0
    assert earlier[0] != earlier[1]
    held.append((missing, len(link), earlier, later, count))
assert len(held) == 10
print("BLIND_HOLDOUTS", json.dumps(held))

# Genuine positive: remove whole packet 200 from a different seeded MT stream,
# discover all graph relations afresh, and recover each withheld native word
# from its three *independently observed* temporal predecessors.
generator = random.Random(90210)
stream = [generator.getrandbits(32) for _ in range(1024)]
synthetic = [(i, b"".join(stream[4*i+j].to_bytes(4,"little") for j in range(4)))
             for i in range(256) if i != 200]
synlinks, observed = discover(synthetic)
gd, groups, ce = stage_graph([i for i, _ in synthetic], synlinks, 256)
assert bounds(gd, ce, 199, 200, 256) == (4, 4)
assert bounds(gd, ce, 200, 201, 256) == (4, 4)
located, pred = reconstruct(gd, ce, observed, 200, 256)
assert len(synlinks) == 297 and len(located) == 1020
assert all(p is not None and temper(p) == stream[800+j] for j,p in enumerate(pred))
print("GENUINE_HIDDEN_PACKET_POSITIVE", len(synlinks), len(located), "4/4")

# Control: shuffle temporal order without altering any of the surviving
# original 16byte packets. Unindexed equations need not vanish completely.
rng = random.Random(20261105)
shuffles = []
for _ in range(32):
    shuffled = original.copy()
    rng.shuffle(shuffled)
    sl, _ = discover(shuffled)
    feasible = True
    try:
        sd, groups, ce = stage_graph([i for i,_ in original], sl, 133)
        roots = {sd.find(r)[0] for r in range(133)}
        dist = {r:0 for r in roots}
        for _ in range(len(roots)):
            change = False
            for a,b,w in ce:
                if dist[b] < dist[a] + w:
                    dist[b] = dist[a] + w
                    change = True
            if not change:
                break
        assert not change
    except AssertionError:
        feasible = False
    shuffles.append((len(sl),feasible))
assert len(shuffles) == 32
assert min(x[0] for x in shuffles) == 1 and max(x[0] for x in shuffles) == 11
assert sum(x[1] for x in shuffles) == 5
print("CHRONOLOGY_SHUFFLE",{
    "runs":32, "link_min":1, "link_max":11,
    "mean_links":sum(x[0] for x in shuffles)/32,
    "feasible_graphs":sum(x[1] for x in shuffles)})
print("ORIGINAL_K04_STATUS", "ZERO AUTHENTIC SELECTED COUPON BITS; NO REC8 RECOVERY")
