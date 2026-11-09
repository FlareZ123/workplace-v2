"""H17 original printer, source-only 42-link unindexed MT stage graph and bounded-gap test.

No selected row129 payload, K04 acceptance/mask or K08 source is parsed.
Run with Python standard library from a repository checkout.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import re

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"resources/evidence/print/spool-reconstruction.log"
SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MAG=0x9908B0DF

def untemper(x: int) -> int:
    x ^= x >> 18
    x ^= (x << 15) & 0xEFC60000
    previous=x
    for _ in range(6):
        x = previous ^ ((x << 7) & 0x9D2C5680)
    previous=x
    for _ in range(6):
        x = previous ^ (x >> 11)
    return x & 0xFFFFFFFF

def twist(predecessor: int, follower: int) -> int:
    y=(predecessor & 0x80000000)|(follower & 0x7FFFFFFF)
    return (y >> 1)^(MAG if follower & 1 else 0)

def relations(raw: bytes) -> set[tuple[int,int,int]]:
    lines=[line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines)==133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    native=[];positions=[]
    for i,line in enumerate(lines):
        if i == 129:
            continue
        m=re.search(r"PAYLOAD=([0-9A-F]{32})",line)
        assert m is not None
        packet=bytes.fromhex(m[1])
        for j in range(4):
            native.append(untemper(int.from_bytes(packet[4*j:4*j+4],"little")))
            positions.append((i,j))
    assert len(native)==528
    lookup=defaultdict(list)
    for a in range(528):
        for b in range(a+1,528):
            lookup[native[a]^native[b]].append((a,b))
    observed=set();edges=set()
    for i,b in enumerate(native):
        for msb in (0,1):
            for k,l in lookup.get(twist(msb<<31,b),()):
                if i>=k:
                    continue
                ri,j=positions[i]
                rk,a=positions[k]
                rl,c=positions[l]
                observed.add((ri,j,rk,a,rl,c))
                edges.add((ri,rk,396+j-a))
                edges.add((ri,rl,623+j-c))
    assert len(observed)==42 and len(edges)==49
    return edges

def bounds(edges: set[tuple[int,int,int]], max_gap: int):
    count=133
    inf=10**10
    d=[[inf]*count for _ in range(count)]
    for i in range(count):
        d[i][i]=0
    for r,k,delta in edges:
        d[r][k]=min(d[r][k],delta)
        d[k][r]=min(d[k][r],-delta)
    for i in range(count-1):
        d[i+1][i]=min(d[i+1][i],-4)
        d[i][i+1]=min(d[i][i+1],max_gap)
    for mid in range(count):
        via=d[mid]
        for a in range(count):
            preceding=d[a][mid]
            if preceding==inf:
                continue
            row=d[a]
            for b in range(count):
                new=preceding+via[b]
                if new<row[b]:
                    row[b]=new
    if any(d[i][i]<0 for i in range(count)):
        return None
    return d

def span(d: list[list[int]], a: int, b: int) -> tuple[int,int]:
    return -d[b][a],d[a][b]

def run() -> None:
    raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA
    graph=relations(raw)
    # Minimal four-relation certificate, independent of any upper start gap.
    adjacency=defaultdict(list)
    for a,b,shift in graph:
        adjacency[a].append((b,shift))
        adjacency[b].append((a,-shift))
    def exact_offset(source: int, destination: int) -> int:
        queue=[(source,0)]
        visited={source}
        for node,shift in queue:
            if node==destination:
                return shift
            for nxt,delta in adjacency[node]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt,shift+delta))
        raise AssertionError("source nodes disconnected")
    assert [(a,b,exact_offset(a,b)) for a,b in
            ((43,128),(44,130),(96,128),(97,130))] == [
            (43,128,623),(44,130,620),(96,128,230),(97,130,226)]
    assert all(bounds(graph,D) is None for D in range(4,13))
    for ceiling in (13,14,17,1000):
        d=bounds(graph,ceiling)
        assert d is not None
        neighbors=[span(d,i,i+1) for i in (128,129,130)]
        target=span(d,0,129)
        near=[(i,span(d,i,129)) for i in (43,44,96,97)]
        prior_a=[i for i in range(129) if span(d,i,129)[0]<=623<=span(d,i,129)[1]]
        prior_b=[i for i in range(129) if span(d,i,129)[0]<=227<=span(d,i,129)[1]]
        assert not prior_a and not prior_b
        if ceiling==13:
            assert neighbors==[(4,4)]*3
            assert near==[(43,(627,627)),(44,(616,616)),(96,(234,234)),(97,(222,222))]
        if ceiling==17:
            assert neighbors==[(4,8),(4,8),(4,4)]
            assert near==[(43,(627,631)),(44,(612,616)),(96,(234,238)),(97,(218,222))]
        if ceiling==1000:
            # Effective no finite maximum: original 42 links and min-4 chronology
            # already force both target-causal donor windows into printed gaps.
            assert neighbors==[(4,58),(4,58),(4,4)]
            assert near==[(43,(627,681)),(44,(562,616)),(96,(234,288)),(97,(168,222))]
            assert near[0][1][0]-623>=4 and near[1][1][1]-620<0
            assert near[2][1][0]-227>=4 and near[3][1][1]-224<0
        assert target==(917,971)
        print("GAP_CEILING",ceiling,"TARGET_STAGE",target,
              "LATE_GAPS",neighbors,"ANTECEDENT_NEIGHBORS",near,
              "FULL_ANTECEDENT_PACKET_SETS",(len(prior_a),len(prior_b)))
    print("ORIGINAL_SOURCE_LINKS 42; INDEPENDENT_STAGE_DIFFERENCES 49")

if __name__=="__main__":
    run()
