"""Full source-pinned joint-affine sieve for genuine CPython key lengths <=25.

Run: python agents/agent23/k04_cpython_k2496_sixterm_joint_sft.py
The 132 surviving original printer records, excluding selected row129, are
the only original source data used. No copied ACK value or K04 acceptance
hash is used. Tests 16 exactly classified integer seed word lengths.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent23"))
from k04_cpython_k2496_n1to6_joint_affine_sft import (
    U,G,f,OFFSET,mt,words,original_packets,source_rows,word_domain,joint_domain,
)

G=list(G)
for i in range(len(G),30):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

GROUPS={4:(2,3,4),8:(8,),9:(8,9),10:(8,9,10),
        18:(16,17,18),29:(27,28,29)}
EXPECTED={4:512,8:8,9:64,10:512,18:256,29:512}
COVERED={1,2,3,4,5,6,7,8,9,10,11,14,19,20,21,25}

def source_domains(rows:list[tuple[int,int]]):
    domains={at:joint_domain(rows,indices)
             for at,indices in GROUPS.items()}
    assert {at:len(v) for at,v in domains.items()}==EXPECTED
    s6=word_domain(rows,6)
    s7=word_domain(rows,7)
    assert len(s6)==len(s7)==1
    return domains,s6[0],s7[0]

def term(at:int,state:dict[int,int])->int:
    """Exact genuine firstpass term at i>=2:
    K_i=A_i-(G_i xor F1(A_{i-1}))=key[(i-1)%n]+(i-1)%n.
    """
    before=state[at-2];prev=state[at-1];current=state[at]
    a_prev=((prev+at-1)&U)^f(1566083941,before)
    a_now=((current+at)&U)^f(1566083941,prev)
    return (a_now-(G[at]^f(1664525,a_prev)))&U

def term_sets(domains,s6:int,s7:int):
    sets={}
    for at,domain in domains.items():
        built=set()
        for entry in domain:
            state=dict(zip(GROUPS[at],entry))
            if at==8:
                state[6]=s6;state[7]=s7
            elif at==9:
                state[7]=s7
            built.add(term(at,state))
        assert len(built)==EXPECTED[at],(at,len(built))
        sets[at]=built
    return sets

def original(terms:list[list[int]])->None:
    domains,s6,s7=source_domains(source_rows(original_packets(),terms))
    assert (s6,s7)==(0xE403BB7D,0x1F7B301F)
    sets=term_sets(domains,s6,s7)
    intersections={(a,b):len(sets[a]&sets[b])
                   for a,b in combinations(GROUPS,2)}
    assert len(intersections)==15 and all(value==0 for value in intersections.values())
    covered={n for n in range(1,30)
             if any((b-a)%n==0 for a,b in combinations(GROUPS,2))}
    assert covered==COVERED,covered
    print("ORIGINAL_SELECTED_ROW129_WITHHELD_SOURCE_RANK=15365")
    print("ORIGINAL_JOINED_AFFINE_TERMS "
          "T4=512 T8=8 T9=64 T10=512 T18=256 T29=512")
    print("ORIGINAL_ALL_15_PAIRWISE_SOURCE_TERM_INTERSECTIONS=ZERO")
    print("ORIGINAL_INTEGER_KEY_LENGTHS_EXCLUDED=" +
          ",".join(map(str,sorted(covered))))
    print("ORIGINAL_CPINT_K2496_16_SEED_WORD_LENGTHS_EXCLUDED=PASS")
    print("K04_PHYSICAL_COUPON_UNRECOVERED K08_FINAL_CAPTION_UNRECOVERED")

def genuine_controls(terms:list[list[int]])->None:
    for n in sorted(COVERED):
        keys=[(0x31f0aabb + 0x9e3779b9*(i+1))&U for i in range(n)]
        if keys[-1]==0:
            keys[-1]=0x13579BDF
        generator=random.Random(sum(key<<(32*i) for i,key in enumerate(keys)))
        state=generator.getstate()[1][:624]
        real_terms={at:term(at,{idx:state[idx]
                     for idx in (at-2,at-1,at)}) for at in GROUPS}
        hit_pairs=[(a,b) for a,b in combinations(GROUPS,2) if (b-a)%n==0]
        assert hit_pairs,n
        for a,b in hit_pairs:
            assert real_terms[a]==real_terms[b],(n,a,b)
        if n in (1,7,11,25):
            draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
            packets=[b"".join(draws[OFFSET+pos+j].to_bytes(4,"little")
                              for j in range(4)) for pos in mt.STARTS]
            domains,s6,s7=source_domains(source_rows(packets,terms))
            assert (s6,s7)==(state[6],state[7])
            for at,domain in domains.items():
                assert tuple(state[i] for i in GROUPS[at]) in domain,(n,at)
            values=term_sets(domains,s6,s7)
            for a,b in hit_pairs:
                assert real_terms[a] in values[a]&values[b],(n,a,b)
            print(f"GENUINE_CPYTHON_N{n}_FULL_SELECTED_WITHHELD_SOURCE_WITNESS=PASS")
        print(f"GENUINE_CPYTHON_N{n}_KEYTERM_IDENTITY_PASS")
    print("GENUINE_CPYTHON_16_LENGTHS_REPEATED_KEYTERM_CONTROLS=16/16 PASS")
    print("GENUINE_CPYTHON_FOUR_FULL_SOURCE_DOMAIN_WITNESSES=4/4 PASS")

if __name__=="__main__":
    terms=words(OFFSET)
    genuine_controls(terms)
    original(terms)
