"""Boolector target-complete xoroshiro128++ source bridge (conjectural).
The selected PS-0417 ACK2 copied bytes never enter state inversion.
Run from repository root; requires PyBoolector on Python 3.11.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pyboolector

R = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK64 = (1 << 64) - 1

def rol(x, k):
    return ((x << k) | (x >> (64-k))) & MASK64

def next64(a, b):
    out = (rol((a+b) & MASK64, 17) + a) & MASK64
    t = a ^ b
    return out, (rol(a,49) ^ t ^ (t << 21)) & MASK64, rol(t,28)

def series(a,b):
    outputs = []
    for _ in range(6):
        y,a,b = next64(a,b)
        outputs.append(y)
    return outputs

def decode(packet, view):
    order = "little" if (view & 1) else "big"
    data = [int.from_bytes(packet[i:i+8],order) for i in (0,8)]
    return data[::-1] if (view & 2) else data

def encode(words, view):
    order = "little" if (view & 1) else "big"
    if view & 2: words = words[::-1]
    return b"".join(w.to_bytes(8,order) for w in words)

def solve_state(first,last,mode):
    bt=pyboolector.Boolector()
    bt.Set_opt(pyboolector.BTOR_OPT_MODEL_GEN,1)
    initial_a=bt.Var(bt.BitVecSort(64),"initial_s0")
    initial_b=(bt.Ror(bt.Const(first[0],64)-initial_a,17)-initial_a
               if mode=="elimination" else bt.Var(bt.BitVecSort(64),"initial_s1"))
    a,b=initial_a,initial_b
    outs=[]
    for _ in range(6):
        outs.append(bt.Rol(a+b,17)+a)
        t=a^b
        a,b=bt.Rol(a,49)^t^(t<<21),bt.Rol(t,28)
    for index,value in zip((0,1,4,5),(*first,*last)):
        bt.Assert(outs[index]==bt.Const(value,64))
    outcome=bt.Sat()
    if outcome==bt.UNSAT:return {"status":"UNSAT"}
    if outcome!=bt.SAT:return {"status":"UNKNOWN","code":int(outcome)}
    state=(int(initial_a.assignment,2),int(initial_b.assignment,2))
    values=series(*state)
    assert values[:2]==list(first) and values[4:]==list(last)
    return {"status":"SAT","middle":values[2:4]}

def original_records():
    log=(R/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(log).hexdigest()==SPOOL_SHA
    rows={}
    for line in log.decode("ascii").splitlines():
        if line.startswith("2026-"):
            t,*tokens=line.split()
            rows[t]=dict(field.split("=",1) for field in tokens)
    assert len(rows)==133
    a,b,c=[rows[f"2026-10-03T18:{minute}:00Z"] for minute in ("01","02","03")]
    assert all(x["JOB"]=="PS-261003-0417" for x in (a,b,c))
    assert [(x["STATE"],x["ATTEMPT"]) for x in (a,b,c)]==[
        ("REQUESTED","1"),("ACK","2"),("REQUESTED","3")]
    # b["PAYLOAD"] is withheld to avoid fitting the unauthenticated dispatch copy.
    first,last=bytes.fromhex(a["PAYLOAD"]),bytes.fromhex(c["PAYLOAD"])
    assert first.hex().upper()=="CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert last.hex().upper()=="44D53DFC29D7943A95D89371DA58EC64"
    return first,last

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--view",type=int,choices=range(4),required=True)
    parser.add_argument("--solver-mode",choices=("direct","elimination"),default="direct")
    parser.add_argument("--control-only",action="store_true")
    args=parser.parse_args()
    before,after=original_records()
    assert encode(decode(bytes(range(16)),args.view),args.view)==bytes(range(16))
    synthetic=series(0x5D1DE1A5CAFEBEEF,0x17A5B3CB69A1CBCA)
    print("PLANTED_CONSTRAINTS",*[f"{synthetic[i]:016X}" for i in (0,1,4,5)],flush=True)
    positive=solve_state(synthetic[:2],synthetic[4:],args.solver_mode)
    assert positive["status"]=="SAT",positive
    assert positive["middle"]==synthetic[2:4],positive
    print("SEEDED_SIX_OUTPUT_CONTROL_PASS",flush=True)
    if args.control_only:return
    original=solve_state(decode(before,args.view),decode(after,args.view),args.solver_mode)
    result={"view":args.view,"mode":args.solver_mode,"original_status":original["status"],"positive":"PASS"}
    if original["status"]=="SAT":
        coupon=encode(original["middle"],args.view)
        mask=bytes.fromhex(json.loads((R/"evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
        component=bytes(x^y for x,y in zip(coupon,mask))
        target=json.loads((R/"acceptance.json").read_text())["slot_sha256"]["K04"]
        passed=hashlib.sha256(component).hexdigest()==target
        result.update({"complete_coupon":coupon.hex().upper(),"original_K04_PASS":passed,
                       "K04_component_if_PASS":component.hex().upper() if passed else None})
    print(json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
