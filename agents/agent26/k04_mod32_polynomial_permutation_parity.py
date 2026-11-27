#!/usr/bin/env python3
"""Exact necessary source gate for ANY-degree 4xuint32 modular polynomial writer.

For an unknown fixed input-lane permutation p and integer polynomial T_j,
test two independently retained source transitions A->B,U->V and the
two-step bracket B->X->C. Does not read an archive or target commitment;
the public module contains source-independent synthetic fixtures only.
"""
from itertools import permutations, product
from random import Random

MASK=(1<<32)-1

def v2_32(n):
    n &= MASK
    return 32 if n==0 else ((n & -n).bit_length()-1)

def necessary(A,B,C,U,V):
    if any(len(v)!=4 for v in (A,B,C,U,V)):
        raise ValueError("all arguments must have exactly four unsigned words")
    if any(not (0<=int(x)<=MASK) for v in (A,B,C,U,V) for x in v):
        raise ValueError("word outside uint32")
    pair_perms=set()
    parity_models=[]
    for p in permutations(range(4)):
        if all(v2_32(A[p[j]]-U[p[j]])<=v2_32(B[j]-V[j])
               for j in range(4)):
            pair_perms.add(p)
        for codes in product(range(4),repeat=4):
            # Every polynomial map Z/2^32 -> Z/2^32 reduces modulo 2
            # to one of the four Boolean maps (0,1,identity,complement).
            f=lambda j,x:(codes[j] >> (x & 1)) & 1
            if not all(f(j,A[p[j]])==(B[j]&1) and
                       f(j,U[p[j]])==(V[j]&1) for j in range(4)):
                continue
            x=[f(j,B[p[j]]) for j in range(4)]
            if all(f(j,x[p[j]])==(C[j]&1) for j in range(4)):
                parity_models.append((p,codes))
    return {
        "pair_feasible_permutations":len(pair_perms),
        "bracket_parity_models":len(parity_models),
        "bracket_parity_permutations":len({p for p,_ in parity_models}),
        "joint_possible":sum(p in pair_perms for p,_ in parity_models)
    }

def synthetic_controls(count=100):
    rng=Random(0x26100317)
    positives=0
    for _ in range(count):
        p=list(range(4));rng.shuffle(p)
        a=[rng.getrandbits(32) for _ in range(4)]
        b=[rng.getrandbits(32) for _ in range(4)]
        c=[rng.getrandbits(32) for _ in range(4)]
        A=[rng.getrandbits(32) for _ in range(4)]
        U=[rng.getrandbits(32) for _ in range(4)]
        T=lambda xx:[(a[j]*xx[p[j]]**2+b[j]*xx[p[j]]+c[j]) & MASK for j in range(4)]
        B=T(A);V=T(U);X=T(B);C=T(X)
        r=necessary(A,B,C,U,V)
        assert r["joint_possible"]>=1,r
        positives+=1
    return positives

if __name__=="__main__":
    print("synthetic_complete_coupons_pass",synthetic_controls())
