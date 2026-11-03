"""H-17 node50: source-only flexible recorder writer model tests.

Use from workplace-v2 root: python agents/agent18/k04_recorder_alt_stage_sft.py
Selected K04 attempt-2, route mask, acceptance, K08 all withheld from model fitting.
"""
import hashlib
import importlib.util
import itertools
import random
import struct
import zlib
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'resources'
SPEC = importlib.util.spec_from_file_location('original_mt', ROOT / 'agents/agent2/20261102_k04_multicarrier_p951_sft.py')
mt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mt)
values, known, offset = mt.source_closure(RES)
raw = (RES / 'evidence/recorder/trip-recorder.raw').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'
records = {}
for i in range(88):
    pos = 16 + 24 * i
    sec, node, event, latch, seq, w, aux, crc = struct.unpack_from('<IHBBI4sII', raw, pos)
    if node == 50:
        assert zlib.crc32(raw[pos:pos+20]) == crc
        records[seq] = {'ts':sec - 1791061740, 'event':event - 1,
                        'latch':latch, 'aux':aux - 2000,
                        'ctrl':mt.untemper(int.from_bytes(w, 'little'))}
assert len(records) == 72 and set(records) == set(range(72))

@lru_cache(None)
def observed(pos):
    idx = offset + pos
    if idx < 0 or idx >= len(known):
        return None
    mask = known[idx]
    if mask == 0xffffffff:
        return (mt.temper(values[idx]),)
    if mask == 0x7fffffff:
        return (mt.temper(values[idx]), mt.temper(values[idx] | 0x80000000))
    return None

@lru_cache(None)
def consumes(pos, field, value, mode, epoch):
    if field == 'ts' and mode in ('latent1', 'latent2'):
        return (1 if mode == 'latent1' else 2,)
    n, bits = {'ts':(400,9),'event':(39,6),'latch':(4,3),'aux':(6000,13)}[field]
    value -= epoch if field == 'ts' else 0
    if not 0 <= value < n:
        return ()
    if mode == 'float53':
        xs, ys = observed(pos), observed(pos+1)
        if xs is not None and ys is not None:
            if not any(int((((x >> 5) * 67108864 + (y >> 6)) / 9007199254740992) * 400) == value
                       for x in xs for y in ys):
                return ()
        return (2,)
    current = observed(pos)
    if mode == 'getbits2':
        return (1,) if current is None or any(x >> 30 == value for x in current) else ()
    if mode == 'u32scale':
        return (1,) if current is None or any(((x*n)>>32) == value for x in current) else ()
    if mode == 'mod':
        return (1,) if current is None or any(((x>>(32-bits))%n) == value for x in current) else ()
    assert mode == 'range', mode
    lengths=[]
    for length in range(1,13):
        valid=True
        for j in range(length):
            x = observed(pos+j)
            if x is None:
                continue
            if j+1 == length:
                if not any(w >> (32-bits) == value for w in x):
                    valid=False
                    break
            elif not any(w >> (32-bits) >= n for w in x):
                valid=False
                break
        if valid:
            lengths.append(length)
    return tuple(lengths)

@lru_cache(None)
def next_stages(seq, start, order, modes, epoch, extra, extra_field):
    before = records[seq]
    after = records[seq+1]
    split = order.index('ctrl')
    # Source 32-bit control was emitted within a record; the next control follows
    # all fields after its predecessor and all fields before the new control.
    fields=[(f,before[f]) for f in order[split+1:]] + [(f,after[f]) for f in order[:split]]
    active={start+1}
    mode_by_field=dict(zip(('ts','event','latch','aux'),modes))
    for field,value in fields:
        fresh=set()
        for pos in active:
            pos += extra if field == extra_field else 0
            for length in consumes(pos,field,value,mode_by_field[field],epoch):
                fresh.add(pos+length)
        active=fresh
        if not active:
            return ()
    result=[]
    for pos in active:
        pos += extra if extra_field=='boundary' else 0
        if pos >= 0 or pos <= -1100:
            continue
        if ((after['ctrl'] ^ values[offset+pos]) & known[offset+pos]) == 0:
            result.append(pos)
    return tuple(sorted(set(result)))

def connects(start_seq, end_seq, origin, model):
    live={origin}
    for seq in range(start_seq, end_seq):
        upper=-339 if start_seq==45 else -769
        nxt={q for p in live for q in next_stages(seq,p,*model) if p<q<=upper}
        live=nxt
        if not live:
            return seq+1, ()
    return end_seq, tuple(sorted(live))

def seeded_control():
    rng=random.Random(20261103)
    draws=[]
    def draw(bits):
        full=rng.getrandbits(32)
        draws.append(full)
        return full >> (32-bits)
    def rr(n):
        while True:
            x=draw(n.bit_length())
            if x<n:return x
    for _ in range(24):
        control=draw(32)
        index=len(draws)-1
        aux=rr(6000)
        ts=rr(400)
        event=rr(39)
        latch=rr(4)
        active=index+1
        for wanted,n in ((aux,6000),(ts,400),(event,39),(latch,4)):
            while True:
                val=draws[active] >> (32-n.bit_length())
                active+=1
                if val<n:
                    assert val==wanted
                    break
        assert active==len(draws) and isinstance(control,int)
    print('CONTROL: 24 genuinely seeded standard Python rejection-sampler transitions PASS')

def main():
    seeded_control()
    assert records[45]['ctrl'] & known[offset-540] == values[offset-540] & known[offset-540]
    fixed_models=[]
    for a,ts,e,l,epoch,field in itertools.product(
        ('range','mod','u32scale'),('range','latent1','latent2','u32scale','float53'),
        ('range','mod','u32scale'),('range','getbits2','u32scale'),(0,2),
        ('none','aux','ts','event','latch')):
        fixed_models.append((('ts','event','latch','ctrl','aux'), (ts,e,l,a), epoch,
                             0 if field=='none' else 1, field))
    variable_models=[]
    for order,ts,l,extra in itertools.product(itertools.permutations(('ts','event','latch','ctrl','aux')),
                                              ('range','latent1','latent2'),('range','getbits2'),range(4)):
        variable_models.append((order,(ts,'range',l,'range'),2,extra,'boundary'))
    for title,models in (('fixed1350',fixed_models),('permuted2880',variable_models)):
        stats=Counter()
        reached=0
        earliest=0
        for model in models:
            end,places=connects(45,70,-540,model)
            stats[end]+=1
            if -339 in places:reached+=1
            if title.startswith('permuted'):
                e,early=connects(9,13,-793,model)
                earliest+=int(e==13 and -769 in early)
        print(title,'models',len(models),'reach70',reached,'max_seq',max(stats),
              'largest_prefix_count',stats[max(stats)],'reach_early_seq13',earliest)
        assert reached==0
    print('No selected K04 original bytes inferred, no K08 final words inferred.')

if __name__=='__main__':
    main()
