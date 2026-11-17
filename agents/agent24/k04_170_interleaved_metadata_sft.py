"""K04: all 170 source-compatible MT chronologies, split metadata draws.

Use the original untouched 132 printer source packets. Selected ACK row129
and original K04/K08 commitments are entirely excluded. If one complete
metadata writer survives source-only training/holdout, it becomes a
candidate for further complete-coupon mechanism reconstruction.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent44"))
import k04_single_root_perturbations_sft as variants
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt

CLASSES=("LABEL","RECOVER","STORES")
DESTS=("bench","desk","store")
PERMS=tuple(itertools.permutations(range(3)))
TRAIN=95
TOTAL=127

def possible_codes(temper_expression,basis):
    low=mt.reduce_row(temper_expression[30]<<1,basis)
    high=mt.reduce_row(temper_expression[31]<<1,basis)
    lows=(low,) if low<=1 else (0,1)
    highs=(high,) if high<=1 else (0,1)
    return {l+2*h for l in lows for h in highs}

def pair_mask(positions):
    """Nine-bit availability mask for two accepted choices at distinct stages."""
    result=0
    for i,left in enumerate(positions):
        for j,right in enumerate(positions):
            if i==j:continue
            for c in left&{0,1,2}:
                for d in right&{0,1,2}:
                    result|=1<<(3*c+d)
    return result

def score_model(masks,ci,di,cls_at,dst_at,pc,pd):
    train=held=0
    for row,allowed in enumerate(masks):
        c=pc[ci[row+cls_at]]
        d=pd[di[row+dst_at]]
        ok=(allowed>>(3*c+d))&1
        if row<TRAIN:train+=ok
        else:held+=ok
    return train,held

def main():
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==mt.SOURCE_SHA
    lines,rows,selected,_=mt.source_rows(raw,ROOT)
    assert selected==129 and len(rows)==len(lines)==133 and rows[129]==[]
    labels=[tuple(re.search(r"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)",line).groups())
            for line in lines]
    assert set(labels[:128])==set(itertools.product(CLASSES,DESTS))
    ci=[CLASSES.index(c) for c,d in labels]
    di=[DESTS.index(d) for c,d in labels]

    end=max(x[-1] for x in six.GEOMETRIES.values())+5
    terms=mt.state_expressions(end)
    tempered=[variants.tempered_bits(word) for word in terms]
    assert pair_mask([{0,3},{1}])&(1<<(3*0+1))
    assert not pair_mask([{0},{1}])&(1<<(3*2+1))

    outcomes=defaultdict(lambda:{"valid":0,"min_train_errors":TRAIN+1,
                                  "min_total_errors":TOTAL+1,
                                  "training_survivors":0,"complete_survivors":0})
    p951=None
    for target_stage,baseline in sorted(six.GEOMETRIES.items()):
        source_valid=0
        for component,delta in [(-1,0)]+[(g,d) for g in range(81) for d in (-2,-1,1,2)]:
            starts=[start+(delta if variants.GROUPS[row]==component else 0)
                    for row,start in enumerate(baseline)]
            if not variants.physical(starts,target_stage):
                continue
            if variants.impossible_threeword(starts,rows):
                continue
            try:
                basis=six.build_source_basis(terms,rows,starts)
            except AssertionError:
                continue
            source_valid+=1
            gaps=[
                pair_mask([possible_codes(tempered[pos],basis)
                           for pos in range(starts[row]+4,starts[row+1])])
                for row in range(127)
            ]
            max_for_bindings=[]
            for cls_at,dst_at in itertools.product((0,1),repeat=2):
                best_full=0
                for pc,pd in itertools.product(PERMS,repeat=2):
                    train,held=score_model(gaps,ci,di,cls_at,dst_at,pc,pd)
                    best_full=max(best_full,train+held)
                    item=outcomes[target_stage]
                    item["min_train_errors"]=min(item["min_train_errors"],TRAIN-train)
                    item["min_total_errors"]=min(item["min_total_errors"],TOTAL-train-held)
                    if train==TRAIN:
                        item["training_survivors"]+=1
                        if held==TOTAL-TRAIN:
                            item["complete_survivors"]+=1
                            print("FULL_SOURCE_WRITER",target_stage,component,delta,
                                  "binding",cls_at,dst_at,"codebook",pc,pd,flush=True)
                max_for_bindings.append(best_full)
            if target_stage==951 and component==-1:
                p951=max_for_bindings
            outcomes[target_stage]["valid"]+=1
        print("STAGE",target_stage,"SOURCE_COMPATIBLE",source_valid,
              "MIN_ERRORS_TRAIN",outcomes[target_stage]["min_train_errors"],
              "MIN_ERRORS_ALL",outcomes[target_stage]["min_total_errors"],
              "FULL_WRITERS",outcomes[target_stage]["complete_survivors"],flush=True)
    expected={950:35,951:28,952:25,953:21,954:31,955:30}
    assert {p:outcomes[p]["valid"] for p in expected}==expected
    assert p951==[114,112,116,113],p951
    print(json.dumps({"spool_sha256":mt.SOURCE_SHA,
        "selected_row129_payload_used":False,"selected_K04_bytes_authenticated":0,
        "source_compatible_chronologies":sum(v["valid"] for v in outcomes.values()),
        "p951_baseline_paircode_best_currentcurrent_currentnext_nextcurrent_nextnext":p951,
        "by_selected_stage":outcomes},indent=2),flush=True)
    if sum(v["complete_survivors"] for v in outcomes.values()):
        print("ACTION: source writer survived, independently test joint free-bit satisfiability")
    else:
        print("NO COMPLETE METADATA WRITER in this optimistic 170-chronology family")


if __name__=="__main__":main()
