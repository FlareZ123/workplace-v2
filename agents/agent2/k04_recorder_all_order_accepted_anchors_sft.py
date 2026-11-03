"""Exhaustive accepted-field stage placements for 24 recorder writer orders.

Use ONLY 13 source-preindexed interior recorder CONTROL anchors to rank field
orders, independent of target-adjacent seq47 and the disputed printer coupon.
Allows arbitrary rejected draws between accepted fields, but rejection-range
tests are deferred: these are NECESSARY code-feasibility conditions.
"""
from itertools import combinations, permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent2"))
sys.path.insert(0, str(ROOT / "agents" / "agent47"))
from k04_p951_symbolic_basis import source, get, temper
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_conditional_onebit_parity_sft import PATH, joint_basis
from k04_seq47_event_aux_joint_sft import recorder_metadata, ANCHORS
from k04_seq47_exact_joint_reject_sft import State

FIELD_N = {"E": 6, "L": 3, "A": 13}


def accepted_code(observed, field):
    event, latch, aux = observed
    return {"E": event - 1, "L": latch, "A": aux - 2000}[field]


def count_accepted_placements(state, vectors, observed, prev, pos, nxt, order):
    """Count source-GF2-compatible full original codeword triplets."""
    n_before = order.index("C")
    before = range(prev + 1, pos)
    after = range(pos + 1, nxt)
    if len(before) < n_before or len(after) < 3 - n_before:
        return 0, None
    fields = [ch for ch in order if ch != "C"]
    values = {field: accepted_code(observed, field) for field in fields}
    cached = {}
    def equations(stage, field):
        key = stage,field
        if key not in cached:
            width = FIELD_N[field]
            code = values[field]
            cached[key] = tuple(
                (vector, (code >> bit) & 1)
                for bit,vector in enumerate(temper(get(vectors,stage))[32-width:])
            )
        return cached[key]

    count = 0
    witness = None
    for pre in combinations(before, n_before):
        for post in combinations(after, 3 - n_before):
            times = pre + post
            additions = []
            compatible = True
            for stage,field in zip(times,fields):
                inserted = state.push(equations(stage,field))
                if inserted is None:
                    compatible = False
                    break
                additions.append(inserted)
            if compatible:
                count += 1
                if witness is None:
                    witness = tuple(zip(fields,times))
            for inserted in reversed(additions):
                state.pop(inserted)
    return count, witness


def main():
    printer,vectors=source(ROOT/"resources")
    assert printer.rank==15365
    controls=recorder_controls()
    meta=recorder_metadata()
    model=joint_basis(printer,vectors,controls,PATH)
    assert model.rank==16663
    index={seq:i for i,(seq,_) in enumerate(PATH)}
    anchors=[seq for seq,_ in PATH[1:-1] if seq in ANCHORS]
    assert len(anchors)==13
    orders=["".join(x) for x in permutations("ELCA")]
    observed={}
    summary=[]
    for order in orders:
        count=0
        total=0
        misses=[]
        wins={}
        for seq in anchors:
            i=index[seq]
            _,pos=PATH[i]
            prev=PATH[i-1][1]
            nxt=PATH[i+1][1]
            n,w=count_accepted_placements(State(model),vectors,meta[seq],prev,pos,nxt,order)
            if n:
                count+=1
                total+=n
                wins[seq]=w
            else:misses.append(seq)
        summary.append((count,total,order,misses,wins))
        print("ORDER",order,"anchor_supported",count,"of",len(anchors),
              "accepted_placement_count",total,"misses",misses,flush=True)
    summary.sort(key=lambda x:(x[0],x[1]),reverse=True)
    print("TOP_FIVE",[(o,c,n) for c,n,o,_,_ in summary[:5]],flush=True)
    # Validate stage alternatives only after ranking source-anchored orders;
    # preserve ties and provide all four possibilities, never select on K04.
    chosen=[row for row in summary if row[0]==summary[0][0]]
    print("HIGHEST_ANCHOR_SUPPORT_ORDERS",[o for _,_,o,_,_ in chosen],flush=True)
    i=index[47]
    for _,_,order,_,_ in chosen:
        candidates=[]
        for stage in (-523,-522,-521,-520):
            n,w=count_accepted_placements(
                State(joint_basis(printer,vectors,controls,
                    tuple((seq,stage if seq==47 else pos) for seq,pos in PATH))),
                vectors,meta[47],PATH[i-1][1],stage,PATH[i+1][1],order)
            candidates.append((stage,n,w))
        print("SEQ47_OUT_OF_SAMPLE",order,candidates,flush=True)
    print("Original target K04 and K08 remain unresolved; sampler order unproven.")


if __name__=="__main__":
    main()
