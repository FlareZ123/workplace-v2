"""Original K04 CPython k2496 n2..4 *short-forward* exact QF_BV model.

No selected ACK2 is used. The generator produces source-only necessary
conditions; SAT is a possible seed, UNKNOWN is never an exclusion, and UNSAT
would exclude only the specified conditional CPython source layout.

Use from a complete workplace-v2 checkout. Python standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized, U, F1, F2, t
from k04_cpython_k2496_shortforward_source_sft import original_source

PRESETS = {2: 17, 3: 41, 4: 83}
G = [19650218]
for i in range(1, 624):
    G.append((1812433253 * t(G[-1]) + i) & U)


def bv(value: int) -> str:
    return f"#x{value & U:08X}"


def model_source(n: int, stop: int, masks: list[tuple[int, int]],
                 source_s6: int, source_s7: int,
                 frozen_keys: list[int] | None = None,
                 timeout_ms: int = 60000) -> str:
    assert n in PRESETS
    assert 8 <= stop <= 623
    assert len(masks) == 624
    assert frozen_keys is None or len(frozen_keys) == n
    a7 = (((source_s7 + 7) & U) ^ (F2 * t(source_s6) & U))
    lines = [
        "(set-option :produce-models true)",
        f"(set-option :timeout {timeout_ms})",
        "(set-logic QF_BV)",
    ]
    for j in range(n):
        lines.append(f"(declare-const k{j} (_ BitVec 32))")
    lines.append(f"(assert (not (= k{n-1} {bv(0)})))")
    lines.append(f"(define-fun a0 () (_ BitVec 32) {bv(G[0])})")
    for i in range(1, stop + 1):
        j = (i - 1) % n
        mix = f"(bvmul {bv(F1)} (bvxor a{i-1} (bvlshr a{i-1} {bv(30)})))"
        expr = f"(bvadd (bvxor {bv(G[i])} {mix}) k{j})"
        if j:
            expr = f"(bvadd {expr} {bv(j)})"
        if i == 7:
            lines.append(f"(define-fun a7 () (_ BitVec 32) {bv(a7)})")
            lines.append(f"(assert (= {expr} a7))")
        else:
            lines.append(f"(define-fun a{i} () (_ BitVec 32) {expr})")
    lines.append(f"(define-fun s7 () (_ BitVec 32) {bv(source_s7)})")
    for i in range(8, stop + 1):
        mix = f"(bvmul {bv(F2)} (bvxor s{i-1} (bvlshr s{i-1} {bv(30)})))"
        lines.append(f"(define-fun s{i} () (_ BitVec 32) (bvsub (bvxor a{i} {mix}) {bv(i)}))")
        mask, value = masks[i]
        if mask:
            lines.append(f"(assert (= (bvand s{i} {bv(mask)}) {bv(value)}))")
    if frozen_keys is not None:
        for j, value in enumerate(frozen_keys):
            lines.append(f"(assert (= k{j} {bv(value)}))")
    lines.append("(check-sat)")
    lines.append("(get-value (" + " ".join(f"k{j}" for j in range(n)) + "))")
    return "\n".join(lines) + "\n"


def seeded_controls(source_masks: list[tuple[int, int]]) -> None:
    """Assert original-index recurrence against actual complete CPython states."""
    complete = 0
    for n, stop in PRESETS.items():
        for trial in range(12):
            keys = [((0x12345678 + j * 0x30158DA + trial * 0x4F89D7) & U)
                    for j in range(n)]
            a, b1, state = direct_initialized(keys)
            a7 = (((state[7] + 7) & U) ^ (F2 * t(state[6]) & U))
            assert a[7] == a7
            previous = state[7]
            for i in range(8, stop + 1):
                previous = ((a[i] ^ (F2 * t(previous))) - i) & U
                mask, _ = source_masks[i]
                assert (previous & mask) == (state[i] & mask)
                assert previous == state[i]
            synthetic_masks = [(m, state[i] & m)
                               for i, (m, _) in enumerate(source_masks)]
            script = model_source(n, stop, synthetic_masks,
                                  state[6], state[7], frozen_keys=keys)
            assert "(check-sat)" in script
            assert len(script) > 1000
            complete += 1
    assert complete == 36
    print("GENUINE_CPYTHON_SOURCE_FORWARD_SEEDED_CONTROLS=36/36 PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, choices=(2, 3, 4))
    parser.add_argument("--print-smt", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=60000)
    args = parser.parse_args()
    masks = original_source()
    seeded_controls(masks)
    for n, stop in PRESETS.items():
        if args.n is not None and n != args.n:
            continue
        model = model_source(n, stop, masks, masks[6][1], masks[7][1],
                             timeout_ms=args.timeout_ms)
        digest = hashlib.sha256(model.encode()).hexdigest()
        observed = 32 + sum(mask.bit_count() for mask, value in masks[8:stop + 1])
        print(f"ORIGINAL_N{n}_STOP={stop}_CONSTRAINED_BITS={observed}_KEY_BITS={n*32}"
              f"_SMT_SHA256={digest}_BYTES={len(model)}")
        if args.print_smt:
            print(model)


if __name__ == "__main__":
    main()
