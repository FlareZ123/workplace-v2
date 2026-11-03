"""Exact source-anchored CPython rejection histories with one fixed hidden gap.

Assume EVENT, LATCH, [h unrecorded 32-bit draws], CONTROL, AUX.
One global h (0..8) for all source-preindexed recorder controls, optional
0..3 genuine rejection draws before each field's acceptance. Fit on 13
source-preindexed interior anchors; only then check four seq47 CONTROL
placements. No K04/K08 acceptance targets nor disputed printer row are read.
"""
from collections import defaultdict, Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
sys.path.insert(0,str(ROOT/"agents"/"agent2"))
sys.path.insert(0,str(ROOT/"agents"/"agent47"))
from k04_p951_symbolic_basis import source
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_conditional_onebit_parity_sft import PATH,joint_basis
from k04_seq47_event_aux_joint_sft import recorder_metadata,ANCHORS
from k04_seq47_exact_joint_reject_sft import accepted,REJECT,solvable


def record_history(pos,prev,nxt,h,er,lr,ar,observed):
    event,latch,aux=observed
    assert 1<=event<=39 and 0<=latch<4 and 2000<=aux<8000
    latch_accepted=pos-h-1
    latch_first=latch_accepted-lr
    event_accepted=latch_first-1
    event_first=event_accepted-er
    aux_accepted=pos+ar+1
    if event_first<=prev or aux_accepted>=nxt:
        return None
    rows=[]
    rows.extend((stage,6,REJECT[6])
                for stage in range(event_first,event_accepted))
    rows.append((event_accepted,6,accepted(6,event-1)))
    rows.extend((stage,3,REJECT[3])
                for stage in range(latch_first,latch_accepted))
    rows.append((latch_accepted,3,accepted(3,latch)))
    rows.extend((stage,13,REJECT[13])
                for stage in range(pos+1,aux_accepted))
    rows.append((aux_accepted,13,accepted(13,aux-2000)))
    assert len(rows)==er+lr+ar+3
    return rows


def candidate_details(model,vectors,pos,prev,nxt,observed,h):
    matches=[]
    checks=0
    for er in range(4):
        for lr in range(4):
            for ar in range(4):
                rows=record_history(pos,prev,nxt,h,er,lr,ar,observed)
                if rows is None:continue
                checks+=1
                feasible,_=solvable(model,vectors,rows)
                if feasible is not None:
                    matches.append((er,lr,ar))
    return matches,checks


def main():
    printer,vectors=source(ROOT/"resources")
    assert printer.rank==15365
    controls=recorder_controls()
    meta=recorder_metadata()
    model=joint_basis(printer,vectors,controls,PATH)
    assert model.rank==16663
    idx={seq:i for i,(seq,_) in enumerate(PATH)}
    anchors=[seq for seq,_ in PATH[1:-1] if seq in ANCHORS]
    assert len(anchors)==13
    ranking=[]
    for h in range(9):
        supported=[]
        histories=0
        evaluated=0
        seq_counts={}
        for seq in anchors:
            i=idx[seq]
            _,pos=PATH[i]
            found,checks=candidate_details(model,vectors,pos,
                PATH[i-1][1],PATH[i+1][1],meta[seq],h)
            evaluated+=checks
            if found:
                supported.append(seq)
                histories+=len(found)
            seq_counts[seq]=len(found)
        ranking.append((len(supported),histories,h,supported,seq_counts))
        print("FROZEN_H",h,"anchor_support",len(supported),
              "of",len(anchors),"total_feasible_histories",histories,
              "tested",evaluated,"supported",supported,
              "per_seq_counts",seq_counts,flush=True)
    ranking.sort(reverse=True)
    max_supported=ranking[0][0]
    winning_h=[h for score,_,h,_,_ in ranking if score==max_supported]
    print("BEST_H",winning_h,"max_source_anchors",max_supported,flush=True)
    i=idx[47]
    for h in range(9):
        if h not in winning_h:
            continue
        for stage in (-523,-522,-521,-520):
            m=joint_basis(printer,vectors,controls,
                tuple((seq,stage if seq==47 else pos) for seq,pos in PATH))
            answers,checks=candidate_details(m,vectors,stage,
                PATH[i-1][1],PATH[i+1][1],meta[47],h)
            print("SEQ47_HOLDOUT","hidden_h",h,"stage",stage,
                  "feasible_histories",answers,"tested",checks,flush=True)
    print("CONDITIONAL_SOURCE_MODEL_ONLY; NO VERIFIED K04 BIT",flush=True)


if __name__=="__main__":
    main()
