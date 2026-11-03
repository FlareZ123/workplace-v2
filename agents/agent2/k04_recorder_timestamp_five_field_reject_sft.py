"""Original-source five-field timestamp/event/latch/CONTROL/AUX MT sampler.

Extends Agent49's source-only seq44→45 timestamp217, event25, latch0,
CONTROL -540 sequence to all 13 independently indexed recorder controls.
Each field uses its natural CPython getrandbits-sized randrange sampler.
Selected printer row129, K04 hashes, route mask, K08 never accessed.
"""
from pathlib import Path
import hashlib,struct,sys,zlib
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents"/"agent49"))
sys.path.insert(0,str(ROOT/"agents"/"agent2"))
sys.path.insert(0,str(ROOT/"agents"/"agent47"))
from k04_p951_symbolic_basis import source
from k04_conditional_onebit_parity_sft import PATH,joint_basis
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_seq47_event_aux_joint_sft import recorder_metadata,ANCHORS,REC_HASH
from k04_seq47_exact_joint_reject_sft import accepted,REJECT,patterns,solvable

TIMESTAMP_BASE=1791061742
TIMESTAMP_REJECT=patterns(9,400)
ALL_REJECT={9:TIMESTAMP_REJECT,**REJECT}


def timestamps():
    raw=(ROOT/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_HASH
    data={}
    for idx in range(88):
        entry=raw[16+24*idx:16+24*(idx+1)]
        ts,node,ev,latch,seq,c,aux,crc=struct.unpack("<IHBBI4sII",entry)
        if node==50:
            assert zlib.crc32(entry[:20])==crc
            code=ts-TIMESTAMP_BASE
            assert 0<=code<400,(seq,code)
            data[seq]=code
    assert set(data)==set(range(72))
    assert data[45]==217 and data[47]==313
    return data


def history(pos,prev,nxt,ts_code,observed,tr,er,lr,ar):
    event,latch,aux=observed
    la=pos-1
    ea=la-lr-1
    ta=ea-er-1
    tf=ta-tr
    aa=pos+ar+1
    if tf<=prev or aa>=nxt:return None
    rows=[]
    for field,start,end,width,threshold,code in (
        ("T",tf,ta,9,400,ts_code),
        ("E",ea-er,ea,6,39,event-1),
        ("L",la-lr,la,3,4,latch),
        ("A",pos+1,aa,13,6000,aux-2000),
    ):
        rows.extend((at,width,ALL_REJECT[width]) for at in range(start,end))
        rows.append((end,width,accepted(width,code)))
    assert len(rows)==4+tr+er+lr+ar
    return rows


def sample(model,vectors,pos,prev,nxt,ts_code,observed,max_reject=3):
    good=[]
    n=0
    for tr in range(max_reject+1):
        for er in range(max_reject+1):
            for lr in range(max_reject+1):
                for ar in range(max_reject+1):
                    rows=history(pos,prev,nxt,ts_code,observed,tr,er,lr,ar)
                    if rows is None:continue
                    n+=1
                    witness,_=solvable(model,vectors,rows)
                    if witness is not None:good.append((tr,er,lr,ar))
    return good,n


def main():
    printer,vectors=source(ROOT/"resources")
    assert printer.rank==15365
    ctrl=recorder_controls()
    metadata=recorder_metadata()
    ts=timestamps()
    model=joint_basis(printer,vectors,ctrl,PATH)
    assert model.rank==16663
    idx={seq:i for i,(seq,_) in enumerate(PATH)}
    anchor=[seq for seq,_ in PATH[1:-1] if seq in ANCHORS]
    good=[]
    for seq in anchor:
        i=idx[seq]; pos=PATH[i][1]
        histories,checks=sample(model,vectors,pos,PATH[i-1][1],
                                PATH[i+1][1],ts[seq],metadata[seq])
        if histories:good.append(seq)
        print("SOURCE_ANCHOR",seq,"stage",pos,"timestamp_code",ts[seq],
              "exact_histories",len(histories),"first",histories[:4],
              "checks",checks,flush=True)
    print("ANCHOR_SUMMARY",len(good),"of",len(anchor),"supported",good,flush=True)
    i=idx[47]
    for stage in (-523,-522,-521,-520):
        m=joint_basis(printer,vectors,ctrl,
             tuple((seq,stage if seq==47 else p) for seq,p in PATH))
        hs,n=sample(m,vectors,stage,PATH[i-1][1],PATH[i+1][1],
                    ts[47],metadata[47])
        print("SEQ47_FIVE_FIELD",stage,"feasible_histories",len(hs),
              "sample",hs[:10],"tested",n,flush=True)
    print("SOURCE_ONLY FIVE_FIELD MODEL; K04 K08 UNRESOLVED",flush=True)


if __name__=="__main__":
    main()
