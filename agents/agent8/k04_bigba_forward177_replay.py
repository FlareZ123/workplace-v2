#!/usr/bin/env python3
"""Source-private K04 forward big/BA replay of complete first-request xoroshiro states.

Reconstruct 24 later generator words after intact REQUESTED1, serialize as
12 big-endian/BA full packets, and test *all 177* 16-byte contiguous windows
against the unchanged full K04 SHA after original routing XOR. Relative to a
9-hidden-packet × 16-slip 144-window baseline, the 0..176 stream gives 33
new raw-stream positions [144..176], corresponding to absolute producer offsets [160..192].
Exact source states and accepted component remain mode0600 private. Not CI/PDF.
"""
import argparse,hashlib,json,os,random,time
from pathlib import Path
import k04_reverse_littleba_private as r

def advance(state):
 a,b=state;t=a^b
 return (r.e.rol(a,49)^t^((t<<21)&r.e.M),r.e.rol(t,28))

def forward_bytes(state,n=24,endian='big',order='ba'):
 p=advance(advance(state))
 out=[]
 for j in range(n):
  out.append((r.e.rol((p[0]+p[1])&r.e.M,17)+p[0])&r.e.M)
  p=advance(p)
 buf=bytearray()
 for j in range(0,n,2):
  pair=out[j:j+2]
  if order=='ba':pair.reverse()
  buf.extend(b''.join(x.to_bytes(8,endian) for x in pair))
 assert len(buf)==192
 return bytes(buf)

def source():
 _,_,mask,target=r.source() # enforces SHA256 of original non-PDF inputs
 p=r.RES/'evidence/print/spool-reconstruction.log'
 lines=p.read_text().splitlines()
 line=[s for s in lines if 'JOB=PS-261003-0417 ' in s and 'ATTEMPT=1 ' in s
       and 'STATE=REQUESTED ' in s and 'CLASS=RECOVER ' in s]
 if len(line)!=1:raise ValueError('Expected exact one original REQUESTED1')
 return r.parse_packet(line[0],'big','ba'),mask,target

def scan(lo,count,folder,ms,retry_ms):
 if not(0<=lo<4096 and 1<=count<=4096-lo and 100<=ms<=retry_ms<=30000):raise ValueError('bad scope')
 folder=r.private_directory(folder)
 first,mask,target=source();obs={0:first[0],1:first[1]}
 stamp=hashlib.sha256((r.stamp('big','ba',r.P16)+'-forward177-v1').encode()).hexdigest()
 counts={'P16_cubes':0,'P16_unsat_empty':0,'P16_unknown':0,'P16_unsat_with_model':0,
         'source_compatible_states':0,'full177_commitment_checks':0,
         'baseline144_commitment_checks':0,'new33_commitment_checks':0,
         'baseline144_hits':0,'new33_hits':0,'all177_hits':0}
 start=time.monotonic()
 for parent in range(lo,lo+count):
  for child in range(16):
   cube=parent|(child<<12)
   path=folder/f'bigBA_forward177_parent{parent:04d}_child{child:02d}.json'
   rec=None
   if path.exists():
    if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Unsafe original state cache')
    rec=json.loads(path.read_text())
    if rec['cube']!=cube or rec['stamp']!=stamp:raise ValueError('State cache mismatch')
   if rec is None or rec['terminal']=='unknown':
    fixed=sum(((cube>>j)&1)<<bit for j,bit in enumerate(r.P16))
    states,status=r.e.solve(obs,fixed,r.P16,ms,True)
    if status=='unknown' and retry_ms>ms:
     more,status=r.e.solve(obs,fixed,r.P16,retry_ms,True)
     states=list(set(states).union(more))
    prior=[(int(a,16),int(b,16)) for a,b in rec['states']] if rec else []
    states=sorted(set(states).union(prior))
    rec={'cube':cube,'stamp':stamp,'terminal':status,
         'states':[[f'{a:016X}',f'{b:016X}'] for a,b in states]}
    r.atomic(path,rec)
   counts['P16_cubes']+=1
   if rec['terminal']=='unknown':counts['P16_unknown']+=1
   elif rec['states']:counts['P16_unsat_with_model']+=1
   else:counts['P16_unsat_empty']+=1
   for state in [(int(a,16),int(b,16)) for a,b in rec['states']]:
    raw=forward_bytes(state)
    counts['source_compatible_states']+=1
    for offset in range(177):
     component=bytes(x^y for x,y in zip(raw[offset:offset+16],mask))
     valid=hashlib.sha256(component).hexdigest()==target
     counts['all177_hits']+=int(valid)
     counts['full177_commitment_checks']+=1
     if 0<=offset<=143:
      counts['baseline144_commitment_checks']+=1
      counts['baseline144_hits']+=int(valid)
     else:
      counts['new33_commitment_checks']+=1
      counts['new33_hits']+=int(valid)
     if valid:r.private_coupon(folder/'K04_ORIGINAL_HASH_HIT.json',offset,component,'K04')
  print('SOURCE_SAFE_AGGREGATE',json.dumps({'original_parent':[lo,parent+1],
       'original_source_or_state_values_printed':False,
       'elapsed_s':round(time.monotonic()-start,2),'counts':counts},sort_keys=True),flush=True)
 return counts

def synthetic():
 for seed in range(20000,20008):
  rng=random.Random(seed);s=(rng.getrandbits(64),rng.getrandbits(64))
  raw=forward_bytes(s)
  # cross-validate independent 24-word stream generated from advancing state
  p=advance(advance(s));seq=[]
  for i in range(24):
   seq.append(r.e.stream(*p,1)[0]);p=advance(p)
  exp=b''.join(b''.join(w.to_bytes(8,'big') for w in reversed(seq[j:j+2])) for j in range(0,24,2))
  assert raw==exp
  mask=rng.randbytes(16)
  for offset in (0,1,15,16,143,144,159,160,176):
   value=bytes(x^y for x,y in zip(raw[offset:offset+16],mask))
   target=hashlib.sha256(value).hexdigest()
   found=[j for j in range(177) if hashlib.sha256(bytes(x^y for x,y in zip(raw[j:j+16],mask))).hexdigest()==target]
   assert found==[offset]
 print({'source_free':True,'forward_full_sha_positives':8*9,'distinct_added_positions':[144,159,160,176]})

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--synthetic',action='store_true')
 p.add_argument('--parent-start',type=int,default=1371)
 p.add_argument('--parent-count',type=int,default=1)
 p.add_argument('--private-dir',type=Path)
 p.add_argument('--timeout-ms',type=int,default=1500)
 p.add_argument('--retry-ms',type=int,default=5000)
 a=p.parse_args()
 if a.synthetic:synthetic()
 else:
  if not a.private_dir:p.error('--private-dir required')
  scan(a.parent_start,a.parent_count,a.private_dir,a.timeout_ms,a.retry_ms)
