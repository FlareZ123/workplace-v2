"""H-17: frozen AES-128 CTR_DRBG no-DF stateful retry candidate test.
NIST SP 800-90A Rev.1 s10.2.1; hypothetical, never identified as printer firmware.
Reads original resources without modifying archive/verifier/commitments.
Dependency: cryptography >= 42.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

root = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
raw = (root/"evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows=[]
for line in raw.decode().splitlines():
    if "PAYLOAD=" not in line: continue
    d=dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)",line))
    d["time"]=line.split(" ",1)[0]
    d["bytes"]=bytes.fromhex(d.pop("PAYLOAD"))
    rows.append(d)
assert len(rows)==133
j17=[r for r in rows if r["JOB"]=="PS-261003-0417"]
j20=[r for r in rows if r["JOB"]=="PS-261003-0420"]
assert [(r["STATE"],r["ATTEMPT"],r["CLASS"]) for r in j17]==[
    ("ACK","1","LABEL"),("REQUESTED","1","RECOVER"),
    ("ACK","2","RECOVER"),("REQUESTED","3","RECOVER")]
assert [(r["STATE"],r["ATTEMPT"],r["CLASS"]) for r in j20]==[
    ("ACK","1","STORES"),("ACK","2","RECOVER")]
route=json.loads((root/"evidence/recovery-routing.json").read_text())
accept=json.loads((root/"acceptance.json").read_text())
mask=bytes.fromhex(route["K04"]["masked_component"])
nonce=bytes.fromhex(route["K08"]["desk_nonce"])
target=accept["slot_sha256"]["K04"]
assert target=="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def bxor(a,b):
    return bytes(x^y for x,y in zip(a,b))
def aes(k,b):
    return Cipher(algorithms.AES(k),modes.ECB()).encryptor().update(b)
class CTRDRBG:
    def __init__(self,entropy):
        assert len(entropy)==32
        self.key=bytes(16)
        self.v=bytes(16)
        self.update(entropy)
    def update(self,provided):
        value=int.from_bytes(self.v,"big")
        stream=[]
        for _ in range(2):
            value=(value+1)&((1<<128)-1)
            stream.append(aes(self.key,value.to_bytes(16,"big")))
        material=bxor(b"".join(stream),provided)
        self.key,self.v=material[:16],material[16:]
    def generate(self,additional=None):
        if additional is not None:self.update(additional)
        value=(int.from_bytes(self.v,"big")+1)&((1<<128)-1)
        packet=aes(self.key,value.to_bytes(16,"big"))
        self.v=value.to_bytes(16,"big")
        self.update(additional if additional is not None else bytes(32))
        return packet

def context(row,mode):
    if mode==0:return None
    if mode==1:return bytes(32)
    if mode==2:text=row["JOB"]
    elif mode==3:text="|".join(row[k] for k in ("JOB","ATTEMPT","STATE","CLASS","DEST"))
    elif mode==4:text=row["time"]
    elif mode==5:text=row["JOB"]+"|"+row["time"]
    else:return hashlib.sha256(bytes([int(row["ATTEMPT"])])).digest()
    return hashlib.sha256(text.encode()).digest()

def seed(first,mode,n):
    a=first["bytes"]
    b=[nonce,mask,hashlib.sha256(first["JOB"].encode()).digest()[:16],
       hashlib.sha256(first["time"].encode()).digest()[:16],
       hashlib.md5(first["JOB"].encode()).digest(),
       hashlib.sha256(a).digest()[:16],bytes(16),a][n]
    if mode==0:return a+b
    if mode==1:return b+a
    if mode==2:return bxor(a,b)+b
    if mode==3:return a+bxor(a,b)
    if mode==4:return hashlib.sha256(a+b).digest()
    return hashlib.sha256(b+a).digest()

# Planted complete physical coupon, with all selectors frozen before enumeration.
plant=(3,5,2,0,0)
producer=CTRDRBG(seed(j17[0],plant[0],plant[1]))
outputs=[producer.generate(context(r,plant[2])) for r in j17[1:]]
synthetic_hash=hashlib.sha256(bxor(outputs[1],mask)).hexdigest()
counts=dict(checks=0,original=0,planted=0,req1=0,req3=0,watch=0)
unique=set()
for s,n,c,rev,from_request in itertools.product(range(6),range(8),range(7),range(2),range(2)):
    first=j17[1] if from_request else j17[0]
    later=j17[2:] if from_request else j17[1:]
    producer=CTRDRBG(seed(first,s,n))
    outputs=[producer.generate(context(r,c)) for r in later]
    if from_request: coupon,req3=outputs;req1=b""
    else:req1,coupon,req3=outputs
    if rev:coupon,req1,req3=coupon[::-1],req1[::-1],req3[::-1]
    counts["req1"]+=int(req1==j17[1]["bytes"])
    counts["req3"]+=int(req3==j17[3]["bytes"])
    watch=CTRDRBG(seed(j20[0],s,n)).generate(context(j20[1],c))
    if rev:watch=watch[::-1]
    counts["watch"]+=int(watch==j20[1]["bytes"])
    component=bxor(coupon,mask)
    digest=hashlib.sha256(component).hexdigest()
    counts["checks"]+=1
    counts["original"]+=int(digest==target)
    counts["planted"]+=int(digest==synthetic_hash)
    unique.add(coupon)
assert counts==dict(checks=1344,original=0,planted=1,req1=0,req3=0,watch=0)
assert len(unique)==1176
print(json.dumps({"status":"NO_MATCH","unique_coupons":len(unique),**counts},sort_keys=True))
