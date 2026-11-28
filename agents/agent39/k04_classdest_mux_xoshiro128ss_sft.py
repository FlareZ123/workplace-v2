#!/usr/bin/env python3
"""K04: source-pinned class/destination-multiplexed xoshiro128** source test.

Read-only; never emits original packet bytes, inferred states, candidate bytes or digests.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
from random import Random

ROOT=Path(__file__).resolve().parents[2] / 'resources'
SOURCE=ROOT/'evidence/print/spool-reconstruction.log'
PIN='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
MASK32=(1<<32)-1

def rotl(v,k):return ((v<<k)|(v>>(32-k)))&MASK32
def rotr(v,k):return ((v>>k)|(v<<(32-k)))&MASK32

def advance(s):
 a,b,c,d=s
 t=(b<<9)&MASK32
 c^=a;d^=b;b^=c;a^=d;c^=t;d=rotl(d,11)
 return (a,b,c,d)

def next_word(s):
 a,b,c,d=s
 y=(rotl((b*5)&MASK32,7)*9)&MASK32
 return y,advance(s)

def raw_s1(y):return (rotr((y*pow(9,-1,1<<32))&MASK32,7)*pow(5,-1,1<<32))&MASK32

def obs(s):
 v=[]
 for i in range(4):
  v.append(s[1]);s=advance(s)
 return sum(u<<(32*i) for i,u in enumerate(v))

def compute_inverse():
 # Columns of 128x128 binary observation map, invert via Gauss Jordan.
 columns=[]
 for i in range(128):
  s=tuple(1<<(i%32) if j==i//32 else 0 for j in range(4))
  columns.append(obs(s))
 rows=[]
 for r in range(128):
  mask=sum(((columns[c]>>r)&1)<<c for c in range(128))
  rows.append(mask | (1<<(128+r)))
 for c in range(128):
  pivot=next((r for r in range(c,128) if (rows[r]>>c)&1),None)
  if pivot is None:raise AssertionError('four native output words do not uniquely fix state')
  rows[c],rows[pivot]=rows[pivot],rows[c]
  for r in range(128):
   if r!=c and ((rows[r]>>c)&1):rows[r]^=rows[c]
 assert all((v&((1<<128)-1))==1<<i for i,v in enumerate(rows))
 return tuple(v>>128 for v in rows)

INV=compute_inverse()
def invert_first_four(ys):
 o=sum(raw_s1(y)<<(32*i) for i,y in enumerate(ys))
 value=sum(((row&o).bit_count()&1)<<i for i,row in enumerate(INV))
 s=tuple((value>>(32*j))&MASK32 for j in range(4))
 assert obs(s)==o
 return s

def parse_source():
 raw=SOURCE.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==PIN
 rows=[]
 for line in raw.decode().splitlines()[1:]:
  kv=dict(re.findall(r'([A-Z]+)=([^ ]+)',line))
  assert len(bytes.fromhex(kv['PAYLOAD']))==16
  rows.append({'kv':kv,'raw':bytes.fromhex(kv['PAYLOAD'])})
 assert len(rows)==133
 assert [int(r['kv']['JOB'][-4:]) for r in rows[:128]]==list(range(300,428))
 assert [r['kv']['ATTEMPT'] for r in rows[128:131]]==['1','2','3']
 return rows

def unpack(buf, endian,reverse):
 words=[int.from_bytes(buf[i:i+4],endian) for i in range(0,16,4)]
 return tuple(reversed(words)) if reverse else tuple(words)
def pack(words,endian,reverse):
 ws=tuple(reversed(words)) if reverse else words
 return b''.join(x.to_bytes(4,endian) for x in ws)

def draw_packet(state):
 vals=[]
 for _ in range(4):
  y,state=next_word(state); vals.append(y)
 return tuple(vals),state

def key_fn(mode,r):
 k=r['kv']
 return k['CLASS'] if mode=='class' else k['DEST'] if mode=='dest' else (k['CLASS'],k['DEST'])

def run_synthetic():
 rng=Random(20261128)
 for endian in ('big','little'):
  for reverse in (False,True):
   for mode in ('class','dest','classdest'):
    states={}
    synthetic=[]
    # Each class/dest group has own independent continuous stream; interleave 100 packets.
    for i in range(150):
     cls=('RECOVER','STORES','LABEL')[rng.randrange(3)]
     dst=('bench','desk','store')[rng.randrange(3)]
     k=cls if mode=='class' else dst if mode=='dest' else (cls,dst)
     if k not in states:states[k]=tuple(rng.getrandbits(32) for _ in range(4))
     output,states[k]=draw_packet(states[k])
     synthetic.append((k,pack(output,endian,reverse)))
    recovered={};matches=0
    for k,buf in synthetic:
     if k not in recovered:
      recovered[k]=invert_first_four(unpack(buf,endian,reverse))
     out,recovered[k]=draw_packet(recovered[k]); assert pack(out,endian,reverse)==buf
     matches+=1
    assert matches==150
 print('SYNTHETIC independent cohort streams 12/12 orientations SELECTOR PASSED')

def evaluate():
 records=parse_source();regular=records[:128]
 t=json.loads((ROOT/'acceptance.json').read_text())
 route=json.loads((ROOT/'evidence/recovery-routing.json').read_text())
 assert t['slot_sha256']['K04'] and route['K04']['masked_component']
 mask=bytes.fromhex(route['K04']['masked_component'])
 target=t['slot_sha256']['K04']
 summaries=[]
 for mode in ('class','dest','classdest'):
  cohorts=defaultdict(list)
  for r in regular: cohorts[key_fn(mode,r)].append(r)
  for endian in ('little','big'):
   for reverse in (False,True):
    tested=matched=holds1=holds2=0
    cross_model_states={}
    for k,seq in sorted(cohorts.items(),key=lambda kv:str(kv[0])):
     state=invert_first_four(unpack(seq[0]['raw'],endian,reverse))
     cross_model_states[k]=state
     for pos,r in enumerate(seq):
      out,state=draw_packet(state)
      if pos==0: assert pack(out,endian,reverse)==r['raw']
      else:
       tested+=1
       if pack(out,endian,reverse)==r['raw']:matched+=1
       if pos==1:holds1+=pack(out,endian,reverse)==r['raw']
       if pos==2:holds2+=pack(out,endian,reverse)==r['raw']
     cross_model_states[k]=state
    # Local-selected source timeline: first REQUESTED1, then unknown physical ACK2.
    # Consume intact 18:01 REQUESTED1 as one packet in its metadata cohort.
    # By construction this is an uncalibrated hypothesis if historical holdouts miss.
    k=key_fn(mode,records[128]);st=cross_model_states[k]
    first,st=draw_packet(st)
    first_match=pack(first,endian,reverse)==records[128]['raw']
    coupon,st=draw_packet(st)
    buf=pack(coupon,endian,reverse)
    component=bytes(a^b for a,b in zip(buf,mask))
    target_hit=hashlib.sha256(component).hexdigest()==target
    later,st=draw_packet(st)
    later_match=pack(later,endian,reverse)==records[130]['raw']
    summaries.append((mode,endian,int(reverse),len(cohorts),tested,matched,int(holds1),int(holds2),int(first_match),int(later_match),int(target_hit)))
 print('ORIGINAL model,endian,reverse,cohorts,heldout_packets,matched,secondpkt,thirdpkt,request1,request3,K04_hit')
 for s in summaries:print('ORIGINAL',*s,sep='\t')
 assert len(summaries)==12 and sum(s[-1] for s in summaries)==0
 return summaries
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--root',type=Path,default=ROOT,help='Path with evidence/, acceptance.json')
 args=parser.parse_args()
 ROOT=args.root.resolve()
 SOURCE=ROOT/'evidence/print/spool-reconstruction.log'
 run_synthetic();evaluate()