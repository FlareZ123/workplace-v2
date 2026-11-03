"""H-17 original node50 metadata-value-dependent hidden draw stage.

Read-only, selected coupon/commitment withheld. Python 3 standard library.
Run: python agents/agent18/k04_recorder_value_gap_sft.py
"""
from collections import Counter
from functools import lru_cache
from itertools import permutations, product
from pathlib import Path
import importlib.util

SPEC=importlib.util.spec_from_file_location('parent',Path(__file__).with_name('k04_recorder_alt_stage_sft.py'))
s=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)
FIELDS=('ts','event','latch','ctrl','aux')
RULES=('none','prev_event','next_event','prev_latch','next_latch','prev_aux','next_aux','prev_ts','next_ts','seq',
       'prev_event_div10','next_event_div10','prev_aux_div1000','next_aux_div1000')

def gap(rule,seq):
    before,after=s.records[seq],s.records[seq+1]
    if rule=='none':return 0
    if rule=='seq':return seq&3
    row=before if rule.startswith('prev') else after
    if rule.endswith('div10'):return row['event']//10
    if rule.endswith('div1000'):return row['aux']//1000
    return row[rule.split('_')[1]]&3

@lru_cache(None)
def accepted(pos,field,value,mode,event40):
    if field!='event' or not event40:return s.consumes(pos,field,value,mode,2)
    assert mode=='range'
    n,bits=40,6
    assert 0<=value<n
    lengths=[]
    for k in range(1,13):
        valid=True
        for j in range(k):
            observed=s.observed(pos+j)
            if observed is None:continue
            if j+1==k:
                if not any(x>>(32-bits)==value for x in observed):valid=False;break
            elif not any(x>>(32-bits)>=n for x in observed):valid=False;break
        if valid:lengths.append(k)
    return tuple(lengths)

@lru_cache(None)
def successors(seq,start,order,tsmode,latchmode,event40,gaprule):
    before,after=s.records[seq],s.records[seq+1]
    mid=order.index('ctrl')
    fields=[(f,before[f]) for f in order[mid+1:]]+[(f,after[f]) for f in order[:mid]]
    active={start+1}
    for f,value in fields:
        mode={'ts':tsmode,'event':'range','latch':latchmode,'aux':'range'}[f]
        active={p+length for p in active for length in accepted(p,f,value,mode,event40)}
        if not active:return ()
    result=[]
    for p in active:
        p+=gap(gaprule,seq)
        if not -1100<=p<0 or p<=start:continue
        at=s.offset+p
        if ((after['ctrl']^s.values[at]) & s.known[at]) == 0:result.append(p)
    return tuple(sorted(set(result)))

def reaches(start,end,origin,model,anchors):
    positions={origin}
    last=start
    for seq in range(start,end):
        positions={q for p in positions for q in successors(seq,p,*model) if q<=anchors[end]}
        if seq+1 in anchors: positions &= {anchors[seq+1]}
        if not positions:break
        last=seq+1
    return last,positions

def main():
    s.seeded_control()
    tested=0;early=0;late=Counter();hits=[]
    for order,ts,latch,e40,rule in product(permutations(FIELDS),('range','latent1','latent2'),
                                            ('range','getbits2'),(False,True),RULES):
        model=(order,ts,latch,e40,rule)
        tested+=1
        reached,possible=reaches(9,13,-793,model,{12:-775,13:-769})
        if reached!=13 or -769 not in possible:continue
        early+=1
        reached,possible=reaches(45,70,-540,model,{61:-417,63:-397,64:-390,70:-339})
        late[reached]+=1
        if -339 in possible:hits.append(model)
    print('FULLY_DEFINED_VALUE_DEPENDENT_EMITTERS',tested)
    print('FITTING_INDEPENDENT_SEQ9_12_13_ORIGINAL_CONTROLS',early)
    print('REACHING_INDEPENDENT_SEQ70_ORIGINAL_CONTROL',len(hits))
    print('MAXIMUM_LATE_PREFIX',max(late),'LATE_PREFIX_HISTOGRAM',sorted(late.items()))
    assert tested==20160 and early==996 and not hits and max(late)==60
    print('PASS: original coupon and K04/K08 commitments untouched')

if __name__=='__main__':main()
