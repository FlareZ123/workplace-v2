"""H-17 original-source node50 stage-order DP, selected K04 coupon withheld.

Run: python agents/agent44/k04_node50_opaque_stage_sft.py resources

Tests all 24 permutations of recorder EVENT/LATCH/CONTROL/AUX fields, and
120 permutations with 1..3 extra *unobserved* MT draws per record. The p951
printer-only index map is conditional, not a documented historical producer.
Only original unselected spool and CRC-valid node50 fields are ingested.
No K04/K08 acceptance, mask, selected ACK or verifier is opened.
"""
from collections import defaultdict
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import permutations
from pathlib import Path
import hashlib
import random
import struct
import sys
import zlib

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ANCHORS = {7:-810,12:-775,13:-769,24:-683,25:-677,41:-568,45:-540,70:-339}
WINDOWS = ((7,12),(12,13),(13,24),(24,25),(25,41),(41,45),(45,70))
FULL = 0xffffffff

def load_source():
    path = Path(__file__).resolve().parents[1] / "agent2/20261102_k04_multicarrier_p951_sft.py"
    spec = spec_from_file_location("p951_source", path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def read_node50(root, source):
    raw = (root/"evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    records={}
    for row in range(88):
        at=16+24*row
        ts,node,event,latch,seq,control,aux,crc = struct.unpack_from("<IHBBI4sII",raw,at)
        if node!=50:continue
        assert zlib.crc32(raw[at:at+20])==crc and 0<=seq<72
        records[seq]={"E":event-1,"L":latch,"A":aux-2000,
                      "C":source.untemper(int.from_bytes(control,"little")),"ts":ts}
    assert sorted(records)==list(range(72))
    return records

class Solver:
    def __init__(self,source,words,masks,offset,records,anchors):
        self.source,self.words,self.masks,self.offset=source,words,masks,offset
        self.records,self.anchors=records,anchors
        self.codes=lru_cache(None)(self._codes)
        self.sampler=lru_cache(None)(self.sampler)
        self.edges=lru_cache(None)(self._edges)

    def _codes(self,p,k):
        at=self.offset+p
        if at<0 or at>=len(self.words):return None
        mask=self.masks[at]
        if mask==FULL:
            return (self.source.temper(self.words[at])>>(32-k),)
        if mask==0x7fffffff:
            base=self.words[at]&mask
            return tuple(self.source.temper(base|(hi<<31))>>(32-k) for hi in (0,1))
        return None  # Low-rank masks deliberately treated as unconstrained.

    def possible(self,p,k,n,value=None):
        values=self.codes(p,k)
        if values is None:return True
        return any(v>=n for v in values) if value is None else value in values

    def sampler(self,field,seq,start,cap):
        k,n={"E":(6,39),"L":(3,4),"A":(13,6000)}[field]
        result=[]
        for draws in range(1,cap+1):
            end=start+draws-1
            if self.possible(end,k,n,self.records[seq][field]) and all(
                    self.possible(p,k,n) for p in range(start,end)):
                result.append(end+1)
        return result

    def compatible(self,seq,p):
        at=self.offset+p
        return 0<=at<len(self.words) and not (
            (self.records[seq]["C"]^self.words[at]) & self.masks[at])

    def _edges(self,order,seq,control,cap,extra,limit):
        ci=order.index("C")
        stages=[(field,seq) for field in order[ci+1:]]
        stages.extend((field,seq+1) for field in order[:ci])
        states={control+1:1}
        for field,record in stages:
            nxt=defaultdict(int)
            for start,count in states.items():
                candidates=(range(start+1,start+extra+1) if field=="X"
                            else self.sampler(field,record,start,cap))
                for p in candidates:
                    if p<=limit:nxt[p]+=count
            states=nxt
            if not states:break
        return tuple((p,n) for p,n in states.items() if self.compatible(seq+1,p))

    def interval(self,order,start,end,cap=8,extra=1):
        states={self.anchors[start]:1}
        for seq in range(start,end):
            nxt=defaultdict(int)
            for control,n in states.items():
                for q,m in self.edges(order,seq,control,cap,extra,self.anchors[end]):
                    if seq+1 in self.anchors and q!=self.anchors[seq+1]:continue
                    nxt[q]+=n*m
            states=nxt
            if not states:return False,seq+1
        return self.anchors[end] in states,end

class CapturingRandom(random.Random):
    def __init__(self,seed):
        super().__init__(seed)
        self.words=[]
    def getrandbits(self,k):
        assert k in (3,6,13,32)
        x=super().getrandbits(32)
        self.words.append(x)
        return x>>(32-k)

def synthetic(source):
    for order in ("EXLCA","ELCA","XLCAE"):
        rng=CapturingRandom(20261102)
        rows={}; positions={}
        for seq in range(6):
            row={}
            for field in order:
                if field=="E":row[field]=rng.randrange(39)
                elif field=="L":row[field]=rng.randrange(4)
                elif field=="A":row[field]=rng.randrange(6000)
                elif field=="C":
                    positions[seq]=len(rng.words)
                    row[field]=source.untemper(rng.getrandbits(32))
                else:rng.getrandbits(32)
            rows[seq]=row
        state=[source.untemper(x) for x in rng.words]
        s=Solver(source,state,[FULL]*len(state),0,rows,positions)
        assert s.interval(tuple(order),0,5)==(True,5)
    print("PASS synthetic seeded MT and CPython sampler stages")

def main(root):
    source=load_source()
    synthetic(source)
    spool=(root/"evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest()==SPOOL_SHA
    words,masks,offset=source.source_closure(root)
    records=read_node50(root,source)
    solver=Solver(source,words,masks,offset,records,ANCHORS)
    assert all(solver.compatible(seq,p) for seq,p in ANCHORS.items())
    for hidden,extra in ((False,1),(True,1),(True,2),(True,3)):
        family=tuple(permutations("ELCAX" if hidden else "ELCA"))
        winners=[];six=[]
        for order in family:
            passes=sum(solver.interval(order,a,b)[0] if not hidden else
                       solver.interval(order,a,b,extra=extra)[0] for a,b in WINDOWS)
            if passes==7:winners.append(order)
            if passes==6:six.append("".join(order))
        assert not winners and len(family)==(120 if hidden else 24)
        print("hidden",hidden,"max_extra_draws",extra,"orders",len(family),
              "all_windows",len(winners),"six_of_seven",len(six))
        if hidden and extra==1:
            assert sorted(six)==["EXLCA","LCAEX","XLCAE"]
    # EXLCA's strongest six-window model consumes an unobserved timestamp
    # draw immediately before seq24's LATCH. Original printer word -685
    # has high nine bits 58 (an accepted Python randrange(400) code), yet
    # the unmodified seq24 timestamp is 21:15:21 (offset 381 from 21:09).
    assert records[24]["L"]==1 and ANCHORS[24]==-683
    assert solver.codes(-684,3)==(1,) and solver.codes(-685,3)==(0,)
    assert solver.codes(-685,9)==(58,)
    assert records[24]["ts"]-1791061740==381
    print("EXLCA timestamp counterexample: accepts code58, original offset381")
    assert [masks[offset+951+j] for j in range(4)]==[0]*4
    print("K04 original selected bits fixed: 0/128; no new REC8 acceptance")

if __name__=="__main__":
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources")
