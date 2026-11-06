"""Source-pinned CPython MT19937 n=1 at true prior-output offset 2496.

Conditional p951 spool chronology; excludes selected job row129 before reduction.
Requires the system libz3.so.4 shared library, not the Python z3 package.
Run: python agents/agent37/k04_cpython_k2496_singleword_sft.py
"""
from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import os
from pathlib import Path
import random
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2] / "resources"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
OFFSET = 2496
U = 0xffffffff


def seeded_initial_state(seed: int) -> tuple[int, ...]:
    return random.Random(seed).getstate()[1][:624]


def initial_genrand() -> list[int]:
    words = [19650218]
    for i in range(1, 624):
        words.append((1812433253 * (words[-1] ^ (words[-1] >> 30)) + i) & U)
    return words


def smt_for_masks(state_masks: list[tuple[int, int]], seed: int | None = None) -> str:
    """Use the exact two-stage CPython init_by_array loop for a one-word seed."""
    h = lambda x: "#x" + format(x & U, "08x")
    lines = [
        "(set-logic QF_BV)",
        "(set-option :produce-models true)",
        "(declare-const k0 (_ BitVec 32))",
    ]
    state = [h(w) for w in initial_genrand()]
    j = 0
    counter = 0
    for _ in range(624):
        x, y = state[j + 1], state[j]
        rhs = (
            f"(bvadd (bvxor {x} (bvmul "
            f"(bvxor {y} (bvlshr {y} #x0000001e)) {h(1664525)})) k0)"
        )
        var = f"x{counter}"
        lines.append(f"(declare-const {var} (_ BitVec 32))")
        lines.append(f"(assert (= {var} {rhs}))")
        state[j + 1] = var
        counter += 1
        j += 1
        if j == 623:
            state[0] = state[623]
            j = 0

    # After the first 624 visits, the next index is 2.
    i = 2
    for _ in range(623):
        x, y = state[i], state[i - 1]
        rhs = (
            f"(bvsub (bvxor {x} (bvmul "
            f"(bvxor {y} (bvlshr {y} #x0000001e)) {h(1566083941)})) {h(i)})"
        )
        var = f"x{counter}"
        lines.append(f"(declare-const {var} (_ BitVec 32))")
        lines.append(f"(assert (= {var} {rhs}))")
        state[i] = var
        counter += 1
        i += 1
        if i == 624:
            state[0] = state[623]
            i = 1
    state[0] = h(0x80000000)
    if seed is not None:
        lines.append(f"(assert (= k0 {h(seed)}))")
        selected = seeded_initial_state(seed)
    else:
        selected = None
    for i, (mask, value) in enumerate(state_masks):
        if mask:
            observed = selected[i] & mask if selected is not None else value
            lines.append(f"(assert (= (bvand {state[i]} {h(mask)}) {h(observed)}))")
    return "\n".join(lines) + "\n"


def check_smt(contents: str) -> int:
    library = ctypes.util.find_library("z3") or "libz3.so.4"
    z3 = ctypes.CDLL(library)
    pointer = ctypes.c_void_p
    def api(name, out, *args):
        func = getattr(z3, name)
        func.restype = out
        func.argtypes = args
        return func
    config = api("Z3_mk_config", pointer)()
    context = api("Z3_mk_context", pointer, pointer)(config)
    api("Z3_del_config", None, pointer)(config)
    solver = api("Z3_mk_solver", pointer, pointer)(context)
    api("Z3_solver_inc_ref", None, pointer, pointer)(context, solver)
    read_smt = api("Z3_solver_from_file", None, pointer, pointer, ctypes.c_char_p)
    check = api("Z3_solver_check", ctypes.c_int, pointer, pointer)
    with tempfile.TemporaryDirectory(prefix="h17_k2496_") as directory:
        path = Path(directory) / "constraints.smt2"
        staged = path.with_suffix(".new")
        staged.write_text(contents, encoding="ascii")
        os.replace(staged, path)
        read_smt(context, solver, os.fsencode(path))
        return check(context, solver)


def main() -> None:
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    packets = [
        bytes.fromhex(value.decode("ascii"))
        for value in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    ]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    masks = source_states(OFFSET, packets)
    assert sum(mask.bit_count() for mask, _ in masks) == 711
    assert sum(mask != 0 for mask, _ in masks) == 88
    assert sum(mask == U for mask, _ in masks) == 4
    print("SOURCE", "offset", OFFSET, "known_bits", 711, "known_words", 88,
          "complete_words", 4, "selected_spool_row", "WITHHELD", flush=True)
    for seed in (0x12345678, 0xa7c913df):
        actual = seeded_initial_state(seed)
        assert check_smt(smt_for_masks(masks, seed)) == 1
        synthetic = random.Random(seed)
        native = [synthetic.getrandbits(32)
                  for _ in range(OFFSET + max(mt.STARTS) + 4)]
        trial = [
            b"".join(native[OFFSET + start + lane].to_bytes(4, "little")
                     for lane in range(4)) for start in mt.STARTS
        ]
        source_mask = source_states(OFFSET, trial)
        assert all(value == (expected & mask)
                   for (mask, value), expected in zip(source_mask, actual))
        print("PLANTED_SEEDED_SOURCE_PASS", hex(seed), flush=True)
    assert check_smt(smt_for_masks(masks)) == -1
    print("ORIGINAL_N1_K2496_UNSAT; original K04 remains unverified", flush=True)


if __name__ == "__main__":
    main()
