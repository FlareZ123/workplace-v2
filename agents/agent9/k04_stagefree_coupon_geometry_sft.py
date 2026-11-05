"""Source-pinned K04 native-MT direct-donor test. Run with original ZIP as argv[1]."""
from collections import defaultdict
import hashlib
import random
import re
import sys
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
N = 133
SELECTED = 129
INF = 10**9

def untemper(y):
    x = y
    for _ in range(2): x = y ^ (x >> 18)
    z = x
    for _ in range(2): z = x ^ ((z << 15) & 0xEFC60000)
    x = z
    for _ in range(6): z = x ^ ((z << 7) & 0x9D2C5680)
    x = z
    for _ in range(4): z = x ^ (z >> 11)
    return z & 0xffffffff

def temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xffffffff

def mix(a, b):
    y = (a & 0x80000000) | (b & 0x7fffffff)
    return (y >> 1) ^ (0x9908b0df if y & 1 else 0)

def load(path):
    with ZipFile(path) as z:
        raw = z.read("evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == N
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[SELECTED]
    packets = {}
    for row, line in enumerate(lines):
        if row == SELECTED:
            continue
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match is not None
        buf = bytes.fromhex(match.group(1))
        packets[row] = [untemper(int.from_bytes(buf[4*j:4*j+4], "little")) for j in range(4)]
    assert len(packets) == N-1
    return packets

def relations(packets):
    flat = [(r,j,w) for r,p in packets.items() for j,w in enumerate(p)]
    words = defaultdict(list)
    for r,j,w in flat: words[w].append((r,j))
    found = []
    for r,j,first in flat:
        low = ((first & 0x7fffffff) >> 1) ^ (0x9908b0df if first & 1 else 0)
        for s,k,middle in flat:
            if s <= r: continue
            for bit in (0,1):
                for t,l in words.get(middle ^ low ^ (bit << 30), ()):
                    if t > s: found.append((r,j,s,k,t,l))
    assert len(found) == 42, len(found)
    return found

def graph(rel):
    d = [[INF]*N for _ in range(N)]
    for i in range(N): d[i][i] = 0
    for r,j,s,k,t,l in rel:
        for q,gap in ((s,396+j-k),(t,623+j-l)):
            d[r][q] = min(d[r][q],gap)
            d[q][r] = min(d[q][r],-gap)
    for r in range(N-1): d[r+1][r] = min(d[r+1][r],-4)
    for k in range(N):
        for i in range(N):
            first = d[i][k]
            if first == INF: continue
            for j in range(N):
                value = first + d[k][j]
                if value < d[i][j]: d[i][j] = value
    assert all(d[i][i] == 0 for i in range(N))
    assert (-d[SELECTED][0], d[0][SELECTED]) == (917,971)
    return d

def feasible(d,rows,offsets):
    return all(offsets[j]-offsets[i] <= d[rows[i]][rows[j]]
               for i in range(len(rows)) for j in range(len(rows)))

def positive():
    rng = random.Random(0x98513927)
    v = [untemper(rng.getrandbits(32)) for _ in range(628)]
    w = [v[397+i] ^ mix(v[i], v[i+1]) for i in range(4)]
    assert w == v[624:628]
    a = b"".join(temper(x).to_bytes(4,"little") for x in w)
    b = b"".join(temper(x).to_bytes(4,"little") for x in v[624:628])
    assert a == b and hashlib.sha256(bytes(x^y for x,y in zip(a,MASK))).digest() == hashlib.sha256(bytes(x^y for x,y in zip(b,MASK))).digest()

def main(path):
    positive()
    packets = load(path)
    rel = relations(packets)
    d = graph(rel)
    direct = 0
    feasible_direct = []
    for a in range(129):
        for b in range(a+1,129):
            for j in range(3):
                for k in range(4):
                    direct += 1
                    if feasible(d,(a,b,SELECTED),(0,397+j-k,624+j)):
                        feasible_direct.append((a,b,j,k))
    assert direct == 99072 and not feasible_direct, feasible_direct[:10]
    source_geometry = 0
    checked = 0
    hits = []
    for a in range(127):
        for b in range(a+2,129):
            if feasible(d,(a,a+1,b,SELECTED),(0,4,397,624)):
                source_geometry += 1
            v = packets[a] + [packets[a+1][0]]
            w = [packets[b][j] ^ mix(v[j],v[j+1]) for j in range(4)]
            for endian in ("little","big"):
                for reverse in (False,True):
                    raw = b"".join(temper(t).to_bytes(4,endian) for t in (w[::-1] if reverse else w))
                    component = bytes(x^y for x,y in zip(raw,MASK))
                    checked += 1
                    if hashlib.sha256(component).digest() == TARGET:
                        hits.append((a,b,endian,reverse,component.hex()))
    assert source_geometry == 0
    assert checked == 32512 and not hits, hits
    print("TRUE_MT_POSITIVE=PASS")
    print("SOURCE_31BIT_RELATIONS",len(rel))
    print("SELECTED_STAGE_BOUNDS",917,971)
    print("SINGLE_TWIST_DIRECT_PLACEMENTS",direct,"STAGE_FEASIBLE",len(feasible_direct))
    print("COMPLETE_THREEPACKET_GEOMETRIES",checked//4,"STAGE_FEASIBLE",source_geometry)
    print("ORIGINAL_K04_COMMITMENT_CHECKS",checked,"HITS",len(hits))

if __name__ == "__main__":
    main(sys.argv[1])
