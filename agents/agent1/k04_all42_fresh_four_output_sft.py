"""H17 all42 42-witness stage MILP with every physical payload consuming >=4 words.

Run: python agents/agent1/k04_all42_fresh_four_output_sft.py
Requires scipy/numpy; sibling all42 source projector. Selected ACK2 payload withheld.
"""
from __future__ import annotations
import hashlib
import random
import re
import numpy as np
from pathlib import Path
from scipy.optimize import milp, Bounds, LinearConstraint
from k04_all42_cpython_n98_extended_sft import S as STAGES, untemper, MAG, U

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'

def twist(a, b):
    pair = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return ((pair >> 1) ^ (MAG if pair & 1 else 0)) & U

def symbolic_words(length):
    words = [[1 << (32*i+j) for j in range(32)] for i in range(624)]
    for k in range(624, length):
        a, b, c = words[k-624], words[k-623], words[k-227]
        words.append([c[j] ^ (a[31] if j == 30 else b[j+1] if j < 30 else 0)
                      ^ (b[0] if MAG & (1 << j) else 0) for j in range(32)])
    return words

def retained_native_words():
    raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(rb'^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$', raw, re.M)
    assert len(rows) == 133
    assert rows[129][:5] == (b'2026-10-03T18:02:00Z', b'PS-261003-0417', b'2', b'ACK', b'RECOVER')
    return [None if r == 129 else tuple(
        untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*q:4*q+4], 'little'))
        for q in range(4)) for r, row in enumerate(rows)]

def find_all42(native):
    inverse = {}
    for row, packet in enumerate(native):
        if packet is None:
            continue
        for lane, value in enumerate(packet):
            inverse.setdefault(value, []).append((row, lane))
    full, partial = [], []
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for k in range(r+1, len(native)):
            other = native[k]
            if other is None:
                continue
            for i, value in enumerate(other):
                for p in range(1, 4):
                    for l, q in inverse.get(value ^ twist(packet[p-1], packet[p]), ()):
                        if l > k:
                            full.append((r, k, l, p, i, q))
                for high in (0, 0x80000000):
                    for l, q in inverse.get(value ^ twist(high, packet[0]), ()):
                        if l > k:
                            partial.append((r, k, l, 0, i, q))
    assert (len(full), len(partial)) == (25, 17)
    return full + partial

def stage_equations(witnesses):
    matrix, right = [], []
    for r, k, l, p, i, q in witnesses:
        for end, amount in ((k, 396+p-i), (l, 623+p-q)):
            row = np.zeros(132)
            row[r:end] = 1
            matrix.append(row)
            right.append(amount)
    mat, rhs = np.array(matrix), np.array(right)
    assert mat.shape == (84, 132)
    assert np.array_equal(mat @ np.diff(STAGES), rhs)
    return mat, rhs

def full_source_fit(stages, native):
    symbols = symbolic_words(int(stages[-1]) + 4)
    basis = {}
    for r, packet in enumerate(native):
        if packet is None:
            continue
        for lane, value in enumerate(packet):
            for bit, term in enumerate(symbols[int(stages[r]) + lane]):
                rhs = (value >> bit) & 1
                while term:
                    pivot = term.bit_length() - 1
                    if pivot not in basis:
                        basis[pivot] = term, rhs
                        break
                    old, old_rhs = basis[pivot]
                    term ^= old
                    rhs ^= old_rhs
                else:
                    if rhs:
                        return False, r, lane, bit, len(basis)
    return True, -1, -1, -1, len(basis)

def genuine_seeded_control():
    rng = random.Random(0x17A11CE)
    stream = [untemper(rng.getrandbits(32)) for _ in range(STAGES[-1] + 4)]
    planted = [None if r == 129 else tuple(stream[stage:stage+4])
               for r, stage in enumerate(STAGES)]
    ok, row, lane, bit, rank = full_source_fit(STAGES, planted)
    assert ok and rank == 15434, (ok, row, lane, bit, rank)
    print('GENUINE_SEEDED_ALL42_SOURCE PASS', rank)

def main():
    genuine_seeded_control()
    native = retained_native_words()
    witnesses = find_all42(native)
    mat, rhs = stage_equations(witnesses)
    assert full_source_fit(STAGES, native) == (True, -1, -1, -1, 15434)
    rng = np.random.default_rng(12345)
    selections = []
    for trial in range(3):
        model = milp(rng.normal(size=132), integrality=np.ones(132),
                     bounds=Bounds(np.full(132, 4.0), np.full(132, 16.0)),
                     constraints=LinearConstraint(mat, rhs, rhs),
                     options={'time_limit': 10.0})
        assert model.success, model.message
        gaps = np.rint(model.x).astype(int)
        assert np.array_equal(mat @ gaps, rhs)
        stage = np.r_[0, np.cumsum(gaps)]
        assert (np.diff(stage) >= 4).all() and (np.diff(stage) <= 16).all()
        fit = full_source_fit(stage, native)
        assert not fit[0], (trial, fit)
        selections.append({'trial': trial,
                           'selected_neighbor_stages': stage[128:131].tolist(),
                           'source_contradiction_row': fit[1],
                           'source_contradiction_lane': fit[2],
                           'source_contradiction_bit': fit[3]})
        print('HISTORICAL_FOUR_FRESH_MILP_REJECTED', selections[-1], flush=True)
    assert [s['selected_neighbor_stages'] for s in selections] == [
        [952, 956, 963], [943, 947, 954], [949, 953, 957]
    ]
    print('RESULT original_all42_source_positive=True historical_4_fresh_MILP_models=3 full_source_models=0 target_coupon_recovered=False')

if __name__ == '__main__':
    main()
