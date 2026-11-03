"""K08 editor placebo: 1024 equal-cardinality source-context shuffles per known label.

Run from repository root with numpy and scipy:
    python agents/agent10/k08_editor_purpose_placebo_sft.py
Original source and route/acceptance are never modified or used as trainable
targets. Both known historic inscriptions are treated as retrospective labels.
"""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import random

import numpy as np
from scipy.sparse import csr_matrix

SCRIPT = Path(__file__).with_name('k08_purpose_editor_sft.py')
spec = importlib.util.spec_from_file_location('editor', SCRIPT)
editor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(editor)
texts = sorted(set(map(editor.norm, editor.candidates())))
assert len(texts) == 21836
words = sorted({w for sentence in texts for w in set(sentence.split()) if len(w)>2})
wid = {w:i for i,w in enumerate(words)}
row, col = [], []
for i, sentence in enumerate(texts):
    for w in set(sentence.split()):
        if w in wid:
            row.append(i)
            col.append(wid[w])
X = csr_matrix((np.ones(len(row)), (row,col)), shape=(len(texts),len(words)))
base = np.zeros(len(texts))
for i, sentence in enumerate(texts):
    w = sentence.split()
    morph = sum(.6 if v in editor.MORPH and editor.MORPH[v] in editor.TOKENS else 1.5
                for v in set(w) if v not in editor.TOKENS)
    bg = sum(.05 if editor.BIGRAMS[(a,b)] else 0 for a,b in zip(w,w[1:]))
    genre = 0 if len(w)<=11 else .8
    base[i] = round(abs(len(w)-8)*.23 + genre + morph - bg,5)

noteids = sorted(set(editor.notes)-{17,18})
assert len(noteids)==22
rng = random.Random(20261103)
positions = np.arange(len(texts))
text_index = {s:i for i,s in enumerate(texts)}

def evaluate_context(ids,label):
    ctx = Counter(editor.norm(' '.join(editor.notes[n] for n in ids)).split())
    weights = np.array([min(ctx[w],2) for w in words])
    scores = np.round(base - 1.1*(X@weights),5)
    phrase = editor.controls[label]
    j = text_index[phrase]
    rank = int(np.count_nonzero(scores<scores[j]) +
               np.count_nonzero((scores==scores[j]) & (positions<j)) + 1)
    if tuple(ids) == tuple(editor.CONTEXT[label]):
        assert abs(scores[j] - editor.score(phrase,label)) < .0001
    return rank

out={}
for label in ('standby','commissioning'):
    actual = evaluate_context(editor.CONTEXT[label],label)
    n = len(editor.CONTEXT[label])
    arr = [evaluate_context(rng.sample(noteids,n),label) for _ in range(1024)]
    better = sum(x<=actual for x in arr)
    out[label] = {
       'actual_rank': actual,
       'n_permutations': len(arr),
       'context_cardinality': n,
       'random_rank_quantiles': {str(q):int(np.quantile(arr,q,method='nearest'))
              for q in (0,.05,.25,.5,.75,.95,1)},
       'random_mean_rank':round(float(np.mean(arr)),2),
       'placebo_contexts_with_equal_or_better_rank': better,
       'empirical_one_sided_p':round((1+better)/(1+len(arr)),5),
    }
print(json.dumps({'fixed_candidate_count':len(texts),
                  'seed':20261103,'results':out},indent=2))
