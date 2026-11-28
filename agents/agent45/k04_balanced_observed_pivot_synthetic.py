#!/usr/bin/env python3
"""Synthetic-only balanced observed-state pivot for official xoroshiro128++ two-word erased packet.
Unanchored primary 64 Boolean bits at an observed output; forward and reverse exact xor state transition.
No archive, route, commitment, original values, or PDF imported.
"""
import ctypes,random,re,sys,time
M=(1<<64)-1

def rol(x,n):return ((x<<n)|(x>>(64-n)))&M
def ror(x,n):return ((x>>n)|(x<<(64-n)))&M
def next(a,b):
 t=a^b
 return rol(a,49)^t^((t<<21)&M),rol(t,28)
def prev(a,b):
 t=ror(b,28);ap=ror(a^t^((t<<21)&M),49)
 return ap,ap^t
def stream(a,b,n=6):
 out=[]
 for _ in range(n):
  out.append((rol((a+b)&M,17)+a)&M)
  a,b=next(a,b)
 return out

def sxor(*xs):
 xs=[s for s in xs if s!='false']
 return 'false' if not xs else xs[0] if len(xs)==1 else '(xor '+' '.join(xs)+')'

def gen(obs,pivot,timeout_ms,sat_seed=0):
 assert len(obs)>=2 and pivot in obs and all(0<=k<6 for k in obs)
 lines=['(set-logic QF_UF)','(set-option :sat.anf true)','(set-option :sat.anf.exlin true)',f'(set-option :sat.random_seed {sat_seed})',f'(set-option :timeout {timeout_ms})']
 def put(n,e):lines.append(f'(define-fun {n} () Bool {e})');return n
 def implied_t(a,y,tag):
  v=['false']*64
  for j in range(63):
   v[j+1]=put(f'v{tag}_{j+1}',f'({"and" if (y>>j)&1 else "or"} {a[j]} {v[j]})')
  u=['false']*64;tt=[]
  for k in range(64):
   j=(k+17)&63
   tbit=put(f't{tag}_{k}',sxor(a[j],v[j],u[k],'true' if (y>>j)&1 else 'false'))
   tt.append(tbit)
   if k<63:u[k+1]=put(f'u{tag}_{k+1}',f'(ite {tbit} {u[k]} {a[k]})')
  return tt
 def advance(a,t,i):
  an=[put(f'af{i}_{j}',sxor(a[(j-49)&63],t[j],t[j-21] if j>=21 else 'false')) for j in range(64)]
  tn=[put(f'tf{i}_{j}',sxor(an[j],t[(j-28)&63])) for j in range(64)]
  return an,tn
 def retreat(a,t,i):
  tp=[put(f'tb{i}_{j}',sxor(a[(j+28)&63],t[(j+28)&63])) for j in range(64)]
  ap=[]
  for j in range(64):
   k=(j+49)&63
   ap.append(put(f'ab{i}_{j}',sxor(a[k],tp[k],tp[k-21] if k>=21 else 'false')))
  return ap,tp
 a=[f'pa_{j}' for j in range(64)];lines.extend(f'(declare-const {v} Bool)' for v in a)
 t=implied_t(a,obs[pivot],f'{pivot}p')
 af,tf=a,t
 for i in range(pivot+1,max(obs)+1):
  af,tf=advance(af,tf,i)
  if i in obs:
   tt=implied_t(af,obs[i],str(i))
   lines.extend(f'(assert (= {tf[j]} {tt[j]}))' for j in range(64))
 ab,tb=a,t
 for i in range(pivot-1,min(obs)-1,-1):
  ab,tb=retreat(ab,tb,i)
  if i in obs:
   tt=implied_t(ab,obs[i],str(i))
   lines.extend(f'(assert (= {tb[j]} {tt[j]}))' for j in range(64))
 lines.append('(check-sat)')
 return '\n'.join(lines)+'\n'

def solve(obs,pivot=1,timeout_ms=5000,sat_seed=0):
 lib=ctypes.CDLL('libz3.so.4');P=ctypes.c_void_p
 lib.Z3_mk_config.restype=P
 lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
 lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p];lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 try:
  s=gen(obs,pivot,timeout_ms,sat_seed)
  status=(lib.Z3_eval_smtlib2_string(ctx,s.encode()) or b'').decode().strip()
  if status!='sat':return status,None
  model=(lib.Z3_eval_smtlib2_string(ctx,('(get-value ('+' '.join(f'pa_{j}' for j in range(64))+'))').encode()) or b'').decode()
  bits={int(i):int(v=='true') for i,v in re.findall(r'\(pa_(\d+)\s+(true|false)\)',model)}
  assert len(bits)==64
  a=sum(v<<i for i,v in bits.items());b=(ror((obs[pivot]-a)&M,17)-a)&M
  for _ in range(pivot):a,b=prev(a,b)
  replay=stream(a,b,6)
  assert all(replay[i]==v for i,v in obs.items())
  return status,(a,b)
 finally:lib.Z3_del_context(ctx)

if __name__=='__main__':
 piv=int(sys.argv[1]) if len(sys.argv)>1 else 1
 seed=int(sys.argv[2]) if len(sys.argv)>2 else 20261128
 timeout_ms=int(sys.argv[3]) if len(sys.argv)>3 else 15000
 rng=random.Random(seed);trial=int(sys.argv[5]) if len(sys.argv)>5 else 0
 for _ in range(trial):rng.getrandbits(64);rng.getrandbits(64)
 a,b=rng.getrandbits(64),rng.getrandbits(64)
 ys=stream(a,b);indices=(0,1,2,3) if len(sys.argv)>4 and sys.argv[4]=="consec" else (0,1,4,5);obs={i:ys[i] for i in indices}
 st=time.monotonic();sat_seed=int(sys.argv[6]) if len(sys.argv)>6 else 0;status,got=solve(obs,piv,timeout_ms,sat_seed)
 print('pivot',piv,'seed',seed,'trial',trial,'solver_seed',sat_seed,'status',status,'correct_full_state',got==(a,b),'elapsed_s',round(time.monotonic()-st,3),flush=True)
 if got:assert got==(a,b) and stream(*got,6)==ys
