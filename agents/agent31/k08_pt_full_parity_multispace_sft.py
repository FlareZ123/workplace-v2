#!/usr/bin/env python3
"""K08 PT source-only exact joint parity/bit/byte/attempt/order sensitivity.

Population: 4 retained transfers x 256 attempt-choice masks x 8! labeled
two-byte chunk permutations x 4 LSB bit/byte serializers x 4 parity choices
(high/low position, even/odd check). A separate no-parity 7-bit control is
reported; source instruction 'LOW IF EVEN' still favors the original even
configuration and alternative conventions are NOT equivalent hypotheses.

The 660,602,880-assignment parity factorial is counted exactly using
multisets and multinomial coefficients, rather than expensive direct loops.
Neither original K08 commitment nor nonce nor phrase appears in this script.

Run: python agents/agent31/k08_pt_full_parity_multispace_sft.py
     resources/evidence/transfers/transfer-audit.jsonl
"""
from collections import Counter
from pathlib import Path
import hashlib
import itertools
import json
import math
import sys

SOURCE_SHA="32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
TRANSFERS=("AX-7778","AX-7781","AX-7782","AX-7783")
LETTERS=(ord("P"),ord("T"))

def read(path):
    p=Path(path)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_SHA
    data={}
    for line in p.read_text().splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if row.get("kind")=="CHUNK":
            data.setdefault(row["transfer"],{})[(row["seq"],row["attempt"])]=bytes.fromhex(row["checkpoint"])
    assert set(data)==set(TRANSFERS)
    for chunks in data.values():
        assert set(chunks)=={(s,a) for s in range(8) for a in (1,2)}
        assert all(len(buf)==2 for buf in chunks.values())
    return data

def encoded(parity):
    if parity=="high_even":
        return (bytes(v|((v.bit_count()&1)<<7) for v in LETTERS),)
    if parity=="high_odd":
        return (bytes(v|(((v.bit_count()+1)&1)<<7) for v in LETTERS),)
    if parity=="low_even":
        return (bytes((v<<1)|(v.bit_count()&1) for v in LETTERS),)
    if parity=="low_odd":
        return (bytes((v<<1)|((v.bit_count()+1)&1) for v in LETTERS),)
    if parity=="unguarded":
        return tuple(bytes((v|(b<<7)) for v,b in zip(LETTERS,(k&1,(k>>1)&1))) for k in range(4))
    raise ValueError(parity)

def reverse8(v):
    return int(f"{v:08b}"[::-1],2)

def preimage(target,reverse_bit,reverse_bytes):
    if reverse_bytes:target=target[::-1]
    if reverse_bit:target=bytes(reverse8(v) for v in target)
    bits=[(v>>j)&1 for v in target for j in range(8)]
    return Counter(tuple(bits[i:i+2]) for i in range(0,16,2))

def score(data,parity,reverse_bit,reverse_bytes):
    patterns=[preimage(t,reverse_bit,reverse_bytes) for t in encoded(parity)]
    results={}
    for name in TRANSFERS:
        chunks=data[name]
        assignments=masks=0
        for mask in range(256):
            pairs=Counter(tuple(v&1 for v in chunks[(s,1+((mask>>s)&1))]) for s in range(8))
            ways=sum(math.prod(math.factorial(n) for n in p.values()) for p in patterns if p==pairs)
            assignments+=ways
            masks+=ways>0
        results[name]=(masks,assignments)
    return results

def brute(data,name,mask,parity,rb,ro):
    target=encoded(parity)
    assert len(target)==1
    t=target[0]
    chunks=[data[name][(s,1+((mask>>s)&1))] for s in range(8)]
    hits=0
    for perm in itertools.permutations(range(8)):
        pairs=[v&1 for j in perm for v in chunks[j]]
        out=bytes(sum(pairs[8*i+j]<<(7-j if rb else j) for j in range(8)) for i in range(2))
        if ro:out=out[::-1]
        hits+=out==t
    return hits

def main(path):
    data=read(path)
    families=("high_even","high_odd","low_even","low_odd","unguarded")
    totals={}
    for parity in families:
        for rb in (False,True):
            for ro in (False,True):
                results=score(data,parity,rb,ro)
                total=sum(n for mask,n in results.values())
                totals[(parity,rb,ro)]=total
                print(parity,"reverse_bit",int(rb),"reverse_byte",int(ro),
                      "PT_assignments",total,"by_transfer",
                      ",".join(str(results[name][1]) for name in TRANSFERS))
    assert totals[("high_even",False,False)]==2304
    assert [totals[("high_even",False,False)],totals[("high_even",False,True)],
            totals[("high_even",True,False)],totals[("high_even",True,True)]]==[2304,2304,4032,4032]
    parity_total=sum(n for (kind,_,_),n in totals.items() if kind!="unguarded")
    unguarded_total=sum(n for (kind,_,_),n in totals.items() if kind=="unguarded")
    assert parity_total==33024 and unguarded_total==46656
    assert brute(data,"AX-7778",49,"high_even",True,False)==144
    assert brute(data,"AX-7782",26,"high_even",False,False)==144
    assert brute(data,"AX-7778",161,"low_even",False,False)==240
    assert brute(data,"AX-7781",0,"high_odd",True,True)==144
    print("BRUTE_FORCE_LABELED_PERMUTATION_CONTROLS=4/4 PASS")
    print("PARITY_FAMILY PT=",parity_total,"total=",4*256*math.factorial(8)*4*4)
    print("UNGUARDED_FAMILY PT=",unguarded_total,"total=",4*256*math.factorial(8)*4)
    print("source_sha256=PASS K08_nonce_or_target_loaded=False")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: script.py transfer-audit.jsonl")
    main(sys.argv[1])
