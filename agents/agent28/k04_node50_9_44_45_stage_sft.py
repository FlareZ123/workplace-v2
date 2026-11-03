"""Source-only p951 printer->recorder heldout metadata across seq9/44/45.

Run: python agents/agent28/k04_node50_9_44_45_stage_sft.py
Selected ACK2, route mask, commitments and verifier are untouched.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import struct
import sys
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"agent49"))
from k04_p951_symbolic_basis import source,get,temper,untemper
ROOT=Path(__file__).resolve().parents[2]/"resources"
REC_HASH="5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"

def word(b,s,p,native=True):
    expressions=get(s,p) if native else temper(get(s,p))
    v=m=0
    for j,expr in enumerate(expressions):
        bit=b.predict(expr)
        if bit is not None:
            v|=bit<<j
            m|=1<<j
    return v,m

def high(b,s,p,k):
    v,m=word(b,s,p,False)
    return v>>(32-k),m>>(32-k)

def original_recorder():
    raw=(ROOT/"evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_HASH
    out={}
    for i in range(88):
        start=16+i*24
        ts,node,event,latch,seq,ctrl,aux,crc=struct.unpack_from(
            "<IHBBI4sII",raw,start)
        if node==50:
            assert zlib.crc32(raw[start:start+20])==crc
            out[seq]=(ts,event,latch,untemper(int.from_bytes(ctrl,"little")),aux)
    assert len(out)==72
    return out

def main():
    b,s=source(ROOT)
    assert b.rank==15365
    records=original_recorder()
    # Use only original CONTROL words to place these records in the
    # printer-only model. Hold back recorder AUX/event/latch/timestamp.
    selected={}
    for seq in (9,44,45):
        control=records[seq][3]
        possible=[]
        for p in range(-1100,-1):
            value,mask=word(b,s,p)
            if mask.bit_count()>=16 and ((control^value)&mask)==0:
                possible.append((p,mask.bit_count()))
        assert len(possible)==1,(seq,possible)
        selected[seq]=possible[0][0]
    assert selected=={9:-793,44:-545,45:-540}
    checks=[
      (9,"latch",-794,3,records[9][2],1),
      (9,"aux",-792,13,records[9][4]-2000,350),
      (44,"event",-547,6,records[44][1]-1,27),
      (44,"latch",-546,3,records[44][2],2),
      (44,"aux",-544,13,records[44][4]-2000,5700),
      (45,"timestamp",-543,9,records[45][0]-1791061742,217),
      (45,"event",-542,6,records[45][1]-1,25),
      (45,"latch",-541,3,records[45][2],0),
    ]
    fixed=0
    for seq,kind,pos,k,observed,expected in checks:
        value,mask=high(b,s,pos,k)
        assert observed==expected,(seq,kind,observed)
        assert mask==(1<<k)-1,(seq,kind,mask)
        assert value==observed,(seq,kind,value,observed)
        fixed+=k
    assert fixed==56
    print("PASS 56/56 high-bit source predictions, 3 control-selected records")
    print("seq9 latch1 AUX2350; seq44 event28 latch2 AUX7700")
    print("seq45 timestamp epoch+217 event26 latch0")
    print("CAUTION stage/epoch/producer not yet historically authenticated")
    print("K04 new independently authenticated selected bits 0, K08 words 0")

if __name__=="__main__":main()
