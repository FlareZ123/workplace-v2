"""Source-derived p951 late-copy stage to complete K04 affine candidate spaces.

Hypothesis only: original K02 signed telemetry halfwords concatenate into an MT donor at native stage 1178.
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
source_hex = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
assert len(source_hex) == len(mt.STARTS) == 133
ROWS = [bytes.fromhex(v.decode()) if i != 129 else None for i, v in enumerate(source_hex)]
assert ROWS[129] is None
# Independently validate the original K02 exact eight accepted GOOD/HOLD readings.
from datetime import datetime
freeze = [json.loads(x) for x in (ROOT / "evidence/telemetry/freeze-export.jsonl").read_text().splitlines()]
assert hashlib.sha256((ROOT / "evidence/telemetry/freeze-export.jsonl").read_bytes()).hexdigest() == "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
lo = datetime.fromisoformat("2026-10-03T21:13:40+00:00")
hi = datetime.fromisoformat("2026-10-03T21:13:48+00:00")
chosen = {}
for item in freeze:
    if (item.get("tag") == "LT-204" and item.get("field") == "DIAG_WORD"
            and item.get("quality") == "GOOD" and item.get("state") == "HOLD"
            and item.get("seq") in range(8) and lo <= datetime.fromisoformat(item["ts"]) < hi):
        n = item["seq"]
        if n not in chosen or item["revision"] > chosen[n]["revision"]:
            chosen[n] = item
assert sorted(chosen) == list(range(8))
halfwords = b"".join(int(chosen[i]["value"]).to_bytes(2, "big") for i in range(8))
assert halfwords.hex().upper() == "E1A5E474BAD7E853A2E8C71D3317D507"
accepted_k02 = hashlib.sha256(halfwords).digest()[:16]
targets = json.loads((ROOT / "acceptance.json").read_text())
assert hashlib.sha256(accepted_k02).hexdigest() == targets["slot_sha256"]["K02"]
b, s = mt.source(ROOT)
assert b.rank == 15365
selected = [v for k in range(4) for v in mt.get(s, 951+k)]
assert sum(b.predict(v) is None for v in selected) == 128
pairs, modes = [], []
for endian in ("big", "little"):
    for reverse_words in (False, True):
        for reverse_halves in (False, True):
            chunks = [halfwords[k:k+4] for k in (0, 4, 8, 12)]
            if reverse_halves:
                chunks = [part[2:4]+part[0:2] for part in chunks]
            if reverse_words:
                chunks.reverse()
            words = [int.from_bytes(part, endian) for part in chunks]
            for native_input in (False, True):
                # Agent38's established output() expects *tempered* printer-word
                # bytes, so temper again if the telemetry has native MT bits.
                donor = b"".join(
                    (scalar_temper(x) if native_input else x).to_bytes(4, "little")
                    for x in words
                )
                mode = (endian, reverse_words, reverse_halves,
                        "native" if native_input else "tempered")
                base, deltas = output(b, donor, 1178, s, selected, 15365)
                modes.append(mode)
                pairs.append((base, deltas))
assert len(pairs) == 16
assert len({base[8:] for base, _ in pairs}) == 16
assert all(ds == pairs[0][1] for _, ds in pairs)
assert pairs[0][0].hex().upper() == "34489314F66E4A22D32AEA1E52228B9D"
if DEST:
    DEST.mkdir(parents=True, exist_ok=True)
    out = DEST / "k02_donor_affine.dat"
    out.write_text("".join(base.hex().upper()+"\n" for base, _ in pairs)
                   + "".join(d.hex().upper()+"\n" for d in pairs[0][1]))
    print("WRITTEN", out, "SHA256", hashlib.sha256(out.read_bytes()).hexdigest(), flush=True)
    assert hashlib.sha256(out.read_bytes()).hexdigest() == "3bcf827847aa2905d4efa4747d2048d3a542a0edcf3cab3b49478388aa26f61d"
    (DEST / "k02_donor_modes.json").write_text(json.dumps(modes, indent=2)+"\n")
print("SOURCE-POSITIVE 132 printer packets, 16 K02 source-donor modes, disjoint 33-bit coupon cosets", flush=True)
