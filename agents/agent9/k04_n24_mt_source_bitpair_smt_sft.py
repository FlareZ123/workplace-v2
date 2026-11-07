"""Original H17 printer source-only n=24 CPython seed SAT frontier.

Reconstructs 1,782 exact single-bit and pair-parity necessary equations from
132 preserved complete printer ACK packets, withholding row129. Tests a
*speculative* 24-word CPython native initializer via actual libz3 C API.
The full original result may be UNKNOWN: a timeout is never UNSAT.

Use Python 3 with the existing system libz3.so.4. No source or checker writes.
Original printer stage p951, true prior native output offset2496 is conditional.
"""
from __future__ import annotations

from collections import defaultdict
import ctypes
import hashlib
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent23"))
from k04_cpython_k2496_n1to6_joint_affine_sft import (
    OFFSET, U, mt, original_packets, source_rows, words,
)

MASK = 0xFFFFFFFF
COUNT = 624
KEY_WORDS = 24
SOURCE_RANK = 15365
SOURCE_BITPAIR_CHECKS = 1782


def native_initialized(seed_words: list[int]) -> tuple[int, ...]:
    """Exact CPython MT19937 init_by_array, including both i=1 wrap visits."""
    state = [19650218]
    for index in range(1, COUNT):
        previous = state[-1]
        state.append((1812433253 * (previous ^ (previous >> 30)) + index) & MASK)

    def f(value: int, multiplier: int) -> int:
        return multiplier * (value ^ (value >> 30)) & MASK

    i, j = 1, 0
    for _ in range(max(COUNT, len(seed_words))):
        state[i] = ((state[i] ^ f(state[i - 1], 1664525))
                    + seed_words[j] + j) & MASK
        i += 1
        j += 1
        if i >= COUNT:
            state[0] = state[-1]
            i = 1
        if j >= len(seed_words):
            j = 0
    for _ in range(COUNT - 1):
        state[i] = ((state[i] ^ f(state[i - 1], 1566083941)) - i) & MASK
        i += 1
        if i >= COUNT:
            state[0] = state[-1]
            i = 1
    state[0] = 0x80000000
    return tuple(state)


def lowweight_equations(rows: list[tuple[int, int]]) -> list[str]:
    """Reduced source affine bit residues: 711 fixed bits, 1071 pair parities."""
    echelon: dict[int, tuple[int, int]] = {}
    for expression, rhs in rows:
        while expression:
            pivot = expression.bit_length() - 1
            previous = echelon.get(pivot)
            if previous is None:
                echelon[pivot] = expression, rhs
                break
            expression ^= previous[0]
            rhs ^= previous[1]
        else:
            assert rhs == 0, "The source is inconsistent at the claimed stage."
    assert len(echelon) == SOURCE_RANK

    groups: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for bit in range(COUNT * 32):
        expression, rhs = 1 << bit, 0
        while expression:
            previous = echelon.get(expression.bit_length() - 1)
            if previous is None:
                break
            expression ^= previous[0]
            rhs ^= previous[1]
        groups[expression].append((bit, rhs))

    constraints: list[str] = []
    n_single = n_pair = 0
    for residual, group in groups.items():
        if residual == 0:
            for bit, rhs in group:
                i, j = divmod(bit, 32)
                constraints.append(
                    f"(assert (= ((_ extract {j} {j}) s{i}) #b{rhs}))"
                )
                n_single += 1
        elif len(group) > 1:
            bit0, rhs0 = group[0]
            i0, j0 = divmod(bit0, 32)
            for bit, rhs in group[1:]:
                i, j = divmod(bit, 32)
                constraints.append(
                    f"(assert (= (bvxor ((_ extract {j0} {j0}) s{i0}) "
                    f"((_ extract {j} {j}) s{i})) #b{rhs0 ^ rhs}))"
                )
                n_pair += 1
    assert (n_single, n_pair) == (711, 1071), (n_single, n_pair)
    assert len(constraints) == SOURCE_BITPAIR_CHECKS
    print("SOURCE_LOWWEIGHT_AFFINE_PIN_PASS rank=15365 fixed=711 pair=1071 "
          "total=1782 row129_withheld=1", flush=True)
    return constraints


def smt_firstpass_secondpass(timeout_ms: int) -> list[str]:
    """The genuine 24-word CPython initializer as named 32-bit SMT functions."""
    initial = [19650218]
    for i in range(1, COUNT):
        x = initial[-1]
        initial.append((1812433253 * (x ^ (x >> 30)) + i) & MASK)

    def f(expr: str, multiplier: int) -> str:
        return (f"(bvmul #x{multiplier:08x} "
                f"(bvxor {expr} (bvlshr {expr} #x0000001e)))")

    lines = ["(set-logic QF_BV)", f"(set-option :timeout {timeout_ms})"]
    for j in range(KEY_WORDS):
        lines.append(f"(declare-fun k{j} () (_ BitVec 32))")
    before = f"(bvxor #x{initial[1]:08x} {f(f'#x{initial[0]:08x}', 1664525)})"
    lines.append(
        f"(define-fun a1first () (_ BitVec 32) (bvadd {before} k0))"
    )
    for i in range(2, COUNT):
        j = (i - 1) % KEY_WORDS
        prior = "a1first" if i == 2 else f"a{i-1}"
        before = f"(bvxor #x{initial[i]:08x} {f(prior, 1664525)})"
        body = f"(bvadd (bvadd {before} k{j}) #x{j:08x})"
        lines.append(f"(define-fun a{i} () (_ BitVec 32) {body})")

    # First-pass iteration624 updates A1 a *second* time and reuses key23.
    before = f"(bvxor a1first {f('a623', 1664525)})"
    lines.append(
        f"(define-fun a1last () (_ BitVec 32) "
        f"(bvadd (bvadd {before} k23) #x00000017))"
    )

    # Second pass updates S2..S623, then S1, then forcibly resets S0.
    for i in range(2, COUNT):
        previous = "a1last" if i == 2 else f"s{i-1}"
        before = f"(bvxor a{i} {f(previous, 1566083941)})"
        body = f"(bvsub {before} #x{i:08x})"
        lines.append(f"(define-fun s{i} () (_ BitVec 32) {body})")
    lines.append(
        f"(define-fun s1 () (_ BitVec 32) "
        f"(bvsub (bvxor a1last {f('s623',1566083941)}) #x00000001))"
    )
    lines.append("(define-fun s0 () (_ BitVec 32) #x80000000)")
    assert len(lines) == 1274
    return lines


def actual_z3_smt(source: str) -> tuple[str, float]:
    """Use published Z3 C API directly, without a nonstandard py package."""
    lib = ctypes.CDLL("libz3.so.4")
    lib.Z3_mk_config.restype = ctypes.c_void_p
    lib.Z3_mk_context.argtypes = [ctypes.c_void_p]
    lib.Z3_mk_context.restype = ctypes.c_void_p
    lib.Z3_eval_smtlib2_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    lib.Z3_del_context.argtypes = [ctypes.c_void_p]
    lib.Z3_del_config.argtypes = [ctypes.c_void_p]

    cfg = lib.Z3_mk_config()
    ctx = lib.Z3_mk_context(cfg)
    started = time.monotonic()
    try:
        raw = lib.Z3_eval_smtlib2_string(ctx, source.encode("ascii"))
        result = raw.decode("ascii").strip()
        if result not in ("sat", "unsat", "unknown"):
            raise RuntimeError(f"Unexpected Z3 result: {result[:500]}")
        return result, round(time.monotonic() - started, 3)
    finally:
        lib.Z3_del_context(ctx)
        lib.Z3_del_config(cfg)


def run(timeout_ms: int) -> None:
    assert 1000 <= timeout_ms <= 300000
    symbols = words(OFFSET)
    original_equations = source_rows(original_packets(), symbols)
    original_constraints = lowweight_equations(original_equations)
    smt = smt_firstpass_secondpass(timeout_ms)
    key = [((i + 3) * 0x13416997) & MASK for i in range(KEY_WORDS)]
    integer = sum(word << (i * 32) for i, word in enumerate(key))
    state = native_initialized(key)
    assert state == random.Random(integer).getstate()[1][:COUNT]
    print("GENUINE_CPYTHON_N24_INITIALIZER_FULL624_STATE_PASS", flush=True)

    generator = random.Random(integer)
    emitted = [generator.getrandbits(32) for _ in range(OFFSET + 974)]
    packets = [
        b"".join(emitted[OFFSET + position + j].to_bytes(4, "little")
                 for j in range(4))
        for position in mt.STARTS
    ]
    assert len(packets) == 133
    synthetic_equations = source_rows(packets, symbols)
    synthetic_constraints = lowweight_equations(synthetic_equations)
    fixed_key = [
        f"(assert (= k{j} #x{value:08x}))"
        for j, value in enumerate(key)
    ]
    planted, duration = actual_z3_smt(
        "\n".join(smt + synthetic_constraints + fixed_key + ["(check-sat)"])
    )
    assert planted == "sat", ("A genuine selected-withheld test must be SAT", planted)
    print(f"SYNTHETIC_N24_FULL133_SELECTED_WITHHELD_SMT_SAT_PASS seconds={duration}",
          flush=True)

    wrong = list(key)
    wrong[0] ^= 1
    wrong_key = [
        f"(assert (= k{j} #x{value:08x}))"
        for j, value in enumerate(wrong)
    ]
    rejected, duration = actual_z3_smt(
        "\n".join(smt + synthetic_constraints + wrong_key + ["(check-sat)"])
    )
    assert rejected == "unsat", ("A modified planted seed must fail", rejected)
    print(f"SYNTHETIC_N24_WRONGSEED_UNSAT_PASS seconds={duration}",
          flush=True)

    original, duration = actual_z3_smt(
        "\n".join(smt + original_constraints + ["(check-sat)"])
    )
    print(f"ORIGINAL_N24_1782_BITPAIR_SOURCE_STATUS={original.upper()} "
          f"timeout_ms={timeout_ms} seconds={duration}", flush=True)
    if original == "sat":
        print("WARNING source-permitted seed exists; no actual seed recovered.")
    elif original == "unsat":
        print("EXACT n24 CPython initial-state source model EXCLUDED "
              "under fixed p951/k2496 chronology.")
    else:
        print("UNKNOWN solver limit; n24 remains OPEN. "
              "No original selected physical bytes may be inferred.")
    print("ORIGINAL_K04_UNRECOVERED ORIGINAL_K08_UNRECOVERED", flush=True)


if __name__ == "__main__":
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    run(ms)
