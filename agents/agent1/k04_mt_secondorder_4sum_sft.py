"""H-17 K04 original-source second-order native MT19937 31-bit 4-sum SFT.

Run: python k04_mt_secondorder_4sum_sft.py h17-archive-dump.zip
The disputed ACK2 bytes, acceptance commitments, mask and verifier are never read.
All source-graph claims are conditional on a consecutive-four-output native MT writer.
"""
import hashlib
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

SPOOL_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
N = 133
MISSING = 129
MASK31 = 0xBFFFFFFF  # Eliminate unknown predecessor-MSB's bit30.
TWIST = 0x9908B0DF
# Reference producer stages for positive CONTROL ONLY. Not an original search input.
STAGES = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def untemper(y):
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


def low_mix(word):
    return ((word & 0x7FFFFFFF) >> 1) ^ (TWIST if word & 1 else 0)


def read_original(path):
    with ZipFile(path) as archive:
        raw = archive.read('evidence/print/spool-reconstruction.log')
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rows = [line for line in raw.decode().splitlines() if 'PAYLOAD=' in line]
    assert len(rows) == N
    assert 'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in rows[MISSING]
    words = []
    for row, line in enumerate(rows):
        if row == MISSING:
            continue  # Withhold entire disputed 18:02 source value before decoding.
        m = re.search(r'PAYLOAD=([0-9A-F]{32})', line)
        assert m is not None
        raw16 = bytes.fromhex(m.group(1))
        for lane in range(4):
            words.append((row, lane, untemper(int.from_bytes(raw16[4*lane:4*lane+4], 'little'))))
    assert len(words) == 528
    return words


def direct_triples(words):
    """Find original unindexed firstword-31bit triple relations, not a stage fit."""
    buckets = defaultdict(list)
    for row, lane, value in words:
        buckets[value].append((row, lane))
    triples = []
    for row, lane, first in words:
        first_mix = low_mix(first)
        for middle_row, middle_lane, middle in words:
            if middle_row <= row:
                continue
            for msb in (0, 1):
                for last_row, last_lane in buckets.get(middle ^ first_mix ^ (msb << 30), ()):
                    if last_row > middle_row:
                        triples.append(((row, lane), (middle_row, middle_lane), (last_row, last_lane), msb))
    return sorted(triples)


def secondorder_quads(words):
    """Find x[t-226],x[t+1],x[t+170],x[t+624] using 31bit 4-sum.

    Eliminate x[t+397] from two twists:
    x[t+624] xor x[t+170] = F(x[t],x[t+1]) xor F(x[t-227],x[t-226]).
    Unknown MSBs of x[t] and x[t-227] affect only bit30.
    Thus L(A) xor L(B) = C xor D with A,B,C,D at offsets 0,227,396,850.
    """
    inputs = defaultdict(list)
    for ai, (ar, al, av) in enumerate(words):
        for bi in range(ai + 1, len(words)):
            br, bl, bv = words[bi]
            if br > ar and br-ar <= 227//4:
                inputs[(low_mix(av) ^ low_mix(bv)) & MASK31].append((ai,bi))
    found = []
    for ci, (cr, cl, cv) in enumerate(words):
        for di in range(ci + 1, len(words)):
            dr, dl, dv = words[di]
            if dr <= cr or dr-cr > 454//4:
                continue
            for ai,bi in inputs.get((cv ^ dv) & MASK31, ()):
                ar,al,_ = words[ai]
                br,bl,_ = words[bi]
                if br >= cr or cr-br > 169//4 or cr-ar > 396//4:
                    continue
                found.append(((ar,al),(br,bl),(cr,cl),(dr,dl)))
    return sorted(found)


def grouped_quads(quads):
    groups = defaultdict(list)
    for item in quads:
        (row,lane) = item[0]
        offsets = tuple(distance + lane - other_lane for distance,(_,other_lane) in zip((227,396,850),item[1:]))
        groups[tuple(position for position,_ in item) + offsets].append(item)
    return groups


class WeightedUnion:
    def __init__(self):
        self.parent = list(range(N))
        self.offset = [0] * N

    def find(self, node):
        if self.parent[node] != node:
            parent,delta = self.find(self.parent[node])
            self.offset[node] += delta
            self.parent[node] = parent
        return self.parent[node],self.offset[node]

    def join(self, a, b, difference):
        ra,da = self.find(a)
        rb,db = self.find(b)
        if ra == rb:
            assert db - da == difference
        else:
            self.parent[rb] = ra
            self.offset[rb] = da + difference - db


def shortest(edges, source):
    infinite = float('inf')
    distance = [infinite] * N
    distance[source] = 0
    for _ in range(N-1):
        changed = False
        for a,b,w in edges:
            if distance[a] + w < distance[b]:
                distance[b] = distance[a] + w
                changed = True
        if not changed:
            break
    assert all(distance[a]+w >= distance[b] for a,b,w in edges), 'Contradictory chronology'
    return distance


def graph(triples, quads):
    uf = WeightedUnion()
    edges = []
    for a,b,c,_ in triples:
        for other,offset in ((b,396+a[1]-b[1]),(c,623+a[1]-c[1])):
            uf.join(a[0],other[0],offset)
            edges.extend(((a[0],other[0],offset),(other[0],a[0],-offset)))
    for quartet in quads:
        ar,al = quartet[0]
        for (br,bl),base in zip(quartet[1:],(227,396,850)):
            offset = base + al - bl
            uf.join(ar,br,offset)
            edges.extend(((ar,br,offset),(br,ar,-offset)))
    for row in range(N-1):
        edges.append((row+1,row,-4))
    minimum = -shortest(edges,MISSING)[0]
    maximum = shortest(edges,0)[MISSING]
    return (len({uf.find(r)[0] for r in range(N) if r!=MISSING}),int(minimum),int(maximum),uf)


def genuine_controls():
    assert len(STAGES) == N
    for seed, expected_total in ((0,14),(1,14),(0x12345678,13),(0xDEADBEEF,17)):
        gen = random.Random(seed)
        native = [untemper(gen.getrandbits(32)) for _ in range(STAGES[-1]+4)]
        test = [(r,l,native[STAGES[r]+l]) for r in range(N) if r!=MISSING for l in range(4)]
        observed = secondorder_quads(test)
        groups = grouped_quads(observed)
        trusted = [items[0] for items in groups.values() if len(items)>=2]
        assert (len(observed),len(groups),len(trusted),sum(len(v) for v in groups.values() if len(v)>=2)) == (expected_total,9 if seed in (0,1) else 8 if seed==0x12345678 else 12,4,9), (seed,len(observed),len(groups),len(trusted))
        for item in trusted:
            a = STAGES[item[0][0]] + item[0][1]
            expected = [227,396,850]
            assert [STAGES[r] + l - a for (r,l) in item[1:]] == expected
    for seed, expected in ((7,3),(8,1),(9,0)):
        gen = random.Random(seed)
        test = [(r,l,gen.getrandbits(32)) for r in range(N) if r!=MISSING for l in range(4)]
        result = grouped_quads(secondorder_quads(test))
        assert (sum(len(v) for v in result.values()),sum(len(v)>=2 for v in result.values()))==(expected,0)
    print('SEEDED_POSITIVE_CONTROLS=4 RANDOM_NEGATIVE_CONTROLS=3 PASS')


def main(path):
    source_words = read_original(path)
    triples = direct_triples(source_words)
    assert len(triples)==42
    raw_quads = secondorder_quads(source_words)
    groups = grouped_quads(raw_quads)
    strong = {k:v for k,v in groups.items() if len(v)>=2}
    assert (len(raw_quads),len(groups),len(strong),sum(len(v) for v in strong.values()))==(15,10,4,9)
    assert set(strong)=={(9,40,63,124,229,398,852),(10,41,64,125,227,397,850),(12,43,66,128,229,396,852),(13,44,67,131,227,395,851)}
    before = graph(triples,[])
    after = graph(triples,[v[0] for v in strong.values()])
    assert before[:3]==(83,917,971),before
    assert after[:3]==(80,917,971),after
    assert len({after[3].find(row)[0] for row in (9,40,63,124)}) == 1
    print('ORIGINAL_SPOOL_SHA256='+SPOOL_SHA)
    print('UNINDEXED_SECONDORDER_MATCHES',len(raw_quads),'RAW_GROUPS',len(groups))
    print('REINFORCED_GROUPS',len(strong),'REINFORCED_31BIT_WITNESSES',sum(len(v) for v in strong.values()))
    print('GRAPH_COMPONENTS_BEFORE_AFTER',before[0],after[0])
    print('SELECTED_START_RANGE_BEFORE_AFTER',before[1:3],after[1:3])
    genuine_controls()
    print('ORIGINAL_K04_AUTHENTICATED_BITS=0; K08_FINAL_WORDS=0; COMBINED_INCOMPLETE')


if __name__=='__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('h17-archive-dump.zip'))
