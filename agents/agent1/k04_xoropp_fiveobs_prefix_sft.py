#!/usr/bin/env python3
"""H-17 K04: five-output xoroshiro128++ 1.0 exact inverse with fixed low16 state prefix.

Source model: 18:01 REQUESTED1 gives outputs0,1; copied ACK2 *tail8*
conditionally gives output3; intact 18:03 REQUESTED3 gives outputs4,5.
Output2, selected ACK2 head8 and full selected coupon are WITHHELD.
Historical printer generator, common-state issuer and copied tail fidelity
are UNAUTHENTICATED. Original SHA is checked on every complete SAT coupon
regardless of previous-packet replay attribution. Unknown != UNSAT.
Run with Python stdlib and libz3.so.4:
  python agents/agent1/k04_xoropp_fiveobs_prefix_sft.py --preflight
  python agents/agent1/k04_xoropp_fiveobs_prefix_sft.py --original --prefix 0 --endian big
"""
import argparse,ctypes,ctypes.util,hashlib,json,random,re,time
from pathlib import Path
MASK=(1<<64)-1
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def rol(x,n):return ((x<<n)|(x>>(64-n)))&MASK
def next_word(a,b):
    word=(rol((a+b)&MASK,17)+a)&MASK
    t=a^b
    return word,rol(a,49)^t^((t<<21)&MASK),rol(t,28)
def stream(state):
    a,b=state;out=[]
    for _ in range(6):
        val,a,b=next_word(a,b);out.append(val)
    return out
def zrol(expr,n):return f"((_ rotate_left {n}) {expr})"

def solve(obs,prefix,limit_ms=20000,max_models=2):
    assert len(obs)==6 and obs[0] is not None and obs[2] is None
    assert 0<=prefix<65536 and 0<limit_ms<=120000
    lib=ctypes.CDLL(ctypes.util.find_library("z3") or "libz3.so.4")
    lib.Z3_mk_config.restype=ctypes.c_void_p
    lib.Z3_mk_context.argtypes=[ctypes.c_void_p]
    lib.Z3_mk_context.restype=ctypes.c_void_p
    lib.Z3_del_config.argtypes=[ctypes.c_void_p]
    lib.Z3_del_context.argtypes=[ctypes.c_void_p]
    lib.Z3_eval_smtlib2_string.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype=ctypes.c_char_p
    cfg=lib.Z3_mk_config();ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
    def run(s):return lib.Z3_eval_smtlib2_string(ctx,s.encode()).decode().strip()
    try:
        x=["(set-option :produce-models true)",f"(set-option :timeout {limit_ms})",
           "(set-logic QF_BV)","(declare-const a0 (_ BitVec 64))",
           f'(define-fun b0 () (_ BitVec 64) (bvsub {zrol(f"(bvsub #x{obs[0]:016x} a0)",47)} a0))',
           f"(assert (= ((_ extract 15 0) a0) #x{prefix:04x}))"]
        for i in range(6):
            if i<5:
                t=f"(bvxor a{i} b{i})"
                x.append(f'(define-fun a{i+1} () (_ BitVec 64) (bvxor (bvxor {zrol(f"a{i}",49)} {t}) (bvshl {t} #x0000000000000015)))')
                x.append(f'(define-fun b{i+1} () (_ BitVec 64) {zrol(t,28)})')
            if obs[i] is not None:
                x.append(f'(assert (= (bvadd {zrol(f"(bvadd a{i} b{i})",17)} a{i}) #x{obs[i]:016x}))')
        run("\n".join(x))
        models=[];statuses=[]
        for count in range(max_models+1):
            started=time.monotonic()
            status=run("(check-sat-using (then simplify bit-blast sat))")
            statuses.append((status,round(time.monotonic()-started,3)))
            if status!="sat":break
            match=re.findall(r"#x([0-9a-fA-F]{16})",run("(get-value (a0 b0))"))
            if len(match)!=2:raise RuntimeError("Z3 returned invalid state")
            a,b=(int(z,16) for z in match)
            replay=stream((a,b))
            assert all(v is None or replay[i]==v for i,v in enumerate(obs))
            models.append({"state":[f"{a:016X}",f"{b:016X}"],
                "middle_words":[f"{replay[2]:016X}",f"{replay[3]:016X}"]})
            run(f"(assert (not (= a0 #x{a:016x})))")
        if statuses[-1][0]=="sat":raise RuntimeError("unresolved >max_models distinct solutions")
        return {"prefix":f"{prefix:04X}","statuses":statuses,
                "enumeration_complete":statuses[-1][0]=="unsat","models":models}
    finally:lib.Z3_del_context(ctx)

def preflight(seconds):
    positives=[]
    for seed_id in (4141,111,222,333,444,555,666):
        rng=random.Random(seed_id)
        state=(rng.getrandbits(64),rng.getrandbits(64))
        original=stream(state);known=original.copy();known[2]=None
        result=solve(known,state[0]&65535,seconds*1000)
        assert result["enumeration_complete"] and len(result["models"])==1
        assert result["models"][0]["state"]==[f"{v:016X}" for v in state]
        assert result["models"][0]["middle_words"]==[f"{v:016X}" for v in original[2:4]]
        positives.append({"seed_id":seed_id,"status":result["statuses"]})
        print(json.dumps({"preflight":"planted withheld whole coupon and unique state",
            "seed_id":seed_id,"status":"PASS","details":result["statuses"]}),flush=True)
    rng=random.Random(4141);state=(rng.getrandbits(64),rng.getrandbits(64))
    original=stream(state);original[2]=None
    bad=solve(original,(state[0]^1)&65535,seconds*1000)
    assert bad["enumeration_complete"] and bad["models"]==[]
    print(json.dumps({"preflight":"wrong prefix UNSAT","status":"PASS","details":bad["statuses"]}),flush=True)
    return positives

def read_original(root,endian):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SPOOL_SHA
    rows=re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw,re.M)
    assert len(rows)==133
    assert rows[129][:5] == (
        b"2026-10-03T18:02:00Z",b"PS-261003-0417",b"2",b"ACK",b"RECOVER")
    assert rows[128][1:4] == (b"PS-261003-0417",b"1",b"REQUESTED")
    assert rows[130][1:4] == (b"PS-261003-0417",b"3",b"REQUESTED")
    # Only decode copied last eight bytes. First eight copied ACK bytes are withheld.
    tail=bytes.fromhex(rows[129][5][-16:].decode())
    first=bytes.fromhex(rows[128][5].decode())
    third=bytes.fromhex(rows[130][5].decode())
    dec=lambda b:[int.from_bytes(b[i:i+8],endian) for i in (0,8)]
    obs=dec(first)+[None,int.from_bytes(tail,endian)]+dec(third)
    route=json.loads((root/"evidence/recovery-routing.json").read_text())
    accepted=json.loads((root/"acceptance.json").read_text())
    mask=bytes.fromhex(route["K04"]["masked_component"])
    assert len(mask)==16 and accepted["slot_sha256"]["K04"]==K04_SHA
    return obs,tail,mask

def original(root,endian,prefix,seconds):
    obs,tail,mask=read_original(root,endian)
    out=solve(obs,prefix,seconds*1000)
    out.update({"endian":endian,"source_sha256":SPOOL_SHA,
        "copied_head8_used":False,
        "issuer_and_tail_integrity":"UNAUTHENTICATED"})
    for rec in out["models"]:
        coupon=b"".join(int(w,16).to_bytes(8,endian) for w in rec["middle_words"])
        assert coupon[8:]==tail
        candidate=bytes(a^b for a,b in zip(coupon,mask))
        rec["coupon"]=coupon.hex().upper()
        rec["component"]=candidate.hex().upper()
        rec["original_K04_commitment"]=(
            "PASS" if hashlib.sha256(candidate).hexdigest()==K04_SHA else "NO_MATCH")
    out["original_K04_commitment"]=(
        "PASS" if any(v["original_K04_commitment"]=="PASS" for v in out["models"]) else
        ("NO_MATCH_COMPLETE_CANDIDATE" if out["models"] else "NOT_EVALUATED"))
    return out

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight",action="store_true")
    group.add_argument("--original",action="store_true")
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    parser.add_argument("--endian",choices=("big","little"),default="big")
    parser.add_argument("--prefix",type=int,default=0)
    parser.add_argument("--seconds",type=int,default=20)
    args=parser.parse_args()
    assert 0<args.seconds<=120
    if args.preflight:preflight(args.seconds)
    else:
        result=original(args.root,args.endian,args.prefix,args.seconds)
        print(json.dumps(result,sort_keys=True),flush=True)
        if result["original_K04_commitment"]=="PASS":raise SystemExit(9)
        if not result["enumeration_complete"]:raise SystemExit(3)

if __name__=="__main__":main()
