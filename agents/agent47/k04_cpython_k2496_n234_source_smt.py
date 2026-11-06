"""K04 CPython k2496 2..4-word seed source-constraint SMT-LIB generator.

Read-only. Call smt(n) to obtain complete QF_BV source constraints as text.
SAT / UNKNOWN is never a recovered coupon; any solver seed needs all 132
original withheld-selected full printer packets validated before K04 hashing.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent28"))
from k04_cpython_real_output_offset_sft import mt, source_states

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
OFFSET = 2496
U = 0xFFFFFFFF
F1 = 1664525
F2 = 1566083941
PAIRS = {
    7: (0xE403BB7D, 0xFFFFFFFF, 0x1F7B301F),
    8: (0x1F7B301F, 0x09CC1C00, 0x008C1000),
    171: (0x664F8F37, 0x4DEE9E40, 0x0D2A1840),
    606: (0x0D8EFC5D, 0x09CC1C00, 0x01880800),
}


def original_source() -> list[bytes]:
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    packets = [bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    observed = source_states(OFFSET, packets)
    assert sum(m.bit_count() for m, v in observed) == 711
    for i, (previous, mask, value) in PAIRS.items():
        assert observed[i-1] == (U, previous)
        assert observed[i] == (mask, value)
    return packets


def initialized(keys: list[int]) -> list[int]:
    n = len(keys)
    s = [19650218]
    for i in range(1, 624):
        s.append((1812433253 * (s[-1] ^ (s[-1] >> 30)) + i) & U)
    i = 1
    j = 0
    for unused in range(max(624, n)):
        s[i] = ((s[i] ^ (F1 * (s[i-1] ^ (s[i-1] >> 30)))) + keys[j] + j) & U
        i += 1
        j += 1
        if i == 624:
            s[0] = s[623]
            i = 1
        if j == n:
            j = 0
    for unused in range(623):
        s[i] = ((s[i] ^ (F2 * (s[i-1] ^ (s[i-1] >> 30)))) - i) & U
        i += 1
        if i == 624:
            s[0] = s[623]
            i = 1
    s[0] = 0x80000000
    return s


def controls() -> None:
    for n in (1, 2, 3, 4):
        keys = [(0x12345678 + i * 0x30158DA) & U for i in range(n)]
        seed = sum(word << (32*i) for i, word in enumerate(keys))
        actual = initialized(keys)
        assert actual == list(random.Random(seed).getstate()[1][:624]), n
        g = [19650218]
        a = [g[0]]
        for i in range(1, 624):
            g.append((1812433253 * (g[-1] ^ (g[-1] >> 30)) + i) & U)
            j = (i-1) % n
            a.append(((g[i] ^ (F1 * (a[-1] ^ (a[-1] >> 30)))) + keys[j] + j) & U)
        for i in PAIRS:
            s = ((a[i] ^ (F2 * (actual[i-1] ^ (actual[i-1] >> 30)))) - i) & U
            assert s == actual[i], (n, i)
        s1 = ((a[1] ^ (F2 * (a[623] ^ (a[623] >> 30)))) - 1) & U
        assert s1 == actual[1]
    print("GENUINE_CPYTHON_POSITIVE_CONTROLS=4/4")


def bv(value: int) -> str:
    return f"#x{value & U:08X}"


def smt(n: int, include_s6: bool = True) -> str:
    """Necessary actual-original source constraints, selected packet excluded.

    SMT-LIB2 can be given to an external QF_BV solver. A solver seed is only
    hypothetical until verified against every one of the 132 original packets.
    """
    assert n in (2, 3, 4)
    g = [19650218]
    out = ["(set-option :produce-models true)", "(set-logic QF_BV)"]
    out += [f"(declare-const k{i} (_ BitVec 32))" for i in range(n)]
    # Python integer seeds with exactly n 32-bit words have nonzero highest word.
    out.append(f"(assert (not (= k{n-1} {bv(0)})))")
    out.append(f"(define-fun a0 () (_ BitVec 32) {bv(g[0])})")
    for i in range(1, 624):
        g.append((1812433253 * (g[-1] ^ (g[-1] >> 30)) + i) & U)
        j = (i-1) % n
        f1 = f"(bvmul {bv(F1)} (bvxor a{i-1} (bvlshr a{i-1} {bv(30)})))"
        expr = f"(bvadd (bvxor {bv(g[i])} {f1}) k{j})"
        if j:
            expr = f"(bvadd {expr} {bv(j)})"
        out.append(f"(define-fun a{i} () (_ BitVec 32) {expr})")
    for i, (previous, mask, value) in PAIRS.items():
        f2 = (F2 * (previous ^ (previous >> 30))) & U
        real = f"(bvsub (bvxor a{i} {bv(f2)}) {bv(i)})"
        out.append(f"(assert (= (bvand {real} {bv(mask)}) {bv(value)}))")
    if include_s6:
        # The second-pass first step crosses the first-pass wrap at A623.
        f = f"(bvmul {bv(F2)} (bvxor a623 (bvlshr a623 {bv(30)})))"
        out.append(f"(define-fun s1 () (_ BitVec 32) (bvsub (bvxor a1 {f}) {bv(1)}))")
        for i in range(2, 7):
            f = f"(bvmul {bv(F2)} (bvxor s{i-1} (bvlshr s{i-1} {bv(30)})))"
            out.append(f"(define-fun s{i} () (_ BitVec 32) (bvsub (bvxor a{i} {f}) {bv(i)}))")
        out.append(f"(assert (= s6 {bv(0xE403BB7D)}))")
    out += ["(check-sat)", "(get-value (" + " ".join(f"k{i}" for i in range(n)) + "))"]
    return "\n".join(out) + "\n"


def validate_seed(keys: list[int], packets: list[bytes]) -> tuple[int, str]:
    """Require 132 original full-packet matches before any target calculation."""
    seed = sum((word & U) << (32*i) for i, word in enumerate(keys))
    r = random.Random(seed)
    words = [r.getrandbits(32) for unused in range(OFFSET + max(mt.STARTS) + 4)]
    predicted = [
        b"".join(words[OFFSET+s+j].to_bytes(4, "little") for j in range(4))
        for s in mt.STARTS
    ]
    matched = sum(a == b for i, (a, b) in enumerate(zip(predicted, packets)) if i != 129)
    return matched, predicted[129].hex().upper()


if __name__ == "__main__":
    original_source()
    controls()
    for count in (2, 3, 4):
        text = smt(count)
        assert len(text) > 60_000
        print(f"N{count}_SMT_SOURCE_CONSTRAINTS_SHA256={hashlib.sha256(text.encode()).hexdigest()} bytes={len(text)}")
