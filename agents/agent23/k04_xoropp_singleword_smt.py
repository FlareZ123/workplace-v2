#!/usr/bin/env python3
"""Exact single-word xoroshiro128++ 1.0 inversion, synthetic controls only.

For first output y0, the state can be parametrized by either one 64-bit
unknown c=a0+b0 or a=a0. Middle outputs can be withheld by observing
indices (0,1,4,5). A SAT witness must be independently replayed.
No H17 source inputs, commitments, candidate values or source diagnostics.
"""
from __future__ import annotations
import ctypes
import random
from typing import Mapping

MASK = (1 << 64) - 1

def rot(x: int, k: int) -> int:
    return ((x << k) | (x >> (64 - k))) & MASK

def emit(a: int, b: int, n: int = 6) -> tuple[int, ...]:
    out = []
    for _ in range(n):
        out.append((rot((a+b) & MASK, 17) + a) & MASK)
        t = a ^ b
        a = rot(a, 49) ^ t ^ ((t << 21) & MASK)
        b = rot(t, 28)
    return tuple(out)

def parametrized(y0: int, x: int, pivot: str) -> tuple[int, int]:
    assert pivot in ("a", "c") and 0 <= x <= MASK and 0 <= y0 <= MASK
    if pivot == "c":
        a = (y0 - rot(x, 17)) & MASK
        b = (x - a) & MASK
    else:
        a = x
        c = rot((y0 - a) & MASK, 47)
        b = (c - a) & MASK
    return a, b

def smtlib(observed: Mapping[int, int], pivot: str = "c",
           high_bits: tuple[int,int] | None = None,
           timeout_ms: int = 10000) -> str:
    """Single unknown and exact later outputs; synthetic prefix only in tests.

    'observed' maps output index to complete 64-bit values; output zero is
    required. high_bits=(n, value) is an optional *explicit* source condition
    or planted-fixture calibration, not an inferred historical witness.
    """
    assert pivot in ("a", "c") and 0 in observed and len(observed) >= 2
    assert all(isinstance(i,int) and 0 <= i <= 50 and isinstance(y,int)
               and 0 <= y <= MASK for i,y in observed.items())
    assert 1 <= timeout_ms <= 600000
    y0 = observed[0]
    def R(x,n): return f"((_ rotate_left {n}) {x})"
    def A(x,y): return f"(bvadd {x} {y})"
    def X(x,y): return f"(bvxor {x} {y})"
    v = "c" if pivot == "c" else "a0"
    s = [f"(set-option :timeout {timeout_ms})", "(set-logic QF_BV)",
         f"(declare-const {v} (_ BitVec 64))"]
    if pivot == "c":
        s.extend([f"(define-fun a0 () (_ BitVec 64) (bvsub #x{y0:016x} {R('c',17)}))",
                  "(define-fun b0 () (_ BitVec 64) (bvsub c a0))"])
    else:
        s.extend([f"(define-fun c0 () (_ BitVec 64) {R(f'(bvsub #x{y0:016x} a0)',47)})",
                  "(define-fun b0 () (_ BitVec 64) (bvsub c0 a0))"])
    if high_bits is not None:
        n, value = high_bits
        assert 1 <= n <= 64 and 0 <= value < (1 << n)
        s.append(f"(assert (= ((_ extract 63 {64-n}) {v}) (_ bv{value} {n})))")
    for i in range(max(observed)+1):
        if i:
            t = f"t{i-1}"
            s.extend([f"(define-fun {t} () (_ BitVec 64) {X(f'a{i-1}',f'b{i-1}')})",
                      f"(define-fun a{i} () (_ BitVec 64) {X(X(R(f'a{i-1}',49),t),f'(bvshl {t} #x0000000000000015)')})",
                      f"(define-fun b{i} () (_ BitVec 64) {R(t,28)})"])
        if i and i in observed:
            output = A(R(A(f"a{i}",f"b{i}"),17),f"a{i}")
            s.append(f"(assert (= {output} #x{observed[i]:016x}))")
    return "\n".join([*s, "(check-sat)"]) + "\n"

def _z3(script: str) -> str | None:
    try: lib = ctypes.CDLL("libz3.so.4")
    except OSError: return None
    lib.Z3_mk_config.restype = ctypes.c_void_p
    lib.Z3_mk_context.argtypes = [ctypes.c_void_p]
    lib.Z3_mk_context.restype = ctypes.c_void_p
    lib.Z3_del_config.argtypes = [ctypes.c_void_p]
    lib.Z3_del_context.argtypes = [ctypes.c_void_p]
    lib.Z3_eval_smtlib2_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    cfg = lib.Z3_mk_config()
    ctx = lib.Z3_mk_context(cfg)
    try:
        out = lib.Z3_eval_smtlib2_string(ctx, script.encode("ascii"))
        return out.decode("utf-8").strip() if out else None
    finally:
        lib.Z3_del_context(ctx)
        lib.Z3_del_config(cfg)

def test_synthetic() -> None:
    rng = random.Random(0x20261127)
    for _ in range(128):
        a,b = rng.getrandbits(64),rng.getrandbits(64)
        y = emit(a,b)
        assert parametrized(y[0],a,"a") == (a,b)
        assert parametrized(y[0],(a+b)&MASK,"c") == (a,b)
    a = random.Random(0x20261127).getrandbits(64)
    b = random.Random(0x20261128).getrandbits(64)
    y = emit(a,b)
    observed = {i:y[i] for i in (0,1,4,5)}
    for pivot,x in (("a",a),("c",(a+b)&MASK)):
        assert smtlib(observed,pivot).count("declare-const") == 1
        good = _z3(smtlib(observed,pivot,(32,x>>32),15000))
        if good is None: continue
        assert good == "sat", f"anchored planted SAT: {good}"
        wrong = dict(observed)
        wrong[1] ^= 1
        bad = _z3(smtlib(wrong,pivot,(64,x),1000))
        assert bad == "unsat", f"anchored poisoned output: {bad}"
    print("synthetic one-word elimination / anchored SAT-UNSAT controls PASS")

if __name__ == "__main__":
    test_synthetic()
