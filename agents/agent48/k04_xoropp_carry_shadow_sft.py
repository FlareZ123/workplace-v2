#!/usr/bin/env python3
"""Synthetic-only full-rank carry shadow for xoroshiro128++ 1.0.
No historical payloads, hashes, source records or recovered components.
Known carry masks suffice to invert two outputs; unknown masks remain open.
"""
import random

MASK=(1<<64)-1
def rol(x,k): return ((x<<k)|(x>>(64-k)))&MASK
def step(a,b):
    t=a^b
    return (rol(a,49)^t^(t<<21))&MASK,rol(t,28)
def add_carries(a,b):
    c=0; mask=0
    for k in range(64):
        mask|=c<<k
        x,y=(a>>k)&1,(b>>k)&1
        c=(x&y)|(x&c)|(y&c)
    return (a+b)&MASK,mask
def outputs(a,b):
    c0,u0=add_carries(a,b)
    y0,v0=add_carries(rol(c0,17),a)
    a1,b1=step(a,b)
    c1,u1=add_carries(a1,b1)
    y1,v1=add_carries(rol(c1,17),a1)
    return y0|(y1<<64),(u0,v0,u1,v1)
def shadow(a,b):
    a1,b1=step(a,b)
    return (rol(a^b,17)^a)|((rol(a1^b1,17)^a1)<<64)
def inverse_rows():
    cols=[shadow(1<<k,0) for k in range(64)]+[shadow(0,1<<k) for k in range(64)]
    rows=[sum(((v>>i)&1)<<j for j,v in enumerate(cols))|(1<<(128+i)) for i in range(128)]
    for j in range(128):
        pivot=next((i for i in range(j,128) if (rows[i]>>j)&1),None)
        assert pivot is not None,"shadow transform is singular"
        rows[j],rows[pivot]=rows[pivot],rows[j]
        for i in range(128):
            if i!=j and (rows[i]>>j)&1: rows[i]^=rows[j]
    assert all((v&((1<<128)-1))==(1<<i) for i,v in enumerate(rows))
    return [v>>128 for v in rows]
def inverse_with_known_carries(y, carries, inv):
    u0,v0,u1,v1=carries
    correction=(rol(u0,17)^v0)|((rol(u1,17)^v1)<<64)
    z=y^correction
    bits=sum((((r&z).bit_count()&1)<<i) for i,r in enumerate(inv))
    return bits&MASK,bits>>64
def run(seed=20261127, trials=512):
    inv=inverse_rows()
    rng=random.Random(seed)
    corrupted_survivors=0
    for _ in range(trials):
        a,b=rng.getrandbits(64),rng.getrandbits(64)
        if a==b==0:b=1
        y,c=outputs(a,b)
        assert inverse_with_known_carries(y,c,inv)==(a,b)
        cc=list(c);cc[rng.randrange(4)]^=1<<rng.randrange(1,64)
        bad=inverse_with_known_carries(y,cc,inv)
        assert bad!=(a,b)
        if outputs(*bad)[0]==y:corrupted_survivors+=1
    assert not corrupted_survivors
    print("rank=128; planted_full_state=%d/%d; corrupted_carry_survivors=%d"%
          (trials,trials,corrupted_survivors))
if __name__=="__main__":run()
