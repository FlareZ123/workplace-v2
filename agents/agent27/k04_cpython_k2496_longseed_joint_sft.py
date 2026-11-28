#!/usr/bin/env python3
"""Exact K04 CPython seed-length exclusions at conditional p951 / output-offset2496.

Extends Agent23's n1..6 joint-affine necessary-term method with original source
triples S16..S18 and S27..S29. A seeded CPython MT first initialization pass
must repeat the same 32-bit key term at positions separated by the seed word
count. We enumerate every possible term in six complete source affine domains
and intersect pairs exactly; a disjoint pair excludes every divisor of the
index separation. Disputed row129, route mask, K04/K08 acceptance and PDF are
never read. Run locally, not in public CI. Only aggregate counts are printed.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent23"))
from k04_cpython_k2496_n1to6_joint_affine_sft import (
    joint_domain, f, OFFSET, mt, words, original_packets, source_rows,
)
U=0xffffffff
G=[19650218]
for i in range(1,624):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

IDS=(4,8,9,10,18,29)
EXPECTED_FREE={4:9,8:3,9:6,10:9,18:8,29:9}
NEW=(7,8,9,10,11,14,19,20,21,25)

def key_term(i:int, state3:tuple[int,int,int])->int:
    """Exact CPython first-pass key[(i-1)%n]+(i-1)%n term, i>=4."""
    s2,s1,s0=state3
    previous=((s1+i-1)&U)^f(1566083941,s2)
    current=((s0+i)&U)^f(1566083941,s1)
    return (current-(G[i]^f(1664525,previous)))&U

def domains(rows:list[tuple[int,int]]):
    out={}
    for i in IDS:
        tuples=joint_domain(rows,(i-2,i-1,i))
        assert len(tuples)==1<<EXPECTED_FREE[i],(i,len(tuples))
        values={key_term(i,s) for s in tuples}
        assert len(values)==len(tuples),(i,len(values))
        out[i]=values
    return out

def seed(n:int)->int:
    words=[(0x12345678+0x030158da*i)&U for i in range(n)]
    words[-1]|=0x80000000
    return sum(value<<(32*i) for i,value in enumerate(words))

def synthetic(terms):
    # True planted integer seeds, complete genuine CPython initialized-state
    # histories and 132-source-packet affine-domain controls. Selected 129
    # is withheld both from original and planted equations.
    for n in NEW:
        rng=random.Random(seed(n))
        initial=rng.getstate()[1][:624]
        raw=[rng.getrandbits(32) for _ in range(OFFSET+974)]
        packets=[b"".join(raw[OFFSET+p+j].to_bytes(4,"little") for j in range(4))
                 for p in mt.STARTS]
        rows=source_rows(packets,terms)
        allowed=domains(rows)
        for i in IDS:
            triple=tuple(initial[i-2:i+1])
            assert triple in joint_domain(rows,(i-2,i-1,i)),(n,i)
            assert key_term(i,triple) in allowed[i],(n,i)
        for j,a in enumerate(IDS):
            for b in IDS[j+1:]:
                if (b-a)%n==0:
                    assert allowed[a]&allowed[b],(n,a,b)
    return len(NEW)

def original(terms):
    allowed=domains(source_rows(original_packets(),terms))
    pair_counts={}
    excluded=set()
    for j,a in enumerate(IDS):
        for b in IDS[j+1:]:
            overlap=len(allowed[a]&allowed[b])
            pair_counts[f"{a}:{b}"]=overlap
            if not overlap:
                excluded.update(n for n in range(1,b-a+1) if (b-a)%n==0)
    assert all(v==0 for v in pair_counts.values())
    expected={1,2,3,4,5,6,*NEW}
    assert excluded==expected,(sorted(excluded),sorted(expected))
    print({"source_model":"conditional_native_MT_offset2496_p951",
           "source_selected_row129_withheld":True,
           "source_joint_affine_domains":{i:len(allowed[i]) for i in IDS},
           "term_pair_intersections":pair_counts,
           "newly_excluded_key_word_lengths":list(NEW),
           "all_excluded_key_word_lengths":sorted(excluded),
           "planted_full_source_seed_controls":"10/10 PASS",
           "selected_coupon_recovered":False})

def main():
    terms=words(OFFSET)
    assert synthetic(terms)==10
    original(terms)

if __name__=="__main__":
    main()
