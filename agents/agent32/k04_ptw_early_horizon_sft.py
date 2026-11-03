"""Exact conditional p951 MT source to K04 target observability-horizon SFT.

Reads original printer evidence through Agent49's published source-only builder.
A homogeneous GF(2) calculation tests whether any unknown native output values in
a counterfactual early prefix could eliminate selected K04 target uncertainty.
No acceptance digest, actual selected payload, or original file is modified.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper

original, symbolic = source(ROOT / "resources")
assert original.rank == 15365
target = [
    vec for stage in range(951, 955)
    for vec in temper(get(symbolic, stage))
]
assert len(target) == 128

def rank_only_original():
    homogeneous = Basis()
    # Original values have no role in *rank*. Preserve original equation rows.
    homogeneous.rows = {pivot: (vec, 0) for pivot, (vec, _) in original.rows.items()}
    homogeneous.rank = original.rank
    return homogeneous

def target_residual_rank(observed_basis):
    combined = Basis()
    combined.rows = dict(observed_basis.rows)
    combined.rank = observed_basis.rank
    for vec in target:
        combined.insert(vec, 0)
    return combined.rank - observed_basis.rank

state = rank_only_original()
assert target_residual_rank(state) == 128
changes = {}
milestones = {}
prior = 128
for stage in range(-1100, -691):
    for bitvec in temper(get(symbolic, stage)):
        state.insert(bitvec, 0)
    if stage in (-880, -861, -860, -859, -858, -857, -806, -692):
        milestones[stage] = (state.rank, target_residual_rank(state))
    if stage >= -890:
        residual = target_residual_rank(state)
        if residual != prior:
            changes[stage] = residual
            prior = residual

assert milestones == {
    -880: (18912, 128),
    -861: (19138, 125),
    -860: (19170, 94),
    -859: (19202, 62),
    -858: (19234, 30),
    -857: (19262, 2),
    -806: (19519, 1),
    -692: (19968, 0),
}, milestones

assert changes == {
    -861: 125,
    -860: 94,
    -859: 62,
    -858: 30,
    -857: 2,
    -806: 1,
    -692: 0,
}, changes

# Genuine linear positive: the first 624 consecutive full native outputs span
# all 19,968 MT state dimensions, fixing every future output.
full = Basis()
for stage in range(-1100, -476):
    for vec in temper(get(symbolic, stage)):
        full.insert(vec, 0)
assert full.rank == 624 * 32
assert target_residual_rank(full) == 0

print("Original intact printer source rank:", original.rank)
print("Complete -1100..-880 early oracle rank:", milestones[-880][0])
print("Early oracle K04 target remaining bits:", milestones[-880][1])
print("First rank loss and later milestones:", changes)
print("Complete original + oracle source rank:", milestones[-692][0])
print("624 full-output positive control: PASS")
print("Original K04/K08 still MISSING")
