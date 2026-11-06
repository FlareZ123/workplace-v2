"""H-17 standard HP PCL5 mode-3 delta-row and mode-1 RLE syntax gate.
Read-only, official source unchanged. Python standard library.
"""
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[2]/"resources"
archive=Path(sys.argv[1]) if len(sys.argv)>1 else root
def read(name):
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            return z.read(name)
    return (archive/name).read_bytes()

spool=read("evidence/print/spool-reconstruction.log")
assert hashlib.sha256(spool).hexdigest()=="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
lines=spool.decode().splitlines()
def get(fragment):
    matches=[x for x in lines if fragment in x]
    assert len(matches)==1
    return bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})",matches[0]).group(1))
copied=get("2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2")
mask=bytes.fromhex(json.loads(read("evidence/recovery-routing.json"))["K04"]["masked_component"])
target=json.loads(read("acceptance.json"))["slot_sha256"]["K04"]
seedrows=[
    bytes(16),
    get("2026-10-03T16:45:00+00:00 JOB=PS-261003-0417"),
    get("2026-10-03T18:01:00Z JOB=PS-261003-0417"),
    get("2026-10-03T18:03:00Z JOB=PS-261003-0417"),
    get("2026-10-03T18:25:00Z JOB=PS-261003-0420"),
    mask,
]
reverse=bytes(int(f"{i:08b}"[::-1],2) for i in range(256))
def versions(b):
    return b,b[::-1],b.translate(reverse),b[::-1].translate(reverse)

def delta(data,seed):
    out=bytearray(seed);pos=0;i=0
    while i<len(data):
        command=data[i];i+=1
        size=(command>>5)+1
        offset=command&31
        if offset==31:
            while True:
                if i>=len(data):return None
                additional=data[i];i+=1
                offset+=additional
                if additional<255:break
        pos+=offset
        if i+size>len(data) or pos+size>len(out):return None
        out[pos:pos+size]=data[i:i+size]
        pos+=size;i+=size
    return bytes(out)

def pcl_mode1(data):
    if len(data)%2:return None
    out=bytearray()
    for n,byte in zip(data[::2],data[1::2]):
        out.extend([byte]*(n+1))
        if len(out)>16:return None
    return bytes(out) if len(out)==16 else None

# HP PCL5 manual delta-row worked example, three rows of five bytes:
a=delta(bytes.fromhex("01FF"),bytes(5))
b=delta(bytes.fromhex("02F0"),a)
c=delta(bytes.fromhex("000F22AAAA"),b)
assert (a.hex(),b.hex(),c.hex())==("00ff000000","00fff00000","0ffff0aaaa")
assert delta(bytes.fromhex("0111"),bytes(16))==bytes.fromhex("00110000000000000000000000000000")

good=0;checks=0;hits=[]
for stage,body in (("copied",copied),("mask",mask),
                   ("prexor",bytes(a^b for a,b in zip(copied,mask)))):
    for orientation,stream in enumerate(versions(body)):
        rle=pcl_mode1(stream)
        if rle is not None:
            checks+=1
            component=(bytes(a^b for a,b in zip(rle,mask if stage=="copied" else copied))
                       if stage!="prexor" else rle)
            if hashlib.sha256(component).hexdigest()==target:hits.append((stage,orientation,"rle",component.hex()))
        for k,seed in enumerate(seedrows):
            good+=1
            decoded=delta(stream,seed)
            if decoded is None:continue
            checks+=1
            component=(bytes(a^b for a,b in zip(decoded,mask if stage=="copied" else copied))
                       if stage!="prexor" else decoded)
            if hashlib.sha256(component).hexdigest()==target:hits.append((stage,orientation,k,component.hex()))
assert good==72 and checks==0 and not hits
print(json.dumps({"strict_pcl_mode3_models":good,"valid_whole_decodes":checks,
                  "full_component_hits":hits,"manual_three_row_example":"PASS"},indent=2))
