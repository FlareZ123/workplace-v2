"""K04 CPython long-startup source-only n2..4 bidirectional register SFT.

Selected printer row129 is excluded from source equations. Python integer
seed states and a genuine planted source provide positive controls.
Bitwuzla is an optional solver for the original necessary conditions.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
import time
from pathlib import Path

MASK = 0xFFFFFFFF
F1, F2 = 1664525, 1566083941
INV_F2 = pow(F2, -1, 1 << 32)
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
# Agent28's 132-intact-packet source-only initialized-register projection
# at real origin 2496, conditional on the p951 printer chronology.
PROJECTION = {
    2: (0x09CC1C00, 0x00C40000),
    5: (0x8000001F, 0x00000011),
    6: (0xFFFFFFFF, 0xE403BB7D),
    7: (0xFFFFFFFF, 0x1F7B301F),
    8: (0x09CC1C00, 0x008C1000),
    15: (0x000000FF, 0x000000B6),
    16: (0x5398BA7D, 0x4010A820),
    17: (0x01800800, 0x00000800),
}


def mix(x: int) -> int:
    return x ^ (x >> 30)


def first_pass(keys: list[int], stop: int = 17) -> list[int]:
    g = [19650218]
    a = [19650218]
    n = len(keys)
    for i in range(1, stop + 1):
        g.append((1812433253 * mix(g[-1]) + i) & MASK)
        j = (i - 1) % n
        a.append(((g[i] ^ (F1 * mix(a[-1]))) + keys[j] + j) & MASK)
    return a


def projection_check(keys: list[int], projection: dict[int, tuple[int, int]]) -> bool:
    a = first_pass(keys)
    s: dict[int, int] = {6: projection[6][1]}
    # Invert the true second-pass state transition from fixed S6 backward.
    # Final S1 is not the actual predecessor of S2 in CPython.
    for i in range(6, 2, -1):
        s[i - 1] = mix(((a[i] ^ ((s[i] + i) & MASK)) * INV_F2) & MASK)
    for i in range(7, 18):
        s[i] = ((a[i] ^ (F2 * mix(s[i - 1]))) - i) & MASK
    return all((s[i] & mask) == value for i, (mask, value) in projection.items())


def initialized(keys: list[int]) -> list[int]:
    s = [19650218]
    for i in range(1, 624):
        s.append((1812433253 * mix(s[-1]) + i) & MASK)
    i, j = 1, 0
    for _ in range(624):
        s[i] = ((s[i] ^ (F1 * mix(s[i - 1]))) + keys[j] + j) & MASK
        i += 1
        j += 1
        if i == 624:
            s[0] = s[623]
            i = 1
        if j == len(keys):
            j = 0
    for _ in range(623):
        s[i] = ((s[i] ^ (F2 * mix(s[i - 1]))) - i) & MASK
        i += 1
        if i == 624:
            s[0] = s[623]
            i = 1
    s[0] = 0x80000000
    return s


def controls() -> None:
    for n in (2, 3, 4):
        keys = [(0x12345678 + i * 0x30158DA) & MASK for i in range(n)]
        seed = sum(word << (32 * i) for i, word in enumerate(keys))
        authentic = list(random.Random(seed).getstate()[1][:624])
        assert initialized(keys) == authentic
        planted = {i: (mask, authentic[i] & mask)
                   for i, (mask, _) in PROJECTION.items()}
        assert projection_check(keys, planted), n
        changed = dict(planted)
        changed[7] = (MASK, authentic[7] ^ 1)
        assert not projection_check(keys, changed), n
        print(f"GENUINE_PYTHON_N{n}_POSITIVE=PASS NEGATIVE=PASS", flush=True)


def bv(x: int) -> str:
    return f"#x{x & MASK:08X}"


def smt(n: int, projection: dict[int, tuple[int, int]] = PROJECTION) -> str:
    assert n in (2, 3, 4)
    f1 = lambda x: f"(bvmul {bv(F1)} (bvxor {x} (bvlshr {x} {bv(30)})))"
    f2 = lambda x: f"(bvmul {bv(F2)} (bvxor {x} (bvlshr {x} {bv(30)})))"
    unmix = lambda x: f"(bvxor {x} (bvlshr {x} {bv(30)}))"
    g = 19650218
    lines = ["(set-logic QF_BV)"]
    lines.extend(f"(declare-const k{i} (_ BitVec 32))" for i in range(n))
    lines.append(f"(assert (not (= k{n - 1} {bv(0)})))")
    lines.append(f"(define-fun a0 () (_ BitVec 32) {bv(g)})")
    for i in range(1, 18):
        g = (1812433253 * mix(g) + i) & MASK
        j = (i - 1) % n
        expr = f"(bvadd (bvxor {bv(g)} {f1('a' + str(i - 1))}) k{j})"
        if j:
            expr = f"(bvadd {expr} {bv(j)})"
        lines.append(f"(define-fun a{i} () (_ BitVec 32) {expr})")
    lines.append(f"(define-fun s6 () (_ BitVec 32) {bv(projection[6][1])})")
    for i in range(6, 2, -1):
        diff = f"(bvxor a{i} (bvadd s{i} {bv(i)}))"
        expr = unmix(f"(bvmul {bv(INV_F2)} {diff})")
        lines.append(f"(define-fun s{i - 1} () (_ BitVec 32) {expr})")
    for i in range(7, 18):
        expr = f"(bvsub (bvxor a{i} {f2('s' + str(i - 1))}) {bv(i)})"
        lines.append(f"(define-fun s{i} () (_ BitVec 32) {expr})")
    for i, (mask, value) in sorted(projection.items()):
        if i != 6:
            lines.append(f"(assert (= (bvand s{i} {bv(mask)}) {bv(value)}))")
    return "\n".join(lines) + "\n"


def check_original_spool(root: Path) -> None:
    spool = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    packets = re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
    assert len(packets) == 133


def bitwuzla_solve(n: int, seconds: int) -> None:
    import bitwuzla

    tm = bitwuzla.TermManager()
    options = bitwuzla.Options()
    options.set(bitwuzla.Option.PRODUCE_MODELS, True)
    parser = bitwuzla.Parser(tm, options)
    parser.parse(smt(n), True, False)
    solver = parser.bitwuzla()
    start = time.monotonic()
    solver.configure_terminator(lambda: time.monotonic() - start >= seconds)
    outcome = solver.check_sat()
    print(f"BITWUZLA_N{n}_RESULT={outcome} SECONDS={time.monotonic() - start:.2f}", flush=True)
    if outcome == bitwuzla.Result.SAT:
        keys = [int(solver.get_value(parser.parse_term(f"k{i}")).value(16), 16)
                for i in range(n)]
        assert projection_check(keys, PROJECTION)
        print("SEED_KEY_WORDS=" + ",".join(f"{x:08X}" for x in keys), flush=True)
        actual = initialized(keys)
        mismatches = [(i, ((actual[i] ^ value) & mask))
                      for i, (mask, value) in PROJECTION.items()
                      if ((actual[i] ^ value) & mask)]
        print(f"FULL_INITIALIZED_SOURCE_MISMATCHES={mismatches}", flush=True)
        if not mismatches:
            print("FULL_INITIALIZED_REGISTER_SOURCE_PASSES_ALL_8_PROJECTIONS", flush=True)
    elif outcome == bitwuzla.Result.UNSAT:
        print("NO_N_WORD_SEED_SATISFIES_7_EARLY_INITIALIZED_SOURCE_MASKS", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--key-words", type=int, choices=(2, 3, 4), default=2)
    ap.add_argument("--seconds", type=int, default=1200)
    ap.add_argument("--solve", action="store_true")
    args = ap.parse_args()
    controls()
    root = Path(__file__).resolve().parents[2]
    check_original_spool(root)
    formula = smt(args.key_words)
    print(f"SOURCE_PIN={SOURCE_SHA} SMT_SHA256={hashlib.sha256(formula.encode()).hexdigest()} SMT_BYTES={len(formula)}", flush=True)
    if args.solve:
        bitwuzla_solve(args.key_words, args.seconds)
