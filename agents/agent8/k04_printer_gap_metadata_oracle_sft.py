"""Source-only optimistic metadata-width oracle for selected K04 coupon, p951 model.

Tests how much selected quartet uncertainty would remain if every hidden native
output between the 128 intact routine printer packets leaked its highest b
TEMPERED bits, b=1..32. No metadata writer or bit value is presumed.

Requires Agent49 k04_p951_symbolic_basis.py, original evidence, no writes.
"""
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'resources'
FIXTURE = Path(__file__).resolve().parents[1] / 'agent49' / 'k04_p951_symbolic_basis.py'
spec = importlib.util.spec_from_file_location('oracle_original_p951', FIXTURE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def insert(rows, vector):
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in rows:
            rows[pivot] = vector
            return True
        vector ^= rows[pivot]
    return False


def independent_target_rank(rows, target):
    test = rows.copy()
    return sum(insert(test, vector) for vector in target)


def main():
    source, stream = model.source(ROOT)
    rows = {p: equation[0] for p, equation in source.rows.items()}
    assert len(rows) == 15365
    targets = [bit for i in range(951, 955) for bit in model.get(stream, i)]
    assert len(targets) == 128
    assert independent_target_rank(rows, targets) == 128
    gap_stages = tuple(
        p for i in range(127)
        for p in range(model.STARTS[i]+4, model.STARTS[i+1])
    )
    assert len(gap_stages) == 434, len(gap_stages)
    assert len(set(gap_stages)) == 434
    assert 951 not in gap_stages
    templated = [model.temper(model.get(stream,p)) for p in gap_stages]
    out = []
    baseline = len(rows)
    joined = rows.copy()
    assert sum(insert(joined, vector) for vector in targets) == 128
    contributions = {}
    for bits in range(1, 33):
        new, target_drop, stage_drops = 0, 0, []
        for stage, word in zip(gap_stages, templated):
            vector = word[32-bits]
            rank_gain = int(insert(rows, vector))
            joint_gain = int(insert(joined, vector))
            assert rank_gain >= joint_gain
            new += rank_gain
            target_drop += rank_gain - joint_gain
            if rank_gain > joint_gain:
                stage_drops.append(stage)
                contributions[stage] = contributions.get(stage,0)+1
        remaining = 128 - (len(rows)-baseline) + (len(joined)-baseline-128)
        assert remaining == independent_target_rank(rows, targets)
        out.append((bits, len(rows)-baseline, new, remaining, target_drop))
        if target_drop:
            print('TARGET_REACH_PLANE',bits,'dimension_drop',target_drop,'gap_stages',stage_drops[:18],'full_count',len(stage_drops),flush=True)
        if bits in (1,2,3,4,5,6,8,10,13,16,20,24,28,32):
            print('ORACLE', 'upper_tempered_bits', bits,
                  'oracle_rank_delta', len(rows)-baseline,
                  'new_equations_this_bitplane', new,
                  'selected_native_dimensions_still_free', remaining, flush=True)
    # Real synthetic MT-state positive: retain the *same source observation
    # coefficient rows* but populate every RHS from a fresh independent 624-word
    # genuine initial MT state. Full hypothetical gap observations must recover
    # all 128 selected words exactly, not merely certify rank.
    planted = int.from_bytes(hashlib.shake_256(b'H17-GAP-ORACLE-AGENT8-20261107').digest(624*4),'little')
    synthetic = model.Basis()
    synthetic.rows = {pivot:(vector,(vector & planted).bit_count() & 1)
                      for pivot,(vector,_) in source.rows.items()}
    synthetic.rank = source.rank
    assert all(synthetic.predict(vector) is None for vector in targets)
    for word in templated:
        for vector in word:
            synthetic.insert(vector, (vector & planted).bit_count() & 1)
    assert all(synthetic.predict(vector) == ((vector & planted).bit_count() & 1)
               for vector in targets)
    print('PLANTED_INDEPENDENT_19968BIT_MT_SOURCE_AND_ALL_128_SELECTED_BITS_PASS')
    assert out[0][3] >= out[-1][3]
    assert all(out[i][3] <= out[i-1][3] for i in range(1,len(out)))
    print('HIGH_LEVERAGE_GAP_STAGES',sorted(contributions.items(),key=lambda x:(-x[1],x[0]))[:35])
    print('SUMMARY',{'source_rank': baseline,'routine_gap_words':len(gap_stages),
           'selected_initial_unknown':128,'last_output_unknown':out[-1][3]})


if __name__ == '__main__':
    main()
