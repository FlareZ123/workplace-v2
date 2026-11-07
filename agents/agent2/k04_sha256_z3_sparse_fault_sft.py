"""Exact Z3 SHA-256 sparse original K04 copier fault inverse pilot.

No source bytes modified, no acceptance weakened. The original copied ACK2
payload and official route mask are pinned; the authentic K04 commitment is
the full target. Synthetic positive solves first validate true 64-round SHA256
against an independently computed Python hashlib digest. This tests whether
a SAT solver can replace 2^8k brute-force over arbitrary damaged positions.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import time

from z3 import BitVec, BitVecVal, Concat, LShR, RotateRight, Solver, sat, unsat, unknown

ROOT=Path(__file__).resolve().parents[2]
SPOOL=ROOT/"resources"/"evidence"/"print"/"spool-reconstruction.log"
SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK=bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
COPY=bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
ORIGINAL_SHA="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
IV=(0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
    0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19)
K=(
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
)


def sha256_one_block(data):
    assert len(data)==16
    W=[Concat(*data[i:i+4]) for i in range(0,16,4)]
    W += [BitVecVal(0x80000000,32)]
    W += [BitVecVal(0,32)]*10
    W += [BitVecVal(128,32)]
    assert len(W)==16
    for i in range(16,64):
        s0=RotateRight(W[i-15],7)^RotateRight(W[i-15],18)^LShR(W[i-15],3)
        s1=RotateRight(W[i-2],17)^RotateRight(W[i-2],19)^LShR(W[i-2],10)
        W.append(W[i-16]+s0+W[i-7]+s1)
    a,b,c,d,e,f,g,h=(BitVecVal(v,32) for v in IV)
    for i in range(64):
        S1=RotateRight(e,6)^RotateRight(e,11)^RotateRight(e,25)
        choose=(e&f)^((~e)&g)
        t1=h+S1+choose+BitVecVal(K[i],32)+W[i]
        S0=RotateRight(a,2)^RotateRight(a,13)^RotateRight(a,22)
        majority=(a&b)^(a&c)^(b&c)
        t2=S0+majority
        a,b,c,d,e,f,g,h=t1+t2,a,b,c,d+t1,e,f,g
    return (a+IV[0],b+IV[1],c+IV[2],d+IV[3],
            e+IV[4],f+IV[5],g+IV[6],h+IV[7])


def source_pins():
    raw=SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    assert COPY.hex().upper() in raw.decode("ascii")
    assert len(MASK)==len(COPY)==16
    assert hashlib.sha256(bytes(a^b for a,b in zip(COPY,MASK))).hexdigest()!=ORIGINAL_SHA


def solve(target: bytes, positions: tuple[int,...], seconds: int, label: str):
    copied_component=bytes(a^b for a,b in zip(COPY,MASK))
    unknown={i:BitVec(f"masked_component_byte_{i}",8) for i in positions}
    data=[unknown.get(i,BitVecVal(copied_component[i],8)) for i in range(16)]
    digest=sha256_one_block(data)
    solver=Solver()
    solver.set(timeout=seconds*1000)
    for i in range(8):
        word=int.from_bytes(target[4*i:4*i+4],"big")
        solver.add(digest[i]==BitVecVal(word,32))
    t=time.monotonic()
    status=solver.check()
    elapsed=round(time.monotonic()-t,3)
    print("SOURCE_PIN_SHA256_SPARSE_SOLVE",label,"positions",positions,
          "status",str(status),"elapsed_s",elapsed,flush=True)
    if status==sat:
        model=solver.model()
        candidate=bytearray(copied_component)
        for i,symbol in unknown.items():
            candidate[i]=model.eval(symbol).as_long()
        checksum=hashlib.sha256(candidate).digest()
        assert checksum==target
        print("EXACT_SHA256_PREIMAGE",label,"positions",positions,
              "component",candidate.hex().upper(),flush=True)
        return bytes(candidate)
    if status==unknown:
        print("SOLVER_REASON",solver.reason_unknown(),flush=True)
    return None


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",choices=("known3","known4","known5","real3","real4","real5","real5ticket"),
                   required=True)
    p.add_argument("--timeout",type=int,default=90)
    args=p.parse_args()
    source_pins()
    cases={"known3":(0,1,2),"known4":(0,1,2,3),"known5":(0,1,2,3,4),
           "real3":(0,1,2),"real4":(0,1,2,3),"real5":(0,1,2,3,4),
           "real5ticket":(0,2,9,13,15)}
    positions=cases[args.case]
    base=bytes(a^b for a,b in zip(COPY,MASK))
    test_target=hashlib.sha256(base).digest()
    target=test_target if args.case.startswith("known") else bytes.fromhex(ORIGINAL_SHA)
    result=solve(target,positions,args.timeout,args.case)
    if args.case.startswith("known"):
        if result is None:
            print("KNOWN_FIXTURE_SOLVER_TIMEOUT_OR_ERROR",flush=True)
        else:
            assert result==base
            print("POSITIVE_COMPLETE_COPIED_COMPONENT_RECOVERY_PASS",len(positions),flush=True)
    elif result is not None:
        print("ORIGINAL_RECOVERY_TARGET_MATCH_K04",result.hex().upper(),flush=True)


if __name__=="__main__":
    main()
