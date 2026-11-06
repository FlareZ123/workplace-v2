"""K04 exact genuine CPython three-word integer-seed source-domain inversion.

Run: python agents/agent23/k04_cpython_k2496_n3_worddomain_sft.py
Uses only 132 intact original printer packets (the selected row129 is withheld).
No source-based assumption on the selected K04 bytes or original acceptance hash.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import re
import sys
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent28"))
from k04_cpython_real_output_offset_sft import words, mt

OFFSET=2496
U=0xffffffff
SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
G=[19650218]
for i in range(1,9):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

def f(multiplier:int,value:int)->int:
    return multiplier*(value^(value>>30))&U

def original_packets()->list[bytes]:
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    packets=[bytes.fromhex(v.decode("ascii")) for v in
             re.findall(rb"PAYLOAD=([0-9A-F]{32})",raw)]
    assert len(packets)==len(mt.STARTS)==133 and mt.STARTS[129]==951
    return packets

def source_rows(packets:list[bytes],terms:list[list[int]])->list[tuple[int,int]]:
    assert len(packets)==len(mt.STARTS)==133
    rows=[]
    for index,(position,packet) in enumerate(zip(mt.STARTS,packets)):
        if index==129:
            continue
        for lane in range(4):
            native=mt.untemper(int.from_bytes(packet[4*lane:4*lane+4],"little"))
            for bit,expression in enumerate(terms[624+OFFSET+position+lane]):
                rows.append((expression,(native>>bit)&1))
    assert len(rows)==16896
    return rows

def word_domain(rows:list[tuple[int,int]],index:int)->list[int]:
    """Complete affine domain of one native initialized 32-bit word.

    Eliminate every outside-word bit BEFORE any within-word bit. This extracts
    all supported same-word parity equations, not just individually known bits.
    """
    mask=U<<(32*index)
    basis:dict[int,tuple[int,int]]={}
    for expression,rhs in rows:
        while expression:
            outside=expression&~mask
            pivot=(outside if outside else expression).bit_length()-1
            prior=basis.get(pivot)
            if prior is None:
                basis[pivot]=(expression,rhs)
                break
            expression^=prior[0]
            rhs^=prior[1]
        else:
            assert rhs==0
    assert len(basis)==15365,len(basis)
    word_eq={}
    for expression,rhs in basis.values():
        if expression&~mask:
            continue
        x=expression>>(32*index)
        pivot=x.bit_length()-1
        assert pivot not in word_eq
        word_eq[pivot]=(x,rhs)
    free=[bit for bit in range(32) if bit not in word_eq]
    assert len(free)<=9,(index,len(free))
    domain=[]
    for choices in range(1<<len(free)):
        value=sum(((choices>>j)&1)<<bit for j,bit in enumerate(free))
        for bit in sorted(word_eq):
            x,rhs=word_eq[bit]
            value|=(rhs^((value&x).bit_count()&1))<<bit
        assert all(((value&x).bit_count()&1)==rhs for x,rhs in word_eq.values())
        domain.append(value)
    assert len(domain)==1<<(32-len(word_eq))
    return domain

def key_from_four_words(s2:int,s3:int,s4:int,s8:int,s6:int,s7:int)->tuple[int,int,int]:
    """Unique length-three genuine CPython key determined by four state words."""
    a7=((s7+7)&U)^f(1566083941,s6)
    a8=((s8+8)&U)^f(1566083941,s7)
    k1=(a8-(G[8]^f(1664525,a7))-1)&U
    a3=((s3+3)&U)^f(1566083941,s2)
    a4=((s4+4)&U)^f(1566083941,s3)
    k0=(a4-(G[4]^f(1664525,a3)))&U
    a1=((G[1]^f(1664525,G[0]))+k0)&U
    a2=((G[2]^f(1664525,a1))+k1+1)&U
    k2=(a3-(G[3]^f(1664525,a2))-2)&U
    return k0,k1,k2

def full_a7(k0:int,k1:int,k2:int)->int:
    """Exact early firstpass through A7, no index1 wrap yet."""
    a=(G[1]^f(1664525,G[0]))+k0&U
    for i in range(2,8):
        j=(i-1)%3
        a=((G[i]^f(1664525,a))+(k0,k1,k2)[j]+j)&U
    return a

def exhaustive(domains:dict[int,list[int]])->tuple[int,list[tuple[int,int,int]]]:
    s6=domains[6][0];s7=domains[7][0]
    a7=((s7+7)&U)^f(1566083941,s6)
    k1s=[key_from_four_words(domains[2][0],domains[3][0],
                            domains[4][0],s8,s6,s7)[1] for s8 in domains[8]]
    total=0
    survivors=[]
    for s2 in domains[2]:
        for s3 in domains[3]:
            a3=((s3+3)&U)^f(1566083941,s2)
            for s4 in domains[4]:
                a4=((s4+4)&U)^f(1566083941,s3)
                k0=(a4-(G[4]^f(1664525,a3)))&U
                a1=((G[1]^f(1664525,G[0]))+k0)&U
                for k1 in k1s:
                    a2=((G[2]^f(1664525,a1))+k1+1)&U
                    k2=(a3-(G[3]^f(1664525,a2))-2)&U
                    a5=((G[5]^f(1664525,a4))+k1+1)&U
                    a6=((G[6]^f(1664525,a5))+k2+2)&U
                    actual_a7=((G[7]^f(1664525,a6))+k0)&U
                    total+=1
                    if actual_a7!=a7:
                        continue
                    assert full_a7(k0,k1,k2)==a7
                    survivors.append((k0,k1,k2))
    assert total==len(domains[2])*len(domains[3])*len(domains[4])*len(domains[8])
    return total,survivors

def state_domains(rows:list[tuple[int,int]])->dict[int,list[int]]:
    domains={index:word_domain(rows,index) for index in (2,3,4,6,7,8)}
    assert {k:len(domains[k]) for k in domains}=={2:8,3:64,4:512,6:1,7:1,8:8}
    return domains

def fourword_repeat(domains:dict[int,list[int]])->tuple[int,list[tuple[int,int,int,int]]]:
    """For genuine CPython n=4, the two exact key terms at i=4,8 must equal k3+3."""
    s6=domains[6][0];s7=domains[7][0]
    a7=((s7+7)&U)^f(1566083941,s6)
    terms8={(((((s8+8)&U)^f(1566083941,s7))-
             (G[8]^f(1664525,a7)))&U) for s8 in domains[8]}
    count=0
    matched=[]
    for s2 in domains[2]:
        for s3 in domains[3]:
            a3=((s3+3)&U)^f(1566083941,s2)
            for s4 in domains[4]:
                a4=((s4+4)&U)^f(1566083941,s3)
                term4=(a4-(G[4]^f(1664525,a3)))&U
                count+=len(domains[8])
                if term4 in terms8:
                    matched.append((s2,s3,s4,term4))
    assert count==2097152 and len(terms8)==len(domains[8])
    return count,matched

def seeded_controls(terms:list[list[int]])->None:
    seeds=((0x12345678,0x23456789,0x3456789A),
           (1,1,1),(U,U,U),(8131,4242,54321),
           (0,0x80000000,0x7fffffff))
    for trial,(k0,k1,k2) in enumerate(seeds):
        generator=random.Random(k0|(k1<<32)|(k2<<64))
        state=generator.getstate()[1][:624]
        draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
        packets=[b"".join(draws[OFFSET+position+j].to_bytes(4,"little")
                          for j in range(4)) for position in mt.STARTS]
        domains=state_domains(source_rows(packets,terms))
        assert all(state[index] in domains[index] for index in domains),trial
        chosen=key_from_four_words(state[2],state[3],state[4],state[8],
                                   state[6],state[7])
        assert chosen==(k0,k1,k2),(trial,chosen)
        assert full_a7(*chosen)==(((state[7]+7)&U)^f(1566083941,state[6]))
        if trial==0:
            total,hits=exhaustive(domains)
            assert total==2097152 and (k0,k1,k2) in hits
            print("GENUINE_CPYTHON_N3_COMPLETE_DOMAIN_SELECTED_WITNESS=PASS")
    print("GENUINE_CPYTHON_N3_REAL_INITIALIZED_SOURCE_DOMAIN_CONTROLS=5/5 PASS")
    seeds4=((0x12345678,0x23456789,0x3456789A,0x456789AB),
            (1,1,1,1),(U,U,U,U),(0,0x80000000,0,0x7fffffff),
            (8131,4242,54321,98989))
    for trial,(k0,k1,k2,k3) in enumerate(seeds4):
        generator=random.Random(k0|(k1<<32)|(k2<<64)|(k3<<96))
        state=generator.getstate()[1][:624]
        a3=((state[3]+3)&U)^f(1566083941,state[2])
        a4=((state[4]+4)&U)^f(1566083941,state[3])
        a7=((state[7]+7)&U)^f(1566083941,state[6])
        a8=((state[8]+8)&U)^f(1566083941,state[7])
        term4=(a4-(G[4]^f(1664525,a3)))&U
        term8=(a8-(G[8]^f(1664525,a7)))&U
        assert term4==term8==((k3+3)&U),trial
        if trial==0:
            draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
            packets=[b"".join(draws[OFFSET+position+j].to_bytes(4,"little")
                              for j in range(4)) for position in mt.STARTS]
            domains=state_domains(source_rows(packets,terms))
            assert all(state[index] in domains[index] for index in domains)
            total,hits=fourword_repeat(domains)
            assert total==2097152
            assert (state[2],state[3],state[4],term4) in hits
            print("GENUINE_CPYTHON_N4_COMPLETE_DOMAIN_SELECTED_WITNESS=PASS")
    print("GENUINE_CPYTHON_N4_REAL_SEEDED_REPEATED_KEYTERM_CONTROLS=5/5 PASS")

def original(terms:list[list[int]])->None:
    source=original_packets()
    rows=source_rows(source,terms)
    domains=state_domains(rows)
    assert domains[6]==[0xE403BB7D] and domains[7]==[0x1F7B301F]
    print("ORIGINAL_SELECTED_WITHHELD_SOURCE_RANK=15365")
    print("ORIGINAL_WORD_DOMAINS S2=8 S3=64 S4=512 S6=1 S7=1 S8=8")
    total,hits=exhaustive(domains)
    assert total==2097152 and hits==[],(total,hits[:10])
    print("K2496_N3_ALL_THREE_WORD_INTEGER_SEEDS_EXCLUDED=PASS "
          "EXACT_DOMAIN_PAIRS=2097152 A7_SURVIVORS=0")
    count,matched=fourword_repeat(domains)
    assert count==2097152 and matched==[],(count,matched[:10])
    print("K2496_N4_ALL_FOUR_WORD_INTEGER_SEEDS_EXCLUDED=PASS "
          "EXACT_DOMAIN_COMPARISONS=2097152 REPEATED_K3_TERM_MATCHES=0")
    print("K04_PHYSICAL_COUPON_UNRECOVERED K08_FINAL_CAPTION_UNRECOVERED")

if __name__=="__main__":
    symbols=words(OFFSET)
    seeded_controls(symbols)
    original(symbols)
