"""H17 K08 read-only AES ciphertext witness scan; requires numpy and cryptography."""
from __future__ import annotations
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SPOOL="7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NOTES="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE="f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT="681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
SIX={"K01":"049AAB2E1CDE7A82CD7C60234303C91A","K02":"0D7E3AB56FB75DA3EB0E2E06786D239E","K03":"1384AF96E25D6ADA666209CB55E062FA","K05":"FF8B78200A56E8586DCDA00EF01E4572","K06":"5DBF40EE52FAAED9A536D3326CF0D95A","K07":"93495F5E425AB8E592123DABAEB68545"}

def source(p:Path, sha:str)->bytes:
    data=p.read_bytes()
    assert hashlib.sha256(data).hexdigest()==sha,p
    return data

def aes(key:bytes, blocks:bytes, decrypt:bool)->bytes:
    c=Cipher(algorithms.AES(key),modes.ECB())
    f=c.decryptor() if decrypt else c.encryptor()
    return f.update(blocks)+f.finalize()

def letters(x:np.ndarray)->np.ndarray:
    return ((x>=32)&(x<=126)).all(axis=1)&((((x>=65)&(x<=90))|((x>=97)&(x<=122))).sum(axis=1)>=9)&((x==32).sum(axis=1)>=1)

def carriers(root:Path)->list[bytes]:
    out=set()
    for p in (root/"evidence").rglob("*"):
        if not p.is_file():continue
        raw=p.read_bytes()
        if p.name=="spool-reconstruction.log":
            assert hashlib.sha256(raw).hexdigest()==SPOOL
            raw=b"\n".join(line for line in raw.splitlines() if b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2" not in line)
        out.update(raw[i:i+16] for i in range(len(raw)-15))
        for m in re.finditer(rb"[0-9A-Fa-f]{32,}",raw):
            s=m.group(0)
            out.update(bytes.fromhex(s[i:i+32].decode()) for i in range(len(s)-31))
    assert len(out)==61695,len(out)
    return sorted(out)

def main(root:Path)->None:
    source(root/"evidence/crew/noticeboard-and-desk-notes.txt",NOTES)
    a=json.loads(source(root/"acceptance.json",ACCEPT))
    r=json.loads(source(root/"evidence/recovery-routing.json",ROUTE))
    keys={k:bytes.fromhex(v) for k,v in SIX.items()}
    for k,v in keys.items():assert hashlib.sha256(v).hexdigest()==a["slot_sha256"][k]
    nonce=bytes.fromhex(r["K08"]["desk_nonce"])
    mask=bytes.fromhex(r["K04"]["masked_component"])
    keys.update(desk_nonce=nonce,route_mask=mask)
    ivs={"nonce":nonce,"mask":mask,"zero":bytes(16)}
    cs=carriers(root)
    b=np.frombuffer(b"".join(cs),dtype=np.uint8).reshape((-1,16))
    tested=ascii_count=english_count=k08_count=0
    for keyname,key in keys.items():
        e=np.frombuffer(aes(key,b.tobytes(),True),dtype=np.uint8).reshape((-1,16))
        views={"ecb":e}
        for ivname,iv in ivs.items():
            views[f"cbc_first_{ivname}"]=e^np.frombuffer(iv,dtype=np.uint8)
            c=Cipher(algorithms.AES(key),modes.CTR(iv)).encryptor()
            pads=c.update(bytes(64))+c.finalize()
            for j in range(4):
                views[f"ctr_{ivname}_{j}"]=b^np.frombuffer(pads[16*j:16*(j+1)],dtype=np.uint8)
        for view,data in views.items():
            tested+=len(cs)
            readable=((data>=32)&(data<=126)).all(axis=1)
            good=letters(data)
            ascii_count+=int(readable.sum())
            english_count+=int(good.sum())
            for i in np.flatnonzero(readable):
                phrase=bytes(data[i]).decode("ascii")
                normalized=" ".join(re.sub(r"[^a-z0-9\s]"," ",phrase.lower()).split())
                comp=hmac.new(nonce,normalized.encode(),hashlib.sha256).digest()[:16]
                if hashlib.sha256(comp).hexdigest()==a["slot_sha256"]["K08"]:
                    k08_count+=1
                    print("ORIGINAL EXACT_K08_MATCH",view,keyname,repr(normalized))
    print("ORIGINAL carriers",len(cs),"keys",len(keys),"views_per_key",len(views),"block_decryptions",tested)
    print("ORIGINAL all_printable",ascii_count,"readable_phrase_blocks",english_count,"K08_hits",k08_count)
    assert tested==7896960
    spool=source(root/"evidence/print/spool-reconstruction.log",SPOOL).splitlines()[1:]
    regular=[]
    for line in spool:
        m=re.search(rb"JOB=PS-261003-(\d+).*?PAYLOAD=([0-9A-F]{32})",line)
        assert m
        if 300<=int(m.group(1))<=427 and b"ATTEMPT=1 STATE=ACK" in line:
            regular.append(bytes.fromhex(m.group(2).decode()))
    assert len(regular)==128
    b2=np.frombuffer(b"".join(regular),dtype=np.uint8).reshape((-1,16))
    pair_count=full_pairs=cbc_second_count=0
    for keyname,key in keys.items():
        d=np.frombuffer(aes(key,b2.tobytes(),True),dtype=np.uint8).reshape((-1,16))
        cbc_follow=d[1:]^b2[:-1]
        second_ok=letters(cbc_follow)
        cbc_second_count+=int(second_ok.sum())
        ecb_ok=letters(d)
        full_pairs+=int((ecb_ok[:-1]&ecb_ok[1:]).sum())
        pair_count+=127
        for iv in ivs.values():
            c=Cipher(algorithms.AES(key),modes.CTR(iv)).encryptor()
            pads=c.update(bytes(32))+c.finalize()
            ctr_first=letters(b2^np.frombuffer(pads[:16],dtype=np.uint8))
            ctr_next=letters(b2[1:]^np.frombuffer(pads[16:],dtype=np.uint8))
            full_pairs+=int((ctr_first[:-1]&ctr_next).sum())
            full_pairs+=int((letters(d^np.frombuffer(iv,dtype=np.uint8))[:-1]&second_ok).sum())
            pair_count+=254
    print("ORIGINAL 128packet_pairs",pair_count,"CBC_follow_readable",cbc_second_count,"two_block_phrases",full_pairs)
    assert pair_count==7112
    sample=b"the sea and voices"+bytes(14)
    key=keys["K01"]
    enc=Cipher(algorithms.AES(key),modes.CBC(nonce)).encryptor()
    ct=enc.update(sample)+enc.finalize()
    assert bytes(np.frombuffer(aes(key,ct[:16],True),dtype=np.uint8)^np.frombuffer(nonce,dtype=np.uint8))==sample[:16]
    ctr=Cipher(algorithms.AES(key),modes.CTR(nonce))
    f=ctr.encryptor();ct=f.update(sample)+f.finalize()
    f=ctr.decryptor();assert f.update(ct)+f.finalize()==sample
    print("PLANTED_AES CBC_and_CTR_two_block_controls PASS")
    assert ascii_count==english_count==k08_count==full_pairs==cbc_second_count==0

if __name__=="__main__":main(Path(sys.argv[1]) if len(sys.argv)>1 else Path("resources"))
