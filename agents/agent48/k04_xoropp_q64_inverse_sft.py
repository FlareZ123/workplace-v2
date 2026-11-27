#!/usr/bin/env python3
"""Source-free closed-form xoroshiro128++ carry-free 2-output inverse.
Computational proof of 64-bit Q invertibility and 100,000 planted roundtrips.
No historical source inputs, printer bytes, acceptance values, or PDF.
"""
import random
MASK=(1<<64)-1
def rol(x,k):return ((x<<k)|(x>>(64-k)))&MASK
def step(a,b):
 t=a^b;return (rol(a,49)^t^(t<<21))&MASK,rol(t,28)
def Q(t):
 x=rol(t,2)^t^((t<<21)&MASK)
 return x^rol(x,17)^rol(t,45)
def Q_inverse_rows():
 cols=[Q(1<<i) for i in range(64)]
 rows=[sum(((col>>i)&1)<<j for j,col in enumerate(cols))|(1<<(64+i)) for i in range(64)]
 for j in range(64):
  pivot=next((i for i in range(j,64) if (rows[i]>>j)&1),None)
  assert pivot is not None,"Q not invertible"
  rows[j],rows[pivot]=rows[pivot],rows[j]
  for i in range(64):
   if i!=j and (rows[i]>>j)&1:rows[i]^=rows[j]
 assert all((row&MASK)==(1<<i) for i,row in enumerate(rows))
 return [row>>64 for row in rows]
def recover(u,v,inv):
 q=v^rol(u,49)^rol(u,2)
 t=sum((((r&q).bit_count()&1)<<i) for i,r in enumerate(inv))
 a=u^rol(t,17);return a,a^t
def test(seed=20261127,trials=100000):
 inv=Q_inverse_rows();rng=random.Random(seed)
 for _ in range(trials):
  a,b=rng.getrandbits(64),rng.getrandbits(64)
  t=a^b;a1,b1=step(a,b)
  u=rol(t,17)^a;v=rol(a1^b1,17)^a1
  assert Q(t)==v^rol(u,49)^rol(u,2)
  assert recover(u,v,inv)==(a,b)
 print("rank(Q)=64; synthetic_exact_recover=%d/%d"%(trials,trials))
if __name__=="__main__":test()
