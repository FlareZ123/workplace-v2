#!/usr/bin/env python3
"""K04 conditional same-job LABEL -> xoshiro256++ initial s0 only.

Source-free synthetic control is default. Historical mode explicitly local only and
strictly named text/json inputs; no PDF, no original components in stdout or Git.
The complete 12-bit c0 anchor cube population can be scanned and resumed from
private chmod0600 ledger; UNKNOWNs remain unresolved, not negative buckets.
"""
import argparse,collections,concurrent.futures,ctypes,hashlib,json,os,pathlib,random,re,time
from k04_xoshiro256pp_samejob_label_sft import invert,unpack,pack,RR,MASK,stream
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
assert len(set(P12))==12

def sx(*xs):
 xs=[x for x in xs if x!='false']
 return 'false' if not xs else xs[0] if len(xs)==1 else '(xor '+' '.join(xs)+')'

def stage2_circuit(a,b,d,y4,y5,anchor,timeout_ms,blocked=()):
 """Fit ONLY later intact two-word packet, initial c0 is one unknown 64-bit word."""
 out=['(set-logic QF_UF)','(set-option :sat.anf true)',
      '(set-option :sat.anf.exlin true)',f'(set-option :timeout {timeout_ms})']
 def p(n,e):out.append(f'(define-fun {n} () Bool {e})');return n
 def implied(aa,y,i):
  bor=['false']*64
  for j in range(63):
   bor[j+1]=p(f'bor{i}_{j+1}',f'({"and" if y>>j&1 else "or"} {aa[j]} {bor[j]})')
  carry=['false']*64;result=[]
  for k in range(64):
   j=(k+23)&63
   q=p(f'out{i}_{k}',sx(aa[j],bor[j],carry[k],'true' if y>>j&1 else 'false'))
   result.append(q)
   if k<63:carry[k+1]=p(f'carry{i}_{k+1}',f'(ite {q} {carry[k]} {aa[k]})')
  return result
 w=lambda x:['true' if x>>j&1 else 'false' for j in range(64)]
 ss=[w(a),w(b),[f'C{j}' for j in range(64)],w(d)]
 out += [f'(declare-const C{j} Bool)' for j in range(64)]
 for i in range(1,6):
  a0,b0,c0,d0=ss
  cc=[p(f'cc{i}_{j}',sx(c0[j],a0[j])) for j in range(64)]
  dd=[p(f'dd{i}_{j}',sx(d0[j],b0[j])) for j in range(64)]
  nb=[p(f'nb{i}_{j}',sx(b0[j],cc[j])) for j in range(64)]
  na=[p(f'na{i}_{j}',sx(a0[j],dd[j])) for j in range(64)]
  nc=[p(f'nc{i}_{j}',sx(cc[j],b0[j-17] if j>=17 else 'false')) for j in range(64)]
  nd=[dd[(j-45)&63] for j in range(64)]
  ss=[na,nb,nc,nd]
  if i in (4,5):
   exp=implied(na,y4 if i==4 else y5,i)
   out.extend(f'(assert (= {sx(na[j],nd[j])} {exp[j]}))' for j in range(64))
 for k,j in enumerate(P12):
  out.append(f'(assert (= C{j} {"true" if anchor>>k&1 else "false"}))')
 for value in blocked:
  out.append('(assert (or '+' '.join(f'(not C{j})' if value>>j&1 else f'C{j}' for j in range(64))+'))')
 return '\n'.join(out)+'\n'

def solve_bucket(task):
 a,b,d,y4,y5,bucket,timeout_ms,limit=task
 lib=ctypes.CDLL('libz3.so.4');Q=ctypes.c_void_p
 lib.Z3_mk_config.restype=Q;lib.Z3_mk_context.argtypes=[Q];lib.Z3_mk_context.restype=Q
 lib.Z3_del_config.argtypes=[Q];lib.Z3_del_context.argtypes=[Q]
 lib.Z3_eval_smtlib2_string.argtypes=[Q,ctypes.c_char_p];lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 def run(s):return (lib.Z3_eval_smtlib2_string(ctx,s.encode())or b'').decode().strip()
 states=[]
 try:
  assert not run(stage2_circuit(a,b,d,y4,y5,bucket,timeout_ms))
  for _ in range(limit):
   outcome=run('(check-sat)')
   if outcome!='sat':return {'bucket':bucket,'status':outcome,'states':states}
   model=run('(get-value ('+' '.join(f'C{j}' for j in range(64))+'))')
   bits={int(j):int(v=='true') for j,v in re.findall(r'\(C(\d+)\s+(true|false)\)',model)}
   assert len(bits)==64
   c=sum(v<<j for j,v in bits.items());assert c not in states
   assert stream((a,b,c,d))[4:6]==[y4,y5]
   states.append(c)
   run('(assert (or '+' '.join(f'(not C{j})' if bits[j] else f'C{j}' for j in range(64))+'))')
  return {'bucket':bucket,'status':'LIMIT','states':states}
 finally:lib.Z3_del_context(ctx)

def control():
 good=0;bad=collections.Counter()
 for seed in (601,602,603,604,605,606):
  r=random.Random(seed);s=tuple(r.getrandbits(64) for _ in range(4));ys=stream(s)
  anchor=sum(((s[2]>>j)&1)<<k for k,j in enumerate(P12))
  outcome=solve_bucket((s[0],s[1],s[3],ys[4],ys[5],anchor,5500,3))
  assert s[2] in outcome['states'],(seed,outcome['status'])
  good+=1
  wrong=solve_bucket((s[0],s[1],s[3],ys[4],ys[5],anchor^1,300,1))
  assert s[2] not in wrong['states']
  bad[wrong['status']]+=1
 print({'source_free':True,'planted_complete_256bit_states':good,
        'wrong_c12_buckets_without_planted_state':sum(bad.values()),
        'wrong_bucket_dispositions':dict(bad)})

def raw_inputs(root):
 paths=[root/'evidence/print/spool-reconstruction.log',root/'evidence/recovery-routing.json',root/'acceptance.json']
 raw=[p.read_bytes() for p in paths]
 source_id=hashlib.sha256(b''.join(hashlib.sha256(v).digest() for v in raw)).hexdigest()
 spool=raw[0].decode();route=json.loads(raw[1]);accept=json.loads(raw[2])
 def src(time,kind,cls):
  rows=[v for v in spool.splitlines() if v.startswith(time) and 'JOB=PS-261003-0417 ' in v and
        f'STATE={kind} ' in v and f'CLASS={cls} ' in v]
  assert len(rows)==1
  return bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})\b',rows[0]).group(1))
 return (source_id,src('2026-10-03T16:45:00+00:00','ACK','LABEL'),
         src('2026-10-03T18:01:00Z','REQUESTED','RECOVER'),
         src('2026-10-03T18:03:00Z','REQUESTED','RECOVER'),
         bytes.fromhex(route['K04']['masked_component']),accept['slot_sha256']['K04'])

def safe_local(p):
 p=pathlib.Path(p)
 if p.is_symlink():raise ValueError('symlink forbidden')
 parent=p.parent.resolve();assert parent.is_relative_to(pathlib.Path('/mnt/data').resolve())
 assert not any(part in ('workplace-v2','.git','agents','results','resources') for part in p.parts)
 if p.exists():assert (p.stat().st_mode&0o077)==0, 'private ledger permission must be 0600'
 return p

def original(args):
 if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
  raise RuntimeError('NO original-source scanning in GitHub CI')
 source_id,label,first,later,mask,target=raw_inputs(args.original_root)
 ledger=safe_local(args.ledger)
 desc={'source_sha':source_id,'solver':'xoshiro256pp-label-a-only-v1',
       'view':args.view,'positions':list(P12),'timeout_ms':args.timeout_ms,'version':1}
 done={}
 if ledger.exists():
  with ledger.open() as f:
   for line in f:
    row=json.loads(line)
    if 'header' in row:
     assert row['header']==desc,'Mismatched source/solver/serializer/timeout/anchor fingerprint';continue
    done[(row['root'],row['bucket'])]=row
 else:
  fd=os.open(ledger,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as f:
   f.write(json.dumps({'header':desc})+'\n');f.flush();os.fsync(f.fileno())
 endian,ordr=args.view.split('-');swap=ordr=='ba'
 a,_=unpack(label,endian,swap);y0,y1=unpack(first,endian,swap);y4,y5=unpack(later,endian,swap)
 d=(RR((y0-a)&MASK,23)-a)&MASK
 roots,term=invert(a,y1)
 assert term=='unsat'
 tasks=[]
 for i,u in enumerate(roots):
  b=d^u
  for bucket in range(args.start,min(4096,args.start+args.count)):
   if (i,bucket) in done and done[(i,bucket)]['status']=='unsat':continue
   tasks.append((a,b,d,y4,y5,bucket,args.timeout_ms,args.max_models))
 counts=collections.Counter();escrow=safe_local(args.escrow);hit_count=0;window_checks=0
 t0=time.monotonic()
 def private_out(record):
  fd=os.open(ledger,os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW)
  with os.fdopen(fd,'a') as f:
   f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
 with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
  for n,row in enumerate(ex.map(solve_bucket,tasks,chunksize=1),1):
   task=tasks[n-1];root_i=roots.index(d^task[1]);bucket=task[5];assert bucket==row['bucket']
   cvals=row['states'];window_checks+=18*len(cvals)
   for c in cvals:
    state=(a,task[1],c,d);ys=stream(state)
    for start in range(2,20):
     component=bytes(x^y for x,y in zip(pack(ys[start:start+2],endian,swap),mask))
     if hashlib.sha256(component).hexdigest()==target:
      fd=os.open(escrow,os.O_WRONLY|os.O_CREAT|os.O_APPEND|os.O_NOFOLLOW,0o600)
      with os.fdopen(fd,'a') as w:w.write(component.hex().upper()+'\n')
      hit_count+=1
   private_out({'root':root_i,'bucket':bucket,'status':row['status'],
                'states':[f'{c:016x}' for c in cvals]})
   counts[row['status']]+=1
   if n%100==0:
    print({'processed_new_cubes':n,'status_counts':dict(counts),
           'complete_coupon_checks':window_checks,
           'original_commitment_hits':hit_count,
           'elapsed_seconds':round(time.monotonic()-t0,1)},flush=True)
 print({'source_private':True,'view':args.view,'roots':len(roots),
        'new_cubes_processed':len(tasks),'status_counts':dict(counts),
        'complete_coupon_checks':window_checks,'original_commitment_hits_escrowed':hit_count,
        'elapsed_seconds':round(time.monotonic()-t0,1),
        'strictly_partial_if_unknown_or_unvisited':True})

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--original-root',type=pathlib.Path)
 p.add_argument('--view',choices=('big-ab','big-ba','little-ab','little-ba'),default='big-ab')
 p.add_argument('--start',type=int,default=0)
 p.add_argument('--count',type=int,default=4096)
 p.add_argument('--timeout-ms',type=int,default=3000)
 p.add_argument('--workers',type=int,default=8)
 p.add_argument('--max-models',type=int,default=16)
 p.add_argument('--ledger',default='/mnt/data/h17_k04_label_s0_c12_ledger.jsonl')
 p.add_argument('--escrow',default='/mnt/data/h17_k04_label_s0_c12_hits.txt')
 args=p.parse_args()
 assert 0<=args.start<4096 and 1<=args.count<=4096 and 100<=args.timeout_ms<=30000
 assert 1<=args.workers<=16 and 1<=args.max_models<=100
 if args.original_root:original(args)
 else:control()
