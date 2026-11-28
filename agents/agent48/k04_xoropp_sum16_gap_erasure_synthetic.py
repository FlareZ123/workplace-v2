#!/usr/bin/env python3
"""Synthetic-only exact xoroshiro128++ two-output sum-coordinate inversion.

Converts observed output y0 to a one-word unknown c = a+b (mod 2^64):
    a = y0 - rotl(c,17); b = c - a.
The second generator output is constrained exactly using QF_BV.
Includes no historical input or acceptance data. Requires libz3.so.4.
"""
import ctypes as C
import random
import time

Z = C.CDLL("libz3.so.4")
P = C.c_void_p
U = C.c_uint
V = C.c_uint64
M = (1 << 64) - 1

API = {
    "Z3_mk_config": (P, []), "Z3_del_config": (None, [P]),
    "Z3_mk_context": (P, [P]), "Z3_del_context": (None, [P]),
    "Z3_mk_string_symbol": (P, [P, C.c_char_p]),
    "Z3_mk_solver_for_logic": (P, [P, P]),
    "Z3_mk_bv_sort": (P, [P, U]), "Z3_mk_const": (P, [P, P, P]),
    "Z3_mk_unsigned_int64": (P, [P, V, P]),
    "Z3_mk_bvadd": (P, [P, P, P]), "Z3_mk_bvsub": (P, [P, P, P]),
    "Z3_mk_bvxor": (P, [P, P, P]), "Z3_mk_bvshl": (P, [P, P, P]),
    "Z3_mk_bvlshr": (P, [P, P, P]), "Z3_mk_bvand": (P, [P, P, P]),
    "Z3_mk_rotate_left": (P, [P, U, P]), "Z3_mk_eq": (P, [P, P, P]),
    "Z3_mk_solver": (P, [P]), "Z3_solver_inc_ref": (None, [P, P]),
    "Z3_solver_dec_ref": (None, [P, P]), "Z3_solver_assert": (None, [P, P, P]),
    "Z3_solver_check": (C.c_int, [P, P]),
    "Z3_solver_get_model": (P, [P, P]),
    "Z3_model_inc_ref": (None, [P, P]), "Z3_model_dec_ref": (None, [P, P]),
    "Z3_model_eval": (C.c_bool, [P, P, P, C.c_bool, C.POINTER(P)]),
    "Z3_get_numeral_uint64": (C.c_bool, [P, P, C.POINTER(V)]),
    "Z3_mk_params": (P, [P]), "Z3_params_inc_ref": (None, [P, P]),
    "Z3_params_dec_ref": (None, [P, P]), "Z3_params_set_uint": (None, [P, P, P, U]),
    "Z3_solver_set_params": (None, [P, P, P]),
}
for k, (ret, args) in API.items():
    f = getattr(Z, k)
    f.restype, f.argtypes = ret, args


def rotl(v, n):
    return ((v << n) | (v >> (64 - n))) & M


def step(a, b):
    out = (rotl((a + b) & M, 17) + a) & M
    x = a ^ b
    return out, (rotl(a, 49) ^ x ^ ((x << 21) & M)) & M, rotl(x, 28)


def exact_two_output(y0, y1, *, known_sum_half=None, half="low", timeout_ms=5000):
    """Return status, elapsed seconds, and any exact recovered sum c.

    known_sum_half is a proposed known 32-bit half of c (not of a or b).
    If not provided the full generic 64-bit c is unknown; timeout is normal.
    """
    cfg = Z.Z3_mk_config()
    ctx = Z.Z3_mk_context(cfg)
    Z.Z3_del_config(cfg)
    solver = Z.Z3_mk_solver_for_logic(ctx, Z.Z3_mk_string_symbol(ctx, b"QF_BV"))
    Z.Z3_solver_inc_ref(ctx, solver)
    sort = Z.Z3_mk_bv_sort(ctx, 64)

    def make(name, *args):
        return getattr(Z, "Z3_mk_" + name)(ctx, *args)

    def n(v):
        return make("unsigned_int64", v & M, sort)

    c = make("const", make("string_symbol", b"c"), sort)
    if known_sum_half is not None:
        if half not in ("low", "high"):
            raise ValueError("half must be low or high")
        shifted = make("bvlshr", c, n(32 if half == "high" else 0))
        maskval = make("bvand", shifted, n(0xffffffff))
        Z.Z3_solver_assert(ctx, solver, make("eq", maskval, n(known_sum_half)))

    a = make("bvsub", n(y0), make("rotate_left", 17, c))
    b = make("bvsub", c, a)
    x = make("bvxor", a, b)
    ap = make("bvxor", make("bvxor", make("rotate_left", 49, a), x),
              make("bvshl", x, n(21)))
    bp = make("rotate_left", 28, x)
    nextout = make("bvadd", make("rotate_left", 17, make("bvadd", ap, bp)), ap)
    Z.Z3_solver_assert(ctx, solver, make("eq", nextout, n(y1)))

    params = Z.Z3_mk_params(ctx)
    Z.Z3_params_inc_ref(ctx, params)
    Z.Z3_params_set_uint(ctx, params, make("string_symbol", b"timeout"), timeout_ms)
    Z.Z3_solver_set_params(ctx, solver, params)
    Z.Z3_params_dec_ref(ctx, params)
    started = time.monotonic()
    r = Z.Z3_solver_check(ctx, solver)
    duration = round(time.monotonic() - started, 3)
    ans = None
    if r == 1:
        model = Z.Z3_solver_get_model(ctx, solver)
        Z.Z3_model_inc_ref(ctx, model)
        out = P()
        word = V()
        assert Z.Z3_model_eval(ctx, model, c, True, C.byref(out))
        assert Z.Z3_get_numeral_uint64(ctx, out, C.byref(word))
        ans = word.value
        Z.Z3_model_dec_ref(ctx, model)
        aa = (y0 - rotl(ans, 17)) & M
        bb = (ans - aa) & M
        assert step(aa, bb)[0] == y0
        assert step(*step(aa, bb)[1:])[0] == y1
    result = ("SAT" if r == 1 else "UNSAT" if r == -1 else "UNKNOWN", duration, ans)
    Z.Z3_solver_dec_ref(ctx, solver)
    Z.Z3_del_context(ctx)
    return result


def synthetic_controls(count=16, seed=20261127):
    rng = random.Random(seed)
    positive = wrong_half = 0
    for _ in range(count):
        a, b = rng.getrandbits(64), rng.getrandbits(64)
        y0, aa, bb = step(a, b)
        y1 = step(aa, bb)[0]
        c = (a + b) & M
        pos = exact_two_output(y0, y1, known_sum_half=c & 0xffffffff)
        neg = exact_two_output(y0, y1, known_sum_half=(c ^ 1) & 0xffffffff)
        assert pos[0] == "SAT" and pos[2] == c
        assert neg[0] == "UNSAT"
        positive += 1
        wrong_half += 1
    return {"seed": seed, "positive_sat": positive, "incorrect_anchor_unsat": wrong_half}



def gap16_erasure_inverse(y0, y1, y4, y5, anchor16, *, offset=0, timeout_ms=15000):
    """Reconstruct the missing middle 64-bit outputs y2/y3, if SAT, from a
    *genuine* 16-bit source witness of the initial 64-bit sum state c=a+b.
    The 16-bit witness is assumed, NOT inferred from either output pair.
    This is synthetic-only; real source/coupon linkage is not asserted.
    """
    assert offset in (0, 16, 32, 48)
    cfg = Z.Z3_mk_config()
    ctx = Z.Z3_mk_context(cfg)
    Z.Z3_del_config(cfg)
    solver = Z.Z3_mk_solver_for_logic(ctx, Z.Z3_mk_string_symbol(ctx, b"QF_BV"))
    Z.Z3_solver_inc_ref(ctx, solver)
    sort = Z.Z3_mk_bv_sort(ctx, 64)

    def make(name, *args):
        return getattr(Z, "Z3_mk_" + name)(ctx, *args)

    def n(v):
        return make("unsigned_int64", v & M, sort)

    c = make("const", make("string_symbol", b"gap_c0"), sort)
    mask = 0xffff << offset
    Z.Z3_solver_assert(ctx, solver,
        make("eq", make("bvand", c, n(mask)), n((anchor16 & 0xffff) << offset)))
    a = make("bvsub", n(y0), make("rotate_left", 17, c))
    b = make("bvsub", c, a)
    for index in range(6):
        if index in (1, 4, 5):
            output = make("bvadd", make("rotate_left", 17, make("bvadd", a, b)), a)
            target = {1: y1, 4: y4, 5: y5}[index]
            Z.Z3_solver_assert(ctx, solver, make("eq", output, n(target)))
        t = make("bvxor", a, b)
        a = make("bvxor", make("bvxor", make("rotate_left", 49, a), t),
                 make("bvshl", t, n(21)))
        b = make("rotate_left", 28, t)

    params = Z.Z3_mk_params(ctx)
    Z.Z3_params_inc_ref(ctx, params)
    Z.Z3_params_set_uint(ctx, params, make("string_symbol", b"timeout"), timeout_ms)
    Z.Z3_solver_set_params(ctx, solver, params)
    Z.Z3_params_dec_ref(ctx, params)
    start = time.monotonic()
    decision = Z.Z3_solver_check(ctx, solver)
    elapsed = time.monotonic() - start
    gap = None
    if decision == 1:
        model = Z.Z3_solver_get_model(ctx, solver)
        Z.Z3_model_inc_ref(ctx, model)
        out = P()
        value = V()
        assert Z.Z3_model_eval(ctx, model, c, True, C.byref(out))
        assert Z.Z3_get_numeral_uint64(ctx, out, C.byref(value))
        sum0 = value.value
        a0 = (y0 - rotl(sum0, 17)) & M
        b0 = (sum0 - a0) & M
        outputs = []
        a, b = a0, b0
        for _ in range(6):
            y, a, b = step(a, b)
            outputs.append(y)
        assert [outputs[i] for i in (0, 1, 4, 5)] == [y0, y1, y4, y5]
        gap = outputs[2], outputs[3]
        Z.Z3_model_dec_ref(ctx, model)
    Z.Z3_solver_dec_ref(ctx, solver)
    Z.Z3_del_context(ctx)
    return ("SAT" if decision == 1 else "UNSAT" if decision == -1 else "UNKNOWN",
            elapsed, gap)


def synthetic_erasure_controls():
    """Tests full deleted-output prediction, not merely SAT on visible flanks."""
    positive_low = positive_high = incorrect_anchor_unsat = 0
    low_seeds = (20261127, 20261128, 2627831, 98743, 1234567, 99999999)
    high_seeds = (20261127, 20261128, 2627831)
    wrong_seeds = (20261128, 2627831, 98743)
    for offset, seeds in ((0, low_seeds), (48, high_seeds)):
        for seed in seeds:
            rng = random.Random(seed)
            a, b = rng.getrandbits(64), rng.getrandbits(64)
            c = (a + b) & M
            ys = []
            for _ in range(6):
                y, a, b = step(a, b)
                ys.append(y)
            anchor = (c >> offset) & 0xffff
            state, _, missing = gap16_erasure_inverse(
                ys[0], ys[1], ys[4], ys[5], anchor, offset=offset)
            assert state == "SAT" and missing == (ys[2], ys[3]), (
                "Reconstruction failed", seed, offset, state)
            if offset == 0:
                positive_low += 1
            else:
                positive_high += 1
            if offset == 0 and seed in wrong_seeds:
                state, _, missing = gap16_erasure_inverse(
                    ys[0], ys[1], ys[4], ys[5], anchor ^ 1, offset=offset)
                assert state == "UNSAT" and missing is None, (
                    "Wrong anchor unexpectedly survived", seed, state)
                incorrect_anchor_unsat += 1
    return {
        "exact_middle_two_words_low16": positive_low,
        "exact_middle_two_words_high16": positive_high,
        "incorrect_anchor_unsat": incorrect_anchor_unsat,
        "historical_component_recovered": False,
    }


if __name__ == "__main__":
    print(synthetic_erasure_controls())
