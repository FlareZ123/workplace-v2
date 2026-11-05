"""H17 K08: original 128-row printer nibble-index literal carrier test."""
import hashlib, hmac, itertools, json, re, sys
from pathlib import Path
r=Path(sys.argv[1] if len(sys.argv)>1 else "resources")
spool=(r/"evidence/print/spool-reconstruction.log").read_bytes()
route=(r/"evidence/recovery-routing.json").read_bytes()
notes=(r/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest()=="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert hashlib.sha256(notes).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
nonce=bytes.fromhex(json.loads(route)["K08"]["desk_nonce"])
target="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
lines=[s for s in spool.decode().splitlines() if "PAYLOAD=" in s]
rows=[]
for n in range(300,428):
    candidates=[s for s in lines if f"JOB=PS-261003-{n:04d} " in s and "STATE=ACK" in s and "ATTEMPT=1" in s]
    assert len(candidates)==1
    rows.append(bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",candidates[0]).group(1)))
assert len(rows)==128
def normalize(s):return " ".join(re.findall(r"[a-z0-9]+",s.lower()))
def component(s):return hmac.new(nonce,normalize(s).encode(),hashlib.sha256).digest()[:16]
assert component("A good watch leaves the room ready for the next pair of hands.").hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
def decode(source,a,b,view,reverse,pack):
    nib=[]
    for i in range(128):
        row=source[127-i if reverse else i]
        p=(a*i+b)&31
        if view&1:p^=1
        if view&2:p=31-p
        byte=row[p>>1]
        nib.append(byte>>4 if p&1==0 else byte&15)
    if pack:nib.reverse()
    return bytes((nib[i]<<4)|nib[i+1] for i in range(0,128,2))
plant=b"Leave the light on for the next watch.".ljust(64,b" ")
synthetic=[bytearray(x) for x in rows]
for i,value in enumerate(y for byte in plant for y in (byte>>4,byte&15)):
    p=(9*i+3)&31;k=p>>1
    if p&1:synthetic[i][k]=(synthetic[i][k]&240)|value
    else:synthetic[i][k]=(synthetic[i][k]&15)|(value<<4)
assert decode(synthetic,9,3,0,0,0)==plant
synthetic_slot=hashlib.sha256(component(plant.decode())).digest()
assert synthetic_slot.hex()!=target
counts=0;phrases=set();matches=[]
for a,b,view,reverse,pack in itertools.product(range(32),range(32),range(4),range(2),range(2)):
    stream=decode(rows,a,b,view,reverse,pack)
    counts+=1
    for m in re.finditer(rb"[ -~]{16,}",stream):
        words=normalize(m.group().decode("ascii")).split()
        for lo in range(len(words)):
            for hi in range(lo+2,min(len(words)+1,lo+33)):
                phrase=" ".join(words[lo:hi]);phrases.add(phrase)
                if hashlib.sha256(component(phrase)).hexdigest()==target:matches.append((a,b,view,reverse,pack,phrase))
assert counts==16384 and not phrases and not matches
assert hashlib.sha256(component(decode(synthetic,9,3,0,0,0).decode())).digest()==synthetic_slot
print(json.dumps({"streams":counts,"distinct_original_text_phrases":len(phrases),"original_K08_hits":matches,"complete_synthetic_positive":True}))
