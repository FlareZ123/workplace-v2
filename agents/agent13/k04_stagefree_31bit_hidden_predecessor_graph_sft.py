"""Read-only H-17 source-only 31-bit MT19937 hidden-predecessor recurrence SFT.

Run: python k04_stagefree_31bit_hidden_predecessor_graph_sft.py h17-archive-dump.zip
The selected copied ACK bytes, K04 mask, acceptance digest and verifier are never read.
"""
import hashlib
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
N = 133
MISSING = 129
INF = float("inf")


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


def source(path):
    with ZipFile(path) as archive:
        raw = archive.read("evidence/print/spool-reconstruction.log")
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode().splitlines() if "PAYLOAD=" in line]
    assert len(lines) == N
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[MISSING]
    output = []
    for row, line in enumerate(lines):
        if row == MISSING:
            continue  # Explicitly bypass reading the disputed selected copy.
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match is not None
        packet = bytes.fromhex(match.group(1))
        for j in range(4):
            output.append((row, j, untemper(int.from_bytes(packet[4*j:4*j+4], "little"))))
    assert len(output) == 528
    return output


def discover(flat):
    """Find x[t+1],x[t+397],x[t+624] with x[t] MSB unknown.

    x[t+624] = x[t+397] xor ((x[t]&0x80000000 |
    x[t+1]&0x7fffffff)>>1) xor ((x[t+1]&1)*0x9908b0df).
    Only one unknown predecessor bit affects the result (bit 30).
    """
    byword = defaultdict(list)
    for index, (_, _, word) in enumerate(flat):
        byword[word].append(index)
    relations = []
    for row, j, first in flat:
        low_mix = ((first & 0x7fffffff) >> 1) ^ (0x9908b0df if first & 1 else 0)
        for middle_row, k, middle in flat:
            if middle_row <= row:
                continue
            for predecessor_msb in (0, 1):
                predicted = middle ^ low_mix ^ (predecessor_msb << 30)
                for at in byword.get(predicted, ()):
                    final_row, l, _ = flat[at]
                    if final_row > middle_row:
                        relations.append((row,j,middle_row,k,final_row,l,predecessor_msb))
    return sorted(relations)


class WeightedUnion:
    def __init__(self):
        self.parent = list(range(N))
        self.offset = [0]*N
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
            assert db - da == delta
        else:
            self.parent[rb] = ra
            self.offset[rb] = da + delta - db


def shortest(edges, origin):
    distance = [INF]*N
    distance[origin] = 0
    for _ in range(N-1):
        changed = False
        for a, b, weight in edges:
            if distance[a] + weight < distance[b]:
                distance[b] = distance[a] + weight
                changed = True
        if not changed:
            break
    assert all(distance[a]+weight >= distance[b] for a,b,weight in edges)
    return distance


def stagegraph(relations):
    uf = WeightedUnion()
    edges = []
    for row, j, srow, k, drow, l, msb in relations:
        for other, gap in ((srow,396+j-k), (drow,623+j-l)):
            uf.join(row,other,gap)
            edges.extend(((row,other,gap),(other,row,-gap)))
    for r in range(N-1):
        edges.append((r+1,r,-4))
    lo = -shortest(edges,MISSING)[0]
    hi = shortest(edges,0)[MISSING]
    components = len({uf.find(i)[0] for i in range(N) if i != MISSING})
    return uf,components,int(lo),int(hi)


# Existing conditional p951 indices used ONLY for real-seeded synthetic controls.
# Source-only relation discovery, source graph and original candidate decisions
# do not use this vector.
STAGES = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def calibrate():
    assert len(STAGES) == N
    for seed in (0,1,0x12345678,0xDEADBEEF):
        generator = random.Random(seed)
        states = [untemper(generator.getrandbits(32)) for _ in range(STAGES[-1]+4)]
        flat = [(r,j,states[STAGES[r]+j]) for r in range(N) if r != MISSING for j in range(4)]
        relations = discover(flat)
        assert len(relations) == 42, (seed,len(relations))
        for r,j,s,k,t,l,msb in relations:
            assert STAGES[s]+k-STAGES[r]-j == 396
            assert STAGES[t]+l-STAGES[r]-j == 623
            assert msb == states[STAGES[r]+j-1] >> 31
    random_source = random.Random(111037)
    noise = [(r,j,random_source.getrandbits(32)) for r in range(N) if r!=MISSING for j in range(4)]
    assert not discover(noise)


def main(path):
    relations = discover(source(path))
    original_fullword = [rel for rel in relations if rel[1] != 0]
    new_firstword = [rel for rel in relations if rel[1] == 0]
    assert (len(relations),len(original_fullword),len(new_firstword)) == (42,25,17)
    old_uf,old_c,old_lo,old_hi = stagegraph(original_fullword)
    new_uf,new_c,new_lo,new_hi = stagegraph(relations)
    assert (old_c,new_c,old_lo,old_hi,new_lo,new_hi)==(96,83,916,971,917,971)
    assert new_uf.find(128)[0] == new_uf.find(43)[0]
    assert new_uf.find(130)[0] == new_uf.find(44)[0]
    assert new_uf.find(128)[0] != new_uf.find(130)[0]
    calibrate()
    print("SOURCE_SHA256", SPOOL_SHA)
    print("STAGEFREE_31BIT_TRIPLES",len(relations),
          "PRIOR_INTERNAL_FULL32",len(original_fullword),"NEW_FIRSTWORD",len(new_firstword))
    print("SOURCE_COMPONENTS_BEFORE_AFTER",old_c,new_c)
    print("NEW_SOURCE_NEIGHBOR_BRIDGES","43->96->128; 44->97->130")
    print("SELECTED_START_BOUNDS_BEFORE_AFTER",(old_lo,old_hi),(new_lo,new_hi))
    print("FOUR_TRUE_GENERATOR_CONTROLS_PASS","UNRELATED_WORD_CONTROL_PASS")
    print("ORIGINAL_K04_PHYSICAL_BITS_RECOVERED",0)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("h17-archive-dump.zip"))
