#!/usr/bin/env python3
"""Conditional K04 later-triad complete-coupon inversion, exact P12 partition.

Source hypothesis ONLY: the final eight bytes of the disputed PS-0417 ACK2
copy are intact and encode generator output3; intact later REQUESTED3
encodes outputs4/5 in the same 64-bit word-endian view. The initial three
outputs0/1 (REQUESTED1), 2/3 (selected coupon) are NOT fitting constraints.

A twelve-bit disjoint partition on state-at-output3 is searched exactly by
native Boolean SMT. Every SAT full-state model produces a FULL 16-byte
middle coupon for ORIGINAL unchanged K04 mask + SHA256 acceptance FIRST;
REQUESTED1 replay is a separate diagnostic. UNKNOWN is never excluded.
Original data/states/components remain owner-private outside repo; source
mode forbidden on GitHub Actions. Synthetic mode reads NO historical source.
"""
import argparse, hashlib, json, os, random, re, time
from pathlib import Path
import k04_pruned_native as e

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'resources'
P12=(0,1,2,3,22,23,24,25,45,46,47,48)
PINS={
 'evidence/print/spool-reconstruction.log':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083',
 'evidence/recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f'
}

def inverse(s):
    a,b=s; t=e.ror(b,28)
    prev_a=e.ror(a^t^((t<<21)&e.M),49)
    return prev_a,prev_a^t

def whole_stream(later_state):
    state=later_state
    for _ in range(3):state=inverse(state)
    return e.stream(*state,6)

def source(endian):
    for rel,dig in PINS.items():
        if hashlib.sha256((RES/rel).read_bytes()).hexdigest()!=dig:
            raise ValueError('Original source SHA mismatch: '+rel)
    lines=(RES/'evidence/print/spool-reconstruction.log').read_text().splitlines()
    rows=[line for line in lines if 'JOB=PS-261003-0417 ' in line
          and 'CLASS=RECOVER ' in line]
    if len(rows)!=3:raise ValueError('Expected exactly three selected-job rows')
    payload={}
    for line in rows:
        attempt=int(re.search(r'ATTEMPT=(\d+)',line).group(1))
        payload[attempt]=bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})',line).group(1))
    if set(payload)!={1,2,3}:raise ValueError('Missing selected attempt')
    pair=lambda p:[int.from_bytes(p[j:j+8],endian) for j in (0,8)]
    first=pair(payload[1])
    triad={0:int.from_bytes(payload[2][8:16],endian),
           1:pair(payload[3])[0],2:pair(payload[3])[1]}
    route=json.loads((RES/'evidence/recovery-routing.json').read_text())
    accept=json.loads((RES/'acceptance.json').read_text())
    return triad,first,bytes.fromhex(route['K04']['masked_component']),accept['slot_sha256']['K04']

def atomic(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as out:
        json.dump(value,out,sort_keys=True,separators=(',',':'))

def synthetic():
    for seed in range(202611281230,202611281234):
        rng=random.Random(seed)
        s=(rng.getrandbits(64),rng.getrandbits(64))
        triad=dict(enumerate(e.stream(*s,3)))
        anchor=sum(s[0]&(1<<j) for j in P12)
        models,status=e.solve(triad,anchor,P12,1500,True)
        assert models==[s] and status=='unsat'
        assert whole_stream(s)[3:6]==e.stream(*s,3)
    print({'source_free':True,'independent_three_output_planted_fixtures':4,
           'complete_state_recovered_and_blocked':4,'historical_data_read':False})

def original(start,count,endian,folder,ms,retry_ms):
    if os.environ.get('GITHUB_ACTIONS') or os.environ.get('GITHUB_REPOSITORY'):
        raise RuntimeError('Original data never in GitHub Actions')
    folder=folder.resolve()
    if folder==ROOT or ROOT in folder.parents or not folder.is_dir() or folder.stat().st_mode&0o077:
        raise ValueError('Private mode0700 folder outside repo required')
    triad,first,mask,target=source(endian)
    totals={'parents':0,'terminal_UNSAT':0,'terminal_UNKNOWN':0,
            'states':0,'earlier_holdout_replays':0,'original_K04_hits':0}
    for ix in range(start,start+count):
        cache=folder/f'triad_{endian}_p12_{ix:04d}.json'
        rec=None
        if cache.exists():
            if cache.is_symlink() or cache.stat().st_mode&0o077:
                raise ValueError('Unsafe private cache')
            rec=json.loads(cache.read_text())
            if rec['parent']!=ix or rec['view']!=endian or rec['tag']!='tail8-v1':
                raise ValueError('Wrong private triad checkpoint')
        else:
            anchor=sum(((ix>>j)&1)<<bit for j,bit in enumerate(P12))
            models,status=e.solve(triad,anchor,P12,ms,True)
            if status=='unknown' and retry_ms>ms:
                additional,status2=e.solve(triad,anchor,P12,retry_ms,True)
                models=sorted(set(models)|set(additional));status=status2
            original_hits=0;replays=0
            for state in models:
                seq=whole_stream(state)
                assert seq[3:6]==[triad[j] for j in range(3)]
                coupon=seq[2].to_bytes(8,endian)+seq[3].to_bytes(8,endian)
                component=bytes(x^y for x,y in zip(coupon,mask))
                match=hashlib.sha256(component).hexdigest()==target
                original_hits+=int(match)
                replays+=int(seq[:2]==first)
                if match:
                    atomic(folder/f'K04_ORIGINAL_TRIAD_HASH_HIT_{endian}_{ix:04d}.json',
                           {'K04':component.hex().upper(),'hypothesis':'ACK2-tail8 intact'})
            rec={'parent':ix,'view':endian,'tag':'tail8-v1','status':status,
                 'states':[[f'{a:016X}',f'{b:016X}'] for a,b in models],
                 'original_hits':original_hits,'earlier_holdout_replays':replays}
            atomic(cache,rec)
        totals['parents']+=1
        totals['terminal_UNSAT' if rec['status']=='unsat' else 'terminal_UNKNOWN']+=1
        totals['states']+=len(rec['states'])
        totals['earlier_holdout_replays']+=rec['earlier_holdout_replays']
        totals['original_K04_hits']+=rec['original_hits']
        if totals['parents']%64==0 or totals['original_K04_hits']:
            print('SOURCE_SAFE_AGGREGATE',json.dumps(
                {'view':endian,'range':[start,start+count],'totals':totals,
                 'historical_source_and_models_printed':False},sort_keys=True),flush=True)
    return totals

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--synthetic',action='store_true')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=64)
    p.add_argument('--endian',choices=('big','little'),default='big')
    p.add_argument('--timeout-ms',type=int,default=500)
    p.add_argument('--retry-ms',type=int,default=1000)
    p.add_argument('--private-dir',type=Path)
    a=p.parse_args()
    synthetic()
    if not a.synthetic:
        if not a.private_dir or not (0<=a.start and 0<a.count and a.start+a.count<=4096):
            p.error('Original mode requires valid P12 range and private directory')
        original(a.start,a.count,a.endian,a.private_dir,a.timeout_ms,a.retry_ms)
