"""H17 source-only *low-halfword* CPython seed-key reconstruction.

A low-b-bit CPython first-pass T_i depends on low-b bits of three
initialized state words, the high two bits of two earlier state words,
and two as-yet-unknown bits of A_(i-1). Enumerate the latter exactly
as a four-way SUPerset, so any real CPython seed is retained.
Projection on ~3*b+4 source-affine state bits can be far smaller
than projecting the full 96-bit S triple. This allows repeated-key
intersections unavailable in the original full-word <=9-bit windows.

The real 18:02 selected physical/copy row129 is never included in
the constraints. All original full-source and genuine-seed checks
are modeled at true prior-draw phase 2496+k.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import random
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent45"))
from k04_source_n24_phase_sweep_sft import (
    OFFSET, mt, words, original_native,
    phase_equations, reduce_source, source_dimension
)
from k04_k2496_nineteen_term_source_sft import G

U=(1<<32)-1
OPEN=(tuple(range(166,202)) + tuple(range(310,338)))


def project_indices(at, bits):
    return tuple(32*word+bit
                 for word in (at-2,at-1,at) for bit in range(bits)) + (
            32*(at-2)+30,32*(at-2)+31,
            32*(at-1)+30,32*(at-1)+31)


def affine_project(coefficients,constants,indices,maxrank):
    off=sum(constants[index]<<bit for bit,index in enumerate(indices))
    projections=defaultdict(int)
    for bit,index in enumerate(indices):
        expr=coefficients[index]
        while expr:
            low=expr&-expr
            projections[low.bit_length()-1] |= 1<<bit
            expr ^= low
    basis={}
    for expr in projections.values():
        while expr:
            pivot=expr.bit_length()-1
            if pivot not in basis:
                basis[pivot]=expr
                break
            expr ^= basis[pivot]
    if len(basis)>maxrank:
        return len(basis),None
    projected=[off]
    for direction in basis.values():
        projected.extend(value^direction for value in list(projected))
    assert len(projected)==1<<len(basis)
    return len(basis),projected


def partial_key_domain(at,key_index,bits,projected):
    mask=(1<<bits)-1
    out=set()
    g=G[at]&mask
    for packed in projected:
        early=packed&mask
        prev=(packed>>bits)&mask
        cur=(packed>>(2*bits))&mask
        early_hi=(packed>>(3*bits))&3
        prev_hi=(packed>>(3*bits+2))&3
        ap=(((prev+at-1)&mask) ^
            ((1566083941*(early^early_hi))&mask))
        ac=(((cur+at)&mask) ^
            ((1566083941*(prev^prev_hi))&mask))
        # Top two bits of the *intermediate* A_(i-1), not S_(i-1),
        # depend on unprojected full state. Enumerating 0..3
        # is sound and avoids false exclusions.
        for ap_hi in range(4):
            f1=(1664525*(ap^ap_hi))&mask
            out.add((ac-(g^f1)-key_index)&mask)
    return out


def analyze(native,symbolic,k,bits,maxrank, n=32):
    coeff,const=reduce_source(phase_equations(native,symbolic,OFFSET+k))
    rank_hist=Counter()
    eligible=Counter()
    candidates=defaultdict(list)
    for at in range(4,624):
        idx=(at-1)%n
        if idx<16:continue
        ind=project_indices(at,bits)
        rank=source_dimension(coeff[i] for i in ind)
        rank_hist[rank]+=1
        if rank>maxrank:continue
        eligible[idx]+=1
        candidates[idx].append((rank,at,ind))
    discovered={}
    attempted=0
    excluded=[]
    for idx,terms in candidates.items():
        terms.sort()
        intersect=None
        for rank,at,ind in terms:
            got,projections=affine_project(coeff,const,ind,maxrank)
            assert got==rank and projections is not None
            domain=partial_key_domain(at,idx,bits,projections)
            attempted+=1
            intersect=domain if intersect is None else intersect&domain
            if not intersect:
                excluded.append((idx,terms[0][1],at))
                break
        discovered[idx]=intersect
        if excluded:break
    return {
        "k":k,"bits":bits,"maxrank":maxrank,
        "rank_hist":dict(sorted(rank_hist.items())),
        "eligible_indices":dict(sorted(eligible.items())),
        "tested_terms":attempted,
        "source_key_repeated_domain_zero":bool(excluded),
        "exclusion":excluded,
        "small_candidate_indices":{idx:sorted(values)
           for idx,values in discovered.items()
           if values is not None and len(values)<=16},
    }


def control(symbolic,k,bits,maxrank):
    raw=(b"After the late watch, a place at the table remains ready " +
         b"for anyone who comes in from the sea at dawn.")[:64]
    assert len(raw)==64
    expanded=int.from_bytes(raw+hashlib.sha512(raw).digest(),"big")
    assert (expanded.bit_length()+31)//32==32
    rng=random.Random(raw)
    stream=[rng.getrandbits(32) for _ in range(OFFSET+k+mt.STARTS[-1]+4)]
    state=rng.getstate()[1][:624] # after stream, irrelevant
    native=[[mt.untemper(stream[OFFSET+k+start+lane])
             for lane in range(4)] for start in mt.STARTS]
    co,cs=reduce_source(phase_equations(native,symbolic,OFFSET+k))
    positives=0
    for at in range(4,624):
        idx=(at-1)%32
        if idx<16:continue
        ind=project_indices(at,bits)
        rank=source_dimension(co[i] for i in ind)
        if rank>maxrank:continue
        dr,proj=affine_project(co,cs,ind,maxrank)
        actual=(expanded>>(32*idx))&((1<<bits)-1)
        domain=partial_key_domain(at,idx,bits,proj)
        assert actual in domain,(k,bits,at,idx,rank,hex(actual))
        positives+=1
    assert positives>=1,(k,bits,maxrank)
    print("GENUINE_CPYTHON_EXACT_LOWBIT_SOURCE_CONTROL_PASS",k,bits,
          "source_terms",positives,flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",type=int,default=190)
    ap.add_argument("--bits",type=int,choices=(8,12,16),default=16)
    ap.add_argument("--max-rank",type=int,default=12)
    args=ap.parse_args()
    assert args.phase in OPEN
    symbolic=words(OFFSET+623)
    control(symbolic,args.phase,args.bits,args.max_rank)
    result=analyze(original_native(),symbolic,args.phase,args.bits,args.max_rank)
    print("ORIGINAL_LOWBIT_KEY_SOURCE",result,flush=True)
    print("ORIGINAL_SOURCE_LOWBIT_PHASE_COMPLETE",args.phase,flush=True)


if __name__=="__main__":main()
