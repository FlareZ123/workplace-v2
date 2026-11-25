#!/usr/bin/env python3
"""Extended bounded K04 screen over same-object transfer checkpoint history.
Run from repository root: python work/h17_k04_cross_transfer_extended_screen.py
"""
import hashlib, itertools, json, re, functools
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'resources'/'evidence'
A=ROOT/'resources'/'acceptance.json'
MOD=1<<128
EXPECTED={
 'transfer':'32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
 'routing':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
 'spool':'7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
}

def main():
    tp=E/'transfers'/'transfer-audit.jsonl'
    rp=E/'recovery-routing.json'
    sp=E/'print'/'spool-reconstruction.log'
    paths={'transfer':tp,'routing':rp,'acceptance':A,'spool':sp}
    for n,p in paths.items():
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=EXPECTED[n]: raise SystemExit(f'{n} changed: {h}')
    target=json.loads(A.read_text())['slot_sha256']['K04']
    mask=bytes.fromhex(json.loads(rp.read_text())['K04']['masked_component'])
    rows=[json.loads(x) for x in tp.read_text().splitlines() if x.strip()]
    groups=defaultdict(dict)
    for r in rows:
        if r['kind']=='CHUNK':
            groups[r['transfer']].setdefault(int(r['seq']),{})[int(r['attempt'])]=bytes.fromhex(r['checkpoint'])
    tids=sorted(groups)
    hits=[]
    def test(label,payload):
        if len(payload)==16:
            component=bytes(a^b for a,b in zip(payload,mask))
            if hashlib.sha256(component).hexdigest()==target:
                hits.append({'label':label,'payload':payload.hex().upper(),'component':component.hex().upper()})
    canonical={}; candidates={}
    for tid in tids:
        for att in (1,2):
            p=b''.join(groups[tid][i][att] for i in range(8))
            canonical[(tid,f'a{att}')]=p
            candidates[f'{tid}:a{att}']=p
            test(f'{tid}:a{att}',p)
        delta=b''.join(bytes(x^y for x,y in zip(groups[tid][i][1],groups[tid][i][2])) for i in range(8))
        canonical[(tid,'dx')]=delta
        candidates[f'{tid}:dx']=delta
        test(f'{tid}:dx',delta)
        candidates[f'{tid}:d21']=b''.join(((int.from_bytes(groups[tid][i][2],'big')-int.from_bytes(groups[tid][i][1],'big'))%65536).to_bytes(2,'big') for i in range(8))
        candidates[f'{tid}:d12']=b''.join(((int.from_bytes(groups[tid][i][1],'big')-int.from_bytes(groups[tid][i][2],'big'))%65536).to_bytes(2,'big') for i in range(8))
        for bits in itertools.product((1,2),repeat=8):
            p=b''.join(groups[tid][i][a] for i,a in enumerate(bits))
            candidates[f'{tid}:mix:{bits}']=p
            test(f'{tid}:mix',p)
    hash_n=0
    for name,p in candidates.items():
        outputs=(hashlib.sha256(p).digest()[:16],hashlib.sha512(p).digest()[:16],
                 hashlib.md5(p).digest(),hashlib.blake2s(p,digest_size=16).digest(),
                 hashlib.sha3_256(p).digest()[:16],hashlib.shake_128(p).digest(16))
        for q in outputs:
            test(name+':hash',q)
            hash_n+=1
    pair_n=0
    for (na,a),(nb,b) in itertools.combinations(canonical.items(),2):
        outputs=(bytes(x^y for x,y in zip(a,b)),
                 ((int.from_bytes(a,'big')+int.from_bytes(b,'big'))%MOD).to_bytes(16,'big'),
                 ((int.from_bytes(a,'big')-int.from_bytes(b,'big'))%MOD).to_bytes(16,'big'),
                 ((int.from_bytes(b,'big')-int.from_bytes(a,'big'))%MOD).to_bytes(16,'big'))
        for q in outputs:
            test(f'{na}/{nb}',q)
            pair_n+=1
    for ta,tb in itertools.combinations(tids,2):
        for aa,ab in itertools.product((1,2),repeat=2):
            q=b''.join(bytes(x^y for x,y in zip(groups[ta][i][aa],groups[tb][i][ab])) for i in range(8))
            test(f'{ta}/a{aa}^{tb}/a{ab}',q)
            pair_n+=1
    for mode in ('a1','a2','dx'):
        chains=[canonical[(t,mode)] for t in tids]
        q=bytes(a^b^c^d for a,b,c,d in zip(*chains))
        test('all/'+mode,q)
        pair_n+=1
    packets={}
    for line in sp.read_text().splitlines():
        fields=dict(re.findall(r'([A-Z]+)=([^\s]+)',line))
        if fields.get('JOB')=='PS-261003-0417' and 'PAYLOAD' in fields:
            packets[(fields.get('CLASS'),fields.get('ATTEMPT'))]=bytes.fromhex(fields['PAYLOAD'])
    if len(packets)!=4: raise SystemExit(f'expected 4 PS-0417 payloads, got {len(packets)}')
    cross_n=0
    for name,p in candidates.items():
        for spool_name,s in packets.items():
            outputs=(bytes(a^b for a,b in zip(p,s)),
                     ((int.from_bytes(p,'big')+int.from_bytes(s,'big'))%MOD).to_bytes(16,'big'),
                     ((int.from_bytes(p,'big')-int.from_bytes(s,'big'))%MOD).to_bytes(16,'big'),
                     ((int.from_bytes(s,'big')-int.from_bytes(p,'big'))%MOD).to_bytes(16,'big'),
                     bytes((a+b)&255 for a,b in zip(p,s)),
                     bytes((a-b)&255 for a,b in zip(p,s)),
                     bytes(a&b for a,b in zip(p,s)),
                     bytes(a|b for a,b in zip(p,s)))
            for q in outputs:
                test(f'{name}x{spool_name}',q)
                cross_n+=1
    perm_n=0
    for name,p in canonical.items():
        words=[p[i:i+2] for i in range(0,16,2)]
        for perm in itertools.permutations(range(8)):
            test(f'{name}:perm',b''.join(words[i] for i in perm))
            perm_n+=1
    reducers={k:[] for k in ('xor','sum','min','max','median-low','median-high','mean-floor','majority')}
    for i in range(8):
        values=sorted(int.from_bytes(groups[t][i][a],'big') for t in tids for a in (1,2))
        reducers['xor'].append(functools.reduce(lambda x,y:x^y,values))
        reducers['sum'].append(sum(values)%65536)
        reducers['min'].append(values[0]); reducers['max'].append(values[-1])
        reducers['median-low'].append(values[3]); reducers['median-high'].append(values[4])
        reducers['mean-floor'].append(sum(values)//8)
        majority=0
        for bit in range(16):
            if sum((v>>bit)&1 for v in values)>=5: majority|=1<<bit
        reducers['majority'].append(majority)
    for name,values in reducers.items():
        test('aggregate:'+name,b''.join(v.to_bytes(2,'big') for v in values))
    print(json.dumps({'transfer_candidate_presentations':len(candidates),
                      'hash_presentations':hash_n,
                      'cross_pair_presentations':pair_n,
                      'cross_spool_presentations':cross_n,
                      'chunk_order_permutations':perm_n,
                      'aggregate_presentations':len(reducers),
                      'hits':hits},indent=2))

if __name__=='__main__': main()
