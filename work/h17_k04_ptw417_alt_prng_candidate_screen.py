#!/usr/bin/env python3
"""Candidate-generating PRNG screen from the PTW-417 signed four-bay state.

No raw candidate is printed. If a K04 commitment hit occurs, write it to a
0600 local file only; do not commit that file or publish the component.
"""
import argparse, json, re, hashlib, random, os
from pathlib import Path
try:
 import numpy as np
 NUMPY_AVAILABLE=True
 NUMPY_VERSION=np.__version__
except ImportError:
 np=None
 NUMPY_AVAILABLE=False
 NUMPY_VERSION=None
MASK32=(1<<32)-1; MASK64=(1<<64)-1
ROOT=Path(__file__).resolve().parents[1]

def rotl32(x,k): return ((x<<k)|(x>>(32-k)))&MASK32
def rotl64(x,k): return ((x<<k)|(x>>(64-k)))&MASK64

def xoshiro128_next(s,variant):
 s0,s1,s2,s3=s
 out=((rotl32((s1*5)&MASK32,7)*9)&MASK32) if variant=='xoshiro128**' else ((rotl32((s0+s3)&MASK32,7)+s0)&MASK32)
 t=(s1<<9)&MASK32; s2^=s0; s3^=s1; s1^=s2; s0^=s3; s2^=t; s3=rotl32(s3,11)
 return out,(s0&MASK32,s1&MASK32,s2&MASK32,s3&MASK32)

def xoroshiro_next(s,variant):
 s0,s1=s
 out=((rotl64((s0+s1)&MASK64,17)+s0)&MASK64) if variant=='xoroshiro128++' else ((rotl64((s0*5)&MASK64,7)*9)&MASK64)
 s1^=s0; s0=(rotl64(s0,49)^s1^((s1<<21)&MASK64))&MASK64; s1=rotl64(s1,28)
 return out,(s0,s1)

def xorshift128plus_next(s):
 s1,s0=s; s1&=MASK64; s0&=MASK64; new0=s0; s1^=(s1<<23)&MASK64; new1=(s1^s0^(s1>>17)^(s0>>26))&MASK64
 return (new1+s0)&MASK64,(new0,new1)

def packet32(state,variant,warmup,endian,reverse):
 s=tuple(state)
 for _ in range(warmup): _,s=xoshiro128_next(s,variant)
 out=[]
 for _ in range(4): x,s=xoshiro128_next(s,variant); out.append(x)
 if reverse: out.reverse()
 return b''.join(x.to_bytes(4,endian) for x in out)

def packet64(state,variant,warmup,endian,reverse):
 s=tuple(state); step=xorshift128plus_next if variant=='xorshift128+' else lambda z:xoroshiro_next(z,variant)
 for _ in range(warmup): _,s=step(s)
 out=[]
 for _ in range(2): x,s=step(s); out.append(x)
 if reverse: out.reverse()
 return b''.join(x.to_bytes(8,endian) for x in out)

def packet_mt(seed,warmup,mode,endian,reverse):
 rng=random.Random(seed)
 if mode=='MT128':
  for _ in range(warmup): rng.getrandbits(128)
  return rng.getrandbits(128).to_bytes(16,endian)
 for _ in range(warmup): rng.getrandbits(32)
 out=[rng.getrandbits(32) for _ in range(4)]
 if reverse: out.reverse()
 return b''.join(x.to_bytes(4,endian) for x in out)

def packet_pcg(seed,warmup,endian,reverse,dxsm=False):
 bg=np.random.PCG64DXSM(seed) if dxsm else np.random.PCG64(seed); rng=np.random.Generator(bg)
 for _ in range(warmup): rng.bit_generator.random_raw()
 out=[int(rng.bit_generator.random_raw()) for _ in range(2)]
 if reverse: out.reverse()
 return b''.join(x.to_bytes(8,endian) for x in out)

# Acceptance/mask are read from supplied resources, never hard-coded.
ap=argparse.ArgumentParser()
ap.add_argument('--resources',type=Path,default=ROOT/'resources')
ap.add_argument('--candidate-output',type=Path,default=None)
args=ap.parse_args()
RES=args.resources; EV=RES/'evidence'
accept=json.loads((RES/'acceptance.json').read_text())
routing=json.loads((EV/'recovery-routing.json').read_text())
target_hash=accept['slot_sha256']['K04']; mask=bytes.fromhex(routing['K04']['masked_component'])
assert len(target_hash)==64 and len(mask)==16
rows=[json.loads(x) for x in (EV/'maintenance/seal-receipts.jsonl').read_text().splitlines() if x.strip()]
by_bay={}
for bay in 'ABCD':
 xs=[r for r in rows if r.get('permit')=='PTW-417' and r.get('bay')==bay and r.get('state')=='CLOSED' and r.get('fitment')=='AS_LEFT' and r.get('signed') is True]
 assert xs
 max_revision=max(int(x['revision']) for x in xs)
 latest=[x for x in xs if int(x['revision'])==max_revision]
 assert len(latest)==1, (bay,max_revision,len(latest))
 rec=latest[0]
 by_bay[bay]=bytes.fromhex(rec['serial'].split('-',1)[1])
# PS-0417 ACK2 is a comparison control, not a seed.
spool=(EV/'print/spool-reconstruction.log').read_text()
m=re.search(r'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32})',spool)
assert m; observed=bytes.fromhex(m.group(1))

# Synthetic reference checks.
assert xoshiro128_next((1,2,3,4),'xoshiro128**')[0]==0x2D00
assert xoshiro128_next((1,2,3,4),'xoshiro128++')[0]==0x281

hits=[]; exact_payload_matches=0; configurations=0
for variant in ('xoshiro128**','xoshiro128++'):
 for order in (('A','B','C','D'),('B','D','A','C')):
  for endian in ('big','little'):
   for warmup in range(65):
    for out_endian in ('big','little'):
     for reverse in (False,True):
      st=tuple(int.from_bytes(by_bay[b],endian) for b in order)
      out=packet32(st,variant,warmup,out_endian,reverse); configurations+=1
      exact_payload_matches += (out==observed)
      cand=bytes(x^y for x,y in zip(out,mask))
      if hashlib.sha256(cand).hexdigest()==target_hash: hits.append((variant,'4x32',order,endian,warmup,out_endian,reverse,cand))
for variant in ('xoroshiro128++','xoroshiro128**','xorshift128+'):
 for order in (('A','B','C','D'),('B','D','A','C')):
  for serial_endian in ('big','little'):
   for state_endian in ('big','little'):
    for swap in (False,True):
     raw=b''.join(by_bay[b] if serial_endian=='big' else by_bay[b][::-1] for b in order)
     st=[int.from_bytes(raw[:8],state_endian),int.from_bytes(raw[8:],state_endian)]
     if swap: st.reverse()
     for warmup in range(65):
      for out_endian in ('big','little'):
       for reverse in (False,True):
        out=packet64(tuple(st),variant,warmup,out_endian,reverse); configurations+=1
        exact_payload_matches += (out==observed)
        cand=bytes(x^y for x,y in zip(out,mask))
        if hashlib.sha256(cand).hexdigest()==target_hash: hits.append((variant,'2x64',order,serial_endian,state_endian,swap,warmup,out_endian,reverse,cand))
for variant in (('MT32','MT128','PCG64','PCG64DXSM') if NUMPY_AVAILABLE else ('MT32','MT128')):
 for order in (('A','B','C','D'),('B','D','A','C')):
  for serial_endian in ('big','little'):
   raw=b''.join(by_bay[b] if serial_endian=='big' else by_bay[b][::-1] for b in order)
   seed=int.from_bytes(raw,'big')
   for warmup in range(33):
    for out_endian in ('big','little'):
     for reverse in ((False,) if variant=='MT128' else (False,True)):
      out=packet_mt(seed,warmup,variant,out_endian,reverse) if variant.startswith('MT') else packet_pcg(seed,warmup,out_endian,reverse,variant=='PCG64DXSM')
      configurations+=1; exact_payload_matches += (out==observed)
      cand=bytes(x^y for x,y in zip(out,mask))
      if hashlib.sha256(cand).hexdigest()==target_hash: hits.append((variant,'seed128',order,serial_endian,warmup,out_endian,reverse,cand))

candidate_saved=False
if hits and args.candidate_output is not None:
 args.candidate_output.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(args.candidate_output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f: f.write(hits[0][-1])
 candidate_saved=True
print(json.dumps({'experiment':'PTW-417 raw quartet alternative PRNG candidate screen','configurations':configurations,
 'K04_commitment_hits':len(hits),'exact_matches_to_selected_ACK2_payload':exact_payload_matches,
 'synthetic_known_answer_checks':'passed','target_K04_hash_used_only_as_filter':True,
 'candidate_saved_locally':candidate_saved,'hit_configurations':[tuple(x[:-1]) for x in hits],
 'numpy_available':NUMPY_AVAILABLE,'numpy_version':NUMPY_VERSION,
 'limitations':['PTW-417 to PS-0417 relation is not source-authenticated','only listed PRNGs, state layouts, serializers and warm-up ranges tested']},indent=2,default=str))
