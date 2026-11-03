"""Exact original metadata-label permutation test for 24 MT field orders.

Order ELCA was retrospectively selected from original anchor metadata and
MUST be judged against 24-order maximum shuffle control, not post-hoc a
single-order p-value. No K04 selected coupon, K04 digest or K08 is used.
"""
from collections import Counter, defaultdict
from itertools import permutations
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
sys.path.insert(0,str(ROOT/"agents"/"agent2"))
sys.path.insert(0,str(ROOT/"agents"/"agent47"))
from k04_p951_symbolic_basis import source
from k04_conditional_onebit_parity_sft import PATH,joint_basis
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_seq47_event_aux_joint_sft import recorder_metadata,ANCHORS
from k04_seq47_exact_joint_reject_sft import State
from k04_recorder_all_order_accepted_anchors_sft import count_accepted_placements


def exact_permutation_distribution(matrix):
    """Exact distribution for matches under 13! permutations via DP."""
    n=len(matrix)
    states={(0,0):1}
    for row in range(n):
        nxt=defaultdict(int)
        for (used,hits),count in states.items():
            for j in range(n):
                if not (used>>j)&1:
                    nxt[(used | (1<<j),hits+int(matrix[row][j]))]+=count
        states=nxt
    distribution=Counter()
    for (used,hits),count in states.items():
        assert used==(1<<n)-1
        distribution[hits]+=count
    total=sum(distribution.values())
    f=1
    for i in range(1,n+1):f*=i
    assert total==f
    return distribution,total


def main():
    printer,vectors=source(ROOT/"resources")
    assert printer.rank==15365
    originals=recorder_controls()
    metadata=recorder_metadata()
    model=joint_basis(printer,vectors,originals,PATH)
    assert model.rank==16663
    index={seq:i for i,(seq,_) in enumerate(PATH)}
    anchors=[seq for seq,_ in PATH[1:-1] if seq in ANCHORS]
    assert len(anchors)==13
    orders=["".join(order) for order in permutations("ELCA")]
    matrices={}
    for order in orders:
        values=[]
        for seq in anchors:
            i=index[seq]
            _,pos=PATH[i]
            prev=PATH[i-1][1]
            nxt=PATH[i+1][1]
            row=[]
            for donor in anchors:
                n,_=count_accepted_placements(State(model),vectors,metadata[donor],
                                              prev,pos,nxt,order)
                row.append(int(n>0))
            values.append(tuple(row))
        matrices[order]=tuple(values)
        diagonal=sum(values[i][i] for i in range(len(anchors)))
        print("ORIGINAL_ORDER",order,"compatible_anchors",diagonal,
              "row_degrees",[sum(a) for a in values],flush=True)

    n=len(anchors)
    actual={order:sum(matrix[i][i] for i in range(n))
            for order,matrix in matrices.items()}
    maximum=max(actual.values())
    winners=[order for order,x in actual.items() if x==maximum]
    assert (maximum,winners)==(12,["ELCA"])
    exact,total=exact_permutation_distribution(matrices["ELCA"])
    tail=sum(x for k,x in exact.items() if k>=actual["ELCA"])
    print("EXACT_ELCA_P",tail,"/",total,"=",(tail/total),
          "distribution",sorted(exact.items()),flush=True)

    rng=random.Random(20261103)
    repeats=20000
    max_null=Counter()
    elca_null=Counter()
    hit_null=0
    for _ in range(repeats):
        idx=list(range(n));rng.shuffle(idx)
        scores={order:sum(matrix[i][idx[i]] for i in range(n))
                for order,matrix in matrices.items()}
        mx=max(scores.values())
        max_null[mx]+=1
        elca_null[scores["ELCA"]]+=1
        hit_null+=mx>=maximum
    print("MC_MAX24_P",(hit_null+1),"/",(repeats+1),"=",
          (hit_null+1)/(repeats+1),
          "hits",hit_null,"runs",repeats,
          "max24_hist",sorted(max_null.items()),flush=True)
    print("MC_ELCA_HIST",sorted(elca_null.items()),flush=True)
    print("ANCHOR_IDS",anchors,flush=True)
    print("SOURCE_ORDER_ONLY; NO K04 COUPON BIT VERIFIED",flush=True)


if __name__=="__main__":
    main()
