"""Complete genuine CPython five-word seed exclusion from repeated source key terms.

Run: python agents/agent23/k04_cpython_k2496_n5_repeat_sft.py
Original selected printer row129 is excluded from source fitting.
"""
from __future__ import annotations

from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent23"))
from k04_cpython_k2496_n3_worddomain_sft import (
    U,G,f,OFFSET,mt,words,original_packets,source_rows,word_domain,
)
G=list(G)
for i in range(len(G),10):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

def term4(s2:int,s3:int,s4:int)->int:
    a3=((s3+3)&U)^f(1566083941,s2)
    a4=((s4+4)&U)^f(1566083941,s3)
    return (a4-(G[4]^f(1664525,a3)))&U

def term9(s7:int,s8:int,s9:int)->int:
    a8=((s8+8)&U)^f(1566083941,s7)
    a9=((s9+9)&U)^f(1566083941,s8)
    return (a9-(G[9]^f(1664525,a8)))&U

def domains_from_rows(rows:list[tuple[int,int]])->dict[int,list[int]]:
    domains={i:word_domain(rows,i) for i in (2,3,4,7,8,9)}
    assert {i:len(v) for i,v in domains.items()}=={
        2:8,3:64,4:512,7:1,8:8,9:64}
    return domains

def repeat_join(domains:dict[int,list[int]])->tuple[int,int,set[int]]:
    """For n5, K4 and K9 both encode k3+3; test exact full domains."""
    left={term4(s2,s3,s4)
          for s2 in domains[2] for s3 in domains[3] for s4 in domains[4]}
    right={term9(domains[7][0],s8,s9)
           for s8 in domains[8] for s9 in domains[9]}
    assert len(left)<=262144 and len(right)==512
    return len(left),len(right),left&right

def seeded_controls(terms:list[list[int]])->None:
    keys_list=(
        (0x12345678,0x23456789,0x3456789A,0x456789AB,0x56789ABC),
        (1,1,1,1,1),(U,U,U,U,U),
        (8131,4242,54321,98989,0x1234),
        (0,0x80000000,0,0x7fffffff,0xf0f0f0f0)
    )
    for trial,keys in enumerate(keys_list):
        generator=random.Random(sum(key<<(32*i) for i,key in enumerate(keys)))
        state=generator.getstate()[1][:624]
        t4=term4(state[2],state[3],state[4])
        t9=term9(state[7],state[8],state[9])
        assert t4==t9==((keys[3]+3)&U),trial
        if trial==0:
            draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
            packets=[b"".join(draws[OFFSET+pos+j].to_bytes(4,"little")
                              for j in range(4)) for pos in mt.STARTS]
            domains=domains_from_rows(source_rows(packets,terms))
            assert all(state[index] in domains[index] for index in domains)
            left,right,matches=repeat_join(domains)
            assert ((keys[3]+3)&U) in matches
            print("GENUINE_CPYTHON_N5_FULL_SOURCE_DOMAIN_SELECTED_WITNESS=PASS")
    print("GENUINE_CPYTHON_N5_REAL_160BIT_KEYTERM_CONTROLS=5/5 PASS")

def original(terms:list[list[int]])->None:
    domains=domains_from_rows(source_rows(original_packets(),terms))
    assert domains[7]==[0x1F7B301F]
    left,right,matches=repeat_join(domains)
    assert (left,right,matches)==(262138,512,set()),(left,right,matches)
    print("ORIGINAL_K2496_N5_K4_DISTINCT=262138 K9_DISTINCT=512 "
          "REPEATED_K3_TERM_INTERSECTION=0")
    print("ORIGINAL_K2496_N5_ALL_160BIT_CPINT_SEEDS_EXCLUDED=PASS")
    print("K04_PHYSICAL_COUPON_UNRECOVERED K08_FINAL_CAPTION_UNRECOVERED")

if __name__=="__main__":
    terms=words(OFFSET)
    seeded_controls(terms)
    original(terms)
