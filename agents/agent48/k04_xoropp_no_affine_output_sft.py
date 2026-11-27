#!/usr/bin/env python3
"""Exact synthetic certificate: no nonzero affine output projection of xoroshiro128++.
Witnesses are second Boolean derivatives of 2, 4, and 8 consecutive outputs.
A full-rank derivative span excludes every nonzero XOR output mask with affine
dependence on initial 128-bit state. No historical records/commitments read.
"""
import random
MASK=(1<<64)-1
def rol(x,k):return ((x<<k)|(x>>(64-k)))&MASK
def emit(x,n):
    a=x&MASK;b=x>>64;result=0
    for j in range(n):
        result|=((rol((a+b)&MASK,17)+a)&MASK)<<(64*j)
        t=a^b
        a,b=(rol(a,49)^t^(t<<21))&MASK,rol(t,28)
    return result
def derivative(x,i,j,n):
    return emit(x,n)^emit(x^(1<<i),n)^emit(x^(1<<j),n)^emit(x^(1<<i)^(1<<j),n)
def rank_certificate(n,seed=20261127,max_trials=12000):
    rng=random.Random(seed+n);basis={};witnesses=[]
    for trial in range(max_trials):
        x=rng.getrandbits(128);i,j=rng.sample(range(128),2)
        d=derivative(x,i,j,n);v=d
        while v:
            k=v.bit_length()-1
            if k in basis:v^=basis[k]
            else:
                basis[k]=v;witnesses.append((x,i,j));break
        if len(basis)==64*n:break
    assert len(basis)==64*n,(n,len(basis))
    replay={}
    for x,i,j in witnesses:
        v=derivative(x,i,j,n)
        while v:
            k=v.bit_length()-1
            if k in replay:v^=replay[k]
            else:replay[k]=v;break
    assert len(replay)==64*n
    return trial+1,len(witnesses)
if __name__=='__main__':
    for n in (2,4,8):
        trials,witnesses=rank_certificate(n)
        print(f'outputs={n} exact_second_derivative_rank={64*n} witness_count={witnesses} trial_count={trials}')
    def f(a,b):return (rol((a+b)&MASK,17)+a)&MASK
    for bit in range(64):
        a,b=(1<<16,1<<63) if bit==17 else (1<<((bit-18)%64),)*2
        delta=f(a,b)^f(a,0)^f(0,b)^f(0,0)
        assert delta==1<<bit,(bit,delta)
    print('individual_output_bits_all_nonaffine=64/64')
