"""Original-source hidden MT donor XOR/additive K04 copy-overlay SFT.

Run from repository root: python agents/agent37/k04_hidden_mt_overlay_sft.py
Only complete four-word native packets inferred from 132 intact original
spool rows enter as hypothetical stale copied-buffer overlay pads.
The selected row is excluded from original MT inference.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re

REPO=Path(__file__).resolve().parents[2]
EVIDENCE=REPO/"resources"
SPOOL_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
MASK128=(1<<128)-1

def pinned(path,expected):
    data=path.read_bytes()
    assert hashlib.sha256(data).hexdigest()==expected,path
    return data

def xor(a,b):
    return bytes(x^y for x,y in zip(a,b))

def main():
    module=REPO/"agents/agent2/20261102_k04_multicarrier_p951_sft.py"
    spec=importlib.util.spec_from_file_location("original_p951_source",module)
    mt=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    spool=pinned(EVIDENCE/"evidence/print/spool-reconstruction.log",SPOOL_SHA)
    lines=[line for line in spool.decode().splitlines() if "PAYLOAD=" in line]
    assert len(lines)==len(mt.STARTS)==133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    copied=bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",lines[129]).group(1))
    route=json.loads(pinned(EVIDENCE/"evidence/recovery-routing.json",ROUTE_SHA))
    accept=json.loads(pinned(EVIDENCE/"acceptance.json",ACCEPT_SHA))
    mask=bytes.fromhex(route["K04"]["masked_component"])
    target=accept["slot_sha256"]["K04"]
    assert len(mask)==len(copied)==16
    assert hashlib.sha256(xor(copied,mask)).hexdigest()!=target

    # Imported original reproducible closure verifies 528 untouched native
    # source words and explicitly avoids selected row129 in the seed basis.
    words,known,offset=mt.source_closure(EVIDENCE)
    assert sum(k==mt.MASK for k in known)==968
    assert sum(0<k<mt.MASK for k in known)==306
    assert [known[offset+mt.STARTS[129]+j] for j in range(4)]==[0]*4
    positions=[i-offset for i in range(len(words)-3)
               if all(k==mt.MASK for k in known[i:i+4])]
    hidden=[stage for stage in positions if stage not in mt.STARTS]
    assert len(positions)==266 and len(hidden)==134
    # Confirm genuine intact packets are completely predicted before
    # using the inferred unrecorded packet windows as hypothetical pads.
    controls=0
    for row,(start,line) in enumerate(zip(mt.STARTS,lines)):
        if row==129:continue
        expected=bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",line).group(1))
        observed=b"".join(mt.temper(words[offset+start+j]).to_bytes(4,"little")
                          for j in range(4))
        assert observed==expected
        controls+=1
    assert controls==132

    def donor(stage,endian,reverse):
        native=[mt.temper(words[offset+stage+j]) for j in range(4)]
        if reverse:native.reverse()
        return b"".join(word.to_bytes(4,endian) for word in native)

    def coupon(pad,op):
        if op=="xor":return xor(copied,pad)
        if op=="direct":return pad
        left=int.from_bytes(copied,"little")
        right=int.from_bytes(pad,"little")
        result=left+right if op=="add" else left-right if op=="sub" else right-left
        return (result&MASK128).to_bytes(16,"little")

    planted_stage=hidden[0]
    planted_coupon=coupon(donor(planted_stage,"little",False),"xor")
    planted_digest=hashlib.sha256(xor(planted_coupon,mask)).digest()
    hits=[];synthetic=[];distinct=set();checks=0
    for stage in positions:
        for endian in ("little","big"):
            for reverse in (False,True):
                pad=donor(stage,endian,reverse)
                for op in ("xor","add","sub","inverse_sub","direct"):
                    component=xor(coupon(pad,op),mask)
                    digest=hashlib.sha256(component).digest()
                    if digest.hex()==target:
                        hits.append((stage,endian,reverse,op,component.hex().upper()))
                    if digest==planted_digest:
                        synthetic.append((stage,endian,reverse,op))
                    distinct.add(component);checks+=1
    assert checks==5320 and len(distinct)==5320
    assert synthetic==[(planted_stage,"little",False,"xor")]
    assert hits==[]
    print("ORIGINAL_SOURCE_BASELINE",controls,"full source packets")
    print("SOURCE_IMPLIED_FOUR_WORD_WINDOWS",len(positions),
          "NOT_LITERAL_RETAINED_PACKET_STARTS",len(hidden))
    print("STAGE_RANGE",min(positions),max(positions))
    print("ORIGINAL_FULL_SHA256_CHECKS",checks,
          "DISTINCT_COMPONENTS",len(distinct),
          "PLANTED_FULL_COMPONENT_HITS",len(synthetic),
          "ORIGINAL_K04_HITS",len(hits))
    print("K04/K08 unresolved; six original PASS, combined INCOMPLETE")

if __name__=="__main__":
    main()
