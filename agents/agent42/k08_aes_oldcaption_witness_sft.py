"""Read-only AES-ECB old-caption carrier test. Requires cryptography and H17_ZIP."""
from hashlib import sha256
from zipfile import ZipFile
import hmac
import os
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

N = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
KEYS = [bytes.fromhex(x) for x in [
"049AAB2E1CDE7A82CD7C60234303C91A",
"0D7E3AB56FB75DA3EB0E2E06786D239E",
"1384AF96E25D6ADA666209CB55E062FA",
"FF8B78200A56E8586DCDA00EF01E4572",
"5DBF40EE52FAAED9A536D3326CF0D95A",
"93495F5E425AB8E592123DABAEB68545",
"5F933DA6A1BD03C32DA5CBC25344F497",
"8556C8CB6140A7F9A5123AC7571BEE1C"]]
with ZipFile(os.environ.get("H17_ZIP","h17-archive-dump.zip")) as z:
    notes=z.read("evidence/crew/noticeboard-and-desk-notes.txt")
    assert sha256(notes).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    controls=[]
    for i in (2,6,17,18):
        m=re.search(rb"^N"+f"{i:02d}".encode()+rb" / Emily[^\n]*\n([^\n]*)",notes,re.M)
        assert m
        phrase=m.group(1).split(b":",1)[1].decode().lower()
        msg=" ".join(re.findall("[a-z0-9]+",phrase)).encode()
        controls.append(hmac.new(N,msg,"sha256").digest()[:16])
    assert controls[0].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    carriers=set()
    for name in z.namelist():
        if not name.startswith("evidence/") or name.endswith("/"):
            continue
        raw=z.read(name)
        if name=="evidence/print/spool-reconstruction.log":
            raw=b"\n".join(line for line in raw.splitlines() if b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2" not in line)
        carriers.update(raw[k:k+16] for k in range(len(raw)-15))
        for m in re.finditer(rb"[0-9A-Fa-f]{32,}",raw):
            s=m.group()
            carriers.update(bytes.fromhex(s[k:k+32].decode()) for k in range(len(s)-31))
assert len(carriers)==61695
hits=[]
for i,control in enumerate(controls):
    words=[control[k:k+4] for k in (0,4,8,12)]
    for view in (control,control[::-1],b"".join(words[::-1]),b"".join(x[::-1] for x in words)):
        for key in KEYS:
            c=Cipher(algorithms.AES(key),modes.ECB())
            for f in (c.encryptor(),c.decryptor()):
                candidate=f.update(view)+f.finalize()
                if candidate in carriers:
                    hits.append((i,candidate.hex()))
assert not hits,hits
positive=Cipher(algorithms.AES(KEYS[2]),modes.ECB()).encryptor()
plant=positive.update(controls[2])+positive.finalize()
assert plant in carriers|{plant}
print("AES predictions 256; original hits 0; synthetic positive PASS")
