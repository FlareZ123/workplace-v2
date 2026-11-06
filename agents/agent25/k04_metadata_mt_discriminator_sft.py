"""Original H17 spool metadata as a source-only MT19937 side channel.

Run with numpy: python agents/agent25/k04_metadata_mt_discriminator_sft.py resources
Read-only; selected row129 coupon and original K04 commitment are not used.
"""
from pathlib import Path
from itertools import permutations
import hashlib
import re
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'agent49'))
import k04_p951_symbolic_basis as mt

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('resources')
raw = (root / 'evidence/print/spool-reconstruction.log').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
records = []
for line in raw.decode().splitlines():
    match = re.search(r'CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)', line)
    if match:
        records.append((match.group(1), bytes.fromhex(match.group(2)), match.group(3)))
assert len(records) == 133
source, bank = mt.source(root)
assert source.rank == 15365

rows = [i for i in range(133) if i != 129]
dest_names = ['store', 'desk', 'bench']
observed = np.array([dest_names.index(records[i][2]) for i in rows], dtype=np.int8)
views = [('native-hi2', [30, 31], False), ('native-lo2', [0, 1], False),
         ('temp-hi2', [30, 31], True), ('temp-lo2', [0, 1], True)]
perms = list(permutations(range(3)))
models = []
descriptions = []

for name, bits, is_tempered in views:
    for offset in range(-12, 13):
        code = [-1] * len(rows)
        for k, row in enumerate(rows):
            pos = mt.STARTS[row] + offset
            if not mt.ORIGIN <= pos <= mt.LAST:
                continue
            word = mt.get(bank, pos)
            if is_tempered:
                word = mt.temper(word)
            pair = [source.predict(word[j]) for j in bits]
            if None not in pair:
                value = pair[0] + (pair[1] << 1)
                if value < 3:
                    code[k] = value
        support = sum(x >= 0 for x in code)
        if support >= 20:
            for order in perms:
                models.append([order[x] if x >= 0 else -1 for x in code])
                descriptions.append((name, offset, order, support))

model_matrix = np.array(models, dtype=np.int8)
valid = model_matrix >= 0
counts = valid.sum(axis=1)
original_hits = ((model_matrix == observed[None, :]) & valid).sum(axis=1)
scores = original_hits / counts
winner = int(np.argmax(scores))
assert descriptions[winner] == ('temp-hi2', 4, (0, 1, 2), 26)
assert (int(original_hits[winner]), int(counts[winner])) == (20, 26)
print('BEST', descriptions[winner], '20/26', 'models', len(models), flush=True)

rng = np.random.default_rng(20261105)
perm_count = 10000
exceed = 0
for _ in range(perm_count):
    shuffled = rng.permutation(observed)
    scores_null = ((model_matrix == shuffled[None, :]) & valid).sum(axis=1) / counts
    exceed += bool(np.max(scores_null) >= scores[winner])
assert exceed == 1
print('SHUFFLE', exceed, '/', perm_count, 'addone_p',
      (exceed + 1) / (perm_count + 1), flush=True)

classes = np.array([records[i][0] for i in rows])
by_class = [np.flatnonzero(classes == name) for name in ('LABEL', 'RECOVER', 'STORES')]
within_exceed = 0
for _ in range(perm_count):
    shuffled = observed.copy()
    for members in by_class:
        shuffled[members] = rng.permutation(shuffled[members])
    scores_null = ((model_matrix == shuffled[None, :]) & valid).sum(axis=1) / counts
    within_exceed += bool(scores_null.max() >= scores[winner])
assert within_exceed == 0
print('WITHIN_CLASS_SHUFFLE', within_exceed, '/', perm_count, 'addone_p',
      (within_exceed + 1) / (perm_count + 1), flush=True)

mask = model_matrix[winner]
for lo, hi, expected in [(0, 64, (5, 7)), (64, 133, (15, 19))]:
    selection = np.array([lo <= row < hi for row in rows]) & (mask >= 0)
    hits = int(((mask == observed) & selection).sum())
    n = int(selection.sum())
    assert (hits, n) == expected
    print('HALF', lo, hi, hits, '/', n, flush=True)

def compatible(bits, value):
    return all(x is None or x == ((value >> j) & 1) for j, x in enumerate(bits))

def possible(window, first, second):
    n = len(window)
    if n < 2:
        return False
    for t in range(n - 1):
        if all(all(x is None or x == 1 for x in window[j]) for j in range(t)):
            if (compatible(window[t], first)
                    and all(all(x is None or x == 1 for x in window[j])
                            for j in range(t + 1, n - 1))
                    and compatible(window[-1], second)):
                return True
    return False

category_names = ['LABEL', 'RECOVER', 'STORES']
windows = []
for i in range(127):
    q, next_q = mt.STARTS[i:i + 2]
    bits = []
    for pos in range(q + 4, next_q):
        v = mt.temper(mt.get(bank, pos))
        bits.append((source.predict(v[30]), source.predict(v[31])))
    windows.append(bits)

best = (0, None)
for order in ('DEST-CLASS', 'CLASS-DEST'):
    for pc in perms:
        for pd in perms:
            passes = 0
            for i, window in enumerate(windows):
                c = pc[category_names.index(records[i][0])]
                d = pd[dest_names.index(records[i][2])]
                x, y = (d, c) if order == 'DEST-CLASS' else (c, d)
                passes += possible(window, x, y)
            if passes > best[0]:
                best = (passes, (order, pc, pd))
assert best == (80, ('DEST-CLASS', (0, 2, 1), (0, 1, 2)))
print('STRICT_ISSUER', best[0], '/', len(windows), 'contradictions',
      len(windows) - best[0], flush=True)

# Conditional target effect only; source has no attestation of this emitter.
assert records[128][2] == 'bench'
predicted_word = mt.temper(mt.get(bank, mt.STARTS[129]))
limited = mt.Basis()
limited.rows = source.rows.copy()
limited.rank = source.rank
limited.insert(predicted_word[30], 0)
limited.insert(predicted_word[31], 1)
assert limited.rank == 15367
print('TARGET', 'conditional 2/128 bits; no authenticated bits', flush=True)
print('Original K04/K08 still unresolved; accepted six unchanged')
