#!/usr/bin/env python3
"""Source-local K04 cross-slot AX retry/PT 16-bit xoroshiro128++ gap solver.

Only aggregate outcomes printed; original state/coupon/component is private.
Run with --root resources in a private local checkout, never public CI.
Reference solver: agents/agent3/k04_xoropp_anchored_gap_synthetic.py.
"""
import argparse,hashlib,json,os,random,re,sys
from pathlib import Path
if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
    raise SystemExit('Source-local experiment: refuse public CI')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'agent3'))
from k04_xoropp_anchored_gap_synthetic import solve,stream

PINS={
 'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 'evidence/transfers/transfer-audit.jsonl':'32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
 'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'}
def source(root):
 for path,sha in PINS.items():
  assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,('source mismatch',path)
 rows=[]
 for line in (root/'evidence/print/spool-reconstruction.log').read_text().splitlines():
  if 'JOB=PS-261003-0417 ' not in line: continue
  rows.append(dict(re.findall(r'([A-Z]+)=([^\s]+)',line)))
 assert len(rows)==4
 def one(attempt):
  matches=[x for x in rows if x['STATE']=='REQUESTED' and x['ATTEMPT']==attempt and x['CLASS']=='RECOVER']
  assert len(matches)==1
  return bytes.fromhex(matches[0]['PAYLOAD'])
 first,last=one('1'),one('3')
 audit=[json.loads(line) for line in (root/'evidence/transfers/transfer-audit.jsonl').read_text().splitlines()]
 entries={(v['seq'],v['attempt']):bytes.fromhex(v['checkpoint']) for v in audit if v['kind']=='CHUNK' and v['transfer']=='AX-7782'}
 assert len(entries)==16 and all(len(x)==2 for x in entries.values())
 mixed=b''.join(entries[(s,1 if s%2==0 else 2)] for s in range(8))
 bits=[x&1 for x in mixed]
 raw=bytes(sum(bits[i+j]<<j for j in range(8)) for i in (0,8))
 assert raw==bytes.fromhex('50D4') and all(x.bit_count()%2==0 for x in raw)
 payload=bytes(x&0x7f for x in raw)
 assert payload==b'PT'
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 acc=json.loads((root/'acceptance.json').read_text())
 mask=bytes.fromhex(route['K04']['masked_component'])
 commitment=acc['slot_sha256']['K04']
 anchors=[int.from_bytes(x,'big') for x in (raw,raw[::-1],payload,payload[::-1])]
 return (first,last),mask,commitment,anchors
def decode(blob,order,swap):
 xs=[int.from_bytes(blob[i:i+8],order) for i in (0,8)]
 return xs[::-1] if swap else xs
def encode(words,order,swap):
 xs=words[::-1] if swap else words
 return b''.join(x.to_bytes(8,order) for x in xs)
def controls():
 rng=random.Random(20261128)
 for i in range(10):
  a,b=rng.getrandbits(64),rng.getrandbits(64)
  ys=stream(a,b,6);obs={j:ys[j] for j in (0,1,4,5)}
  verdict,got=solve(obs,a&0xffff,5000)
  assert verdict=='sat' and got==(a,b),('planted',i,verdict)
  for order in ('big','little'):
   for swap in (False,True):
    assert decode(encode(ys[2:4],order,swap),order,swap)==ys[2:4]
 a,b=rng.getrandbits(64),rng.getrandbits(64);ys=stream(a,b,6)
 for bit in (0,17,39,63):
  obs={j:ys[j] for j in (0,1,4,5)};obs[4]^=1<<bit
  verdict,_=solve(obs,a&0xffff,5000)
  assert verdict=='unsat',('poison',bit,verdict)
 print('PLANTED_CONTROLS=10/10 full middle replay; poisoned=4/4 UNSAT; serializer=PASS')
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--root',type=Path,required=True)
 p.add_argument('--timeout-ms',type=int,default=5000)
 p.add_argument('--start',type=int,default=0)
 p.add_argument('--count',type=int,default=16)
 p.add_argument('--skip-controls',action='store_true')
 arg=p.parse_args()
 assert 0<=arg.start<16 and 1<=arg.count<=16-arg.start and 100<=arg.timeout_ms<=600000
 if not arg.skip_controls:controls()
 (first,last),mask,commit,anchors=source(arg.root)
 tallies={'unsat':0,'unknown':0,'sat':0}
 for case in range(arg.start,arg.start+arg.count):
  aidx=case//4;layout=case%4;order=('little','big')[layout//2];swap=bool(layout%2)
  y0,y1=decode(first,order,swap);y4,y5=decode(last,order,swap)
  status,state=solve({0:y0,1:y1,4:y4,5:y5},anchors[aidx],arg.timeout_ms)
  assert status in tallies,('solver',status)
  tallies[status]+=1
  if state is not None:
   predicted=encode(stream(*state,6)[2:4],order,swap)
   coupon=bytes(x^y for x,y in zip(predicted,mask))
   if hashlib.sha256(coupon).hexdigest()==commit:
    raise RuntimeError('PRIVATE COMMITMENT HIT: escrow privately, never log candidate')
  print('AX_PT_16ANCHOR case=%02d status=%s K04_hit=0'%(case,status),flush=True)
 print('AX_PT_16ANCHOR bounded_tallies=',tallies)
if __name__=='__main__':main()
