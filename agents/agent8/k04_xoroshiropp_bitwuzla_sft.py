#!/usr/bin/env python3
"""Independent Bitwuzla bit-vector engine for an exact-job xoroshiro128++ middle coupon.

This exploratory hypothesis treats two intact 18:01/18:03 same-job requests
as four raw64 observations at native offsets 0,1,4,5. Recover offsets 2,3 as
the hypothetical missing whole 18:02 RECOVER coupon. No historical source
establishes that the printer used this generator.

The selected ACK2 copied bytes are strictly excluded from the source solve.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
import time
from pathlib import Path

from bitwuzla import Bitwuzla, Kind, Options, Option, Result, TermManager

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FIRST = "CD3E4F216ADB2FB180DA2AA90B33F7A4"
THIRD = "44D53DFC29D7943A95D89371DA58EC64"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
TEST_SEED = 0x5D1DE1A5CAFEBEEF, 0x17A5B3CB69A1CBCA
U64 = (1 << 64) - 1


def rotate(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & U64


def native(a: int, b: int) -> tuple[int, int, int]:
    y = (rotate((a+b)&U64,17)+a)&U64
    t = a ^ b
    return y, (rotate(a,49)^t^((t<<21)&U64))&U64, rotate(t,28)


def six_outputs(a: int, b: int) -> list[int]:
    out = []
    for _ in range(6):
        y,a,b = native(a,b)
        out.append(y)
    return out


def decode(payload: bytes, view: int) -> tuple[int,int]:
    endian = "<" if view & 1 == 0 else ">"
    words = list(struct.unpack(endian+"QQ",payload))
    if view & 2:
        words.reverse()
    return words[0],words[1]


def encode(words: tuple[int,int], view: int) -> bytes:
    endian = "<" if view & 1 == 0 else ">"
    seq = words[::-1] if view & 2 else words
    return struct.pack(endian+"QQ",*seq)


def read_original(root: Path) -> tuple[bytes,bytes]:
    source = (root/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    if hashlib.sha256(source).hexdigest()!=SPOOL_SHA:
        raise ValueError("original spool SHA drift")
    values = {}
    for line in source.decode("ascii").splitlines():
        if not line.startswith(("2026-10-03T18:01:00Z ","2026-10-03T18:03:00Z ")):
            continue
        cells = dict(t.split("=",1) for t in line.split() if "=" in t)
        if (cells.get("JOB"), cells.get("CLASS"), cells.get("STATE")) != (
            "PS-261003-0417","RECOVER","REQUESTED"
        ):
            raise ValueError("original request identity mismatch")
        num = int(cells["ATTEMPT"])
        if num in values:
            raise ValueError("duplicate exact-time request")
        values[num] = bytes.fromhex(cells["PAYLOAD"])
    expected = {1:bytes.fromhex(FIRST),3:bytes.fromhex(THIRD)}
    if values!=expected:
        raise ValueError("original source request bytes mismatch")
    return values[1],values[3]


def solve(flanks: tuple[int,int,int,int], limit_seconds: float, low16: int|None):
    tm = TermManager()
    sort64=tm.mk_bv_sort(64)
    opts=Options()
    opts.set(Option.PRODUCE_MODELS,True)
    solver=Bitwuzla(tm,opts)
    first_a = tm.mk_const(sort64,"first_state_a")
    first_b = tm.mk_const(sort64,"first_state_b")
    def op(kind, *terms):
        return tm.mk_term(kind,list(terms))
    def rol(term,n:int):
        return tm.mk_term(Kind.BV_ROLI,[term],[n])
    def val(number:int):
        return tm.mk_bv_value(sort64,number)

    if low16 is not None:
        solver.assert_formula(op(Kind.EQUAL,
                                 op(Kind.BV_AND,first_a,val(65535)),val(low16)))
    a,b=first_a,first_b
    out=[]
    for _ in range(6):
        y=op(Kind.BV_ADD,rol(op(Kind.BV_ADD,a,b),17),a)
        t=op(Kind.BV_XOR,a,b)
        next_a=op(Kind.BV_XOR,op(Kind.BV_XOR,rol(a,49),t),op(Kind.BV_SHL,t,val(21)))
        next_b=rol(t,28)
        out.append(y)
        a,b=next_a,next_b
    for pos,number in zip((0,1,4,5),flanks):
        solver.assert_formula(op(Kind.EQUAL,out[pos],val(number)))
    started=time.monotonic()
    solver.configure_terminator(lambda: time.monotonic()-started>=limit_seconds)
    result=solver.check_sat()
    print(f"bitwuzla={result} time_sec={time.monotonic()-started:.3f}",flush=True)
    if result != Result.SAT:
        return None
    state = tuple(int(solver.get_value(v).value(16),16) for v in (first_a,first_b))
    full=six_outputs(*state)
    if tuple(full[p] for p in (0,1,4,5))!=flanks:
        raise AssertionError("model failed exact complete-source holdout")
    print(f"initial_state={state[0]:016X}/{state[1]:016X}",flush=True)
    return full


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase",choices=("positive","original"),required=True)
    p.add_argument("--view",type=int,choices=range(4),default=0)
    p.add_argument("--limit-seconds",type=float,default=300.0)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    args=p.parse_args()
    if args.limit_seconds<=0:
        p.error("positive limit required")
    if args.phase=="positive":
        outputs=six_outputs(*TEST_SEED)
        flanks=tuple(outputs[p] for p in (0,1,4,5))
        proposed=solve(flanks,args.limit_seconds,TEST_SEED[0]&0xFFFF)
        if proposed is None:
            print("PLANTED_SOLVER_LIMIT; original untested",flush=True)
            return 2
        if proposed[2:4]!=outputs[2:4]:
            raise AssertionError("wrong full planted middle")
        print("PLANTED_WHOLE_MIDDLE_PASS",encode(tuple(proposed[2:4]),args.view).hex().upper(),flush=True)
        return 0
    before,after=read_original(args.root)
    flanks=(*decode(before,args.view),*decode(after,args.view))
    proposed=solve(flanks,args.limit_seconds,None)
    if proposed is None:
        print("ORIGINAL_SOLVER_UNRESOLVED_OR_UNSAT (consult result)",flush=True)
        return 0
    coupon=encode(tuple(proposed[2:4]),args.view)
    part=bytes(a^b for a,b in zip(coupon,MASK))
    h=hashlib.sha256(part).hexdigest()
    print("ORIGINAL_MIDDLE",coupon.hex().upper(),flush=True)
    print("ORIGINAL_K04_COMPONENT",part.hex().upper(),"SHA256",h,flush=True)
    print("K04_PASS" if h==TARGET else "K04_NO_MATCH",flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
