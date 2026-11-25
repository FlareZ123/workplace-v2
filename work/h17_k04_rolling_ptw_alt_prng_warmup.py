#!/usr/bin/env python3
"""Extend the target-blind rolling-PTW PRNG screen with warm-ups/alternatives.

Uses the existing resource loader and does not read PS-0417 for fitting.
Prints aggregate counts only; never emits packet/candidate bytes.
"""
from __future__ import annotations
import argparse, json, random, sys
from pathlib import Path

MASK32=(1<<32)-1
MASK64=(1<<64)-1
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"resources"/"work"))
import test_rolling_ptw_xoroshiro128pp as base  # noqa: E402


def rotl32(x,k): return ((x<<k)|(x>>(32-k)))&MASK32
def rotl64(x,k): return ((x<<k)|(x>>(64-k)))&MASK64

def xoshiro128_next(s,variant):
    s0,s1,s2,s3=s
    if variant=="xoshiro128**": out=(rotl32((s1*5)&MASK32,7)*9)&MASK32
    else: out=(rotl32((s0+s3)&MASK32,7)+s0)&MASK32
    t=(s1<<9)&MASK32
    s2^=s0; s3^=s1; s1^=s2; s0^=s3; s2^=t; s3=rotl32(s3,11)
    return out,(s0&MASK32,s1&MASK32,s2&MASK32,s3&MASK32)

def xoroshiro_next(s,variant):
    s0,s1=s
    if variant=="xoroshiro128++": out=(rotl64((s0+s1)&MASK64,17)+s0)&MASK64
    else: out=(rotl64((s0*5)&MASK64,7)*9)&MASK64
    s1^=s0; s0=(rotl64(s0,49)^s1^((s1<<21)&MASK64))&MASK64; s1=rotl64(s1,28)
    return out,(s0,s1)

def xorshift128plus_next(s):
    s1,s0=s; s1&=MASK64; s0&=MASK64; new0=s0
    s1^=(s1<<23)&MASK64; new1=(s1^s0^(s1>>17)^(s0>>26))&MASK64
    return (new1+s0)&MASK64,(new0,new1)

def make_state32(by_bay,order,endian): return tuple(int.from_bytes(by_bay[b],endian) for b in order)
def make_state64(by_bay,order,serial_endian,state_endian,swap):
    raw=b"".join(by_bay[b] if serial_endian=="big" else by_bay[b][::-1] for b in order)
    words=[int.from_bytes(raw[:8],state_endian),int.from_bytes(raw[8:],state_endian)]
    if swap: words.reverse()
    return tuple(words)
def packet32(state,variant,warmup,endian,reverse):
    s=tuple(state)
    for _ in range(warmup): _,s=xoshiro128_next(s,variant)
    words=[]
    for _ in range(4): o,s=xoshiro128_next(s,variant); words.append(o)
    if reverse: words.reverse()
    return b"".join(x.to_bytes(4,endian) for x in words)
def packet64(state,variant,warmup,endian,reverse):
    s=tuple(state)
    step=xorshift128plus_next if variant=="xorshift128+" else lambda z:xoroshiro_next(z,variant)
    for _ in range(warmup): _,s=step(s)
    words=[]
    for _ in range(2): o,s=step(s); words.append(o)
    if reverse: words.reverse()
    return b"".join(x.to_bytes(8,endian) for x in words)
def packet_mt(seed,warmup,mode,endian,reverse):
    rng=random.Random(seed)
    if mode=="MT128":
        for _ in range(warmup): rng.getrandbits(128)
        return rng.getrandbits(128).to_bytes(16,endian)
    for _ in range(warmup): rng.getrandbits(32)
    words=[rng.getrandbits(32) for _ in range(4)]
    if reverse: words.reverse()
    return b"".join(x.to_bytes(4,endian) for x in words)
def packet_pcg(seed,warmup,endian,reverse,dxsm=False):
    import numpy as np
    bg=np.random.PCG64DXSM(seed) if dxsm else np.random.PCG64(seed)
    rng=np.random.Generator(bg)
    for _ in range(warmup): rng.bit_generator.random_raw()
    words=[int(rng.bit_generator.random_raw()) for _ in range(2)]
    if reverse: words.reverse()
    return b"".join(x.to_bytes(8,endian) for x in words)

def sanity_checks():
    assert xoshiro128_next((1,2,3,4),"xoshiro128**")[0] == 0x2D00
    assert xoshiro128_next((1,2,3,4),"xoshiro128++")[0] == 0x281
    state=(0x123456789ABCDEF0,0x0FEDCBA987654321)
    for view in range(4):
        endian="little" if view & 1 else "big"
        reverse=bool(view & 2)
        assert packet64(state,"xoroshiro128++",0,endian,reverse) == base.packet_from_state(state,view)

def main():
    sanity_checks()
    ap=argparse.ArgumentParser(); ap.add_argument("--evidence",type=Path,required=True); args=ap.parse_args()
    receipts=base.load_receipts(args.evidence/"maintenance"/"seal-receipts.jsonl")
    packets=base.load_packets(args.evidence/"print"/"spool-reconstruction.log")
    rolling={}; states={}
    for n in range(390,417):
        bay,serial=receipts[n]; rolling[bay]=serial
        if len(rolling)==4 and n in packets: states[n]=dict(rolling)
    assert set(states)==set(range(395,417))
    results=[]
    for variant in ("xoshiro128**","xoshiro128++"):
      for order in base.BAY_ORDERS:
       for state_endian in ("big","little"):
        for warmup in range(65):
         for out_endian in ("big","little"):
          for reverse in (False,True):
           matches=sum(packet32(make_state32(states[n],order,state_endian),variant,warmup,out_endian,reverse)==packets[n] for n in range(395,417))
           results.append(matches)
    for variant in ("xoroshiro128++","xoroshiro128**","xorshift128+"):
      for order in base.BAY_ORDERS:
       for serial_endian in ("big","little"):
        for state_endian in ("big","little"):
         for swap in (False,True):
          for warmup in range(65):
           for out_endian in ("big","little"):
            for reverse in (False,True):
             matches=sum(packet64(make_state64(states[n],order,serial_endian,state_endian,swap),variant,warmup,out_endian,reverse)==packets[n] for n in range(395,417))
             results.append(matches)
    numpy_available=True
    try: import numpy as np; numpy_version=np.__version__
    except ImportError: numpy_available=False; numpy_version=None
    variants=("MT32","MT128","PCG64","PCG64DXSM") if numpy_available else ("MT32","MT128")
    for variant in variants:
      for order in base.BAY_ORDERS:
       for serial_endian in ("big","little"):
        for warmup in range(33):
         for out_endian in ("big","little"):
          reverse_views=(False,) if variant=="MT128" else (False,True)
          for reverse in reverse_views:
           matches=0
           for n in range(395,417):
            raw=b"".join(states[n][b] if serial_endian=="big" else states[n][b][::-1] for b in order)
            seed=int.from_bytes(raw,"big")
            if variant.startswith("MT"): pred=packet_mt(seed,warmup,variant,out_endian,reverse)
            else: pred=packet_pcg(seed,warmup,out_endian,reverse,variant=="PCG64DXSM")
            matches += pred==packets[n]
           results.append(matches)
    print(json.dumps({"experiment":"rolling-PTW alternative PRNG/warm-up screen","training_pairs":22,
      "training_jobs":[f"PS-{n:04d}" for n in range(395,417)],"target_PS_0417_used_for_fitting":False,
      "configuration_count":len(results),"maximum_exact_packet_matches_of_22":max(results),
      "zero_match_configurations":sum(x==0 for x in results),"numpy_available":numpy_available,"numpy_version":numpy_version,
      "synthetic_known_answer_checks":"passed","target_candidate_emitted":False,"limitations":["PTW/PS same-suffix join is exploratory and not source-authenticated",
      "only listed state layouts, PRNGs, output serializers and warm-up ranges were tested","zero matches do not exclude other producer algorithms or source relationships"]},indent=2))
if __name__=="__main__": main()
