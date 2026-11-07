"""Selected-withheld K04 JSF32 whole-late-ACK source control.

Condition: one uninterrupted JenkinsSmallFast32 32-bit word stream emits one
16-byte packet per late spool event in source chronological order. The 0417
18:02 copied selected ACK payload is not used as input or control.
No record claims JSF32; this is an explicit new falsifiable issuer candidate.

Use: pip install z3-solver==4.13.3.0
     python agents/agent18/k04_jsf32_dual_late_ack_sft.py
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from z3 import BitVec, BitVecVal, RotateLeft, Solver, sat, unsat

ROOT = Path(__file__).resolve().parents[2]
SPOOL_PATH = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTE_PATH = ROOT / "resources/evidence/recovery-routing.json"
ACCEPT_PATH = ROOT / "resources/acceptance.json"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED_COPIED = "A9A9DC5731A5E2AE879C47215C2559D5"
UINT = (1 << 32) - 1

def parse_rows():
    raw = SPOOL_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_HASH
    rows = []
    for line in raw.decode("ascii").splitlines():
        m = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        if m:
            rows.append((line, bytes.fromhex(m.group(1))))
    assert len(rows) == 133
    assert len([v for line,v in rows if "STATE=ACK" in line]) == 131
    assert rows[129][1].hex().upper() == SELECTED_COPIED
    assert all("STATE=ACK CLASS=RECOVER" in rows[i][0] for i in (131,132))
    assert all("STATE=REQUESTED CLASS=RECOVER" in rows[i][0] for i in (128,130))
    return rows

def word_view(b, order, endian):
    w = [int.from_bytes(b[i:i+4],endian) for i in range(0,16,4)]
    return w[::-1] if order else w

def serialize(w, order, endian):
    items = w[::-1] if order else w
    return b"".join(int(x).to_bytes(4,endian) for x in items)

def step_py(s):
    a,b,c,d=s
    rot=lambda x,k:((x<<k)|(x>>(32-k))) & UINT
    e=(a-rot(b,27))&UINT
    aa=b^rot(c,17)
    return (aa,(c+d)&UINT,(d+e)&UINT,(e+aa)&UINT)

def make_outputs_py(initial, count):
    out=[]
    state=initial
    for _ in range(count):
        state=step_py(state)
        out.append(state[3])
    return out

def z3_step(s):
    a,b,c,d=s
    e=a-RotateLeft(b,27)
    aa=b ^ RotateLeft(c,17)
    return (aa,c+d,d+e,e+aa)

def solve(request1, request3, timeout_ms=120000):
    # The first emitted word algebraically eliminates initial state a.
    # After each constrained output, substitute the known whole source value
    # before constructing later steps to simplify nonlinear carry logic.
    b0=BitVec("jsf_b0",32)
    c0=BitVec("jsf_c0",32)
    d0=BitVec("jsf_d0",32)
    a0=BitVecVal(request1[0],32) - (b0 ^ RotateLeft(c0,17)) + RotateLeft(b0,27)
    state=(a0,b0,c0,d0)
    observed={**{i:w for i,w in enumerate(request1)},
              **{8+i:w for i,w in enumerate(request3)}}
    s=Solver()
    s.set("timeout",timeout_ms)
    output_terms=[]
    for index in range(20):
        state=z3_step(state)
        observed_value=observed.get(index)
        output_terms.append(state[3])
        if observed_value is not None:
            s.add(state[3] == BitVecVal(observed_value,32))
            state=(state[0],state[1],state[2],BitVecVal(observed_value,32))
    start=time.monotonic()
    status=s.check()
    elapsed=round(time.monotonic()-start,3)
    if status!=sat:
        return {"status":str(status),"elapsed_seconds":elapsed,
                "unknown_reason":s.reason_unknown() if status!=unsat else None}
    model=s.model()
    initial=tuple(model.eval(x).as_long() for x in (a0,b0,c0,d0))
    py=make_outputs_py(initial,20)
    assert py[0:4]==request1 and py[8:12]==request3
    # Check whether any other consistent full 131/132 prediction exists.
    s.add((output_terms[12]!=py[12]) | (output_terms[13]!=py[13]) |
          (output_terms[14]!=py[14]) | (output_terms[15]!=py[15]) |
          (output_terms[16]!=py[16]) | (output_terms[17]!=py[17]) |
          (output_terms[18]!=py[18]) | (output_terms[19]!=py[19]))
    uniqueness_status=s.check()
    return {"status":"sat","elapsed_seconds":elapsed,
            "initial_hex":[f"{x:08X}" for x in initial],
            "predicted_selected":py[4:8],
            "predicted_ack131":py[12:16],"predicted_ack132":py[16:20],
            "joint_late_unique":str(uniqueness_status)}

def main():
    rows=parse_rows()
    route=json.loads(ROUTE_PATH.read_text())
    acceptance=json.loads(ACCEPT_PATH.read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=acceptance["slot_sha256"]["K04"]
    assert target=="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
    synthetic_initial=(0xF1EA5EED,0x12345678,0x9ABCDEF0,0x0BADF00D)
    synth=make_outputs_py(synthetic_initial,20)
    # Forward algorithm check: each output is the 4th current state word.
    assert len(set(synth))>18 and len(synth)==20
    planted=solve(synth[:4],synth[8:12],timeout_ms=30000)
    assert planted["status"]=="sat", planted
    assert planted["predicted_ack131"]==synth[12:16]
    assert planted["predicted_ack132"]==synth[16:20]
    print("SOURCE_AND_JSF32_GENUINE_FULL_WHOLEPACKET_POSITIVE_PASS",flush=True)
    hits=[]
    for order in (0,1):
        for endian in ("big","little"):
            input128=word_view(rows[128][1],order,endian)
            input130=word_view(rows[130][1],order,endian)
            r=solve(input128,input130)
            record={"order":order,"endian":endian,"source_only_fit":r["status"],
                    "elapsed_seconds":r["elapsed_seconds"]}
            if r["status"]=="sat":
                late131=serialize(r["predicted_ack131"],order,endian)
                late132=serialize(r["predicted_ack132"],order,endian)
                selected=serialize(r["predicted_selected"],order,endian)
                record.update({
                    "late131_full_match":late131==rows[131][1],
                    "late132_full_match":late132==rows[132][1],
                    "late_joint_unique":r["joint_late_unique"],
                    "predicted_selected_coupon_hex":selected.hex().upper(),
                })
                if late131==rows[131][1] and late132==rows[132][1]:
                    comp=bytes(a^b for a,b in zip(selected,mask))
                    record["original_K04_full_commitment_hit"]=hashlib.sha256(comp).hexdigest()==target
                    if record["original_K04_full_commitment_hit"]:
                        hits.append({"K04":comp.hex().upper(),"source_geometry":record})
            if r["status"]=="unknown":
                record["solver_reason"]=r["unknown_reason"]
            print("ORIGINAL_VIEW",json.dumps(record),flush=True)
    print("FINAL_RESULT",json.dumps({"original_full_K04_hits":hits}),flush=True)

if __name__=="__main__":
    main()
