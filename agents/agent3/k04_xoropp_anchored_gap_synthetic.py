#!/usr/bin/env python3
"""Synthetic-only xoroshiro128++ two-packet erasure recovery with a known low-16 a0 anchor.
This proves a conditional full-output solver mechanism; no archive bytes or commitment are used.
Requires system libz3.so.4. Compare all replayed outputs, including both erased middle words.
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

def circuit(obs,anchor,timeout_ms):
 """obs maps visible stream indices 0,1,4,5 to complete 64bit values."""
 assert set(obs)=={0,1,4,5}
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
 for j in range(16):
  lines.append(f'(assert (= a0_{j} {"true" if anchor&(1<<j) else "false"}))')
 lines.append('(check-sat)')
 return '\n'.join(lines)+'\n'

def solve(obs,anchor,timeout_ms=5000):
 lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
 lib.Z3_mk_config.restype=P
 lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
 lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
 lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 try:
  status=(lib.Z3_eval_smtlib2_string(ctx,circuit(obs,anchor,timeout_ms).encode()) or b'').decode().strip()
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
 seeds=[20261128,12345,2027,2048,124,48,19,123456,8773,2]
 t0=time.monotonic();counts={}
 for seed in seeds:
  rng=random.Random(seed);a,b=rng.getrandbits(64),rng.getrandbits(64)
  ys=stream(a,b);obs={i:ys[i] for i in (0,1,4,5)}
  st,got=solve(obs,a&65535,5000)
  if got:assert got==(a,b) and stream(*got)==ys
  counts[st]=counts.get(st,0)+1
  print('seed',seed,'result',st,'correct_complete_gap',got==(a,b),flush=True)
 # Poisoned outer-output controls exercise rejection without a manufactured state.
 rng=random.Random(20261128);a,b=rng.getrandbits(64),rng.getrandbits(64);ys=stream(a,b)
 for bit in (0,17,39,63):
  obs={i:ys[i] for i in (0,1,4,5)};obs[4]^=1<<bit
  st,_=solve(obs,a&65535,5000)
  assert st=='unsat',('poisoned control',bit,st)
  print('poisoned',bit,st,flush=True)
 print('RESULT',counts,'elapsed_seconds',round(time.monotonic()-t0,2),flush=True)
