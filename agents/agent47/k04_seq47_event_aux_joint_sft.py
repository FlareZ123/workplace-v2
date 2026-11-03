"""Seq47 target-bearing stage discriminator via EVENT/LATCH/AUX rejection samplers.

Pure original-source test. Uses p951 printer + 55 other CRC-valid node50 CONTROL
records and the candidate seq47 CONTROL, but no selected printer ACK, route mask,
K04 target, or K08 material. Conditional historical CPython sampler hypothesis.
"""
import hashlib
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"agents"/"agent49"))
sys.path.insert(0, str(ROOT/"agents"/"agent2"))
from k04_p951_symbolic_basis import source, get, temper
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_conditional_onebit_parity_sft import PATH, joint_basis

REC_HASH="5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
ANCHORS={7,9,12,13,14,24,25,41,43,44,45,61,63,64,70}

def recorder_metadata():
    raw=(ROOT/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==REC_HASH
    assert raw[:8]==b"TRP2DUMP" and len(raw)==16+88*24
    records={}
    for i in range(88):
        data=raw[16+24*i:16+24*(i+1)]
        _,node,event,latch,seq,_,aux,crc=struct.unpack("<IHBBI4sII",data)
        if node==50:
            assert zlib.crc32(data[:20])==crc
            records[seq]=(event,latch,aux)
    assert set(records)==set(range(72))
    return records

def fixed_bits(model,vectors,stage,n):
    # CPython getrandbits(n) consumes the high n bits of the tempered word.
    return tuple(model.predict(v) for v in temper(get(vectors,stage))[32-n:])

def fit_code(bits,value):
    return all(bit is None or bit==((value>>i)&1) for i,bit in enumerate(bits))

def maybe_rejected(bits,threshold):
    # Maximum available output by setting all free bits to one.
    maximum=sum(((1 if bit is None else bit)<<i) for i,bit in enumerate(bits))
    return maximum>=threshold

def fixed_accuracy(bits,value):
    fixed=sum(bit is not None for bit in bits)
    correct=sum(bit==((value>>i)&1) for i,bit in enumerate(bits) if bit is not None)
    return fixed,correct

def stage_report(model,vectors,position,observed,max_rejects=4):
    event,latch,aux=observed
    assert (event,latch,aux)==(4,1,3075)
    cache={}
    def bits(stage,n):
        k=(stage,n)
        if k not in cache:cache[k]=fixed_bits(model,vectors,stage,n)
        return cache[k]
    valid=[]
    rejected={}
    for er in range(max_rejects+1):
        for lr in range(max_rejects+1):
            first=position-(er+lr+2)
            # No staged seq47 EVENT/LATCH draw may run before prior CONTROL seq46=-531.
            if first<=-531:continue
            for ar in range(max_rejects+1):
                e_stages=range(first,first+er+1)
                l_stages=range(first+er+1,position)
                a_stages=range(position+1,position+ar+2)
                if len(l_stages)!=lr+1:raise AssertionError("latch topology")
                if len(a_stages)!=ar+1:raise AssertionError("aux topology")
                e_good=all(maybe_rejected(bits(t,6),39) for t in tuple(e_stages)[:-1])
                e_good=e_good and fit_code(bits(tuple(e_stages)[-1],6),event-1)
                l_good=all(maybe_rejected(bits(t,3),4) for t in tuple(l_stages)[:-1])
                l_good=l_good and fit_code(bits(tuple(l_stages)[-1],3),latch)
                a_good=all(maybe_rejected(bits(t,13),6000) for t in tuple(a_stages)[:-1])
                a_good=a_good and fit_code(bits(tuple(a_stages)[-1],13),aux-2000)
                if e_good and l_good and a_good:
                    obs=(
                        fixed_accuracy(bits(tuple(e_stages)[-1],6),event-1),
                        fixed_accuracy(bits(tuple(l_stages)[-1],3),latch),
                        fixed_accuracy(bits(tuple(a_stages)[-1],13),aux-2000),
                    )
                    valid.append((er,lr,ar,first,obs))
                else:
                    key=("E" if not e_good else "")+("L" if not l_good else "")+("A" if not a_good else "")
                    rejected[key]=rejected.get(key,0)+1
    return valid,rejected

def main():
    printer,vectors=source(ROOT/"resources")
    assert printer.rank==15365
    controls=recorder_controls()
    meta=recorder_metadata()
    assert meta[47]==(4,1,3075)
    others=tuple((seq,pos) for seq,pos in PATH if seq!=47)
    rows=[]
    for stage in (-523,-522,-521,-520):
        model=joint_basis(printer,vectors,controls,others+((47,stage),))
        assert model.rank in (16663,16664)
        valid,errors=stage_report(model,vectors,stage,meta[47])
        direct=next((v for v in valid if v[:3]==(0,0,0)),None)
        summary={
            "stage":stage,
            "rank":model.rank,
            "compatible_exact_rejection_histories_0_to_4":len(valid),
            "direct_no_rejection_history_survives":direct is not None,
            "first_compatible_paths":valid[:12],
            "rejected_class_counts":errors,
        }
        rows.append(summary)
        print("STAGE_REPORT",summary,flush=True)
    # Separately calibrate the simplest (0,0,0) source-scoped architecture
    # on the other 55 original node50 controls, with independent metadata.
    reference=joint_basis(printer,vectors,controls,PATH)
    strata={"original_anchor":[],"other_placed":[]}
    for seq,pos in PATH:
        if seq==47:continue
        ev,la,au=meta[seq]
        data=(
            fixed_accuracy(fixed_bits(reference,vectors,pos-2,6),ev-1),
            fixed_accuracy(fixed_bits(reference,vectors,pos-1,3),la),
            fixed_accuracy(fixed_bits(reference,vectors,pos+1,13),au-2000),
        )
        strata["original_anchor" if seq in ANCHORS else "other_placed"].append((seq,data))
    for label,records in strata.items():
        for i,kind in enumerate(("event","latch","aux")):
            fixed=sum(row[i][0] for _,row in records)
            correct=sum(row[i][1] for _,row in records)
            print("HOLDOUT",label,kind,"source_fixed",fixed,"correct",correct)
    print("Conditional stage selection is not historical authentication. No K04 target bit claimed.")

if __name__=="__main__":
    main()
