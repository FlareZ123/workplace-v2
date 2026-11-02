"""Original-source AES-128 counter emitter test, read-only.

python agents/agent28/k04_aes_counter_sft.py
Requires cryptography. Uses only ordinary intact printer rows.
"""
from pathlib import Path
import datetime as dt
import hashlib
import re
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BASE=Path(__file__).resolve().parents[2]/"resources"
SOURCE=BASE/"evidence/print/spool-reconstruction.log"
regex=re.compile(r"JOB=PS-261003-(\d{4}) .*PAYLOAD=([0-9A-F]{32})")
ordinary=[(int(m.group(1)),bytes.fromhex(m.group(2)))
          for line in SOURCE.read_text().splitlines()
          if "+00:00 JOB=" in line if (m:=regex.search(line))]
assert len(ordinary)==128 and [j for j,_ in ordinary]==list(range(300,428))
keys={
 "K01":"049AAB2E1CDE7A82CD7C60234303C91A",
 "K02":"0D7E3AB56FB75DA3EB0E2E06786D239E",
 "K03":"1384AF96E25D6ADA666209CB55E062FA",
 "K05":"FF8B78200A56E8586DCDA00EF01E4572",
 "K06":"5DBF40EE52FAAED9A536D3326CF0D95A",
 "K07":"93495F5E425AB8E592123DABAEB68545",
 "MASK":"8556C8CB6140A7F9A5123AC7571BEE1C",
 "NONCE":"5F933DA6A1BD03C32DA5CBC25344F497"
}
keys={k:bytes.fromhex(v) for k,v in keys.items()}
def aes(key,block):
    e=Cipher(algorithms.AES(key),modes.ECB()).encryptor()
    return e.update(block)+e.finalize()
assert aes(bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
           bytes.fromhex("00112233445566778899aabbccddeeff")).hex()=="69c4e0d86a7b0430d8cdb78070b4c55a"

def forms(j,i):
    ts=int(dt.datetime(2026,10,3,7,tzinfo=dt.timezone.utc).timestamp())+300*i
    values={"row":i,"job":j,"unix_seconds":ts,"unix_minutes":ts//60,
            "clock_hhmm":(7+i//12)*100+(i%12)*5,"job_attempt":j*10+1}
    b={f"{name}-{order}":x.to_bytes(16,order) for name,x in values.items()
       for order in ("big","little")}
    b["job-md5"]=hashlib.md5(f"PS-261003-{j:04d}".encode()).digest()
    b["job-ascii"]=f"PS-261003-{j:04d}".encode().ljust(16,b"\0")
    return b
def serialize(b):
    return {"plain":b,"reversed":b[::-1],"swapped8":b[8:]+b[:8],
            "reverse-each8":b[:8][::-1]+b[8:][::-1]}

hits=[]
max_equal=0
models=0
for name,key in keys.items():
    for form in forms(300,0):
        for view in serialize(b"0123456789abcdef"):
            for mode in ("plain","xor-input","xor-mask"):
                models+=1
                full=[]
                for i,(job,want) in enumerate(ordinary[:20]):
                    inp=forms(job,i)[form]
                    got=serialize(aes(key,inp))[view]
                    if mode=="xor-input":got=bytes(x^y for x,y in zip(got,inp))
                    if mode=="xor-mask":got=bytes(x^y for x,y in zip(got,keys["MASK"]))
                    same=sum(x==y for x,y in zip(got,want))
                    max_equal=max(max_equal,same)
                    if same==16:full.append(job)
                if full:hits.append([name,form,view,mode,full])
assert models==1344
print(json.dumps({"source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "models":models,"ordinary_training_rows":20,"full_matches":hits,
                  "max_matching_bytes":max_equal,"AES_FIPS197_control":"PASS"},indent=2))
