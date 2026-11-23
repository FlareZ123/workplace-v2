"""H17 original all42 source MT -> CPython n98 exact partial triple domain sieve.

Original selected printer ACK2 omitted before hexadecimal decoding.
No commitment used during seeding consistency tests.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import random
import re
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
U=0xffffffff
MAG=0x9908B0DF
SOURCE_SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
S=(0, 10, 14, 23, 32, 43, 47, 54, 67, 80, 84, 92, 99, 110, 119, 124, 130,
 134, 138, 151, 155, 160, 167, 177, 182, 189, 195, 204, 211, 215, 224, 230,
 237, 242, 251, 258, 263, 275, 288, 297, 305, 311, 318, 328, 337, 345, 350,
 360, 366, 370, 378, 385, 389, 394, 402, 411, 417, 425, 430, 434, 445, 458,
 463, 472, 481, 489, 495, 505, 514, 520, 532, 537, 542, 548, 558, 565, 572,
 581, 592, 596, 604, 613, 617, 624, 632, 641, 645, 652, 662, 666, 677, 682,
 689, 696, 705, 714, 721, 731, 739, 745, 751, 755, 767, 771, 779, 784, 792,
 796, 804, 811, 822, 833, 842, 846, 853, 861, 871, 877, 885, 891, 903, 909,
 914, 921, 927, 934, 940, 947, 951, 952, 957, 961, 966)
G=[19650218]
for i in range(1,624):G.append((1812433253*(G[-1]^(G[-1]>>30))+i)&U)

def untemper(v):
 for shift,left,mask in ((18,0,U),(15,1,0xEFC60000),(7,1,0x9D2C5680),(11,0,U)):
  old=v
  for _ in range(6):v=(old^((v<<shift)&mask if left else (v>>shift)))&U
 return v

def keyterm(x,y,z,i):
 prev=(((y+i-1)&U)^(1566083941*(x^(x>>30))&U))
 curr=(((z+i)&U)^(1566083941*(y^(y>>30))&U))
 return (curr-(G[i]^(1664525*(prev^(prev>>30))&U)))&U

def projection(offset,packets):
 assert len(packets)==len(S)==133 and packets[129] is None
 words=[[1<<(32*i+j) for j in range(32)] for i in range(624)]
 for k in range(624,624+offset+970):
  a,b,c=words[k-624],words[k-623],words[k-227]
  words.append([c[j]^(a[31] if j==30 else b[j+1] if j<30 else 0)^(b[0] if MAG&(1<<j) else 0) for j in range(32)])
 basis={}
 def add(v,rhs):
  while v:
   pivot=v.bit_length()-1
   if pivot not in basis:
    basis[pivot]=(v,rhs)
    return
   old,oldrhs=basis[pivot];v^=old;rhs^=oldrhs
  assert rhs==0
 def known(v):
  rhs=0
  while v:
   pivot=v.bit_length()-1
   if pivot not in basis:return None
   old,oldrhs=basis[pivot];v^=old;rhs^=oldrhs
  return rhs
 for r,p in enumerate(packets):
  if p is None:continue
  for q in range(4):
   observed=untemper(int.from_bytes(p[4*q:4*q+4],'little'))
   for bit,expr in enumerate(words[624+offset+S[r]+q]):
    add(expr,(observed>>bit)&1)
 assert len(basis)==15434,len(basis)
 states=[]
 for w in words[:624]:
  m=v=0
  for bit,expr in enumerate(w):
   b=known(expr)
   if b is not None:m|=1<<bit;v|=b<<bit
  states.append((m,v))
 return states

def local_missing(states,i):
 return sum(32-states[i-j][0].bit_count() for j in (2,1,0))

def possibilities(m,v):
 missing=U^m
 values=[v]
 while missing:
  b=missing&-missing
  values += [x|b for x in values]
  missing-=b
 return values

def terms(states, max_unknown):
 for i in range(4,624):
  n=local_missing(states,i)
  if n>max_unknown:continue
  arrays=(possibilities(*states[i-2]),possibilities(*states[i-1]),
          possibilities(*states[i]))
  yield i,n,{keyterm(a,b,c,i) for a,b,c in itertools.product(*arrays)}

def no_conflict(states,max_unknown,n=98):
 residues={}
 considered=0
 for i,unknown,dom in terms(states,max_unknown):
  r=(i-1)%n
  considered+=1
  if r in residues:
   residues[r].intersection_update(dom)
   if not residues[r]:
    return False,considered, i, unknown, r, len(dom)
  else:residues[r]=dom
 return True,considered,0,0,0,len(residues)

def source():
 raw=(ROOT/'resources/evidence/print/spool-reconstruction.log').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 rows=re.findall(rb'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$',raw,re.M)
 assert len(rows)==133 and rows[129][:5]==(b'2026-10-03T18:02:00Z',b'PS-261003-0417',b'2',b'ACK',b'RECOVER')
 return [None if r==129 else bytes.fromhex(row[5].decode()) for r,row in enumerate(rows)]

def planted(n,offset):
 seed=sum(((0x12345678+i*0x10101)&U)<<(32*i) for i in range(n))
 rng=random.Random(seed)
 state=rng.getstate()[1][:624]
 emitted=[rng.getrandbits(32) for _ in range(offset+970)]
 packets=[None if r==129 else b''.join(emitted[offset+stage+j].to_bytes(4,'little') for j in range(4)) for r,stage in enumerate(S)]
 return seed,state,packets

def main():
 # Validate local inverse on genuine CPython integer seeds with exactly 98 words.
 for offset in (0, 616):
  seed,actual,packet=planted(98,offset)
  p=projection(offset,packet)
  assert all((actual[i]&m)==v for i,(m,v) in enumerate(p))
  for cap in (1,16):
   good,*rest=no_conflict(p,cap)
   assert good,(offset,cap,rest)
   print('PLANTED_N98',offset,'CAP',cap,'PASS',flush=True)
 original=source()
 survivors=[];extended=[]
 t=time.monotonic()
 for offset in range(624):
  states=projection(offset,original)
  if (states[0][1]^0x80000000)&states[0][0]:
   continue
  good,*stats=no_conflict(states,1)
  if not good:continue
  survivors.append(offset)
  better=no_conflict(states,16)
  if better[0]:extended.append(offset)
  else:print('ORIGINAL_N98_EXCLUDED',offset,'BY_EXTRA',better[2:],flush=True)
  if len(survivors)%8==0:
   print('CHECKPOINT',len(survivors),'N98_SURVIVORS',len(extended),'SECONDS',round(time.monotonic()-t,1),flush=True)
 assert len(survivors)==29,len(survivors)
 assert not extended,extended
 print('RESULT',json.dumps({'original_source_sha256':SOURCE_SHA,'selected_payload_decoded':False,'seed_words':98,'real_offsets_tested':624,'simple_survivors':survivors,'extended_survivors':extended,'extended_excluded':len(survivors)-len(extended),'max_unknown_bits_per_three_word_key_term':16},sort_keys=True),flush=True)

if __name__=='__main__':main()
