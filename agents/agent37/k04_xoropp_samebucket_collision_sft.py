#!/usr/bin/env python3
"""Synthetic-only same-cube xoroshiro128++ first-packet collision certificate.

Two distinct planted 128-bit states share all 128 bits of the first output pair,
and all 12 initial-a bits used by the zero-witness cube solver. Their erased
middle and withheld later packets differ. Exhaustive *within-cube* model
blocking recovers both SAT states followed by UNSAT. No archive, source, K04
commitment, route mask or PDF is opened. Requires the existing Agent27 circuit
and libz3.so.4. The constants below are synthetic mathematical witnesses.
"""
import ctypes
import re
import time
from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit

M = (1 << 64) - 1
P12 = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)
# Explicit source-independent SAT collision witnesses, not original printer states.
WITNESSES = (
    (0xB02543CFB686BB4A, 0xF9DA21F56A996103),
    (0xCE695E4122B2739A, 0xFF6DF861F134F29D),
)

def rot(x, n):
    return ((x << n) | (x >> (64 - n))) & M

def inverse_rot(x, n):
    return ((x >> n) | (x << (64 - n))) & M

def independent_forward(a, b, n=6):
    out = []
    for _ in range(n):
        out.append((rot((a + b) & M, 17) + a) & M)
        t = a ^ b
        a, b = rot(a, 49) ^ t ^ ((t << 21) & M), rot(t, 28)
    return out

def anchor(a):
    return sum((a >> p & 1) << p for p in P12)

def query_models(first, witness_anchor, timeout_ms=30000):
    """Yield all first-pair states in one P12 cube, blocking each exact a0."""
    lib = ctypes.CDLL('libz3.so.4')
    P = ctypes.c_void_p
    lib.Z3_mk_config.restype = P
    lib.Z3_mk_context.argtypes = [P]
    lib.Z3_mk_context.restype = P
    lib.Z3_del_config.argtypes = [P]
    lib.Z3_del_context.argtypes = [P]
    lib.Z3_eval_smtlib2_string.argtypes = [P, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    cfg = lib.Z3_mk_config()
    ctx = lib.Z3_mk_context(cfg)
    lib.Z3_del_config(cfg)
    def ev(source):
        return (lib.Z3_eval_smtlib2_string(ctx, source.encode()) or b'').decode().strip()
    try:
        start_code = circuit({0: first[0], 1: first[1]},
                             witness_anchor, P12, timeout_ms)
        assert start_code.endswith('(check-sat)\n')
        status = ev(start_code)
        models = []
        while status == 'sat':
            raw = ev('(get-value (' + ' '.join(f'a0_{j}' for j in range(64)) + '))')
            bits = {int(j): int(value == 'true')
                    for j, value in re.findall(r'\\(a0_(\\d+)\\s+(true|false)\\)', raw)}
            assert len(bits) == 64, 'Incomplete SAT model'
            a = sum(bits[j] << j for j in range(64))
            b = (inverse_rot((first[0] - a) & M, 17) - a) & M
            assert independent_forward(a, b, 2) == first
            models.append((a, b))
            if len(models) > 16:
                raise AssertionError('Unexpected >16 models: adjust bound, not exclude')
            # Exact state elimination, NOT a prohibition on other states
            # in the same 12-bit cube. This repairs first-model-only loss.
            change = ' '.join(
                f'(not a0_{j})' if bits[j] else f'a0_{j}'
                for j in range(64))
            ev(f'(assert (or {change}))')
            status = ev('(check-sat)')
        assert status in ('unsat', 'unknown'), status
        return models, status
    finally:
        lib.Z3_del_context(ctx)

def main():
    t0 = time.monotonic()
    a, b = WITNESSES
    xa, xb = independent_forward(*a), independent_forward(*b)
    assert a != b and xa[:2] == xb[:2]
    assert xa[2:4] != xb[2:4] and xa[4:6] != xb[4:6]
    assert anchor(a[0]) == anchor(b[0])
    models, final_status = query_models(xa[:2], anchor(a[0]))
    assert final_status == 'unsat', 'UNKNOWN is not a uniqueness certificate'
    assert len(models) == 2 and set(models) == set(WITNESSES)
    assert sum(independent_forward(*m)[4:6] == xa[4:6] for m in models) == 1
    assert sum(independent_forward(*m)[4:6] == xb[4:6] for m in models) == 1
    print({'synthetic_only': True, 'full_first_packet_collision': True,
           'same_12_bit_bucket': True, 'different_erased_128bit_packet': True,
           'different_independent_later_128bit_packet': True,
           'within_bucket_models': len(models), 'completion': final_status,
           'blocking_models_recovers_both': True,
           'first_model_only_is_incomplete_in_general': True,
           'elapsed_seconds': round(time.monotonic() - t0, 3)})

if __name__ == '__main__':
    main()
