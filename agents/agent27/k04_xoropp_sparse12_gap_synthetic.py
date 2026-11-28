#!/usr/bin/env python3
"""Synthetic-only xoroshiro128++ erased-middle reconstruction with SPARSE 12-bit initial-a witness.
Derived from Agent 3's conditional 16-low-bit two-packet erasure solver; no H-17 original records, source values,
acceptance, or physical coupon are loaded. Visible outputs indices 0,1,4,5; outputs 2 and 3 erased.
The bit-positions were selected on 2 synthetic train fixtures from 28 three-block geometries;
8 independent synthetic heldout fixtures and deliberate wrong-anchor controls are separate.
Requires libz3.so.4. Source-independent synthetic math test, not a historical K04 recovery.
"""
import ctypes,random,re,sys,time
M=(1<<64)-1

def rol(x,n):return ((x<<n)|(x>>(64-n)))&M
def ror(x,n):return ((x>>n)|(x<<(64-n)))&M
def stream(a,b,n=6):
 out=[]
 for _ in range(n):
  out.append((rol((a+b)&M,17)+a)&M)
  t=a^b;a,b=rol(a,49)^t^((t<<21)&M),rol(t,28)
 return out

def xor(*xs):
 xs=[x for x in xs if x!='false']
 if not xs:return 'false'
 return xs[0] if len(xs)==1 else '(xor '+' '.join(xs)+')'

def circuit(obs,anchor,positions,timeout_ms):
 """obs maps visible stream indices 0,1,4,5 to complete 64bit values."""
 assert set(obs) in ({0,1,4,5},{0,1})
 lines=['(set-logic QF_UF)','(set-option :sat.anf true)',
        '(set-option :sat.anf.exlin true)',f'(set-option :timeout {timeout_ms})']
 def put(name,expr):
  lines.append(f'(define-fun {name} () Bool {expr})');return name
 def implied_t(a,y,s):
  v=['false']*64
  for j in range(63):
   v[j+1]=put(f'v{s}_{j+1}',f'({"and" if (y>>j)&1 else "or"} {a[j]} {v[j]})')
  u=['false']*64;t=[]
  for k in range(64):
   j=(k+17)&63
   tk=put(f't{s}_{k}',xor(a[j],v[j],u[k],'true' if (y>>j)&1 else 'false'))
   t.append(tk)
   if k<63:u[k+1]=put(f'u{s}_{k+1}',f'(ite {tk} {u[k]} {a[k]})')
  return t
 a=[f'a0_{i}' for i in range(64)]
 lines.extend(f'(declare-const {x} Bool)' for x in a)
 t=implied_t(a,obs[0],'0')
 for i in range(1,6):
  an=[put(f'a{i}_{j}',xor(a[(j-49)&63],t[j],t[j-21] if j>=21 else 'false')) for j in range(64)]
  tn=[put(f'tf{i}_{j}',xor(an[j],t[(j-28)&63])) for j in range(64)]
  a,t=an,tn
  if i in obs:
   require=implied_t(a,obs[i],str(i))
   lines.extend(f'(assert (= {t[j]} {require[j]}))' for j in range(64))
 for j in positions:
  lines.append(f'(assert (= a0_{j} {"true" if anchor&(1<<j) else "false"}))')
 lines.append('(check-sat)')
 return '\n'.join(lines)+'\n'

def solve(obs,anchor,positions,timeout_ms=5000):
 lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
 lib.Z3_mk_config.restype=P
 lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
 lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
 lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 try:
  status=(lib.Z3_eval_smtlib2_string(ctx,circuit(obs,anchor,positions,timeout_ms).encode()) or b'').decode().strip()
  if status!='sat':return status,None
  names=' '.join(f'a0_{i}' for i in range(64))
  model=(lib.Z3_eval_smtlib2_string(ctx,f'(get-value ({names}))'.encode()) or b'').decode()
  bits={int(i):int(v=='true') for i,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',model)}
  assert len(bits)==64
  a=sum(v<<i for i,v in bits.items());b=(ror((obs[0]-a)&M,17)-a)&M
  replay=stream(a,b,6)
  assert all(replay[i]==y for i,y in obs.items())
  return status,(a,b)
 finally:lib.Z3_del_context(ctx)

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser()
 parser.add_argument('--suite', choices=('positive','poison','baseline','onebit','twobit','firstpairtwobit','firstpairninebit'), default='positive')
 parser.add_argument('--timeout-ms', type=int, default=5000)
 parser.add_argument('--fresh20', action='store_true', help='independent fresh seeds80903..80922')
 parser.add_argument('--first', type=int, default=0, help='first synthetic seed index')
 parser.add_argument('--count', type=int, default=10, help='maximum synthetic seed cases')
 args=parser.parse_args()
 assert 0<args.timeout_ms<=15000
 # Source-free deterministic fixtures, train first 2; following 8 were withheld.
 seeds=(20261128,12345,2027,2048,124,48,19,123456,8773,2)
 if args.fresh20:
  seeds=tuple(range(80903,80923))
 sparse=(0,1,2,3,22,23,24,25,45,46,47,48)
 assert len(sparse)==12 and len(set(sparse))==12
 assert 0<=args.first<len(seeds) and 1<=args.count<=len(seeds)
 chosen=seeds[args.first:args.first+args.count]
 assert chosen
 baseline=tuple(range(12))
 successes=0
 started=time.monotonic()
 for seed in chosen:
  rng=random.Random(seed)
  actual_a,actual_b=rng.getrandbits(64),rng.getrandbits(64)
  ys=stream(actual_a,actual_b)
  obs={i:ys[i] for i in ((0,1) if args.suite in ('firstpairtwobit','firstpairninebit') else (0,1,4,5))}
  if args.suite=='firstpairninebit':
   # Nine externally supplied sparse state bits, unknown bits0,1,24
   # explicitly enumerated (eight complete 12-bit SAT problems).
   missing=(0,1,24)
   known=tuple(p for p in sparse if p not in missing)
   assert len(known)==9
   known_mask=sum(1<<p for p in known)
   outcomes=[]
   recovered=None
   for assignment in range(8):
    proposed=(actual_a & known_mask) | sum(((assignment>>j)&1)<<p for j,p in enumerate(missing))
    t0=time.monotonic()
    status,state=solve(obs,proposed,sparse,args.timeout_ms)
    outcomes.append((status,round(time.monotonic()-t0,3)))
    if state is not None and stream(*state)[4:6]==ys[4:6]:
     # Independently held-out later two-word packet, never a fit input.
     assert state==(actual_a,actual_b), (seed,'later packet false match')
     assert stream(*state)[2:4]==ys[2:4],(seed,'missing packet mismatch')
     recovered=state
     break
   if recovered is None and not args.fresh20:
    raise AssertionError((seed,'ninebit full-output candidate not recovered',outcomes))
   if recovered is not None:
    successes+=1
   positions=known
   print({'seed':seed,'train':not args.fresh20 and seed in (20261128,12345),
          'suite':args.suite,'observed_output_indices':(0,1),
          'independently_heldout_output_indices':(4,5),
          'erased_output_indices':(2,3),
          'externally_supplied_a0_bits':9,'enumerated_a0_bits':list(missing),
          'branches_executed':len(outcomes),
          'sat_branches':sum(v[0]=='sat' for v in outcomes),
          'unsat_branches':sum(v[0]=='unsat' for v in outcomes),
          'unknown_branches':sum(v[0]=='unknown' for v in outcomes),
          'elapsed_seconds':round(sum(v[1] for v in outcomes),3),
          'complete_state_middle_and_later_recovered':recovered is not None},flush=True)
   continue
  if args.suite in ('twobit','firstpairtwobit'):
   # Exactly TEN initial-a bits supplied externally; neither bit0 nor
   # bit24 is known. The only extra work is four exhaustive fast 12-bit
   # branches, not a source oracle or an unchecked heuristic completion.
   positions=tuple(p for p in sparse if p not in (0,24))
   assert len(positions)==10
   omitted=(1<<0)|(1<<24)
   outcomes=[]
   for assignment in range(4):
    proposed=(actual_a & ~omitted) | ((assignment&1)<<0) | (((assignment>>1)&1)<<24)
    t0=time.monotonic()
    status,state=solve(obs,proposed,sparse,args.timeout_ms)
    outcomes.append((status,state,round(time.monotonic()-t0,3)))
   sats=[state for status,state,_ in outcomes if status=='sat']
   assert all(status in ('sat','unsat','unknown') for status,_,_ in outcomes)
   assert all(state==(actual_a,actual_b) for state in sats), (seed,'wrong SAT state')
   assert all(stream(*state)==ys for state in sats), (seed,'heldout replay')
   complete=len(sats)==1 and sum(status=='unsat' for status,_,_ in outcomes)==3
   if not complete and not args.fresh20:
    raise AssertionError((seed,'twobit alternative inconclusive',[(o[0],o[2]) for o in outcomes]))
   if complete:
    successes+=1
   print({'seed':seed,'train':not args.fresh20 and seed in (20261128,12345),
          'suite':args.suite,'observed_output_indices':tuple(obs),
          'independently_heldout_output_indices':(4,5) if args.suite=='firstpairtwobit' else (),
          'erased_output_indices':(2,3),
          'externally_supplied_a0_bits':10,'enumerated_bit0_bit24_branches':4,
          'sat_branches':len(sats),'unsat_branches':sum(o[0]=='unsat' for o in outcomes),
          'unknown_branches':sum(o[0]=='unknown' for o in outcomes),
          'elapsed_seconds':round(sum(x[2] for x in outcomes),3),
          'complete_branch_decision':complete,'every_found_state_exact':True},flush=True)
   continue
  if args.suite=='onebit':
   # Only eleven scattered initial-a bits are supplied; bit0 is genuinely
   # omitted. Resolve it with exactly TWO complete 12-bit solver branches.
   positions=sparse[1:]
   outcomes=[]
   for bit0 in (0,1):
    proposed=(actual_a & ~1) | bit0
    t0=time.monotonic()
    status,state=solve(obs,proposed,sparse,args.timeout_ms)
    outcomes.append((status,state,round(time.monotonic()-t0,3)))
   sats=[state for status,state,_ in outcomes if status=='sat']
   assert len(sats)==1 and sats[0]==(actual_a,actual_b), (seed,'onebit state')
   assert sum(status=='unsat' for status,_,_ in outcomes)==1,(seed,'onebit alternative unproven')
   assert stream(*sats[0])==ys,(seed,'onebit erased packet')
   successes+=1
   print({'seed':seed,'train':seed in seeds[:2],'suite':args.suite,
          'observed_output_indices':(0,1,4,5),'erased_output_indices':(2,3),
          'externally_supplied_a0_bits':len(positions),'enumerated_bit0_branches':2,
          'sat_branches':1,'unsat_branches':1,
          'elapsed_seconds':round(sum(x[2] for x in outcomes),3),
          'exact_complete_state_and_gap':True},flush=True)
   continue
  if args.suite=='poison':
   anchored_a=actual_a ^ (1 << sparse[0])
   positions=sparse
   want='unsat'
  else:
   anchored_a=actual_a
   positions=baseline if args.suite=='baseline' else sparse
   want='sat'
  t0=time.monotonic()
  status,state=solve(obs,anchored_a,positions,args.timeout_ms)
  elapsed=round(time.monotonic()-t0,3)
  if args.suite=='poison':
   assert status=='unsat' and state is None, (seed,status)
   successes+=1
  elif status=='sat':
   assert state==(actual_a,actual_b), (seed,'wrong recovered state')
   assert stream(*state)==ys, (seed,'erased middle mismatch')
   successes+=1
  elif status!='unknown':
   raise AssertionError((seed,status))
  print({'seed':seed,'train':seed in seeds[:2],'suite':args.suite,
         'observed_output_indices':(0,1,4,5),'erased_output_indices':(2,3),
         'anchor_bits':len(positions),'status':status,'exact':state==(actual_a,actual_b),
         'elapsed_seconds':elapsed},flush=True)
 if args.suite!='baseline' and not args.fresh20:
  assert successes==len(chosen), (args.suite,successes)
 print({'suite':args.suite,'successes':successes,'cases':len(chosen),
        'witness_positions':list(positions),'elapsed_total_s':round(time.monotonic()-started,2),
        'synthetic_only':True,'historical_key_recovered':False},flush=True)
