"""Exact H17 seven-recorder native-stage path screen; original selected ACK withheld.
Run from repository root: python agents/agent6/k04_node50_late_exact_stage_paths_sft.py
The p951 shared-MT and 15 indexed node50 anchors are hypotheses, not an
originally authenticated printer/recorder producer. Original evidence is read only.
"""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper, untemper

REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ANCHORS = {7:-810,9:-793,12:-775,13:-769,14:-759,24:-683,25:-677,41:-568,
           43:-552,44:-545,45:-540,61:-417,63:-397,64:-390,70:-339}
TRUE_CONTROL_STAGES = (-388,-385,-381,-353,-347)

def recorder():
    raw=(ROOT/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_SHA
    assert raw[:8]==b"TRP2DUMP" and len(raw)==16+88*24
    rows={}
    for i in range(88):
        line=raw[16+i*24:16+(i+1)*24]
        ts,node,event,latch,seq=struct.unpack_from("<IHBBI",line)
        ctrl,aux,crc=struct.unpack_from("<III",line,12)
        if node==50:
            assert zlib.crc32(line[:20])==crc
            rows[seq]={"control":ctrl,"aux":aux,"event":event,"latch":latch,"time":ts}
    assert set(rows)==set(range(72))
    return rows

def predicted(b,s,stage):
    mask=value=0
    for bit,eq in enumerate(temper(get(s,stage))):
        k=b.predict(eq)
        if k is not None:
            mask |= 1<<bit
            value |= k<<bit
    return mask,value

def path_candidates(known,controls,gap):
    allowed={}
    for seq,ctrl in zip(range(65,70),controls):
        allowed[seq]=[stage for stage,(mask,value) in known.items()
                      if ((ctrl^value)&mask)==0]
    out=[]
    def visit(seq,last,path):
        if seq==70:
            if -339-last>=gap:out.append(tuple(path))
            return
        for pos in allowed[seq]:
            if pos < last+gap:continue
            if pos+gap*(70-seq)>-339:break
            visit(seq+1,pos,[*path,pos])
    visit(65,-390,[])
    return out

def jointly_consistent(b,s,controls,stages):
    test=Basis()
    test.rows=b.rows.copy()
    test.rank=b.rank
    for ctrl,stage in zip(controls,stages):
        native=untemper(ctrl)
        for bit,eq in enumerate(get(s,stage)):
            try:test.insert(eq,(native>>bit)&1)
            except AssertionError:return None
    return test

def target_rank(b,s):
    hom=Basis()
    hom.rows={p:(eq,0) for p,(eq,_) in b.rows.items()}
    hom.rank=b.rank
    for stage in range(951,955):
        for eq in get(s,stage):hom.insert(eq,0)
    return hom.rank-b.rank

def actual_tempered(b,s,stage):
    # A source-consistent 19,968-bit symbolic state with free coordinates zero.
    state=0
    for pivot in sorted(b.rows):
        eq,rhs=b.rows[pivot]
        bit=rhs^((state&eq).bit_count()&1)
        if bit:state|=1<<pivot
    assert all(((state&eq).bit_count()&1)==rhs for eq,rhs in b.rows.values())
    native=sum((((state&eq).bit_count()&1)<<bit) for bit,eq in enumerate(get(s,stage)))
    out=native^(native>>11)
    out^=(out<<7)&0x9d2c5680
    out^=(out<<15)&0xefc60000
    out^=out>>18
    return out&0xffffffff

def main():
    rows=recorder()
    b,s=source(ROOT/"resources")
    assert b.rank==15365
    for seq,stage in ANCHORS.items():
        native=untemper(rows[seq]["control"])
        for bit,eq in enumerate(get(s,stage)):
            b.insert(eq,(native>>bit)&1)
    assert b.rank==15375

    known={p:predicted(b,s,p) for p in range(-389,-339)}
    originals=[rows[seq]["control"] for seq in range(65,70)]
    clear_sites=[p for p,(mask,_) in known.items() if mask==0]
    assert clear_sites==[-389,-388,-387,-385,-381,-380,-370,-353,-352,-347,-343,-342]
    checks={}
    all_good=[]
    for gap,expected_paths,expected_good in ((4,20,0),(3,64,0),(2,168,8),(1,792,46)):
        proposals=path_candidates(known,originals,gap)
        assert len(proposals)==expected_paths,(gap,len(proposals))
        matches=[]
        for path in proposals:
            joint=jointly_consistent(b,s,originals,path)
            if joint is not None:matches.append((path,joint))
        assert len(matches)==expected_good,(gap,len(matches))
        checks[gap]={"individually_compatible_paths":len(proposals),
                     "jointly_consistent_paths":len(matches)}
        if gap==2:all_good=matches

    exact_paths={path for path,_ in all_good}
    assert exact_paths=={
        (a,-385,-381,b0,c)
        for a in (-388,-387) for b0 in (-353,-352) for c in (-347,-343)
    }
    stage_gaps=[]
    ranks=[]
    for path,joint in all_good:
        consecutive=(-390,*path,-339)
        stage_gaps.append(tuple(y-x for x,y in zip(consecutive,consecutive[1:])))
        ranks.append(joint.rank)
        assert target_rank(joint,s)==128

    # Plant source-consistent controls from a genuine symbolic-MT state
    # satisfying all original printer and anchored-recorder equations.
    synthetic=[actual_tempered(b,s,p) for p in TRUE_CONTROL_STAGES]
    assert all(actual_tempered(b,s,ANCHORS[seq])==rows[seq]["control"] for seq in ANCHORS)
    assert TRUE_CONTROL_STAGES in path_candidates(known,synthetic,2)
    assert jointly_consistent(b,s,synthetic,TRUE_CONTROL_STAGES) is not None

    print(json.dumps({
        "printer_source_rank":15365,
        "source_plus_15_control_rank":15375,
        "conditional_model":"p951 native MT19937, fixed 15 node50 control stage anchors",
        "original_source_gap_screens":checks,
        "eight_joint_paths":[list(path) for path,_ in all_good],
        "eight_joint_stage_gaps":[list(x) for x in stage_gaps],
        "eight_joint_ranks":ranks,
        "largest_necessary_gap":28,
        "target_coupon_unknown_bits":128,
        "source_consistent_state_positive":"PASS",
        "original_K04_and_K08":"MISSING",
        "original_combined":"INCOMPLETE"
    },sort_keys=True))

if __name__=="__main__":main()
