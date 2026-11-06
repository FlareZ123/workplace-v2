"""Conditional K04 CPython/k2496 source seed sieve with (A7,S7) fixed.

Generated QF_BV is a necessary relaxation of the complete CPython seed
constraints. SAT requires full first-pass and all intact printer validation;
UNSAT would exclude the fixed offset/producer model only. The selected ACK2
and K04 target hash are never used in formula construction.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized, F1, F2, t, U
from k04_cpython_k2496_shortforward_source_sft import original_source

G = [19650218]
for i in range(1, 624):
    G.append((1812433253 * t(G[-1]) + i) & U)


def forward_sieve(n: int, stop: int, masks: list[tuple[int,int]]) -> str:
    assert n in (2, 3, 4) and 8 <= stop <= 623
    s6, s7 = masks[6][1], masks[7][1]
    assert masks[6][0] == masks[7][0] == U
    a7 = ((s7 + 7) & U) ^ (F2 * t(s6) & U)
    assert a7 == 0x2AED5290
    h = lambda x: f"#x{x & U:08X}"
    out = ["(set-logic QF_BV)", "(set-option :produce-models true)"]
    out += [f"(declare-const k{j} (_ BitVec 32))" for j in range(n)]
    out += [f"(define-fun a7 () (_ BitVec 32) {h(a7)})",
            f"(define-fun s7 () (_ BitVec 32) {h(s7)})"]
    for i in range(8, stop + 1):
        j = (i-1) % n
        mix = f"(bvmul {h(F1)} (bvxor a{i-1} (bvlshr a{i-1} {h(30)})))"
        out.append(f"(define-fun a{i} () (_ BitVec 32) (bvadd (bvxor {h(G[i])} {mix}) k{j} {h(j)}))")
        mix = f"(bvmul {h(F2)} (bvxor s{i-1} (bvlshr s{i-1} {h(30)})))"
        out.append(f"(define-fun s{i} () (_ BitVec 32) (bvsub (bvxor a{i} {mix}) {h(i)}))")
        mask, val = masks[i]
        if mask:
            out.append(f"(assert (= (bvand s{i} {h(mask)}) {h(val)}))")
    out.append("(check-sat)")
    out.append("(get-value (" + " ".join(f"k{j}" for j in range(n)) + "))")
    return "\n".join(out) + "\n"


def check_forward_real_python() -> None:
    import random
    count = 0
    for n in (1, 2, 3, 4, 5, 8, 16):
        for trial in range(12):
            keys = [(0x12345678 + j*0x30158DA + trial*0x4F89D7) & U for j in range(n)]
            a, _, s = direct_initialized(keys)
            assert s == list(random.Random(sum(k << (32*j) for j,k in enumerate(keys))).getstate()[1][:624])
            ai, si = a[7], s[7]
            for i in range(8, 84):
                j = (i-1) % n
                ai = ((G[i] ^ (F1*t(ai))) + keys[j] + j) & U
                si = ((ai ^ (F2*t(si))) - i) & U
                assert si == s[i]
            count += 1
    assert count == 84
    print("Genuine complete CPython initialization + A7-forward controls: 84/84 PASS")


if __name__ == "__main__":
    check_forward_real_python()
    masks = original_source()
    for n, stop in ((2,17),(2,41),(2,83),(3,83),(4,83)):
        script = forward_sieve(n, stop, masks)
        print(f"N{n}_STOP{stop}: source constraints "
              f"{sum(m.bit_count() for m,v in masks[8:stop+1])}, "
              f"SMTLIB2 bytes={len(script)}, SHA256={hashlib.sha256(script.encode()).hexdigest()}")
    print("No source-fitted seed or K04 accepted component claimed.")
