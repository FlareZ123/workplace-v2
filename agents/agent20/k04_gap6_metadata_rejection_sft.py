"""Source-only p951 rejection-cost falsifier of two categorical emitters.

Hypothesis: each ordinary 16-byte printer packet uses four MT32 outputs;
its CLASS and DEST values are each produced by CPython randrange(3)
using getrandbits(2) with rejection of value 3. If the next packet begins
six draws after the current one, the two hidden outputs must both be <=2.

The selected disputed K04 row129 is omitted from all fitted observations.
The printed source model is a hypothesis, not authenticated printer firmware.
"""
import json
import re
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import source, temper, STARTS, get

def main():
    printer, state = source(ROOT / 'resources')
    assert printer.rank == 15365
    raw = (ROOT / 'resources/evidence/print/spool-reconstruction.log').read_text()
    rows = [dict(re.findall(r'(JOB|CLASS|DEST|ATTEMPT|STATE)=([^ ]+)', ln))
            for ln in raw.splitlines() if 'PAYLOAD=' in ln]
    assert len(rows) == len(STARTS) == 133
    contradictions = []
    n_gap6 = 0
    partially_known = 0
    for i in range(128):
        pos = STARTS[i]
        if STARTS[i+1] - pos != 6:
            continue
        n_gap6 += 1
        for stage in (pos+4, pos+5):
            top2 = [printer.predict(eq) for eq in temper(get(state,stage))[30:32]]
            if None in top2:
                continue
            partially_known += 1
            value = top2[0] | (top2[1]<<1)
            if value == 3:
                contradictions.append(dict(row=i, job=rows[i]['JOB'],
                    stage=stage, native_top2=value, gap=6,
                    category_pair=[rows[i]['CLASS'], rows[i]['DEST']]))
    assert n_gap6 == 53
    assert [(r['row'],r['stage']) for r in contradictions] == [(22,174),(23,180),(77,586)]
    # Whole seeded sampler positive, including rejection/cumulative draw count.
    seeded = random.Random(2603)
    positives = 0
    for _ in range(128):
        for _ in range(4): seeded.getrandbits(32)
        replay = random.Random(); replay.setstate(seeded.getstate())
        skips = []
        for _ in range(2):
            n = 3
            k = n.bit_length()
            v = replay.getrandbits(k)
            skips.append(v)
            while v >= n:
                v = replay.getrandbits(k)
                skips.append(v)
        for _ in range(2): seeded.randrange(3)
        assert seeded.getstate() == replay.getstate()
        if len(skips) == 2:
            positives += 1
            assert all(x < 3 for x in skips)
    assert positives == 66
    print(json.dumps(dict(model='two consecutive getrandbits(2) / randrange(3) metadata draws',
        p951_source_rank=printer.rank, gap6_rows=n_gap6,
        synthetic_gap6_positive=positives,
        independently_known_hidden_draws=partially_known,
        rejecting_top2_source_witnesses=contradictions,
        model_compatible=False, original_selected_K04_bits=0),sort_keys=True))

if __name__=='__main__': main()
