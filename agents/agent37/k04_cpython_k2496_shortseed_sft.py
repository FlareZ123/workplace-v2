"""Exact CPython short integer-seed k2496 nonlinear model (n2..4).

Run from repository root: python3 agents/agent37/k04_cpython_k2496_shortseed_sft.py 2
Uses system libz3.so.4; the original selected spool ACK row129 is withheld.
A SAT model is a hypothesis only and is independently checked on all intact rows.
"""
from __future__ import annotations

import ctypes as ct
import ctypes.util
import hashlib
import os
from pathlib import Path
import random
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
OFFSET = 2496
U = 0xffffffff


def as_seed(words: list[int]) -> int:
    return sum((word & U) << (32 * j) for j, word in enumerate(words))


def seeded_packets(words: list[int]) -> list[bytes]:
    rng = random.Random(as_seed(words))
    generated = [rng.getrandbits(32)
                 for _ in range(OFFSET + max(mt.STARTS) + 4)]
    return [b"".join(generated[OFFSET + start + lane].to_bytes(4, "little")
                     for lane in range(4)) for start in mt.STARTS]


def smt(masks: list[tuple[int, int]], key_words: int,
        forced: list[int] | None = None, timeout_ms: int = 1800000) -> str:
    assert 1 <= key_words <= 4
    hx = lambda value: "#x" + format(value & U, "08x")
    lines = ["(set-logic QF_BV)", "(set-option :produce-models true)",
             f"(set-option :timeout {timeout_ms})"]
    lines.extend(f"(declare-const k{j} (_ BitVec 32))" for j in range(key_words))
    # CPython init_genrand(19650218), first loop of init_by_array.
    initial = [19650218]
    for i in range(1, 624):
        prior = initial[-1]
        initial.append((1812433253 * (prior ^ (prior >> 30)) + i) & U)
    state = [hx(v) for v in initial]
    i = 1
    key_index = 0
    counter = 0
    for _ in range(624):
        current, prior = state[i], state[i - 1]
        raw = (f"(bvadd (bvxor {current} "
               f"(bvmul (bvxor {prior} (bvlshr {prior} #x0000001e)) "
               f"{hx(1664525)})) (bvadd k{key_index} {hx(key_index)}))")
        variable = f"v{counter}"
        lines.extend((f"(declare-const {variable} (_ BitVec 32))",
                      f"(assert (= {variable} {raw}))"))
        state[i] = variable
        counter += 1
        i += 1
        if i == 624:
            state[0] = state[623]
            i = 1
        key_index = (key_index + 1) % key_words

    i = 2
    for _ in range(623):
        current, prior = state[i], state[i - 1]
        raw = (f"(bvsub (bvxor {current} "
               f"(bvmul (bvxor {prior} (bvlshr {prior} #x0000001e)) "
               f"{hx(1566083941)})) {hx(i)})")
        variable = f"v{counter}"
        lines.extend((f"(declare-const {variable} (_ BitVec 32))",
                      f"(assert (= {variable} {raw}))"))
        state[i] = variable
        counter += 1
        i += 1
        if i == 624:
            state[0] = state[623]
            i = 1
    state[0] = hx(0x80000000)
    for j, (mask, expected) in enumerate(masks):
        if mask:
            if forced is not None:
                expected = random.Random(as_seed(forced)).getstate()[1][j] & mask
            lines.append(f"(assert (= (bvand {state[j]} {hx(mask)}) {hx(expected)}))")
    if forced is not None:
        lines.extend(f"(assert (= k{j} {hx(value)}))"
                     for j, value in enumerate(forced))
    return "\n".join(lines) + "\n"


def invoke(source: str, key_words: int, limit_ms: int) -> tuple[int, list[int] | None, str]:
    z = ct.CDLL(ctypes.util.find_library("z3") or "libz3.so.4")
    P, C, B = ct.c_void_p, ct.c_char_p, ct.c_bool
    def api(name: str, out, *types):
        f = getattr(z, name)
        f.argtypes, f.restype = types, out
        return f
    config = api("Z3_mk_config", P)()
    context = api("Z3_mk_context", P, P)(config)
    api("Z3_del_config", None, P)(config)
    solver = api("Z3_mk_solver", P, P)(context)
    api("Z3_solver_inc_ref", None, P, P)(context, solver)
    parse = api("Z3_solver_from_file", None, P, P, C)
    check = api("Z3_solver_check", ct.c_int, P, P)
    reason = api("Z3_solver_get_reason_unknown", C, P, P)
    with tempfile.TemporaryDirectory(prefix="h17_k2496_") as folder:
        file = Path(folder) / "query.smt2"
        stage = file.with_suffix(".new")
        stage.write_text(source, encoding="ascii")
        os.replace(stage, file)
        parse(context, solver, os.fsencode(file))
        # The SMT-LIB (set-option :timeout ...) from solver_from_file can
        # persist across separate contexts. Set each solver's limit directly.
        params = api("Z3_mk_params", P, P)(context)
        api("Z3_params_inc_ref", None, P, P)(context, params)
        symbol_for_param = api("Z3_mk_string_symbol", P, P, C)
        api("Z3_params_set_uint", None, P, P, P, ct.c_uint)(
            context, params, symbol_for_param(context, b"timeout"), limit_ms)
        api("Z3_solver_set_params", None, P, P, P)(context, solver, params)
        api("Z3_params_dec_ref", None, P, P)(context, params)
        answer = check(context, solver)
        keys = None
        unknown = reason(context, solver).decode() if answer == 0 else ""
        if answer == 1:
            model = api("Z3_solver_get_model", P, P, P)(context, solver)
            symbol = api("Z3_mk_string_symbol", P, P, C)
            bv_sort = api("Z3_mk_bv_sort", P, P, ct.c_uint)
            mk_const = api("Z3_mk_const", P, P, P, P)
            evaluate = api("Z3_model_eval", B, P, P, P, B, ct.POINTER(P))
            numeral = api("Z3_get_numeral_uint", B, P, P, ct.POINTER(ct.c_uint))
            sort = bv_sort(context, 32)
            keys = []
            for j in range(key_words):
                atom = mk_const(context, symbol(context, f"k{j}".encode()), sort)
                result = P()
                assert evaluate(context, model, atom, True, ct.byref(result))
                value = ct.c_uint()
                assert numeral(context, result, ct.byref(value))
                keys.append(int(value.value))
    return answer, keys, unknown


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("2", "3", "4"):
        raise SystemExit("Supply one integer seed word count: 2, 3 or 4")
    n = int(sys.argv[1])
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    packets = [bytes.fromhex(x.decode("ascii")) for x in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    source = source_states(OFFSET, packets)
    assert sum(mask.bit_count() for mask, _ in source) == 711
    print("ORIGINAL_SOURCE", "seed_words", n, "known_init_bits", 711,
          "selected_row", "WITHHELD", flush=True)

    planted = [0x12345678 + j * 0x11111111 & U for j in range(n)]
    constructed = seeded_packets(planted)
    seed_state = random.Random(as_seed(planted)).getstate()[1][:624]
    planted_source = source_states(OFFSET, constructed)
    assert all(v == (seed_state[j] & mask)
               for j, (mask, v) in enumerate(planted_source))
    # Fixed-seed model checks exact nonlinear initialization, separate from
    # the observed real packet source used in the original model.
    positive, keys, _ = invoke(smt(planted_source, n, planted, 60000), n, 60000)
    assert positive == 1 and keys == planted, (positive, keys)
    print("SYNTHETIC_GENUINE_PYTHON_SEED_SOURCE_PASS", n, flush=True)

    answer, keys, why = invoke(smt(source, n), n, 1800000)
    if answer == -1:
        print("ORIGINAL_SOURCE_N", n, "UNSAT", flush=True)
    elif answer == 0:
        print("ORIGINAL_SOURCE_N", n, "UNKNOWN", why, flush=True)
    else:
        assert keys is not None
        generated = seeded_packets(keys)
        correct = sum(a == b for i, (a, b) in enumerate(zip(generated, packets))
                      if i != 129)
        coupon = generated[129]
        component = bytes(x ^ y for x, y in zip(coupon, MASK))
        match = hashlib.sha256(component).hexdigest() == K04_SHA
        print("SOURCE_PROJECTION_SAT", "n", n, "key", [hex(x) for x in keys],
              "intact_packet_matches", f"{correct}/132",
              "K04_SHA_MATCH", match, flush=True)
        if correct == 132 and match:
            print("COMPLETE_K04_CANDIDATE", component.hex().upper(), flush=True)
        elif correct < 132:
            print("NECESSARY_PROJECTION_ONLY; no original-source model", flush=True)


if __name__ == "__main__":
    main()
