"""Source-derived p951 late-copy stage to complete K04 affine candidate spaces.

Hypothesis only: preserved ACK2 copy arose at native MT stage 1178 or 1405.
The selected source row129 is omitted before fitting 132 intact packets.
The original route mask is used for final component XOR; the original K04
commitment is never used for source fitting or affine basis construction.

Uses existing agent49/k04_p951_symbolic_basis.py. Run with resources path and
optional destination directory. Source evidence and original verifier read-only.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
DEST = Path(sys.argv[2]) if len(sys.argv) > 2 else None
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 1500
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def scalar_temper(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF

def packet(native_bits):
    return b"".join(scalar_temper(sum(native_bits[32*k+j] << j for j in range(32))).to_bytes(4, "little") for k in range(4))

def residual_expr(b, v):
    r, c = 0, 0
    while v:
        p = v.bit_length()-1
        if p in b.rows:
            q, e = b.rows[p]
            v ^= q
            c ^= e
        else:
            r ^= 1 << p
            v ^= 1 << p
    return r, c

def state(b, free=0):
    x = free
    for p in sorted(b.rows):
        row, value = b.rows[p]
        assert row.bit_length() == p+1
        if (value ^ ((row & x).bit_count() & 1)) & 1:
            x |= 1 << p
    return x

def output(rules, copy, stage, s, selected, known_original):
    b = mt.Basis()
    b.rows = rules.rows.copy()
    b.rank = rules.rank
    for lane in range(4):
        word = mt.untemper(int.from_bytes(copy[4*lane:4*lane+4], "little"))
        for j, v in enumerate(mt.get(s, stage+lane)):
            b.insert(v, (word >> j) & 1)
    assert b.rank == known_original+128, (stage, b.rank)
    reduction = [residual_expr(b, v) for v in selected]
    assert sum(r == 0 for r, c in reduction) == 95
    basis, basis_rows, coeff, constant = {}, [], [], []
    for residual, constant_bit in reduction:
        mask = 0
        while residual:
            p = residual.bit_length()-1
            if p in basis:
                row, tag = basis[p]
                residual ^= row
                mask ^= tag
            else:
                new = 1 << len(basis_rows)
                basis[p] = (residual, new)
                basis_rows.append(residual)
                mask ^= new
                break
        coeff.append(mask)
        constant.append(constant_bit)
    assert len(basis_rows) == 33
    base = bytes(a ^ b for a, b in zip(packet(constant), MASK))
    deltas = [packet([(x >> j) & 1 for x in coeff]) for j in range(33)]
    pivots = {}
    for d in deltas:
        x = int.from_bytes(d, "little")
        while x:
            p = x.bit_length()-1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    assert len(pivots) == 33
    # Original-source aligned full-state controls: 132 genuine intact printer
    # packets plus the imposed late-stage ACK copy, then 11 free-state changes.
    s0 = state(b)
    for row, (payload, pos) in enumerate(zip(ROWS, mt.STARTS)):
        if row == 129:
            continue
        actual = packet([((v & s0).bit_count() & 1) for lane in range(4) for v in mt.get(s, pos+lane)])
        assert actual == payload, ("original_source", row)
    late_copy = packet([((v & s0).bit_count() & 1) for lane in range(4) for v in mt.get(s, stage+lane)])
    assert late_copy == copy, ("late_copy", stage)
    selected_s0 = packet([((v & s0).bit_count() & 1) for v in selected])
    assert bytes(a ^ b for a, b in zip(selected_s0, MASK)) == base
    free_indices = [k for k in range(19968) if k not in b.rows]
    for q in random.Random(stage).sample(free_indices, 11):
        x = state(b, 1 << q)
        actual = packet([((v & x).bit_count() & 1) for v in selected])
        mask = sum(((r & x).bit_count() & 1) << j for j, r in enumerate(basis_rows))
        predict = bytearray(base)
        for j, d in enumerate(deltas):
            if mask >> j & 1:
                predict[:] = bytes(a ^ v for a, v in zip(predict, d))
        assert bytes(a ^ b for a, b in zip(actual, MASK)) == predict, ("free_state", q)
    print("STAGE", stage, "BASE", base.hex().upper(), "source_rank", known_original,
          "new_rank", b.rank, "target_dim", len(pivots), "source_packets", 132,
          "genuine_source_state_controls", 12, flush=True)
    return base, deltas

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
MASK = bytes.fromhex(route["K04"]["masked_component"])
assert MASK.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
ROWS = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(ROWS) == len(mt.STARTS) == 133
b, s = mt.source(ROOT)
assert b.rank == 15365
selected = [v for k in range(4) for v in mt.get(s, 951+k)]
assert sum(b.predict(v) is None for v in selected) == 128
pairs = []
for stage in (1178, 1405):
    base, deltas = output(b, ROWS[129], stage, s, selected, 15365)
    pairs.append((base, deltas))
    if DEST:
        DEST.mkdir(parents=True, exist_ok=True)
        p = DEST / f"k04_stage{stage}_affine.dat"
        p.write_text(base.hex().upper() + "\n" + "\n".join(d.hex().upper() for d in deltas) + "\n")
        print("WRITTEN", p, flush=True)
assert pairs[0][1] == pairs[1][1]
assert pairs[0][0][8:] != pairs[1][0][8:]
print("PASS: Two disjoint source-derived 33-dimensional complete-K04-candidate affine cosets", flush=True)
