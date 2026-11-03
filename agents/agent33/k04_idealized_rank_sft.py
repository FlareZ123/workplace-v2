"""K04 stage-source rank ceiling. Run from repo root with Python 3."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent49"))
from k04_p951_symbolic_basis import Basis,source,get,temper
ANCHORS={7:-810,9:-793,12:-775,13:-769,14:-759,24:-683,
25:-677,41:-568,43:-552,44:-545,45:-540,61:-417,63:-397,64:-390,70:-339}
FIELDS=((-3,9),(-2,6),(-1,3),(0,32),(1,13))
def main():
    base,words=source(ROOT/"resources")
    assert base.rank==15365
    stages=[]
    for q in range(72):
        before=max((x for x in ANCHORS if x<=q),default=None)
        after=min((x for x in ANCHORS if x>=q),default=None)
        if before is None:p=ANCHORS[after]-8*(after-q)
        elif after is None:p=ANCHORS[before]+8*(q-before)
        elif before==after:p=ANCHORS[before]
        else:p=round(ANCHORS[before]+(ANCHORS[after]-ANCHORS[before])*
                      (q-before)/(after-before))
        stages.append(p)
    assert all(stages[i]<stages[i+1] for i in range(71))
    vectors={j:temper(get(words,j)) for j in set(
        list(range(-950,-250))+list(range(-324,-312))+list(range(-157,-93)))}
    def add_field(b,index,width):
        for equation in vectors[index][-width:]:b.insert(equation,0)
    def report(node49,transfers):
        b=Basis()
        b.rows={p:(v,0) for p,(v,_) in base.rows.items()}
        b.rank=base.rank
        for p in stages:
            for delta,width in FIELDS:add_field(b,p+delta,width)
        if node49:
            for p in range(-324,-312):add_field(b,p,32)
        if transfers:
            for start in (-157,-141,-125,-109):
                for p in range(start,start+16):add_field(b,p,16)
        original_rank=b.rank
        for p in range(951,955):
            for equation in get(words,p):b.insert(equation,0)
        return original_rank,b.rank-original_rank
    values=[report(False,False),report(True,False),report(True,True)]
    assert values==[(17154,128),(17232,128),(17589,126)],values
    print("Optimistic 72-recorder source rank and K04 residual:",values)
    print("Source-authenticated K04 selected bits: zero")
if __name__=="__main__":main()
