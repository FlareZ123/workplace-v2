#!/usr/bin/env python3
"""Exhaustive raw checkpoint-selection screen for K04.
Run from repository root: python work/h17_k04_cross_transfer_selection_screen.py
"""
import hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'resources'/'evidence'
A=ROOT/'resources'/'acceptance.json'
EXPECTED={
 'transfer-audit.jsonl':'32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf',
 'recovery-routing.json':'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
 'acceptance.json':'681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
}

def main():
    tp=E/'transfers'/'transfer-audit.jsonl'
    rp=E/'recovery-routing.json'
    for name,p in [('transfer-audit.jsonl',tp),('recovery-routing.json',rp),('acceptance.json',A)]:
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=EXPECTED[name]: raise SystemExit(f'{name} changed: {h}')
    target=json.loads(A.read_text())['slot_sha256']['K04']
    mask=bytes.fromhex(json.loads(rp.read_text())['K04']['masked_component'])
    rows=[json.loads(x) for x in tp.read_text().splitlines() if x.strip()]
    groups=defaultdict(dict); status={}
    for r in rows:
        if r['kind']=='CHUNK':
            groups[r['transfer']].setdefault(int(r['seq']),{})[int(r['attempt'])]=bytes.fromhex(r['checkpoint'])
        else: status[r['transfer']]=r
    tids=sorted(groups)
    assert len(tids)==4 and all(sorted(groups[t])==list(range(8)) and all(set(groups[t][i])=={1,2} for i in range(8)) for t in tids)
    choices=[[(t,a,groups[t][seq][a]) for t in tids for a in (1,2)] for seq in range(8)]
    hits=[]; checked=0
    for combo in itertools.product(*choices):
        payload=b''.join(x[2] for x in combo)
        component=bytes(a^b for a,b in zip(payload,mask))
        if hashlib.sha256(component).hexdigest()==target:
            hits.append({'verified':True,'selection':[(x[0],x[1]) for x in combo],'candidate_bytes':'[REDACTED]'})
        checked+=1
    print(json.dumps({'transfer_ids':tids,'transfer_status':status,'candidate_count':checked,'hits':hits},indent=2,default=str))

if __name__=='__main__': main()
