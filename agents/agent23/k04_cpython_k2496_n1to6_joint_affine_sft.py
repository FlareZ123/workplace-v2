"""Exact source-only exclusion of all CPython integer key word lengths n=1..6.

Run: python agents/agent23/k04_cpython_k2496_n1to6_joint_affine_sft.py
This exploits *joint* original printer-source affine domains in adjacent
initialized MT words, including cross-word parities dropped by per-bit
projections. The disputed selected printer ACK2 row129 is omitted throughout.
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
for i in range(len(G),11):
    G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

def joint_domain(rows:list[tuple[int,int]],
                 indices:tuple[int,...])->list[tuple[int,...]]:
    """Enumerate the exact joint affine projection of all 132 source packets."""
    support=sum(U<<(32*i) for i in indices)
    basis:dict[int,tuple[int,int]]={}
    for expr,rhs in rows:
        while expr:
            outside=expr&~support
            pivot=(outside if outside else expr).bit_length()-1
            prior=basis.get(pivot)
            if prior is None:
                basis[pivot]=(expr,rhs)
                break
            expr^=prior[0];rhs^=prior[1]
        else:
            assert rhs==0
    assert len(basis)==15365
    equations={}
    for expr,rhs in basis.values():
        if expr&~support:
            continue
        pivot=expr.bit_length()-1
        assert pivot not in equations
        equations[pivot]=(expr,rhs)
    free=[32*i+bit for i in indices for bit in range(32)
          if 32*i+bit not in equations]
    assert len(free)<=9,(indices,len(free))
    domain=[]
    for choice in range(1<<len(free)):
        state=sum(((choice>>j)&1)<<bit for j,bit in enumerate(free))
        for bit in sorted(equations):
            expr,rhs=equations[bit]
            state|=(rhs^((state&expr).bit_count()&1))<<bit
        assert all(((state&expr).bit_count()&1)==rhs for expr,rhs in equations.values())
        domain.append(tuple((state>>(32*i))&U for i in indices))
    assert len(domain)==1<<len(free)
    return domain

def key_term(at:int,states:dict[int,int])->int:
    """Known CPython firstpass K_i=key[(i-1)%n]+(i-1)%n for i=4,8,9,10."""
    if at==4:
        s2,s3,s4=states[2],states[3],states[4]
        previous=((s3+3)&U)^f(1566083941,s2)
        current=((s4+4)&U)^f(1566083941,s3)
    elif at in (8,9,10):
        s_prev=states[at-2]
        s_before=states[at-1]
        s_current=states[at]
        previous=((s_before+at-1)&U)^f(1566083941,s_prev)
        current=((s_current+at)&U)^f(1566083941,s_before)
    else:
        raise ValueError(at)
    return (current-(G[at]^f(1664525,previous)))&U

def domains_from_rows(rows:list[tuple[int,int]]):
    d234=joint_domain(rows,(2,3,4))
    d8=joint_domain(rows,(8,))
    d89=joint_domain(rows,(8,9))
    d8910=joint_domain(rows,(8,9,10))
    assert (len(d234),len(d8),len(d89),len(d8910))==(512,8,64,512)
    s6=word_domain(rows,6)
    s7=word_domain(rows,7)
    assert len(s6)==len(s7)==1
    return d234,d8,d89,d8910,s6[0],s7[0]

def term_sets(domains):
    d234,d8,d89,d8910,s6,s7=domains
    T4={key_term(4,dict(zip((2,3,4),entry))) for entry in d234}
    T8={key_term(8,{6:s6,7:s7,8:s8}) for (s8,) in d8}
    T9={key_term(9,{7:s7,8:s8,9:s9}) for s8,s9 in d89}
    T10={key_term(10,{8:s8,9:s9,10:s10}) for s8,s9,s10 in d8910}
    assert (len(T4),len(T8),len(T9),len(T10))==(512,8,64,512)
    return T4,T8,T9,T10

def positive_controls(terms:list[list[int]])->None:
    # Each highest key word is nonzero, so true CPython key-array length is n.
    samples={
        1:(0x12345678,),
        2:(0x12345678,0x23456789),
        3:(0x12345678,0x23456789,0x3456789a),
        4:(0x12345678,0x23456789,0x3456789a,0x456789ab),
        5:(0x12345678,0x23456789,0x3456789a,0x456789ab,0x56789abc),
        6:(0x12345678,0x23456789,0x3456789a,0x456789ab,0x56789abc,0x6789abcd),
    }
    for n,keys in samples.items():
        generator=random.Random(sum(key<<(32*i) for i,key in enumerate(keys)))
        state=generator.getstate()[1][:624]
        observed={i:state[i] for i in (2,3,4,6,7,8,9,10)}
        t4=key_term(4,observed)
        for at in (8,9,10):
            if (at-4)%n==0:
                assert t4==key_term(at,observed),n
        draws=[generator.getrandbits(32) for _ in range(OFFSET+974)]
        packets=[b"".join(draws[OFFSET+pos+j].to_bytes(4,"little")
                          for j in range(4)) for pos in mt.STARTS]
        domains=domains_from_rows(source_rows(packets,terms))
        d234,d8,d89,d8910,s6,s7=domains
        assert tuple(state[i] for i in (2,3,4)) in d234,n
        assert (state[8],) in d8 and (state[8],state[9]) in d89,n
        assert tuple(state[i] for i in (8,9,10)) in d8910,n
        assert (s6,s7)==(state[6],state[7]),n
        T4,T8,T9,T10=term_sets(domains)
        assert t4 in T4,n
        for at,T in ((8,T8),(9,T9),(10,T10)):
            if (at-4)%n==0:
                assert t4 in T,n
        print(f"GENUINE_CPYTHON_SEED_LENGTH_N{n}_JOINT_SOURCE_WITNESS=PASS")
    print("GENUINE_CPYTHON_N1_TO_N6_JOINT_SOURCE_CONTROLS=6/6 PASS")

def original(terms:list[list[int]])->None:
    domains=domains_from_rows(source_rows(original_packets(),terms))
    T4,T8,T9,T10=term_sets(domains)
    assert domains[4]==0xE403BB7D and domains[5]==0x1F7B301F
    hits48=T4&T8
    hits49=T4&T9
    hits410=T4&T10
    assert not hits48 and not hits49 and not hits410,(hits48,hits49,hits410)
    print("ORIGINAL_JOINT_DOMAIN_S234_RANK=87 VALUES=512; "
          "S8_RANK=29 VALUES=8; S89_RANK=58 VALUES=64; "
          "S8910_RANK=87 VALUES=512")
    print("ORIGINAL_TERM_SETS K4=512 K8=8 K9=64 K10=512")
    print("ORIGINAL_REPEATED_KEY_TERM_INTERSECTIONS "
          "K4_K8=0 K4_K9=0 K4_K10=0")
    print("ORIGINAL_CPINT_N1_TO_N6_TRUE_OFFSET2496_ALL_EXCLUDED=PASS")
    print("K04_PHYSICAL_COUPON_UNRECOVERED K08_FINAL_CAPTION_UNRECOVERED")

if __name__=="__main__":
    terms=words(OFFSET)
    positive_controls(terms)
    original(terms)
