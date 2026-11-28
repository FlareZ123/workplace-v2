#!/usr/bin/env python3
"""Exact xorshift128+ full-state inversion of the historical PS-0417 gap.

The untouched 18:01 RECOVER REQUESTED1 and 18:03 RECOVER REQUESTED3
are six-output positions 0,1 and 4,5. The 18:02 ACK2 is withheld
completely as positions 2,3. Solves all 128 unknown state bits with SMT,
using official Vigna (23,18,5) and V8 (23,17,26) transitions.

For the V8 after-update emitter, the unknown initial state is redefined
as its post-first-update state. The GF(2)-linear update is bijective;
hence this one-step origin shift preserves ALL possible six-word streams
while making the first observed word a sum of the initial state.

Only run locally against SHA-pinned original resources. Original values
and any key material never printed; public source-bearing CI refused.
Usage: python agents/agent3/k04_xorshiftplus_samejob_gap_sft.py
"""
import ctypes, hashlib, json, os, random, re
from pathlib import Path
if os.getenv("GITHUB_ACTIONS", "").lower()=="true":
    raise SystemExit("No public source-bearing CI")
ROOT=Path(__file__).resolve().parents[2]/"resources"
PINS={
"evidence/print/spool-reconstruction.log":"7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
"evidence/recovery-routing.json":"f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
"acceptance.json":"681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
Z=ctypes.CDLL("libz3.so.4")
Z.Z3_mk_config.restype=ctypes.c_void_p
Z.Z3_set_param_value.argtypes=(ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p)
Z.Z3_mk_context.argtypes=(ctypes.c_void_p,)
Z.Z3_mk_context.restype=ctypes.c_void_p
Z.Z3_eval_smtlib2_string.argtypes=(ctypes.c_void_p,ctypes.c_char_p)
Z.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
Z.Z3_del_context.argtypes=(ctypes.c_void_p,)
MASK=(1<<64)-1

def evaluate(smt):
    cfg=Z.Z3_mk_config()
    Z.Z3_set_param_value(cfg,b"timeout",b"35000")
    ctx=Z.Z3_mk_context(cfg)
    try:
        return Z.Z3_eval_smtlib2_string(ctx,smt.encode()).decode().strip()
    finally:
        Z.Z3_del_context(ctx)

def source_stream(a,b,variant):
    observed=[]
    for _ in range(6):
        observed.append((a+b)&MASK)
        s1=a;s0=b;a=s0
        s1^=(s1<<23)&MASK
        if variant==0:b=s1^s0^(s1>>18)^(s0>>5)
        else:
            s1^=s1>>17
            b=s1^s0^(s0>>26)
    return observed

def equation(outputs,variant,model=False):
    code=["(set-option :timeout 35000)","(set-logic QF_BV)",
          "(set-option :produce-models true)",
          "(declare-fun a0 () (_ BitVec 64))",
          "(declare-fun b0 () (_ BitVec 64))"]
    for i in range(6):
        code.append(f"(define-fun o{i} () (_ BitVec 64) (bvadd a{i} b{i}))")
        code.append(f"(define-fun u{i} () (_ BitVec 64) (bvxor a{i} (bvshl a{i} (_ bv23 64))))")
        code.append(f"(define-fun a{i+1} () (_ BitVec 64) b{i})")
        if variant==0:
            code.append(f"(define-fun b{i+1} () (_ BitVec 64) (bvxor (bvxor (bvxor u{i} b{i}) (bvlshr u{i} (_ bv18 64))) (bvlshr b{i} (_ bv5 64))))")
        else:
            code.append(f"(define-fun v{i} () (_ BitVec 64) (bvxor u{i} (bvlshr u{i} (_ bv17 64))))")
            code.append(f"(define-fun b{i+1} () (_ BitVec 64) (bvxor (bvxor v{i} b{i}) (bvlshr b{i} (_ bv26 64))))")
    for i in (0,1,4,5):
        code.append(f"(assert (= o{i} #x{outputs[i]:016x}))")
    code.append("(check-sat)")
    if model:code.append("(get-value (a0 b0))")
    return "\n".join(code)+"\n"

def state_values(result):
    vals=re.findall(r"#x([0-9a-fA-F]{16})",result)
    if not result.startswith("sat") or len(vals)!=2:
        raise RuntimeError("Solver did not produce a complete state")
    return tuple(int(s,16) for s in vals)

def planted_controls():
    for variant in (0,1):
        rng=random.Random(20261128+variant)
        planted=rng.getrandbits(64),rng.getrandbits(64)
        outs=source_stream(*planted,variant)
        actual=state_values(evaluate(equation(outs,variant,True)))
        if actual!=planted or source_stream(*actual,variant)!=outs:
            raise RuntimeError("Full 128-bit planted inversion failed")

def load():
    for rel,digest in PINS.items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()!=digest:
            raise RuntimeError("Source checksum mismatch: "+rel)
    seen={}
    for line in (ROOT/"evidence/print/spool-reconstruction.log").read_text().splitlines():
        if ("JOB=PS-261003-0417 " not in line
            or "STATE=REQUESTED " not in line or "CLASS=RECOVER " not in line):
            continue
        label=("before" if "ATTEMPT=1 " in line else
               "after" if "ATTEMPT=3 " in line else None)
        if label is None:continue
        m=re.search(r"PAYLOAD=([0-9A-Fa-f]{32})(?:\s|$)",line)
        if not m or label in seen:raise RuntimeError("Source stage selection mismatch")
        seen[label]=bytes.fromhex(m[1])
    if set(seen)!={"before","after"}:raise RuntimeError("Source flank absent")
    route=json.loads((ROOT/"evidence/recovery-routing.json").read_text())
    acceptance=json.loads((ROOT/"acceptance.json").read_text())
    return seen,bytes.fromhex(route["K04"]["masked_component"]),bytes.fromhex(acceptance["slot_sha256"]["K04"])

def packet_words(packet,endian,reverse):
    words=[int.from_bytes(packet[i:i+8],endian) for i in (0,8)]
    return words[::-1] if reverse else words

def packet_bytes(words,endian,reverse):
    words=words[::-1] if reverse else words
    return b"".join(w.to_bytes(8,endian) for w in words)

def main():
    planted_controls()
    seen,mask,target=load()
    assert len(mask)==16 and len(target)==32
    sat=unsat=unknown=accepted=0
    for variant in (0,1):
        for endian in ("big","little"):
            for reverse in (False,True):
                obs=[*packet_words(seen["before"],endian,reverse),0,0,
                     *packet_words(seen["after"],endian,reverse)]
                ans=evaluate(equation(obs,variant))
                if ans=="unsat":unsat+=1
                elif ans=="unknown":unknown+=1
                elif ans=="sat":
                    sat+=1
                    state=state_values(evaluate(equation(obs,variant,True)))
                    history=source_stream(*state,variant)
                    assert all(history[i]==obs[i] for i in (0,1,4,5))
                    coupon=packet_bytes(history[2:4],endian,reverse)
                    component=bytes(x^y for x,y in zip(coupon,mask))
                    if hashlib.sha256(component).digest()==target:
                        accepted+=1
                        raise RuntimeError("Authentic K04 hit: do not disclose raw key; preserve privately")
                else:raise RuntimeError("Unexpected solver result")
    print({"models":8,"historical_sat":sat,"historical_unsat":unsat,
           "historical_unknown":unknown,"original_k04_hits":accepted,
           "planted_128bit_state_recoveries":"2/2 PASS",
           "selected_ack2_used":False})

if __name__=="__main__":main()
