"""H-17 K04: unique complete native-MT two-gap donor pair in original spool.

Read-only original-source test. Run from repository root:
    python agents/agent50/k04_printer_gap_pair_unique_sft.py

The selected 18:02 ESC-N ACK2 payload and target K04 hash are excluded.
The MT printer chronology is a conditional model, not authenticated firmware.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
import k04_p951_symbolic_basis as mt

source, symbolic = mt.source(ROOT)
assert source.rank == 15365
assert mt.STARTS[129] == 951
assert len(mt.STARTS) == 133

def reduce_source(value):
    """Canonical source quotient with free (nonpivot) coordinates intact."""
    remainder = 0
    while value:
        high = value.bit_length() - 1
        if high in source.rows:
            value ^= source.rows[high][0]
        else:
            bit = 1 << high
            remainder |= bit
            value ^= bit
    return remainder

target = tuple(
    reduce_source(v)
    for stage in range(951, 955)
    for v in mt.get(symbolic, stage)
)
assert len(target) == 128

def insert(basis, value):
    while value:
        high = value.bit_length() - 1
        if high not in basis:
            basis[high] = value
            return
        value ^= basis[high]

def predicted_quotient(first, second, bank):
    """Remaining independent target bits after both complete donor quartets."""
    rank_basis = {}
    for start in (first, second):
        for vector in bank[start]:
            insert(rank_basis, vector)
    before = len(rank_basis)
    for vector in target:
        insert(rank_basis, vector)
    return len(rank_basis) - before

gaps = []
gap_owner = {}
for row, (start, following) in enumerate(zip(mt.STARTS, mt.STARTS[1:])):
    if row in (128, 129):
        continue
    for word_stage in range(start + 4, following - 3):
        gaps.append(word_stage)
        gap_owner[word_stage] = row
assert len(gaps) == 106 and len(set(gaps)) == 106

bank = {
    start: tuple(
        reduce_source(v)
        for word_stage in range(start, start + 4)
        for v in mt.get(symbolic, word_stage)
    )
    for start in gaps
}
assert all(len(block) == 128 for block in bank.values())

evaluated = 0
complete = []
near32 = []
for i, first in enumerate(gaps):
    for second in gaps[i + 1:]:
        if gap_owner[first] == gap_owner[second]:
            continue
        evaluated += 1
        missing = predicted_quotient(first, second, bank)
        if missing == 0:
            complete.append((first, second))
        elif missing == 32:
            near32.append((first, second))
assert evaluated == 5417
assert complete == [(328, 724)], complete
assert sorted(near32) == [(328, 723), (328, 725), (329, 724)]

# Synthetic real-source-compatible generator state, using only a fixed test
# seed for free variables. Original recorded source values are preserved.
rng = random.Random(0x504951)
state = sum(
    rng.getrandbits(1) << p
    for p in range(19968)
    if p not in source.rows
)
for pivot, (equation, rhs) in sorted(source.rows.items()):
    state |= (rhs ^ ((equation & state).bit_count() & 1)) << pivot
assert all(
    ((equation & state).bit_count() & 1) == rhs
    for equation, rhs in source.rows.values()
)

augmented = mt.Basis()
augmented.rows = dict(source.rows)
augmented.rank = source.rank
for start in (328, 724):
    for word_stage in range(start, start + 4):
        for equation in mt.get(symbolic, word_stage):
            augmented.insert(equation, (equation & state).bit_count() & 1)
assert augmented.rank == source.rank + 256

all_target_bits = [
    augmented.predict(equation)
    for word_stage in range(951, 955)
    for equation in mt.get(symbolic, word_stage)
]
assert all(bit is not None for bit in all_target_bits)
actual_target_bits = [
    (equation & state).bit_count() & 1
    for word_stage in range(951, 955)
    for equation in mt.get(symbolic, word_stage)
]
assert all_target_bits == actual_target_bits

print(json.dumps({
    "original_source_rank": source.rank,
    "source_visible_fourword_gap_starts": len(gaps),
    "distinct_gap_pairs_evaluated": evaluated,
    "complete_target_pair": complete,
    "pairs_leaving_32_target_bits": sorted(near32),
    "synthetic_full_128bit_target_reconstruction": "PASS",
    "original_K04_physical_coupon_recovered": False,
}, sort_keys=True))
