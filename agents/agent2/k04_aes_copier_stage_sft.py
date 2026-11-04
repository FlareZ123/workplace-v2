"""Source-pinned AES copy-stage K04 candidate study. Requires cryptography; no writes."""
import hashlib
import json
import re
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT=Path(__file__).resolve().parents[2]
TARGET="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
SOURCE_SHA="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
spool=(ROOT/"resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest()==SOURCE_SHA
route=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text(encoding="utf-8"))
assert route["K04"]["masked_component"]=="8556C8CB6140A7F9A5123AC7571BEE1C"
mask=bytes.fromhex(route["K04"]["masked_component"])
nonce=bytes.fromhex(route["K08"]["desk_nonce"])
ps={}
for row in spool.decode().splitlines()[1:]:
    p=re.search(r"JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)",row)
    if p:
        ps[(p[1],int(p[2]),p[3],p[4])]=bytes.fromhex(p[5])
job="PS-261003-0417"
sel=ps[(job,2,"ACK","RECOVER")]
req1=ps[(job,1,"REQUESTED","RECOVER")]
req3=ps[(job,3,"REQUESTED","RECOVER")]
label=ps[(job,1,"ACK","LABEL")]
south=ps[("PS-261003-0448",1,"ACK","RECOVER")]
spare=ps[("PS-261003-0420",2,"ACK","RECOVER")]
known=json.loads((ROOT/"candidate.json").read_text(encoding="utf-8"))
assert known["K04"] is None and known["K08"] is None
keys={k:bytes.fromhex(v) for k,v in known.items() if v is not None}
assert set(keys)=={"K01","K02","K03","K05","K06","K07"}
keys.update({"mask":mask,"nonce":nonce,"request1":req1,"request3":req3,
             "label0417":label,"south0448":south,"spare0420":spare})
keyset={}
for name,k in keys.items():
    keyset[name+"-128"]=k
    keyset[name+"-sha256"]=hashlib.sha256(k).digest()
    keyset[name+"-double"]=k+k
for a,b in [("mask","nonce"),("nonce","mask"),("K01","K05"),("K05","K01"),("K06","K07"),("K02","K03")]:
    keyset[a+"+"+b]=keys[a]+keys[b]
whiten={"zero":bytes(16),"mask":mask,"nonce":nonce,"req1":req1,
        "req3":req3,"label":label,"south":south,"spare":spare}
views={
    "raw":lambda v:v,
    "reverse16":lambda v:v[::-1],
    "rev_each_word":lambda v:b"".join(v[i:i+4][::-1] for i in range(0,16,4)),
    "reverse_word_order":lambda v:b"".join(v[i:i+4] for i in range(12,-1,-4)),
}
def xor(a,b):
    return bytes(x^y for x,y in zip(a,b))
checked=set()
hits=[]
synthetic_count=0
# Independently constructed planted AES-CBC stage: source-derived K01, nonce IV.
plant_coupon=Cipher(algorithms.AES(keys["K01"]),modes.CBC(nonce)).decryptor().update(xor(sel,mask))
plant_sha=hashlib.sha256(xor(plant_coupon,mask)).hexdigest()
for keyname,key in keyset.items():
    for ivname,iv in whiten.items():
        mode_list=[("ECB",modes.ECB()),("CBC",modes.CBC(iv)),
                   ("CTR",modes.CTR(iv)),("CFB",modes.CFB(iv)),("OFB",modes.OFB(iv))]
        for mode_name,mode in mode_list:
            if mode_name=="ECB" and ivname!="zero":
                continue
            directions=("encrypt","decrypt") if mode_name in ("ECB","CBC","CFB") else ("encrypt",)
            for direction in directions:
                cipher=Cipher(algorithms.AES(key),mode)
                for viewname,view in views.items():
                    data=view(sel)
                    for before_name,before in whiten.items():
                        context=cipher.encryptor() if direction=="encrypt" else cipher.decryptor()
                        derived=context.update(xor(data,before))+context.finalize()
                        for after_name,after in whiten.items():
                            comp=xor(xor(view(derived),after),mask)
                            if comp in checked:
                                continue
                            checked.add(comp)
                            digest=hashlib.sha256(comp).hexdigest()
                            if digest==plant_sha:
                                synthetic_count+=1
                            if digest==TARGET:
                                hits.append((keyname,ivname,mode_name,direction,
                                             viewname,before_name,after_name,comp.hex()))
assert synthetic_count==1
print(json.dumps({"key_count":len(keyset),"unique_components":len(checked),
                  "synthetic_positive_hits":synthetic_count,"real_hits":hits,
                  "source_spool_sha256":SOURCE_SHA,"selected_copy":sel.hex().upper()},indent=2))
