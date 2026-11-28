#!/usr/bin/env python3
"""Synthetic-only exhaustive P12->P13 xoroshiro128++ timeout rescue.

A P12 firstpair solver can return UNKNOWN. Since one additional fixed a0
bit partitions the P12 cube exactly, the union of two model-exhausted P13
children is a complete proof. Prove the technique on a fixed planted
same-P12 firstpair collision and a separate fake P12 cube with variable
P12 timeout outcome while two P13 children reach UNSAT/UNSAT. No H17 source.
"""
from __future__ import annotations
import ctypes,hashlib,json,random,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit,stream
from agents.agent4.k04_xoropp_zero_witness_synthetic import POSITIONS
from agents.agent37.k04_xoropp_samebucket_collision_sft import WITNESSES, independent_forward

M=(1<<64)-1
P=ctypes.c_void_p

def rotr(x,n):return ((x>>n)|(x<<(64-n)))&M

def all_models(first,anchor,positions,timeout_ms=5000,cap=32):
 lib=ctypes.CDLL('libz3.so.4');lib.Z3_mk_config.restype=P
 lib.Z3_mk_context.argtypes=[P];lib.Z3_mk_context.restype=P
 lib.Z3_del_config.argtypes=[P];lib.Z3_del_context.argtypes=[P]
 lib.Z3_eval_smtlib2_string.argtypes=[P,ctypes.c_char_p]
 lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
 cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 def eval(s):return (lib.Z3_eval_smtlib2_string(ctx,s.encode()) or b'').decode().strip()
 try:
  status=eval(circuit({0:first[0],1:first[1]},anchor,positions,timeout_ms));found=[]
  while status=='sat':
   raw=eval('(get-value ('+' '.join(f'a0_{j}' for j in range(64))+'))')
   bits={int(j):int(v=='true') for j,v in re.findall(r'\(a0_(\d+)\s+(true|false)\)',raw)}
   assert len(bits)==64
   a=sum(bits[j]<<j for j in range(64))
   b=(rotr((first[0]-a)&M,17)-a)&M
   assert independent_forward(a,b,2)==list(first)
   found.append((a,b))
   if len(found)>=cap:return set(found),'unknown'
   clause=' '.join((f'(not a0_{j})' if bits[j] else f'a0_{j}') for j in range(64))
   eval(f'(assert (or {clause}))')
   status=eval('(check-sat)')
  assert status in ('unsat','unknown'), status
  return set(found),status
 finally:lib.Z3_del_context(ctx)

def split(first,anchor,bit=4,timeout_ms=5000):
 assert bit not in POSITIONS
 kids=[]
 for side in (0,1):
  child_anchor=anchor|(side<<bit)
  got,status=all_models(first,child_anchor,POSITIONS+(bit,),timeout_ms)
  assert all(((s[0]>>bit)&1)==side for s in got)
  kids.append((got,status))
 all_state=kids[0][0]|kids[1][0]
 return all_state,('unsat' if all(x[1]=='unsat' for x in kids) else 'unknown'),[x[1] for x in kids]

def main():
 t0=time.monotonic();a,b=WITNESSES
 x=independent_forward(*a);assert x[:2]==independent_forward(*b)[:2]
 anchor=sum(a[0]&(1<<p) for p in POSITIONS)
 pred,terminal,children=split(tuple(x[:2]),anchor,bit=4,timeout_ms=5000)
 assert terminal=='unsat' and len(pred)==2 and pred==set(WITNESSES)
 assert children==['unsat','unsat']
 mask=bytes(range(16))
 for witness in WITNESSES:
  actual=independent_forward(*witness,6)
  middle=b''.join(word.to_bytes(8,'big') for word in actual[2:4])
  target=hashlib.sha256(bytes(x^y for x,y in zip(middle,mask))).digest()
  assert sum(hashlib.sha256(bytes(x^y for x,y in zip(
      b''.join(v.to_bytes(8,'big') for v in independent_forward(*state,6)[2:4]),mask
      ))).digest()==target for state in pred)==1
 print('POSITIVE',json.dumps({'source_free':True,'same_firstpacket_and_P12_collision':True,
          'two_P13_children_complete':True,'all_true_states_recovered':len(pred)==2,
          'elapsed_seconds':round(time.monotonic()-t0,3)}),flush=True)
 rng=random.Random(80903)
 aa,bb=rng.getrandbits(64),rng.getrandbits(64)
 first=tuple(independent_forward(aa,bb,2))
 false_cube=sum(aa&(1<<p) for p in POSITIONS)^1
 old,oldstatus=all_models(first,false_cube,POSITIONS,5000)
 new,newstatus,kidstatuses=split(first,false_cube,bit=4,timeout_ms=5000)
 print('NEGATIVE_PARENT_OBSERVED',json.dumps({'source_free':True,'oldstatus':oldstatus,'n_models':len(old),'childstatuses':kidstatuses,'newstatus':newstatus,'child_models':len(new),'elapsed_seconds':round(time.monotonic()-t0,3)}),flush=True)
 assert newstatus=='unsat' and len(new)==0 and kidstatuses==['unsat','unsat']
 print('SPLIT_DISPOSITION',json.dumps({'source_free':True,
       'parent_status':oldstatus,'parent_timeout_ms':5000,
       'children_model_complete_statuses':kidstatuses,
       'new_exact_result':'unsat',
       'previously_unresolved_cube_now_decisively_excluded':oldstatus=='unknown',
       'historical_source_not_read':True,
       'elapsed_seconds':round(time.monotonic()-t0,3)}),flush=True)

if __name__=='__main__':main()
