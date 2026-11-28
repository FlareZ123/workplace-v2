#!/usr/bin/env python3
"""Synthetic-only xoroshiro128++ inversion with 64 Boolean primary variables.

Given y=ROTL(a+b,17)+a, choosing any a determines b uniquely. Instead of a
word-level subtraction circuit, reconstruct t=a XOR b with the exact output-
conditioned binary carry recurrences. Assert t at later visible generator steps
against the (linear) state transition. Erased outputs advance the state without
constraining their values. This file uses no historical records or commitments.

Requires the system libz3.so.4; no Python z3 package is required.
"""
import argparse
import ctypes as C
import random
import time

Z=C.CDLL("libz3.so.4")
P=C.c_void_p; U=C.c_uint; M=(1<<64)-1
API={
"Z3_mk_config":(P,[]),"Z3_del_config":(None,[P]),
"Z3_mk_context":(P,[P]),"Z3_del_context":(None,[P]),
"Z3_mk_string_symbol":(P,[P,C.c_char_p]),
"Z3_mk_solver":(P,[P]),"Z3_mk_solver_for_logic":(P,[P,P]),
"Z3_mk_bool_sort":(P,[P]),"Z3_mk_const":(P,[P,P,P]),
"Z3_mk_true":(P,[P]),"Z3_mk_false":(P,[P]),
"Z3_mk_eq":(P,[P,P,P]),"Z3_mk_not":(P,[P,P]),
"Z3_mk_xor":(P,[P,P,P]),"Z3_mk_and":(P,[P,U,C.POINTER(P)]),
"Z3_mk_or":(P,[P,U,C.POINTER(P)]),"Z3_mk_ite":(P,[P,P,P,P]),
"Z3_solver_inc_ref":(None,[P,P]),"Z3_solver_dec_ref":(None,[P,P]),
"Z3_solver_assert":(None,[P,P,P]),"Z3_solver_check":(C.c_int,[P,P]),
"Z3_solver_get_model":(P,[P,P]),
"Z3_model_inc_ref":(None,[P,P]),"Z3_model_dec_ref":(None,[P,P]),
"Z3_model_eval":(C.c_bool,[P,P,P,C.c_bool,C.POINTER(P)]),
"Z3_get_bool_value":(C.c_int,[P,P]),
"Z3_mk_params":(P,[P]),"Z3_params_inc_ref":(None,[P,P]),
"Z3_params_dec_ref":(None,[P,P]),"Z3_params_set_uint":(None,[P,P,P,U]),
"Z3_solver_set_params":(None,[P,P,P])}
for name,(ret,args) in API.items():
 f=getattr(Z,name);f.restype=ret;f.argtypes=args
ROL=lambda x,n:((x<<n)|(x>>(64-n)))&M
ROR=lambda x,n:((x>>n)|(x<<(64-n)))&M

def step(a,b):
 y=(ROL((a+b)&M,17)+a)&M
 t=a^b
 return y,(ROL(a,49)^t^((t<<21)&M))&M,ROL(t,28)

def stream(a,b,n):
 out=[]
 for _ in range(n):
  y,a,b=step(a,b);out.append(y)
 return out

def t_from_a_and_output(a,y):
 """Exact t from chosen a and observed y, using output-conditioned carries."""
 v=[0]*64
 for j in range(63):
  v[j+1]=((a>>j)&1)&v[j] if (y>>j)&1 else ((a>>j)&1)|v[j]
 u=0;t=0
 for k in range(64):
  j=(k+17)&63
  w=((y>>j)&1)^((a>>j)&1)^v[j]
  tk=w^u;t|=tk<<k
  u=u if tk else ((a>>k)&1)
 return t

def solve(observed,timeout_ms=90000,anchor_a=None,anchor_bits=0,logic=""):
 """Return exact replay-validated initial state or UNKNOWN/UNSAT."""
 assert len(observed)>=2 and observed[0] is not None
 cfg=Z.Z3_mk_config();ctx=Z.Z3_mk_context(cfg);Z.Z3_del_config(cfg)
 if logic:
  solver=Z.Z3_mk_solver_for_logic(ctx,Z.Z3_mk_string_symbol(ctx,logic.encode()))
 else:
  solver=Z.Z3_mk_solver(ctx)
 Z.Z3_solver_inc_ref(ctx,solver)
 sort=Z.Z3_mk_bool_sort(ctx)
 def mk(name,*args):return getattr(Z,"Z3_mk_"+name)(ctx,*args)
 def xor(*xs):
  z=xs[0]
  for v in xs[1:]:z=mk("xor",z,v)
  return z
 def and_(a,b):return mk("and",2,(P*2)(a,b))
 def or_(a,b):return mk("or",2,(P*2)(a,b))
 def not_(a):return mk("not",a)
 def assert_eq(a,b):Z.Z3_solver_assert(ctx,solver,mk("eq",a,b))
 T=mk("true");F=mk("false")
 def t_given_a_output(a,y):
  # Second addition: carry[j+1] = (a[j] & carry[j]) if y[j]
  # else (a[j] | carry[j]). Carry[0]=0.
  v=[F]*64
  for j in range(63):
   v[j+1]=and_(a[j],v[j]) if (y>>j)&1 else or_(a[j],v[j])
  # First addition: u[k+1]=u[k] if t[k] else a[k].
  u=[F]*64;t=[]
  for k in range(64):
   j=(k+17)&63
   w=xor(a[j],v[j])
   if (y>>j)&1:w=not_(w)
   tk=xor(w,u[k]);t.append(tk)
   if k<63:u[k+1]=mk("ite",tk,u[k],a[k])
  return t
 def advance(a,t):
  next_a=[];next_t=[]
  for j in range(64):
   terms=[a[(j-49)&63],t[j]]
   if j>=21:terms.append(t[j-21])
   ap=xor(*terms)
   next_a.append(ap)
   next_t.append(xor(ap,t[(j-28)&63]))
  return next_a,next_t

 initial=[mk("const",mk("string_symbol",("a%02d"%j).encode()),sort)
          for j in range(64)]
 a=initial;t=t_given_a_output(a,observed[0])
 for y in observed[1:]:
  a,t=advance(a,t)
  if y is not None:
   required=t_given_a_output(a,y)
   for j in range(64):assert_eq(t[j],required[j])
 if anchor_bits:
  assert anchor_a is not None and 0<=anchor_bits<=64
  for j in range(anchor_bits):
   Z.Z3_solver_assert(ctx,solver,initial[j] if (anchor_a>>j)&1
                      else not_(initial[j]))
 params=Z.Z3_mk_params(ctx);Z.Z3_params_inc_ref(ctx,params)
 Z.Z3_params_set_uint(ctx,params,mk("string_symbol",b"timeout"),timeout_ms)
 Z.Z3_solver_set_params(ctx,solver,params);Z.Z3_params_dec_ref(ctx,params)
 start=time.monotonic();status=Z.Z3_solver_check(ctx,solver)
 elapsed=time.monotonic()-start
 recovered=None
 if status==1:
  model=Z.Z3_solver_get_model(ctx,solver);Z.Z3_model_inc_ref(ctx,model)
  a0=0
  for j,x in enumerate(initial):
   out=P()
   assert Z.Z3_model_eval(ctx,model,x,True,C.byref(out))
   value=Z.Z3_get_bool_value(ctx,out)
   assert value in (-1,1)
   if value==1:a0|=1<<j
  t0=t_from_a_and_output(a0,observed[0])
  recovered=(a0,a0^t0)
  replay=stream(*recovered,len(observed))
  assert all(y is None or replay[i]==y for i,y in enumerate(observed))
  Z.Z3_model_dec_ref(ctx,model)
 Z.Z3_solver_dec_ref(ctx,solver);Z.Z3_del_context(ctx)
 return ("SAT" if status==1 else "UNSAT" if status==-1 else "UNKNOWN",
         elapsed,recovered)

def inverse_controls(count=10000,seed=20261128):
 rng=random.Random(seed)
 for _ in range(count):
  a=rng.getrandbits(64);y=rng.getrandbits(64)
  t=t_from_a_and_output(a,y)
  b=(ROR((y-a)&M,17)-a)&M
  assert t==a^b and step(a,b)[0]==y
 return count

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--timeout",type=int,default=90000)
 p.add_argument("--trials",type=int,default=1)
 p.add_argument("--nobs",type=int,default=4)
 p.add_argument("--gap",action="store_true")
 p.add_argument("--anchor",type=int,default=0)
 p.add_argument("--logic",default="")
 p.add_argument("--seed",type=int,default=20261128)
 args=p.parse_args()
 print({"inverse_algebra_controls":inverse_controls()},flush=True)
 rng=random.Random(args.seed)
 for i in range(args.trials):
  a,b=rng.getrandbits(64),rng.getrandbits(64)
  outputs=stream(a,b,args.nobs)
  if args.gap:
   assert args.nobs>=6
   outputs[2:4]=[None,None]
  state,seconds,found=solve(outputs,args.timeout,a,args.anchor,args.logic)
  print({"case":i,"observations":args.nobs,"gap":args.gap,
         "anchor_bits":args.anchor,"status":state,
         "seconds":round(seconds,3),"exact_plant":found==(a,b)},flush=True)
