"""Synthetic-positive complete K04 coupon from 22 hypothetical early MT donors.

Uses original intact printer source equations and the unchanged K04 route mask.
The donor values are constructed from one genuine source-consistent MT state,
not claimed to be historically observed or the missing printer ACK2 payload.
No original selected coupon, target commitment, or verifier is used.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper

original, symbolic = source(ROOT / "resources")
assert original.rank == 15365
DONORS = (
    -1088, -1087, -1086, -1085, -1084,
    -1033, -1028, -1027, -1026, -975,
    -919, -918, -917, -916, -915,
    -861, -860, -859, -858, -857, -806, -692,
)
TARGET = tuple(range(951, 955))
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")

# Back-substitute a genuine full-state satisfying every original 132-packet
# printer equation, choosing arbitrary nonpivot coordinates zero.
state = 0
for pivot, (vector, bit) in sorted(original.rows.items()):
    existing = (vector & state).bit_count() & 1
    state |= (bit ^ existing) << pivot
assert all(
    (vector & state).bit_count() % 2 == bit
    for vector, bit in original.rows.values()
)

def native_word(stage):
    return sum(
        (((vector & state).bit_count() & 1) << bit)
        for bit, vector in enumerate(temper(get(symbolic, stage)))
    )

def source_basis():
    result = Basis()
    result.rows = dict(original.rows)
    result.rank = original.rank
    return result

def rank_only_basis():
    result = Basis()
    result.rows = {
        pivot: (vec, 0) for pivot, (vec, _) in original.rows.items()
    }
    result.rank = original.rank
    return result

augmented = source_basis()
for stage in DONORS:
    observed = native_word(stage)
    for bit, vector in enumerate(temper(get(symbolic, stage))):
        augmented.insert(vector, (observed >> bit) & 1)
assert augmented.rank == 16004

known_target = bytearray()
for stage in TARGET:
    rebuilt = 0
    for bit, vector in enumerate(temper(get(symbolic, stage))):
        value = augmented.predict(vector)
        assert value is not None
        rebuilt |= value << bit
    known_target.extend(rebuilt.to_bytes(4, "little"))

real_target = b"".join(native_word(t).to_bytes(4, "little") for t in TARGET)
assert bytes(known_target) == real_target
assert real_target.hex().upper() == "054AD23723EAFB47DDF71A422DD941CB"
component = bytes(x ^ y for x, y in zip(real_target, MASK))
assert component.hex().upper() == "801C1AFC42AA5CBE78E520857AC2AFD7"
assert hashlib.sha256(component).hexdigest() == (
    "53d08e162f125c2b07816bcf0c112a035d2a70dfb439b5b1f1e66da69725807e"
)

target_vectors = [
    vec for stage in TARGET for vec in temper(get(symbolic, stage))
]

def residual_rank(stages):
    only_rank = rank_only_basis()
    for stage in stages:
        for vector in temper(get(symbolic, stage)):
            only_rank.insert(vector, 0)
    original_rank = only_rank.rank
    for vector in target_vectors:
        only_rank.insert(vector, 0)
    return only_rank.rank - original_rank

assert residual_rank(DONORS) == 0
for excluded in DONORS:
    remaining = [t for t in DONORS if t != excluded]
    assert residual_rank(remaining) > 0

print("Original basis rank:", original.rank)
print("Rank after 22 donor oracle:", augmented.rank)
print("Genuine heldout selected 16 bytes:", real_target.hex().upper())
print("Reconstructed heldout 16 bytes:", known_target.hex().upper())
print("Synthetic candidate component:", component.hex().upper())
print("All 22 remove-one controls: PASS")
print("Authentic K04 and K08: NOT RECOVERED")
