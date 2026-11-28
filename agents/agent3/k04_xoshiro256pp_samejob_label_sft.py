#!/usr/bin/env python3
"""H-17 K04 conditional xoshiro256++ LABEL(s0,s2) bridge.

Safe source-free synthetic default. Original mode is strictly local, emits only
aggregate counters and escrows a hypothetical original commitment hit outside Git.
This is a conditional hypothesis, not a claim about the historical printer.
"""
import argparse, ctypes, hashlib, json, os, pathlib, random, re
MASK=(1<<64)-1
R=lambda x,n:((x<<n)|(x>>(64-n)))&MASK
RR=lambda x,n:((x>>n)|(x<<(64-n)))&MASK

def stream(state,n=21):
 a,b,c,d=state;out=[]
 for _ in range(n):
  out.append((R((a+d)&MASK,23)+a)&MASK)
  t=(b<<17)&MASK;c^=a;d^=b;b^=c;a^=d;c^=t;d=R(d,45)
 return out

def smt(a,y,ms):
 q=['(set-logic QF_UF)','(set-option :sat.anf true)',
    '(set-option :sat.anf.exlin true)',f'(set-option :timeout {ms})']
 def put(n,e):q.append(f'(define-fun {n} () Bool {e})');return n
 u=[f'u{i}' for i in range(64)]
 q += [f'(declare-const {v} Bool)' for v in u]
 x=[put(f'x{i}',f'(xor {u[i]} {"true" if a>>i&1 else "false"})') for i in range(64)]
 bor=['false']*64
 for j in range(63):
  bor[j+1]=put(f'bor{j+1}',f'({"and" if y>>j&1 else "or"} {x[j]} {bor[j]})')
 car=['false']*64
 for k in range(64):
  j=(k+23)&63
  z=put(f'z{k}',f'(xor {x[j]} {bor[j]} {car[k]} {"true" if y>>j&1 else "false"})')
  q.append(f'(assert (= (xor {x[k]} {u[(k-45)&63]}) {z}))')
  if k<63:car[k+1]=put(f'car{k+1}',f'(ite {z} {car[k]} {x[k]})')
 return '\n'.join(q)+'\n'

def invert(a,y,ms=3000,limit=32):
 """Enumerate compatible 64-bit u, with a terminal UNSAT required for closure."""
 lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
 lib.Z3_mk_config.restype=P
 lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
 lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p];lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 def run(s):return (lib.Z3_eval_smtlib2_string(ctx,s.encode())or b'').decode().strip()
 models=[]
 try:
  assert not run(smt(a,y,ms))
  for _ in range(limit):
   status=run('(check-sat)')
   if status!='sat':return models,status
   vals=run('(get-value ('+' '.join(f'u{i}' for i in range(64))+'))')
   bits={int(k):int(v=='true') for k,v in re.findall(r'\(u(\d+)\s+(true|false)\)',vals)}
   assert len(bits)==64
   u=sum(v<<k for k,v in bits.items());assert u not in models
   assert ((R(((a^u)+R(u,45))&MASK,23)+(a^u))&MASK)==y
   models.append(u)
   assert not run('(assert (or '+' '.join(f'(not u{k})' if bits[k] else f'u{k}' for k in range(64))+'))')
  return models,'LIMIT'
 finally:lib.Z3_del_context(ctx)

def pack(words,endian,swap):
 return b''.join(v.to_bytes(8,endian) for v in (words[::-1] if swap else words))
def unpack(data,endian,swap):
 w=[int.from_bytes(data[i:i+8],endian) for i in (0,8)]
 return w[::-1] if swap else w

def recover(label,first,endian,swap):
 a,c=unpack(label,endian,swap)
 y0,y1=unpack(first,endian,swap)
 d=(RR((y0-a)&MASK,23)-a)&MASK
 choices,term=invert(a,y1)
 if term!='unsat':raise RuntimeError('Nonterminal state partition: '+term)
 states=[(a,d^u,c,d) for u in choices]
 assert all(pack(stream(s,2),endian,swap)==first for s in states)
 return states

def coupon_reductions(states,endian,swap,route_mask):
 for state in states:
  outputs=stream(state)
  for start in range(2,20):
   coupon=pack(outputs[start:start+2],endian,swap)
   yield bytes(x^y for x,y in zip(coupon,route_mask))

def synthetic():
 positives=0;poison=0
 for seed in range(3001,3007):
  r=random.Random(seed);s=tuple(r.getrandbits(64) for _ in range(4))
  ys=stream(s);mask=r.randbytes(16)
  for endian in ('big','little'):
   for swap in (False,True):
    label=pack([s[0],s[2]],endian,swap)
    first=pack(ys[:2],endian,swap)
    got=recover(label,first,endian,swap)
    assert s in got
    trial=list(coupon_reductions(got,endian,swap,mask))
    for start in range(2,20):
     true=bytes(x^y for x,y in zip(pack(ys[start:start+2],endian,swap),mask))
     assert trial.count(true)==1
     positives+=1
    damaged=bytearray(label);damaged[0]^=1
    wrong=list(coupon_reductions(recover(bytes(damaged),first,endian,swap),endian,swap,mask))
    assert not set(trial)&set(wrong)
    poison+=1
 print({'synthetic_positive_complete_coupons':positives,
        'poisoned_label_negative_controls':poison,'source_accessed':False})

def original(root,escrow):
 if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
  raise SystemExit('Original source forbidden in public CI; use local trusted environment')
 spool=(root/'evidence/print/spool-reconstruction.log').read_text()
 route=json.loads((root/'evidence/recovery-routing.json').read_text())
 accept=json.loads((root/'acceptance.json').read_text())
 mask=bytes.fromhex(route['K04']['masked_component']);target=accept['slot_sha256']['K04']
 def src(time,kind,cls):
  rows=[v for v in spool.splitlines() if v.startswith(time) and
        'JOB=PS-261003-0417 ' in v and f'STATE={kind} ' in v and f'CLASS={cls} ' in v]
  assert len(rows)==1
  return bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})\b',rows[0]).group(1))
 label=src('2026-10-03T16:45:00+00:00','ACK','LABEL')
 first=src('2026-10-03T18:01:00Z','REQUESTED','RECOVER')
 later=src('2026-10-03T18:03:00Z','REQUESTED','RECOVER')
 totals=[];hits=[]
 for endian in ('big','little'):
  for swap in (False,True):
   states=recover(label,first,endian,swap)
   accepted=[v for v in coupon_reductions(states,endian,swap,mask)
             if hashlib.sha256(v).hexdigest()==target]
   hits.extend(accepted)
   totals.append({'view':endian+('-ba' if swap else '-ab'),
        'states':len(states),'coupon_windows':len(states)*18,
        'withheld_later_matches':sum(pack(stream(s)[4:6],endian,swap)==later for s in states),
        'original_commitment_hits':len(accepted)})
 if hits:
  f=pathlib.Path(escrow).resolve()
  assert f.is_relative_to(pathlib.Path('/mnt/data').resolve()) and not f.is_symlink()
  fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as w:w.write(json.dumps([v.hex().upper() for v in hits]))
 print({'conditional_family':'samejob_LABEL_as_xoshiro256pp_s0_s2',
        'selected_ack2_fitted':False,'results':totals,
        'result':'HIT_ESCROWED' if hits else 'NO_MATCH'})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original-root',type=pathlib.Path)
 p.add_argument('--escrow',default='/mnt/data/h17_k04_labelbridge_hits.json')
 a=p.parse_args()
 if a.original_root:original(a.original_root,a.escrow)
 else:synthetic()
