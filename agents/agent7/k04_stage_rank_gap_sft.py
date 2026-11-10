"""H-17 conditional native MT stage relocation rank spectrum; selected row withheld."""
from collections import Counter
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'agents/agent49/k04_p951_symbolic_basis.py'
spec = importlib.util.spec_from_file_location('h17_mt_basis', MODEL)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
source, words = mt.source(ROOT)
assert source.rank == 15365
assert mt.STARTS[129] == 951


def residual(value):
    while value:
        pivot = value.bit_length() - 1
        if pivot in source.rows:
            value ^= source.rows[pivot][0]
        else:
            yield pivot
            value ^= 1 << pivot


def packet_rank(stage):
    pivots = {}
    for lane in range(4):
        for form in mt.get(words, stage + lane):
            value = sum(1 << bit for bit in residual(form))
            while value:
                pivot = value.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = value
                    break
                value ^= pivots[pivot]
    return len(pivots)

ranks = {stage: packet_rank(stage) for stage in range(mt.ORIGIN, mt.LAST - 2)}
counts = Counter(ranks.values())
assert len(ranks) == 2138
assert tuple(counts[r] for r in range(5)) == (284, 118, 43, 9, 4)
assert all(counts[r] == 0 for r in range(5, 28))
assert [s for s, r in ranks.items() if r == 28] == [-1082]
assert ranks[951] == 128
assert sum(counts.values()) == 2138
print('source_rank', source.rank, 'candidate_native_stages', len(ranks))
for rank, number in sorted(counts.items()):
    print(f'rank={rank:3d} count={number:4d}')
print('LOW_RANK_GAP_5_THROUGH_27_CONFIRMED', 'selected_target_rank=128')
