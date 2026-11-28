#!/usr/bin/env python3
"""Source-free exact P18 refinement of unresolved xoroshiro128++ first-packet cubes.

A P16 cube fixes sixteen scattered a0 bits. Splitting on the two otherwise
unknown bits a0[8], a0[9] partitions it into exactly four P18 child cubes.
No historical witness is presumed. Child UNSAT closes only that generator's
specified first-two-output model; UNKNOWN stays unresolved.
Original H-17 sources, route masks, and target commitments are never read.
"""
import ctypes
import json
import random
import re
import time

from agents.agent27.k04_xoropp_sparse12_gap_synthetic import circuit, stream, ror

P12 = (0, 1, 2, 3, 22, 23, 24, 25, 45, 46, 47, 48)
P16 = P12 + (4, 5, 6, 7)
P18 = P16 + (8, 9)
MASK64 = (1 << 64) - 1


def exact_models(first_pair, p18_cube, timeout_ms=350, max_models=32):
    assert len(first_pair) == 2 and 0 <= p18_cube < (1 << 18)
    anchor = sum(((p18_cube >> j) & 1) << p for j, p in enumerate(P18))
    script = circuit({0: first_pair[0], 1: first_pair[1]},
                     anchor, P18, timeout_ms)
    lib = ctypes.CDLL('libz3.so.4')
    p = ctypes.c_void_p
    lib.Z3_mk_config.restype = p
    lib.Z3_mk_context.argtypes = [p]
    lib.Z3_mk_context.restype = p
    lib.Z3_del_config.argtypes = [p]
    lib.Z3_del_context.argtypes = [p]
    lib.Z3_eval_smtlib2_string.argtypes = [p, ctypes.c_char_p]
    lib.Z3_eval_smtlib2_string.restype = ctypes.c_char_p
    cfg = lib.Z3_mk_config()
    ctx = lib.Z3_mk_context(cfg)
    lib.Z3_del_config(cfg)

    def ask(command):
        return (lib.Z3_eval_smtlib2_string(ctx, command.encode()) or b'').decode().strip()

    try:
        result = ask(script)
        models = []
        while result == 'sat':
            raw = ask('(get-value (' +
                      ' '.join(f'a0_{j}' for j in range(64)) + '))')
            bits = {int(j): int(v == 'true') for j, v in re.findall(
                r'\(a0_(\d+)\s+(true|false)\)', raw)}
            assert len(bits) == 64
            a0 = sum(bits[j] << j for j in range(64))
            b0 = (ror((first_pair[0] - a0) & MASK64, 17) - a0) & MASK64
            assert stream(a0, b0, 2) == list(first_pair)
            assert all(((a0 >> pos) & 1) == ((p18_cube >> j) & 1)
                       for j, pos in enumerate(P18))
            models.append((a0, b0))
            if len(models) >= max_models:
                return models, 'unknown'
            block = ' '.join(f'(not a0_{j})' if bits[j] else f'a0_{j}'
                             for j in range(64))
            ask('(assert (or ' + block + '))')
            result = ask('(check-sat)')
        assert result in ('unsat', 'unknown')
        return models, result
    finally:
        lib.Z3_del_context(ctx)


def refine_parent(first_pair, p16_cube, timeout_ms=350, retry_ms=700):
    assert 0 <= p16_cube < (1 << 16)
    assert 100 <= timeout_ms <= retry_ms <= 30_000
    states = set()
    dispositions = []
    for child in range(4):
        bucket = p16_cube | (child << 16)
        found, status = exact_models(first_pair, bucket, timeout_ms)
        if status == 'unknown' and retry_ms > timeout_ms:
            again, status = exact_models(first_pair, bucket, retry_ms)
            found = list(set(found + again))
        states.update(found)
        dispositions.append(status)
    return states, dispositions


def synthetic_controls():
    started = time.monotonic()
    total_models = 0
    for seed in range(771031, 771039):
        rng = random.Random(seed)
        original = (rng.getrandbits(64), rng.getrandbits(64))
        first = stream(*original, 2)
        bucket = sum(((original[0] >> pos) & 1) << j
                     for j, pos in enumerate(P16))
        models, status = refine_parent(first, bucket, 350, 1500)
        assert original in models, (seed, 'planted state absent')
        assert status == ['unsat'] * 4, (seed, status)
        total_models += len(models)
    print(json.dumps({
        'source_free': True, 'fixtures': 8, 'P18_children': 32,
        'terminal_UNSAT_children': 32,
        'planted_original_states_recovered': 8,
        'enumerated_models': total_models,
        'elapsed_seconds': round(time.monotonic() - started, 2),
    }, sort_keys=True))


if __name__ == '__main__':
    synthetic_controls()
