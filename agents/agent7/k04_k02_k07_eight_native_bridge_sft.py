"""Source-pinned K02/K07 eight-halfword native MT bridge to complete K04 coupon.

Run from repo root: python agents/agent7/k04_k02_k07_eight_native_bridge_sft.py
No original evidence, verification or candidate files are modified.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

base, symbolic = mt.source(ROOT / "resources")
assert base.rank == 15365
stages = (328, 329, 330, 331, 724, 725, 726, 727)

k02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
k07 = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
assert hashlib.sha256(k02).digest()[:16].hex().upper() == "0D7E3AB56FB75DA3EB0E2E06786D239E"
assert hashlib.sha256(k07).digest()[:16].hex().upper() == "93495F5E425AB8E592123DABAEB68545"
route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "resources/acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])

def with_donors(values):
    basis = mt.Basis()
    basis.rows = base.rows.copy()
    basis.rank = base.rank
    for stage, word in zip(stages, values):
        for bit, expr in enumerate(mt.get(symbolic, stage)):
            basis.insert(expr, (word >> bit) & 1)
    assert basis.rank == 15621
    return basis

def coupon(basis):
    output = bytearray()
    for stage in range(951, 955):
        native = []
        for expr in mt.get(symbolic, stage):
            bit = basis.predict(expr)
            assert bit in (0, 1)
            native.append(bit)
        word = sum(bit << j for j, bit in enumerate(mt.temper(native)))
        output.extend(word.to_bytes(4, "little"))
    return bytes(output)

def digest(c):
    component = bytes(x ^ y for x, y in zip(c, mask))
    return hashlib.sha256(component).digest(), component

def assemble(k2, k7, endian2, endian7, back2, back7, swap, native):
    a = [int.from_bytes(k2[i:i+2], endian2) for i in range(0, 16, 2)]
    b = [int.from_bytes(k7[i:i+2], endian7) for i in range(0, 16, 2)]
    if back2: a.reverse()
    if back7: b.reverse()
    words = [(x << 16 | y) if swap else (y << 16 | x)
             for x, y in zip(a, b)]
    return words if native else [mt.untemper(x) for x in words]

# Independently planted complete original-source-compatible state and donor.
state = 0
for pivot, (expr, rhs) in sorted(base.rows.items()):
    if rhs ^ ((expr & state).bit_count() & 1):
        state |= 1 << pivot
native_words = [sum(((expr & state).bit_count() & 1) << bit
                    for bit, expr in enumerate(mt.get(symbolic, stage)))
                for stage in stages]
planted_k02 = b"".join((x & 65535).to_bytes(2, "big") for x in native_words)
planted_k07 = b"".join((x >> 16).to_bytes(2, "big") for x in native_words)
planted_coupon = coupon(with_donors(native_words))
test_words = assemble(planted_k02, planted_k07, "big", "big",
                      False, False, False, True)
assert coupon(with_donors(test_words)) == planted_coupon
print("Synthetic complete original-source donor control PASS", planted_coupon.hex().upper())

# Authentic K02 and K07 record values, 64 complete layout/view assignments.
matches = []
count = 0
for e2, e7 in itertools.product(("big", "little"), repeat=2):
    for b2, b7, swap, native in itertools.product((False, True), repeat=4):
        values = assemble(k02, k07, e2, e7, b2, b7, swap, native)
        full = coupon(with_donors(values))
        h, component = digest(full)
        count += 1
        if h == target:
            matches.append((e2, e7, b2, b7, swap, native,
                            component.hex().upper()))
assert count == 64
print("Original complete K04 candidates:", count,
      "original commitment matches:", matches)
assert not matches
