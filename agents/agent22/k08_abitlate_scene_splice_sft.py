"""K08 note-initialism anchor plus three-scene source-literal splice. Read-only."""
from __future__ import annotations
import email
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
HASHES = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "evidence/mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
ROLES = (
    (("N01","N08","N14","N20","MAIL11"), {"sea","water","window","horizon","colors"}),
    (("N02","N06","N13","N20","MAIL11"), {"watch","night","morning","end","lamp","quiet"}),
    (("N02","N09","N11","N19","N20","MAIL20"), {"people","table","voices","room","mugs","hands","cup","cups"}),
)
ANCHORS = ("a bit late", "a teal bit")

def pinned(name):
    data = (ROOT / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == HASHES[name], name
    return data

def main():
    note_text = pinned("evidence/crew/noticeboard-and-desk-notes.txt").decode("utf-8")
    notes = {f"N{int(k):02d}": v.split(":",1)[-1] if ":" in v else v
             for k,v in re.findall(r"N(\d+) / [^\n]+\n([^\n]+)", note_text)}
    for number in (11,20):
        msg = email.message_from_bytes(pinned(f"evidence/mail/{number:02d}.eml"))
        notes[f"MAIL{number:02d}"] = msg.get_payload(decode=True).decode("utf-8")
    initials = "".join(re.findall(r"[a-z0-9]+",notes[f"N{i:02d}"].lower())[0][0]
                       for i in (2,6,11,13,17,18,20,23))
    assert initials == "ATEALBIT"
    route=json.loads(pinned("evidence/recovery-routing.json"))
    acceptance=json.loads(pinned("acceptance.json"))
    key=bytes.fromhex(route["K08"]["desk_nonce"])
    target=bytes.fromhex(acceptance["slot_sha256"]["K08"])
    first_draft="a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(key,first_draft.encode(),"sha256")[:16].hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    groups=[]
    for selected,motifs in ROLES:
        spans=set()
        for name in selected:
            words=re.findall(r"[a-z0-9]+", notes[name].lower())
            for length in range(2,7):
                for start in range(len(words)-length+1):
                    phrase=words[start:start+length]
                    if motifs.intersection(phrase):
                        spans.add(" ".join(phrase))
        groups.append(sorted(spans))
    assert tuple(map(len,groups))==(96,153,119)
    plant=" ".join((ANCHORS[0],groups[0][0],groups[1][0],groups[2][0]))
    plant_hash=hashlib.sha256(hmac.digest(key,plant.encode(),"sha256")[:16]).digest()
    count=0
    positives=0
    hits=[]
    for sea,night,people in itertools.product(*groups):
        spans=(sea,night,people)
        for anchor in ANCHORS:
            for pos in range(4):
                phrase=" ".join((*spans[:pos],anchor,*spans[pos:]))
                digest=hashlib.sha256(hmac.digest(key,phrase.encode("ascii"),"sha256")[:16]).digest()
                count+=1
                if digest==plant_hash:
                    assert phrase==plant
                    positives+=1
                if digest==target:
                    hits.append(phrase)
                    print("K08 ORIGINAL MATCH:",phrase,flush=True)
    assert count==13982976 and positives==1
    print("COMPLETE", "checks",count,"original_matches",len(hits),
          "planted_positive",positives,"N02_control","PASS")

if __name__=="__main__":
    main()
