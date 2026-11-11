"""Source-only p951 printer metadata/rejection-sampler whole-label holdout.

Run from a repository checkout with:
    python agents/agent1/k04_metadata_randbelow3_gap_sft.py
Original selected row129, K04 mask, K04 digest, and K08 are never loaded.
Requires the exact source-only helper in agents/agent4.
"""
from __future__ import annotations
import itertools
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent4"))
import k04_mt_full_state_gf2 as mt

def possible(positions, expected):
    for bit, (residual, value) in enumerate(positions):
        if residual==0 and ((expected>>bit)&1)!=value:
            return False
    return True

def allowed_split(hidden, label1, label2, map1, map2):
    n=len(hidden)
    if n<2:
        return 0
    count=0
    for s in range(1,n):
        outputs=[(bits,3) for bits in hidden[:s-1]]
        outputs.append((hidden[s-1],map1[label1]))
        outputs.extend((bits,3) for bits in hidden[s:-1])
        outputs.append((hidden[-1],map2[label2]))
        if all(possible(bits, value) for bits,value in outputs):
            count+=1
    return count

def main():
    root=ROOT/"resources"
    words=mt.symbolic_words()
    basis=mt.Basis()
    for index,value in mt.printer_observations(root):
        basis.add_word(words[index-mt.START],value)
    assert len(basis.rows)==15365
    raw=(root/"evidence"/"print"/"spool-reconstruction.log").read_bytes()
    rows=re.findall(rb"CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)",raw)
    assert len(rows)==133
    spans=[]
    for i in range(127):
        hidden=[]
        for stage in range(mt.STARTS[i]+4,mt.STARTS[i+1]):
            high_two=mt.tempered_bits(words[stage-mt.START])[30:32]
            hidden.append(tuple(basis.reduce(bit) for bit in high_two))
        spans.append((i,rows[i][0].decode(),rows[i][2].decode(),
                      rows[i+1][0].decode(),rows[i+1][2].decode(),hidden))
    assert sum(len(row[-1]) for row in spans)==434
    classes=("LABEL","STORES","RECOVER")
    destinations=("store","bench","desk")
    outcomes=[]
    for cv in itertools.permutations(range(3)):
        classmap=dict(zip(classes,cv))
        for dv in itertools.permutations(range(3)):
            destmap=dict(zip(destinations,dv))
            for alignment in ("current","next"):
                for order in ("class-first","dest-first"):
                    decisions=[]
                    for i,c,d,nc,nd,hidden in spans:
                        c=c if alignment=="current" else nc
                        d=d if alignment=="current" else nd
                        if order=="class-first":
                            n=allowed_split(hidden,c,d,classmap,destmap)
                        else:
                            n=allowed_split(hidden,d,c,destmap,classmap)
                        decisions.append(n>0)
                    outcomes.append((sum(decisions[:96]),sum(decisions[96:]),
                                     alignment,order,cv,dv,decisions))
    outcomes.sort(key=lambda x:(x[0],x[1]),reverse=True)
    best=outcomes[0]
    assert (best[0],best[1])==(62,18),best[:6]
    assert max(sum(x[-1]) for x in outcomes)<=80
    assert len(outcomes)==144
    print("Original selected coupon and acceptance commitments withheld")
    print("MT p951 source rank:",len(basis.rows))
    print("Regular interpacket spans:",len(spans),
          "hidden native MT words:",sum(len(x[-1]) for x in spans))
    print("Enumerated global 3! x 3! x 2 x 2 metadata producer models:",len(outcomes))
    print("Best training span fits: 62/96")
    print("Heldout metadata span fits for training winner: 18/31")
    print("Best original whole-record fit: <=80/127")
    print("Best model:",best[2:6])
    print("This conditional generator model does not produce an original K04 coupon.")

if __name__=="__main__":
    main()
