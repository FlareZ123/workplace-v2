#!/usr/bin/env python3
"""Target-reaching K08 *opaque-component* 128-bit note-bitplane channel.

Only original, SHA-pinned source chains, original K08 acceptance, synthetic
positive are read. No original component bytes/candidate source text printed.
"""
from pathlib import Path
from hashlib import sha256
import json,re,sys

SOURCE_SHA="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
P20_SHA="4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c"

def pack(chars,plane,lsb_first,reverse):
    assert len(chars)==128
    bits=[(ord(c)>>plane)&1 for c in chars]
    data=bytes(sum(bits[i*8+j] << (j if lsb_first else 7-j)
                   for j in range(8)) for i in range(16))
    return data[::-1] if reverse else data

def main(root):
    root=Path(root)
    raw=(root/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert sha256(raw).hexdigest()==SOURCE_SHA
    notes={}
    for m in re.finditer(r"^N(\d{2}) / [^\n]+\n([^\n]+)",raw.decode(),re.M):
        notes[int(m.group(1))]=m.group(2).split(":",1)[-1].lstrip()
    assert set(notes)==set(range(1,25))
    head=notes[20][:24]
    assert bytes(sum((ord(head[8*i+j])&1)<<j for j in range(8))
                 for i in range(3))==b"MHI"
    wordlist=lambda s:re.findall(r"[a-z0-9]+",s.lower())
    p20=" ".join(wordlist(notes[20])[6:19])
    assert sha256(p20.encode()).hexdigest()==P20_SHA
    chains={
        "N20_literal_body":[20],
        "MHI_N13_N08_N09":[13,8,9],
        "draft_N02_N06_photo_N01":[2,6,1],
        "version_N02_N06_N03_N13_N23":[2,6,3,13,23],
        "N20_then_N09_AES":[20,9]
    }
    target=json.loads((root/"acceptance.json").read_text())["slot_sha256"]["K08"]
    # A planted source-stream target exists at source-selected MHI head.
    plant=pack("".join(notes[i] for i in (13,8,9))[:128],0,True,False)
    plant_digest=sha256(plant).hexdigest()
    # An independently prepared 128-bit synthetic plaintext exercises each bit.
    sample=b"PLANTED 16 BYTES"
    assert len(sample)==16
    encoded="".join("a" if byte>>bit&1 else "b"
                    for byte in sample for bit in range(8))
    assert pack(encoded,0,True,False)==sample
    totals={};checked=real_hits=planted_hits=0
    for name,ids in chains.items():
        checks=real=planted=0
        for sep in (""," ","\n"):
            joined=sep.join(notes[i] for i in ids)
            for off in range(max(0,len(joined)-127)):
                window=joined[off:off+128]
                for plane in range(8):
                    for lsb in (False,True):
                        for reverse in (False,True):
                            digest=sha256(pack(window,plane,lsb,reverse)).hexdigest()
                            real+=(digest==target)
                            planted+=(digest==plant_digest)
                            checks+=1
        totals[name]={"checks":checks,"original_hits":real,"planted_hits":planted}
        checked+=checks;real_hits+=real;planted_hits+=planted
    assert checked==56640 and planted_hits==1
    print(json.dumps({"source_sha":"PASS","MHI":"PASS","P20":"PASS",
          "synthetic_full_opaque_digest":"PASS",
          "full_component_assignment_checks":checked,
          "planted_original_stream_control_hits":planted_hits,
          "original_K08_commitment_hits":real_hits,"chain_details":totals},
          sort_keys=True))
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: SCRIPT original-extracted-root")
    main(sys.argv[1])
