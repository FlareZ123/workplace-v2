"""Exact n=6 CPython 192-bit source-word-domain inverse at genuine k2496.

Run: python agents/agent23/k04_cpython_k2496_n6_wordjoin_sft.py
The 132 original retained printer packets provide all source constraints;
the copied selected row129 is excluded from all source fitting.
"""
from __future__ import annotations

from pathlib import Path
import random
import sys
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent23"))
from k04_cpython_k2496_n3_worddomain_sft import (
    U,G,f,OFFSET,mt,words,original_packets,source_rows,word_domain,
)
sys.path.insert(0,str(ROOT/"agents"/"agent28"))
from k04_cpython_real_output_offset_sft import source_states

G=list(G)
for i in range(len(G),11):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

F1=1664525
F2=1566083941
INVF1=pow(F1,-1,1<<32)
INVF2=pow(F2,-1,1<<32)
SOURCE_S5_MASK=0x8000001f
SOURCE_S5_VALUE=0x00000011

def inverse(multiplier_inverse:int,value:int)->int:
    z=(multiplier_inverse*value)&U
    return z^(z>>30)

def key_from_eight_words(s2:int,s3:int,s4:int,s6:int,s7:int,
                         s8:int,s9:int,s10:int)->tuple[tuple[int,...],int]:
    """Reconstruct all six CPython key words with no guessed seed bits."""
    a3=((s3+3)&U)^f(F2,s2)
    a4=((s4+4)&U)^f(F2,s3)
    a7=((s7+7)&U)^f(F2,s6)
    a8=((s8+8)&U)^f(F2,s7)
    a9=((s9+9)&U)^f(F2,s8)
    a10=((s10+10)&U)^f(F2,s9)
    t4=(a4-(G[4]^f(F1,a3)))&U
    t10=(a10-(G[10]^f(F1,a9)))&U
    assert t4==t10,(t4,t10)
    k3=(t4-3)&U
    k1=(a8-(G[8]^f(F1,a7))-1)&U
    k2=(a9-(G[9]^f(F1,a8))-2)&U
    a2=inverse(INVF1,G[3]^((a3-k2-2)&U))
    a1=inverse(INVF1,G[2]^((a2-k1-1)&U))
    k0=(a1-(G[1]^f(F1,G[0])))&U
    a6=inverse(INVF1,G[7]^((a7-k0)&U))
    s5=inverse(INVF2,a6^((s6+6)&U))
    a5=((s5+5)&U)^f(F2,s4)
    k4=(a5-(G[5]^f(F1,a4))-4)&U
    k5=(a6-(G[6]^f(F1,a5))-5)&U
    return (k0,k1,k2,k3,k4,k5),s5

def domains_from_rows(rows:list[tuple[int,int]])->dict[int,list[int]]:
    domains={i:word_domain(rows,i) for i in (2,3,4,6,7,8,9,10)}
    assert {i:len(v) for i,v in domains.items()}=={
        2:8,3:64,4:512,6:1,7:1,8:8,9:64,10:512
    }
    return domains

def exact_join(domains:dict[int,list[int]],s5_value:int=SOURCE_S5_VALUE)->tuple[int,int,int,list[tuple[tuple[int,...],int]]]:
    """Full necessary source-domain join on repeated key3 term at i4/i10."""
    left={}
    for s2 in domains[2]:
        for s3 in domains[3]:
            a3=((s3+3)&U)^f(F2,s2)
            for s4 in domains[4]:
                a4=((s4+4)&U)^f(F2,s3)
                term=(a4-(G[4]^f(F1,a3)))&U
                left.setdefault(term,[]).append((s2,s3,s4))
    right={}
    for s8 in domains[8]:
        for s9 in domains[9]:
            a9=((s9+9)&U)^f(F2,s8)
            for s10 in domains[10]:
                a10=((s10+10)&U)^f(F2,s9)
                term=(a10-(G[10]^f(F1,a9)))&U
                right.setdefault(term,[]).append((s8,s9,s10))
    assert sum(len(v) for v in left.values())==262144
    assert sum(len(v) for v in right.values())==262144
    source_matches=0
    s5_passes=[]
    for term in left.keys()&right.keys():
        for s2,s3,s4 in left[term]:
            for s8,s9,s10 in right[term]:
                source_matches+=1
                keys,s5=key_from_eight_words(s2,s3,s4,
                    domains[6][0],domains[7][0],s8,s9,s10)
                if (s5&SOURCE_S5_MASK)==s5_value:
                    s5_passes.append((keys,s5))
    return len(left),len(right),source_matches,s5_passes

def genuine_controls(terms:list[list[int]])->None:
    seeds=(
        (0x12345678,0x23456789,0x3456789A,0x456789AB,0x56789ABC,0x6789ABCD),
        (1,1,1,1,1,1),(U,U,U,U,U,U),
        (8131,4242,54321,98989,0,88888),
        (0,0x80000000,0,0x7fffffff,0xf0f0f0f0,0x00abcdef)
    )
    for trial,keys in enumerate(seeds):
        generator=random.Random(sum(key<<(32*i) for i,key in enumerate(keys)))
        state=generator.getstate()[1][:624]
        recovered,s5=key_from_eight_words(*(state[i] for i in
                                        (2,3,4,6,7,8,9,10)))
        assert recovered==keys and s5==state[5],(trial,recovered,keys)
        if trial==0:
            draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
            packets=[b"".join(draws[OFFSET+pos+j].to_bytes(4,"little")
                              for j in range(4)) for pos in mt.STARTS]
            domains=domains_from_rows(source_rows(packets,terms))
            assert all(state[index] in domains[index] for index in domains)
            left,right,matches,s5passes=exact_join(domains,state[5]&SOURCE_S5_MASK)
            assert keys in (candidate for candidate,s5 in s5passes)
            print("GENUINE_CPYTHON_N6_FULL_SOURCE_DOMAIN_JOIN_WITNESS=PASS",
                  left,right,matches,len(s5passes))
    print("GENUINE_CPYTHON_N6_REAL_SIX_WORD_KEY_RECONSTRUCTION=5/5 PASS")

def original(terms:list[list[int]])->None:
    packets=original_packets()
    rows=source_rows(packets,terms)
    domains=domains_from_rows(rows)
    assert domains[6]==[0xE403BB7D] and domains[7]==[0x1F7B301F]
    masks=source_states(OFFSET,packets)
    assert masks[5]==(SOURCE_S5_MASK,SOURCE_S5_VALUE)
    left,right,matches,s5passes=exact_join(domains)
    assert (left,right,matches,len(s5passes))==(262138,262130,16,0),(
        left,right,matches,s5passes[:5])
    print("ORIGINAL_K2496_N6_SOURCE_DOMAIN_LEFT_DISTINCT=262138 "
          "RIGHT_DISTINCT=262130 REPEATED_K3_TERM_PAIRS=16 "
          "SOURCE_S5_SURVIVORS=0")
    print("ORIGINAL_K2496_N6_ALL_192BIT_CPINT_SEEDS_EXCLUDED=PASS")
    print("K04_PHYSICAL_COUPON_UNRECOVERED K08_FINAL_CAPTION_UNRECOVERED")

if __name__=="__main__":
    terms=words(OFFSET)
    genuine_controls(terms)
    original(terms)
