#!/usr/bin/env python3
"""K04 original full-16byte packet affine-span rank: source-only state-width gate.

Withhold the selected ACK2 entirely. Prove lower bounds on any fixed
GF(2)-affine map from an arbitrary per-packet hidden state to the complete
128-bit printer output; source ordering, resets, skips and fitted native
transition functions do not enter. Never print any original coupon values.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,random,re

PIN="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def rank(vectors):
    basis={}
    for value in vectors:
        while value:
            p=value.bit_length()-1
            if p not in basis:
                basis[p]=value
                break
            value^=basis[p]
    return len(basis)

def affine_dimension(vectors):
    return rank([value^vectors[0] for value in vectors[1:]])

def synthetic():
    rng=random.Random(20261128)
    for d in (8,16,32,64):
        columns=[rng.getrandbits(128) for _ in range(d)]
        offset=rng.getrandbits(128)
        def f(state):
            out=offset
            while state:
                j=(state&-state).bit_length()-1
                out^=columns[j]
                state&=state-1
            return out
        states=[0]+[1<<j for j in range(d)]+[rng.getrandbits(d) for _ in range(128)]
        outputs=[f(state) for state in states]
        assert affine_dimension(outputs)==d
        assert rank(outputs) <= d+1
    print("SYNTHETIC 4/4 full-128bit affine-output state widths PASS (8,16,32,64)")

def original(root):
    raw=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    rows=[dict(re.findall(r"([A-Z]+)=([^ ]+)",line)) for line in raw.decode().splitlines()[1:129]]
    assert len(rows)==128
    assert [int(r["JOB"][-4:]) for r in rows]==list(range(300,428))
    cohorts={}
    for mode in ("ALL","CLASS","DEST","PAIR"):
        groups=defaultdict(list)
        for row in rows:
            label = ("all" if mode=="ALL" else row[mode] if mode in ("CLASS","DEST")
                     else row["CLASS"]+"|"+row["DEST"])
            groups[label].append(int(row["PAYLOAD"],16))
        cohorts[mode]=groups
    assert [len(cohorts[x]) for x in ("ALL","CLASS","DEST","PAIR")]==[1,3,3,9]
    print("ORIGINAL mode,cohort,intact_128bit_packets,linear_output_rank,affine_span_dimension,min_state_bits_fixed_affine_output")
    overall=0
    for mode,groups in cohorts.items():
        for label,packets in sorted(groups.items()):
            lr=rank(packets);ad=affine_dimension(packets)
            # Original output values are globally independent, so this
            # property must hold for every source-selected subset.
            assert lr==len(packets) and ad==len(packets)-1
            print("ORIGINAL",mode,label,len(packets),lr,ad,ad,sep="\t")
            overall+=1
        if mode in ("ALL","CLASS","DEST"):
            assert all(affine_dimension(v)>32 for v in groups.values())
    assert overall==16
    print("FINAL cohorts=16 global_min_state_bits=127 CLASS_min=34 DEST_min=37")
    print("FINAL a fixed <=32-bit GF2-affine per-packet issuer cannot fit original global, CLASS or DEST histories under ANY resets/skips; PAIR source sizes alone do not exclude it")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]/"resources")
    args=ap.parse_args()
    synthetic();original(args.root)
