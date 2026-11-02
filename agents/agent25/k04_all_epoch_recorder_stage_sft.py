"""K04 p951 Node50 seq46-to47: all-epoch four-field CPython stage exclusion.

Run: python agents/agent25/k04_all_epoch_recorder_stage_sft.py
Original intact printer and TRP2 controls; selected printer ACK, XOR mask,
K04/K08 commitments, candidate and verifier excluded from source inference.
"""
from functools import lru_cache
from itertools import permutations
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "original_joint_stage", HERE / "k04_seq46_47_joint_stage_sft.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ROOT = HERE.parents[1] / "resources"
ALL = (1 << 400) - 1

def epoch_options(basis, symbolic, start, end, aux, event, latch):
    fields = {"aux":(6000,aux-2000),
              "event":(39,event-1),"latch":(4,latch)}
    can = {}
    for name,(limit,value) in fields.items():
        for pos in range(start+1,end):
            can[name,pos,True] = m.possible(basis,symbolic,pos,limit,value)
            can[name,pos,False] = m.possible(basis,symbolic,pos,limit,None)
    for pos in range(start+1,end):
        n,k = 400,400 .bit_length()
        predictions = [basis.predict(expr)
                       for expr in m.temper(m.get(symbolic,pos))[32-k:]]
        allowed=0
        reject=False
        for value in range(1 << k):
            if any(got is not None and got != ((value>>bit)&1)
                   for bit,got in enumerate(predictions)):
                continue
            if value < n:allowed |= 1<<value
            else:reject=True
        can["time",pos,True] = allowed
        can["time",pos,False] = reject
    result={}
    for order in permutations(("aux","time","event","latch")):
        @lru_cache(None)
        def solve(which,position):
            if which==4:return ALL
            name=order[which]
            outcome=0
            for lo in range(position,end):
                for hi in range(lo,end):
                    if any(not can[name,at,False] for at in range(lo,hi)):
                        continue
                    options=(can[name,hi,True] if name=="time"
                             else ALL if can[name,hi,True] else 0)
                    if options:
                        outcome |= options & solve(which+1,hi+1)
            return outcome
        result[order]=solve(0,start+1)
    return result

def main():
    basis,symbolic=m.source(ROOT)
    assert basis.rank==15365
    records=m.recorder_controls()
    next46=m.insert_control(basis,symbolic,-531,records[46])
    assert next46 is not None and next46.rank-basis.rank == 32
    joint=m.insert_control(next46,symbolic,-523,records[47])
    assert joint is not None and joint.rank-basis.rank == 63
    # With completely unknown state, all 400 timestamp codes are possible
    # in each interval; this verifies stage order/spacing machinery itself.
    for start,end,aux,event,latch in ((-540,-531,5088,6,1),
                                      (-531,-523,3111,4,1)):
        empty=m.Basis()
        optimistic=epoch_options(empty,symbolic,start,end,aux,event,latch)
        assert len(optimistic)==24 and all(x==ALL for x in optimistic.values())
    for name,model in (("printer-only",basis),("seq46+47",joint)):
        first=epoch_options(model,symbolic,-540,-531,5088,6,1)
        second=epoch_options(model,symbolic,-531,-523,3111,4,1)
        assert sum(v.bit_count() for v in first.values())==516
        assert all(v==0 for v in second.values())
        # Original UTC: seq46 at21:11:52 => 172 s after21:09:00;
        # seq47 at21:14:15 => 315 s, difference 143 s.
        shared={order:(first[order]&(second[order]>>143))
                for order in first}
        assert not any(shared.values())
        # Earlier locally studied baseline epoch +0 gives zero each.
        assert not any(v & (1<<172) for v in first.values())
        assert not any(v & (1<<315) for v in second.values())
        # Preserve Agent49's earlier +2-second epoch possibility:
        # six first-interval orders fit; none for the second interval.
        assert sum(bool(v&(1<<170)) for v in first.values())==6
        assert not any(v & (1<<313) for v in second.values())
        print(name, "45->46 code/order combos",516,
              "46->47 code/order combos",0,"common epoch/order",0)
    print("PASS: no four-field original recorder stage for seq46->47 at ANY epoch")
    print("Historical producer and exact control indices still hypotheses; K04 unknown")

if __name__ == "__main__":
    main()
