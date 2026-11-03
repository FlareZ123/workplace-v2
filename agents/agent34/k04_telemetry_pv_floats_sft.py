"""Source-only K04 probe: telemetry PV floats as shared MT draw witnesses.

Run at workplace-v2 root: python agents/agent34/k04_telemetry_pv_floats_sft.py
No selected ACK, K04/K08 commitment, nonce or route mask is read.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TELEM = ROOT / 'resources/evidence/telemetry/freeze-export.jsonl'
TELEM_SHA = '3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f'
MODEL = ROOT / 'agents/agent2/20261102_k04_multicarrier_p951_sft.py'

def mt_state():
    spec = importlib.util.spec_from_file_location('h17_p951_source_only', MODEL)
    assert spec and spec.loader
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    values, known, offset = obj.source_closure(ROOT / 'resources')
    assert len(values) == len(known) == 6000
    assert all(known[offset + i] == 0 for i in range(951,955))
    return values, known, offset, obj.temper

def python_random_float(a,b):
    return ((a >> 5) * 67108864 + (b >> 6)) / 9007199254740992.0

def run():
    raw = TELEM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TELEM_SHA
    original = [json.loads(line) for line in raw.splitlines()]
    pv = [(i,r) for i,r in enumerate(original) if r['field'] == 'PV']
    assert len(original) == 145 and len(pv) == 112
    assert all(10 <= r['value'] < 90 for _,r in pv)

    # Full Python random.random() control uses exactly two consecutive MT32 words.
    q = random.Random(9372)
    words = [q.getrandbits(32) for _ in range(2)]
    q2 = random.Random(9372)
    assert python_random_float(*words) == q2.random()
    q3 = random.Random(3219)
    for _ in range(100):
        state = q3.getstate()
        a,b = q3.getrandbits(32),q3.getrandbits(32)
        check = random.Random()
        check.setstate(state)
        assert python_random_float(a,b) == check.random()

    values, known, offset, temper = mt_state()
    by_milli = defaultdict(list)
    by_17 = defaultdict(list)
    for i,r in pv:
        by_milli[round(r['value'],3)].append((i,r['tag'],r['unit']))
        by_17[int(round((r['value']-10)*1000))].append((i,r['tag'],r['unit']))
    complete_pairs = []
    full_words = []
    for native in range(-1100, 1040):
        if known[offset + native] == 0xffffffff:
            full_words.append(native)
        if native < 1039 and all(known[offset + native + j] == 0xffffffff for j in (0,1)):
            a,b = (temper(values[offset + native+j]) for j in (0,1))
            complete_pairs.append((native,python_random_float(a,b)))
    assert len(complete_pairs) == 584

    uniform_hits = []
    for idx, u in complete_pairs:
        for row in by_milli[round(10+80*u,3)]:
            uniform_hits.append((idx,*row))
    discrete_hits=[]
    for idx in full_words:
        code=temper(values[offset+idx])>>15
        for row in by_17[code]:
            discrete_hits.append((idx,*row))
    assert uniform_hits == [(526,12,'FT-13','kPa')],uniform_hits
    assert discrete_hits == [],discrete_hits
    print('PV',len(pv),'full consecutive native pairs',len(complete_pairs),
          'full single words',len(full_words))
    print('python random.random() 10+80*uniform rounded to 0.001:',uniform_hits)
    print('17-bit discrete randint code 1000*(value-10):',discrete_hits)
    print('independent null expected float pair coincidences ~',
          round(len(pv)*len(complete_pairs)/80000,5))
    print('No source-indexed high-width target donor and no authenticated K04 bits')

if __name__=='__main__':
    run()
