"""H-17 K04 p951 stage metadata-writer SFT; original selected row129 withheld."""
from __future__ import annotations
import hashlib,itertools,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
import k04_p951_symbolic_basis as mt

SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ACCEPT=set(range(9))
REJECT=set(range(9,16))
CLASSES=("LABEL","RECOVER","STORES")
DESTS=("bench","desk","store")

def nibble_domain(bits):
    return {v for v in range(16) if all(b is None or b==((v>>j)&1) for j,b in enumerate(bits))}

def double_accepted(window,observed):
    states={(0,None)}
    for domain in window:
        new=set()
        for count,label in states:
            if domain&REJECT:new.add((count,label))
            if count<2:
                for code in domain&ACCEPT:
                    new.add((count+1,code if count==observed else label))
        states=new
    return {label for count,label in states if count==2 and label is not None}

def split_possible(window,c,d):
    return any(c in a and d in b for i,a in enumerate(window) for j,b in enumerate(window) if i!=j)

def main():
    raw=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA
    labels=[tuple(s.decode() for s in pair) for pair in re.findall(rb"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)",raw)]
    assert len(labels)==len(mt.STARTS)==133 and labels[129]==("RECOVER","bench")
    assert set(labels[:128])==set(itertools.product(CLASSES,DESTS))
    basis,bank=mt.source(ROOT)
    assert basis.rank==15365
    windows=[]
    for row in range(127):
        window=[]
        for stage in range(mt.STARTS[row]+4,mt.STARTS[row+1]):
            native_bits=mt.temper(mt.get(bank,stage))
            window.append(nibble_domain(tuple(basis.predict(native_bits[j]) for j in (28,29,30,31))))
        assert len(window)>=2
        windows.append(window)
    assert nibble_domain((1,None,0,1))=={9,11}

    single=[set().union(*(d&ACCEPT for d in w)) for w in windows]
    def empties(candidates,offset):
        domains={}
        for i,opts in enumerate(candidates):
            domains.setdefault(labels[i+offset],set(ACCEPT)).intersection_update(opts)
        assert len(domains)==9
        return sum(not d for d in domains.values())
    single_empty=[empties(single,s) for s in (0,1)]
    assert single_empty==[3,4],single_empty

    assert double_accepted([{15},{2},{9},{7}],0)=={2}
    assert double_accepted([{15},{2},{9},{7}],1)=={7}
    assert double_accepted([{2},{15}],0)==set()
    double=[[double_accepted(w,k) for w in windows] for k in (0,1)]
    impossible=[sum(not x for x in candidates) for candidates in double]
    assert impossible==[14,14],impossible
    double_empty=[empties(x,s) for x in double for s in (0,1)]
    assert double_empty==[9,8,9,9],double_empty

    twoword=[[{v>>2 for v in domain} for domain in w] for w in windows]
    assert split_possible([{0,2},{3},{1}],2,1)
    assert not split_possible([{0},{1},{3}],2,1)
    perms=list(itertools.permutations(range(3)))
    best=[]
    for cs,ds in itertools.product((0,1),repeat=2):
        score=max(sum(split_possible(twoword[r],cp[CLASSES.index(labels[r+cs][0])],dp[DESTS.index(labels[r+ds][1])]) for r in range(127))
                  for cp,dp in itertools.product(perms,repeat=2))
        best.append(score)
    assert best==[114,112,116,112],best
    print(json.dumps({"spool_sha256":SHA,"source_rank":basis.rank,"intact_packets":132,"ordinary_gaps":127,
        "joint9_one_draw_empty_cells_current_next":single_empty,
        "joint9_two_draw_impossible_gaps":impossible,
        "joint9_two_draw_empty_cells_first_second_current_next":double_empty,
        "two_threeway_any_distinct_stage_best_gaps":best,
        "synthetic_controls":"PASS","selected_K04_coupon_bits":0,
        "verifier":"not queried; no complete coupon constructed"},indent=2))

if __name__=="__main__":main()
