#!/usr/bin/env python3
"""Local-only P16/P20 exact later-first xoroshiro128++ candidate search.

Uses ONLY intact REQUESTED3 to fit the producer. The disputed RECOVER ACK2
is not used or opened. Every complete inferred coupon is checked against the
original K04 commitment before an optional earlier-packet diagnostic.
P12 is split exactly into 16 P16 children; any P16 timeout can be split
exactly into 16 P20 grandchildren. Only terminal UNSAT closes a subcube.
Original-source execution is CI denied, and matches stay outside the repo.
"""
import argparse,ctypes,hashlib,json,multiprocessing as mp,os,random,re,time
from pathlib import Path
M=(1<<64)-1
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
P16=P12+(4,5,6,7)
P20=P16+(8,9,10,11)
SPOOL_HASH='7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def rol(x,n):return ((x<<n)|(x>>(64-n)))&M
def ror(x,n):return ((x>>n)|(x<<(64-n)))&M
def draw(a,b):return (rol((a+b)&M,17)+a)&M
def advance(a,b):
 t=a^b
 return rol(a,49)^t^((t<<21)&M),rol(t,28)
def invert(a,b):
 t=ror(b,28)
 x=ror(a^t^((t<<21)&M),49)
 return x,x^t
def firstpair(a,b):
 y0=draw(a,b);a,b=advance(a,b)
 return y0,draw(a,b)
def earlier_words(a,b,n=20):
 out=[]
 for _ in range(n):
  a,b=invert(a,b);out.append(draw(a,b))
 return out
def pack(w,endian,order):
 if order=='ba':w=w[::-1]
 return b''.join(x.to_bytes(8,endian) for x in w)
def xor(*items):
 vals=[v for v in items if v!='false']
 return 'false' if not vals else vals[0] if len(vals)==1 else '(xor '+' '.join(vals)+')'

def circuit(obs,anchor,bits=P16,timeout_ms=350):
 """Full-width QF_UF Boolean equation for first TWO 64-bit outputs."""
 lines=['(set-logic QF_UF)','(set-option :sat.anf true)',
        '(set-option :sat.anf.exlin true)',f'(set-option :timeout {timeout_ms})']
 def put(name,expr):
  lines.append(f'(define-fun {name} () Bool {expr})');return name
 def implied(a,y,s):
  v=['false']*64
  for j in range(63):
   v[j+1]=put(f'v{s}_{j+1}',f'({"and" if y>>j&1 else "or"} {a[j]} {v[j]})')
  u=['false']*64;t=[]
  for k in range(64):
   j=(k+17)&63
   tk=put(f't{s}_{k}',xor(a[j],v[j],u[k],'true' if y>>j&1 else 'false'))
   t.append(tk)
   if k<63:u[k+1]=put(f'u{s}_{k+1}',f'(ite {tk} {u[k]} {a[k]})')
  return t
 a=[f'a0_{i}' for i in range(64)]
 lines.extend(f'(declare-const {x} Bool)' for x in a)
 t=implied(a,obs[0],'0')
 a1=[put(f'a1_{j}',xor(a[(j-49)&63],t[j],t[j-21] if j>=21 else 'false')) for j in range(64)]
 t1=[put(f'w1_{j}',xor(a1[j],t[(j-28)&63])) for j in range(64)]
 required=implied(a1,obs[1],'1')
 lines.extend(f'(assert (= {t1[j]} {required[j]}))' for j in range(64))
 for j in bits:lines.append(f'(assert (= a0_{j} {"true" if anchor>>j&1 else "false"}))')
 lines.append('(check-sat)')
 return '\n'.join(lines)+'\n'

def exact_states(obs,cube,timeout_ms=350,max_models=32,positions=P16):
 anchor=sum(((cube>>j)&1)<<p for j,p in enumerate(positions))
 lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
 lib.Z3_mk_config.restype=P;lib.Z3_mk_context.argtypes=[P]
 lib.Z3_mk_context.restype=P;lib.Z3_del_config.argtypes=[P]
 lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
 lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 def ask(s):return (lib.Z3_eval_smtlib2_string(ctx,s.encode()) or b'').decode().strip()
 try:
  status=ask(circuit(obs,anchor,bits=positions,timeout_ms=timeout_ms))
  states=[]
  while status=='sat':
   raw=ask('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
   bits={int(j):int(v=='true') for j,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',raw)}
   if len(bits)!=64:raise RuntimeError('Incomplete SAT model')
   a=sum(bits[j]<<j for j in range(64))
   b=(ror((obs[0]-a)&M,17)-a)&M
   if firstpair(a,b)!=tuple(obs):raise RuntimeError('Model replay mismatch')
   states.append((a,b))
   if len(states)>=max_models:return states,'unknown'
   change=' '.join((f'(not a0_{j})' if bits[j] else f'a0_{j}') for j in range(64))
   ask('(assert (or '+change+'))');status=ask('(check-sat)')
  if status not in ('unsat','unknown'):raise RuntimeError('Solver status '+status)
  return states,status
 finally:lib.Z3_del_context(ctx)

def check_state(state,mask,goal,endian,order):
 prev=earlier_words(*state,20);hits=[]
 for j in range(2,20):
  coupon=pack((prev[j-1],prev[j-2]),endian,order)
  component=bytes(x^y for x,y in zip(coupon,mask))
  if hashlib.sha256(component).hexdigest()==goal:hits.append(component)
 return 18,hits

def task(args):
 parent,first,mask,goal,endian,order,ms,retry,split=args
 totals=dict(children=0,terminal_unsat=0,terminal_unknown=0,models=0,
             checks=0,hits=0,p20_queries=0,p20_unsat=0,p20_unknown=0)
 found=[]
 for child in range(16):
  cube=parent|(child<<12)
  states,status=exact_states(first,cube,ms)
  if status=='unknown' and split:
   submodels=set(states);p20_status=[]
   for sub in range(16):
    more,terminal=exact_states(first,cube|(sub<<16),retry,positions=P20)
    totals['p20_queries']+=1
    totals['p20_unsat']+=int(terminal=='unsat')
    totals['p20_unknown']+=int(terminal=='unknown')
    submodels.update(more);p20_status.append(terminal)
   states=list(submodels)
   status='unsat' if all(x=='unsat' for x in p20_status) else 'unknown'
  elif status=='unknown' and not states and retry>ms:
   states,status=exact_states(first,cube,retry)
  totals['children']+=1
  totals['terminal_unsat']+=int(status=='unsat')
  totals['terminal_unknown']+=int(status=='unknown')
  totals['models']+=len(states)
  for state in states:
   num,hit=check_state(state,mask,goal,endian,order)
   totals['checks']+=num;totals['hits']+=len(hit);found.extend(hit)
 return parent,totals,found

def source(root,endian,order):
 log=(root/'evidence/print/spool-reconstruction.log').read_bytes()
 if hashlib.sha256(log).hexdigest()!=SPOOL_HASH:raise RuntimeError('Spool checksum')
 pattern=rb'JOB=PS-261003-0417 ATTEMPT=3 STATE=REQUESTED CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench'
 matches=re.findall(pattern,log)
 if len(matches)!=1:raise RuntimeError('Later attempt-3 packet missing')
 raw=bytes.fromhex(matches[0].decode())
 w=(int.from_bytes(raw[:8],endian),int.from_bytes(raw[8:],endian))
 if order=='ba':w=w[::-1]
 rt=json.loads((root/'evidence/recovery-routing.json').read_text())
 acc=json.loads((root/'acceptance.json').read_text())
 mask=bytes.fromhex(rt['K04']['masked_component'])
 goal=acc['slot_sha256']['K04']
 assert len(mask)==16 and re.fullmatch('[a-f0-9]{64}',goal)
 return w,mask,goal

def synthetic():
 rng=random.Random(260113)
 for _ in range(10000):
  a,b=rng.getrandbits(64),rng.getrandbits(64)
  assert invert(*advance(a,b))==(a,b)
 actual=rng.getrandbits(64),rng.getrandbits(64)
 obs=firstpair(*actual)
 parent=sum(((actual[0]>>p)&1)<<j for j,p in enumerate(P12))
 mask=rng.randbytes(16)
 prev=earlier_words(*actual)
 coupon=pack((prev[7],prev[6]),'big','ab')
 goal=hashlib.sha256(bytes(x^y for x,y in zip(coupon,mask))).hexdigest()
 states=[];statuses=[]
 for i in range(16):
  found,status=exact_states(obs,parent|(i<<12),350)
  statuses.append(status);states.extend(found)
 assert actual in states
 assert sum(len(check_state(s,mask,goal,'big','ab')[1]) for s in states)>=1
 for _ in range(5):
  a,b=rng.getrandbits(64),rng.getrandbits(64)
  x=firstpair(a,b)
  cube=sum(((a>>p)&1)<<j for j,p in enumerate(P20))
  found,status=exact_states(x,cube,350,positions=P20)
  assert status=='unsat' and (a,b) in found
 print({'synthetic_only':True,'inverse_roundtrips':10000,
        'P16_child_cases':16,'P20_planted_controls':5,
        'planted_full_commitment_hit':True,
        'P16_terminal_unknown':statuses.count('unknown')},flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--synthetic',action='store_true')
 p.add_argument('--resources-root',type=Path)
 p.add_argument('--endian',choices=['big','little'],default='big')
 p.add_argument('--order',choices=['ab','ba'],default='ab')
 p.add_argument('--start',type=int,default=0)
 p.add_argument('--count',type=int,default=16)
 p.add_argument('--timeout-ms',type=int,default=350)
 p.add_argument('--retry-timeout-ms',type=int,default=700)
 p.add_argument('--workers',type=int,default=4)
 p.add_argument('--split-p20',action='store_true')
 p.add_argument('--escrow',type=Path)
 a=p.parse_args()
 if a.synthetic:return synthetic()
 if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
  p.error('Historical source forbidden in CI')
 if not a.resources_root or not a.escrow:
  p.error('Local sources root and private escrow required')
 if not (0<=a.start<4096 and 0<a.count<=4096-a.start):p.error('Bad P12 interval')
 if not (100<=a.timeout_ms<=a.retry_timeout_ms<=10000):p.error('Bad timeout')
 if not (1<=a.workers<=4):p.error('Max four workers')
 # No repository-side writing of any accepted component.
 if a.escrow.resolve()==Path(__file__).resolve().parents[2] or Path(__file__).resolve().parents[2] in a.escrow.resolve().parents:
  p.error('Escrow must be outside the repository')
 first,mask,goal=source(a.resources_root,a.endian,a.order)
 started=time.monotonic()
 sums=dict(parents=0,closed=0,children=0,terminal_unsat=0,
           terminal_unknown=0,models=0,checks=0,hits=0,
           p20_queries=0,p20_unsat=0,p20_unknown=0)
 with mp.Pool(a.workers) as pool:
  jobs=((parent,first,mask,goal,a.endian,a.order,
         a.timeout_ms,a.retry_timeout_ms,a.split_p20)
        for parent in range(a.start,a.start+a.count))
  for parent,totals,found in pool.imap_unordered(task,jobs,chunksize=1):
   sums['parents']+=1;sums['closed']+=int(totals['terminal_unsat']==16)
   for k,v in totals.items():sums[k]+=v
   if found:
    path=a.escrow.resolve()
    if not path.parent.is_dir():p.error('Private escrow parent absent')
    fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'a') as f:
     os.fchmod(f.fileno(),0o600)
     for c in found:f.write(c.hex().upper()+'\n')
     f.flush();os.fsync(f.fileno())
   if sums['parents']%16==0 or sums['parents']==a.count:
    print({'aggregate_only':True,'hypothesis':'later-first xoroshiro128++',
           'view':a.endian+'/'+a.order,'parent_range_start':a.start,
           'completed':sums['parents'],'elapsed_seconds':round(time.monotonic()-started,2),
           **sums},flush=True)
if __name__=='__main__':main()
