#!/usr/bin/env python3
"""Prune unused output-conditioned XOR gates; exact conditional xoroshiro128++ solver.
Synthetic performance experiment. Original-source runner provided separately.
"""
import ctypes,random,re,time,sys
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

def circuit(obs,anchor,positions,timeout_ms,pruned=True,assumptions=False):
 assert set(obs) in ({0,1,4,5},{0,1})
 lines=['(set-logic QF_UF)','(set-option :sat.anf true)','(set-option :sat.anf.exlin true)',f'(set-option :timeout {timeout_ms})']
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
 a=[f'a0_{i}' for i in range(64)];lines.extend(f'(declare-const {x} Bool)' for x in a)
 t=implied_t(a,obs[0],'0')
 for i in range(1,max(obs)+1 if pruned else 6):
  an=[put(f'a{i}_{j}',xor(a[(j-49)&63],t[j],t[j-21] if j>=21 else 'false')) for j in range(64)]
  tn=[put(f'tf{i}_{j}',xor(an[j],t[(j-28)&63])) for j in range(64)]
  a,t=an,tn
  if i in obs:
   require=implied_t(a,obs[i],str(i))
   lines.extend(f'(assert (= {t[j]} {require[j]}))' for j in range(64))
 if assumptions:
  for j in positions:
   lines.append(f'(declare-fun q{j} () Bool)')
   lines.append(f'(assert (= q{j} a0_{j}))')
 else:
  for j in positions:
   lines.append(f'(assert (= a0_{j} {"true" if anchor&(1<<j) else "false"}))')
 lines.append('(check-sat)' if not assumptions else '')
 return '\n'.join(lines)+'\n'

lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
lib.Z3_mk_config.restype=P;lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p];lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p

class Session:
 def __init__(self,obs,positions,timeout_ms=350,pruned=True,assumptions=False,anchor=0):
  self.obs=obs;self.pos=positions;self.assumptions=assumptions
  cfg=lib.Z3_mk_config();self.ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
  self.ask=lambda s:(lib.Z3_eval_smtlib2_string(self.ctx,s.encode()) or b'').decode().strip()
  self.ask(circuit(obs,anchor,positions,timeout_ms,pruned,assumptions).replace("(check-sat)", ""))
 def do(self,anchor,max_models=32):
  if self.assumptions:
   terms=' '.join(f'q{j}' if anchor&(1<<j) else f'(not q{j})' for j in self.pos)
   st=self.ask('(check-sat-assuming ('+terms+'))')
  else:st=self.ask('(check-sat)')
  states=[]
  while st=='sat':
   vals=self.ask('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
   bits={int(j):int(v=='true') for j,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',vals)}
   if len(bits)!=64:raise AssertionError('Incomplete model')
   a=sum(v<<j for j,v in bits.items());b=(ror((self.obs[0]-a)&M,17)-a)&M
   assert all(stream(a,b,6)[i]==v for i,v in self.obs.items())
   states.append((a,b))
   if len(states)>=max_models:return states,'unknown'
   terms=' '.join((f'(not a0_{j})' if bits[j] else f'a0_{j}') for j in range(64))
   self.ask('(assert (or '+terms+'))')
   st=self.ask('(check-sat)')
  if st not in ('unknown','unsat'):raise AssertionError(st)
  return states,st
 def close(self):lib.Z3_del_context(self.ctx)

def solve(obs,anchor,positions,timeout_ms=350,pruned=True):
 ss=Session(obs,positions,timeout_ms,pruned,False,anchor)
 try:return ss.do(anchor)
 finally:ss.close()

if __name__=='__main__':
 rng=random.Random(88126)
 pos=[0,1,2,3,4,5,6,7,22,23,24,25,45,46,47,48]
 for pruned in [False,True]:
  t0=time.monotonic();score={'sat':0,'unsat':0,'unknown':0}; recovered=0
  for i in range(16):
   a,b=rng.getrandbits(64),rng.getrandbits(64)
   obs={j:v for j,v in enumerate(stream(a,b,2))}
   states,status=solve(obs,a,pos,350,pruned)
   score[status]+=1;recovered+=int((a,b) in states)
  print('pruned',pruned,score,'recovered',recovered,'elapsed',time.monotonic()-t0,flush=True)
