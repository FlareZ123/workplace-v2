"""Finite five-field node50 source-only stage DP and seq46 falsifier.

python agents/agent28/k04_node50_five_record_dp_sft.py
The p951 printer model omits selected ESC-N ACK2, and this test never uses
K04/K08 commitments, source route mask, candidates, or a live facility.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
from k04_p951_symbolic_basis import source,get,temper,Basis
from k04_node50_9_44_45_stage_sft import original_recorder
from k04_node50_three_record_branch_sft import (
    add_control,add_high,fixed_top,target_residual_rank)

ROOT=Path(__file__).resolve().parents[2]/"resources"
b,states=source(ROOT)
observed=original_recorder()
r={seq:{"time":row[0]-1791061742,"event":row[1]-1,
        "latch":row[2],"control":row[3],"aux":row[4]-2000}
   for seq,row in observed.items()}
bounds={"time":400,"event":39,"latch":4,"aux":6000}
widths={key:bound.bit_length() for key,bound in bounds.items()}

def fit(index,field,value):
    if field=="control":
        exprs=get(states,index)
    else:
        exprs=temper(get(states,index))[32-widths[field]:]
    for j,expr in enumerate(exprs):
        fixed=b.predict(expr)
        if fixed is not None and fixed!=((value>>j)&1):
            return False
    return True

def can_reject(index,field):
    k=widths[field]
    value,mask=fixed_top(b,states,index,k)
    return (value|(((1<<k)-1)^mask))>=bounds[field]

def stages(seq,start,limit):
    paths=[(start,())]
    for field in ("time","event","latch","control","aux"):
        following=[]
        for index,history in paths:
            if field=="control":
                if index<=limit and fit(index,field,r[seq][field]):
                    following.append((index+1,history+((field,index,0),)))
            else:
                for rejects in range(9):
                    chosen=index+rejects
                    if chosen>limit:break
                    if all(can_reject(p,field) for p in range(index,chosen)):
                        if fit(chosen,field,r[seq][field]):
                            following.append((chosen+1,history+((field,chosen,rejects),)))
        paths=following
        if not paths:break
    return paths

def main():
    assert b.rank==15365 and target_residual_rank(b,states)==128
    assert fit(-568,"control",r[41]["control"])
    assert can_reject(-567,"aux") and not fit(-567,"aux",r[41]["aux"])
    assert fit(-566,"aux",r[41]["aux"])
    # Seq41 control is independently indexed -568. Its first AUX draw at
    # -567 is source-proven reject; second at -566 accepts original AUX.
    frontier=[(-565,())]
    for seq in (42,43,44):
        following=[]
        for start,history in frontier:
            for end,stage in stages(seq,start,-543):
                if seq==43 and stage[3][1]!=-552:continue
                if seq==44 and stage[3][1]!=-545:continue
                following.append((end,history+((seq,stage),)))
        frontier=following
    complete=[history for end,history in frontier if end==-543]
    assert len(complete)==9,len(complete)
    for chain in complete:
        model=Basis()
        model.rows=b.rows.copy()
        model.rank=b.rank
        for seq,index in ((41,-568),(45,-540)):
            add_control(model,states,index,r[seq]["control"])
        add_high(model,states,-566,13,r[41]["aux"])
        rejections=[]
        for seq,stage in chain:
            add_control(model,states,stage[3][1],r[seq]["control"])
            for field,index,skips in stage:
                if field!="control":
                    add_high(model,states,index,widths[field],r[seq][field])
                    rejections.extend((p,field) for p in range(index-skips,index))
        for field,index in (("time",-543),("event",-542),("latch",-541)):
            add_high(model,states,index,widths[field],r[45][field])
        assert model.rank-b.rank==76
        assert target_residual_rank(model,states)==128
        for index,field in rejections:
            k=widths[field]
            value,mask=fixed_top(model,states,index,k)
            assert (value|(((1<<k)-1)^mask))>=bounds[field]
    assert {chain[0][1][3][1] for chain in complete}=={-562}
    print("PASS 9 complete source-feasible stage histories, seq42 control -562")
    print("PASS each adds 76 independent equations, target free rank 128")
    # Exact global five-field order cannot cross seq45->46 immediately after
    # any original source-feasible AUX45 completion (even with 8 rejects/stage).
    exits=[]
    for index in (-539,-538,-537):
        if fit(index,"aux",r[45]["aux"]) and all(
            can_reject(p,"aux") for p in range(-539,index)):
            exits.append(index+1)
    assert exits==[-538,-537,-536]
    assert all(not stages(46,index,-414) for index in exits)
    print("PASS seq46 fails timestamp-first strict global stage after 45")
    print("No authenticated K04 selected bit or K08 final word")

if __name__=="__main__":
    main()
