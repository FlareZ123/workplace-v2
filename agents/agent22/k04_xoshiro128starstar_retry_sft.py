"""Recover full xoshiro128** state from a 16-byte printer packet; test retry coupon.

Read-only, source-pinned, exact complete K04 acceptance checks. The selected
ACK2 copied payload is never used for initial-state inference.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/'resources'
SPOOL=ROOT/'evidence/print/spool-reconstruction.log'
ROUTE=ROOT/'evidence/recovery-routing.json'
ACCEPTANCE=ROOT/'acceptance.json'
SHA='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK32=(1<<32)-1
INV9=pow(9,-1,1<<32)
INV5=pow(5,-1,1<<32)

def rotl(v,k):return ((v<<k)|(v>>(32-k)))&MASK32
def rotr(v,k):return ((v>>k)|(v<<(32-k)))&MASK32

def step(x):
 a,b,c,d=x
 t=(b<<9)&MASK32
 c^=a; d^=b; b^=c; a^=d; c^=t; d=rotl(d,11)
 return (a,b,c,d)

def output(x):return (rotl((x[1]*5)&MASK32,7)*9)&MASK32
def inverse_output(v):return (rotr((v*INV9)&MASK32,7)*INV5)&MASK32

def iter_steps(s,n):
 for _ in range(n):
  s=step(s)
  yield s

def state_from_four(observations):
 # Four s1 words are linear in the original 128-bit state.
 bases=[]
 for i in range(128):
  a=[0]*4;a[i//32]=1<<(i%32);bases.append(tuple(a))
 rows=[]
 for _ in range(4):
  for bit in range(32):
   rows.append(sum(((bases[i][1]>>bit)&1)<<i for i in range(128)))
  bases=[step(b) for b in bases]
 eqs=[(row | (((inverse_output(observations[p//32])>>(p%32))&1)<<128)) for p,row in enumerate(rows)]
 pivots={}
 for row in eqs:
  while row & ((1<<128)-1):
   idx=(row & ((1<<128)-1)).bit_length()-1
   if idx in pivots:row^=pivots[idx]
   else:pivots[idx]=row;break
  else:
   if row>>128:return None,len(pivots),False
 if len(pivots)!=128:return None,len(pivots),True
 bits=0
 for idx in sorted(pivots):
  row=pivots[idx]
  others=(row&((1<<idx)-1))&bits
  bit=((row>>128)&1)^(others.bit_count()&1)
  bits|=bit<<idx
 state=tuple((bits>>(32*j))&MASK32 for j in range(4))
 assert all(output(x)==y for x,y in zip([state,*iter_steps(state,3)],observations))
 return state,len(pivots),True

def parse():
 assert hashlib.sha256(SPOOL.read_bytes()).hexdigest()==SHA
 rows=[]
 for line in SPOOL.read_text().splitlines():
  m=re.search(r'JOB=([^ ]+).*?ATTEMPT=(\d+).*?STATE=(\w+).*?CLASS=(\w+).*?PAYLOAD=([0-9A-F]{32})',line)
  if m:rows.append({'job':m[1], 'attempt':int(m[2]),'state':m[3],'class':m[4],'payload':bytes.fromhex(m[5])})
 assert len(rows)==133
 return rows

def words(buf,mode):
 vals=[int.from_bytes(buf[i:i+4],mode&1 and 'big' or 'little') for i in range(0,16,4)]
 if mode&2:vals.reverse()
 return vals

def bytes_from_words(vals,mode):
 if mode&2:vals=list(reversed(vals))
 return b''.join(x.to_bytes(4,mode&1 and 'big' or 'little') for x in vals)

def emit4(state):
 vals=[]
 for _ in range(4):vals.append(output(state));state=step(state)
 return vals,state

def seek_pair(a,b,gap_max=4096):
 matches=[];ranks=[]
 for mode in range(4):
  state,rank,okay=state_from_four(words(a,mode))
  ranks.append(rank)
  if state is None:continue
  wanted=tuple(words(b,mode));x=state
  for gap in range(1,gap_max+1):
   x=step(x)
   if gap>=4:
    vv,_=emit4(x)
    if tuple(vv)==wanted:matches.append({'mode':mode,'gap':gap})
 return matches,ranks

def run(source, mode, mask, wanted, max_gap, synthetic_wanted=None):
 packet=words(source,mode)
 state,rank,ok=state_from_four(packet)
 assert ok and rank==128 and state is not None
 found=[];synthetic=[];x=state
 for gap in range(1,max_gap+1):
  x=step(x)
  if gap<4:continue
  out,_=emit4(x)
  payload=bytes_from_words(out,mode)
  component=bytes(a^b for a,b in zip(payload,mask))
  h=hashlib.sha256(component).digest()
  if h==wanted:
   found.append({'gap':gap,'mode':mode,'component':component.hex().upper()})
  if synthetic_wanted is not None and h==synthetic_wanted:synthetic.append(gap)
 return found,synthetic

def main():
 rows=parse()
 assert rows[128]['job'].endswith('0417') and rows[128]['attempt']==1 and rows[128]['state']=='REQUESTED'
 assert rows[129]['job'].endswith('0417') and rows[129]['attempt']==2 and rows[129]['state']=='ACK'
 assert rows[130]['job'].endswith('0417') and rows[130]['attempt']==3 and rows[130]['state']=='REQUESTED'
 route=json.loads(ROUTE.read_text())
 acceptance=json.loads(ACCEPTANCE.read_text())
 mask=bytes.fromhex(route['K04']['masked_component'])
 wanted=bytes.fromhex(acceptance['slot_sha256']['K04'])
 seeds={'0417-label-ACK1':117,'0417-recover-REQUESTED1':128,
        '0417-recover-REQUESTED3':130,'0420-stores-ACK1':120}
 checks=0;outputs={}
 for name,idx in seeds.items():
  row=rows[idx];found=[]
  for mode in range(4):
   hits,_=run(row['payload'],mode,mask,wanted,65536)
   checks+=65536-3;found+=hits
  outputs[name]={'job':row['job'],'attempt':row['attempt'],'state':row['state'],
                 'original_hits':found}
 original_pairs={}
 for name,i,j in [('0417-recover-requested-flanks',128,130),
                  ('0420-ack-retry-flanks',120,132),
                  ('ordinary-first-two',0,1)]:
  matches,ranks=seek_pair(rows[i]['payload'],rows[j]['payload'])
  assert ranks==[128]*4
  original_pairs[name]=matches
 seed=(0x12345678,0xAABBCCDD,0x9A87BCDE,0xC104C104)
 cases=[]
 for mode in range(4):
  seedpkt=bytes_from_words(emit4(seed)[0],mode)
  z=seed
  for _ in range(137):z=step(z)
  y=bytes_from_words(emit4(z)[0],mode)
  planted=hashlib.sha256(bytes(a^b for a,b in zip(y,mask))).digest()
  hits,positive=run(seedpkt,mode,mask,wanted,140,synthetic_wanted=planted)
  assert positive==[137],positive
  known=seed
  for _ in range(37):known=step(known)
  subsequent=bytes_from_words(emit4(known)[0],mode)
  pairs,ranks=seek_pair(seedpkt,subsequent,40)
  assert {'mode':mode,'gap':37} in pairs
  cases.append({'mode':mode,'stage':positive[0],'source_pair_gap':37})
 print(json.dumps({'generator':'xoshiro128**','source_sha256':SHA,
     'full_original_checks':checks,'source_anchors':outputs,
     'source_pair_matches':original_pairs,'synthetic_positives':cases},indent=2))

if __name__=='__main__':main()
