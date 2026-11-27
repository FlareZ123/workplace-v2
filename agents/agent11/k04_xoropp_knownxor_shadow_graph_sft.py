#!/usr/bin/env python3
"""Exact GF(2) functional-graph inversion with known XOR-state and second-add carry mask.
Synthetic only; never reads archive, commitments, original outputs or PDF.
"""
from collections import deque,Counter
import random,time
M=(1<<64)-1
R=lambda x,k:((x<<k)|(x>>(64-k)))&M

def first_add(a,t):
 b=a^t
 c=(a+b)&M
 u=0;prev=0
 for i in range(64):
  u|=prev<<i
  prev=prev if (t>>i)&1 else (a>>i)&1
 assert c==(t^u)
 return c

def second_carry(q,a):
 v=0;carry=0
 for j in range(64):
  v|=carry<<j
  x=(q>>j)&1;y=(a>>j)&1
  carry=(x&y)|(x&carry)|(y&carry)
 return v

def obs(a,t):
 q=R(first_add(a,t),17)
 return (q+a)&M,second_carry(q,a)

def parents(t):
 ans=[]
 for j in range(64):
  k=(j-17)%64
  ans.append(next((i for i in range(k-1,-1,-1) if ((t>>i)&1)==0),None))
 return ans

def recover(a_t,y,second_add_carry):
 """Enumerate all states a consistent with known t and known second-addition carry.
 Complexity O(64 + 64 * 2**number_of_cycles) with outputs to validate.
 Returns all fully checked (a,a^t), including if known carry mask was adversarial.
 """
 t=a_t; p=parents(t)
 constbits=sum(((t>>((j-17)%64))&1)<<j for j in range(64))
 rhs=y^second_add_carry^constbits
 links=[[] for _ in range(64)]
 for j,par in enumerate(p):
  if par is not None:
   links[j].append((par,j));links[par].append((j,j))
 basis=[None]*64; cycle_groups=[]
 for i in range(64):
  if basis[i] is not None:continue
  component=[];queue=deque([i]);component.append(i);basis[i]=0
  conflict=False
  while queue:
   j=queue.popleft()
   for nb,child in links[j]:
    val=basis[j]^((rhs>>child)&1)
    if basis[nb] is None:
     basis[nb]=val;component.append(nb);queue.append(nb)
    elif basis[nb]!=val:
     conflict=True
  if conflict:return []
  roots=[z for z in component if p[z] is None]
  if roots:
   # Rooted tree: its absolute additive bit is fixed.
   root=roots[0]
   if basis[root]!=((rhs>>root)&1):
    for z in component:basis[z]^=1
  else:
   cycle_groups.append(component)
 # Validate all source equations before candidate enumeration.
 for j in range(64):
  got=basis[j]^(basis[p[j]] if p[j] is not None else 0)
  if got!=((rhs>>j)&1):return []
 found=[]
 for mask in range(1<<len(cycle_groups)):
  val=basis[:]
  for i,grp in enumerate(cycle_groups):
   if (mask>>i)&1:
    for j in grp:val[j]^=1
  a=sum(bit<<j for j,bit in enumerate(val))
  yy,vv=obs(a,t)
  if yy==y and vv==second_add_carry:found.append((a,a^t))
 return found

def test(seed=20261127,trials=10000):
 rng=random.Random(seed);cycles=Counter();exact=multi=poison_survivors=0;tic=time.monotonic()
 for i in range(trials):
  a,b=rng.getrandbits(64),rng.getrandbits(64);t=a^b;y,v=obs(a,t)
  fits=recover(t,y,v)
  if (a,b) not in fits:raise RuntimeError('loss of planted state '+str(i))
  exact+=(len(fits)==1);multi+=(len(fits)>1)
  if i<512:
   vv=v^(1<<rng.randrange(1,64))
   poison_survivors+=bool(recover(t,y,vv))
  # Count source-free graph cycles without dense matrix elimination.
  p=parents(t);seen=set();count=0
  for j in range(64):
   if j in seen:continue
   cur=j;idx={};path=[]
   while cur is not None and cur not in seen and cur not in idx:
    idx[cur]=len(path);path.append(cur);cur=p[cur]
   if cur in idx:count+=1
   seen.update(path)
  cycles[count]+=1
 for t in [0,M,0xaaaaaaaaaaaaaaaa,0x5555555555555555]:
  a=rng.getrandbits(64);y,v=obs(a,t)
  assert (a,a^t) in recover(t,y,v)
 assert poison_survivors==0
 print('known_carry_planted=',trials,'found=',trials,'unique=',exact,'multi=',multi,'poisoned_carry_survivors=',poison_survivors,'edge_cases=',4,'cycle_distribution=',sorted(cycles.items()),'elapsed_seconds=',round(time.monotonic()-tic,2))
if __name__=='__main__':test()
