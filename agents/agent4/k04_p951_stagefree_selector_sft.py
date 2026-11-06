"""Source-blind printer stage selector falsifier for p951 native MT.

Withhold each of 127 ordinary packets (and always selected row129), fit all
other intact source packets, then select a source-stage between neighbors
that minimizes the missing complete native rank. Check exact full-value
predictions only after selecting the output stage.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"agents/agent49"))
from k04_p951_symbolic_basis import STARTS,Basis, get, untemper,words

SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U=0xffffffff

def temper(y:int)->int:
    y^=y>>11
    y^=(y<<7)&0x9d2c5680
    y^=(y<<15)&0xefc60000
    y^=y>>18
    return y&U

def candidate_rank(basis:Basis,symbolic:list,q:int)->int:
    pivots={p:v for p,(v,_) in basis.rows.items()}
    delta=0
    for lane in range(4):
        for vec in get(symbolic,q+lane):
            while vec:
                p=vec.bit_length()-1
                old=pivots.get(p)
                if old is None:
                    pivots[p]=vec
                    delta+=1
                    break
                vec^=old
    return delta

def predicted_packet(basis:Basis,symbolic:list,q:int)->bytes:
    bits=[basis.predict(v) for lane in range(4) for v in get(symbolic,q+lane)]
    assert all(bit is not None for bit in bits)
    return b"".join(temper(sum(bits[32*lane+j]<<j for j in range(32))).to_bytes(4,"little")
                    for lane in range(4))

def main()->None:
    source=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(source).hexdigest()==SHA
    packets=[bytes.fromhex(h.decode()) for h in re.findall(rb"PAYLOAD=([0-9A-F]{32})",source)]
    assert len(packets)==len(STARTS)==133
    packets[129]=b""  # disputed physical/copy never fitted
    symbolic=words()
    observations={}
    for i,pkt in enumerate(packets):
        if i==129: continue
        rows=[]
        for lane in range(4):
            native=untemper(int.from_bytes(pkt[lane*4:lane*4+4],"little"))
            rows.extend((vec,(native>>bit)&1) for bit,vec in enumerate(get(symbolic,STARTS[i]+lane)))
        observations[i]=rows
    true_in_min=unique_correct=deterministic_wrong_rows=full_wrong_candidates=0
    zero_rows=[]
    for i in range(1,128):
        basis=Basis()
        for row,items in observations.items():
            if row==i:continue
            for vec,bit in items:
                basis.insert(vec,bit)
        low=STARTS[i-1]+4
        high=STARTS[i+1]-4
        assert low<=STARTS[i]<=high
        ranks=[(q,candidate_rank(basis,symbolic,q)) for q in range(low,high+1)]
        minrank=min(r for q,r in ranks)
        possible=[q for q,r in ranks if r==minrank]
        true=int(STARTS[i] in possible)
        true_in_min+=true
        unique_correct+=int(true and len(possible)==1)
        if minrank==0 and not true:
            deterministic_wrong_rows+=1
            zero_rows.append(i)
            for q in possible:
                guessed=predicted_packet(basis,symbolic,q)
                assert guessed!=packets[i]
                full_wrong_candidates+=1
                print(f"WRONG_COMPLETE_WITHHELD_ROW={i} TRUE_STAGE={STARTS[i]}"
                      f" CHOSEN_STAGE={q} GUESSED={guessed.hex().upper()}"
                      f" TRUE_PACKET={packets[i].hex().upper()}")
    assert (true_in_min,unique_correct,deterministic_wrong_rows,full_wrong_candidates)==(26,5,6,9)
    assert zero_rows==[44,92,93,94,95,96]
    print("SOURCE_ONLY_STAGE_MINRANK_LOO=127 TRUE_IN_CHOICES=26 UNIQUE_TRUE=5"
          " FULL_WRONG_ROWS=6 FULL_WRONG_PACKET_CANDIDATES=9 PASS")
    print("K04_SELECTED_STAGE951_ZERO_128_SOURCE_BITS__K08_UNRECOVERED")

if __name__=="__main__": main()
