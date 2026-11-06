"""Source-pinned, read-only K08 two-frame author-draft style editor.

Both actual Emily N02 and N06 complete historical drafts are explicitly included
once, but neither is claimed to be the selected final keeper inscription.
"""
from pathlib import Path
import hashlib
import hmac
import itertools
import json
import re
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
notes=(root/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(notes).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
route=json.loads((root/"evidence/recovery-routing.json").read_text())
accept=json.loads((root/"acceptance.json").read_text())
key=bytes.fromhex(route["K08"]["desk_nonce"])
target=accept["slot_sha256"]["K08"]
assert target=="285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
def norm(s):
    return " ".join(re.sub(r"[^a-z0-9\s]"," ",s.lower()).split())
def comp(s):
    return hmac.digest(key,norm(s).encode(),"sha256")[:16]
def digest(s):
    return hashlib.sha256(comp(s)).hexdigest()
n02="a good watch leaves the room ready for the next pair of hands"
n06="the little lamp stays on until the corridor has gone quiet"
assert n02.encode() in notes.lower() and n06.encode() in notes.lower()
assert comp(n02).hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
subjects=["a good watch","the sea","the water","the last watch","the late crew",
          "the voices at the table","the night","a quiet room","the little lamp",
          "the table","the mugs","one last cup"]
verbs=["leaves","keeps","holds","saves","makes","finds","remembers","brings",
       "kept","left","made","holds onto"]
objects=["the room","a place","a place at the table","the table","one more place",
         "the light","the lamp","the cups","the water outside","one more seat",
         "the chair","the voices","our place","the galley"]
states=["ready","open","warm","quiet","waiting","still","where it was",
        "behind","for us","for each other","lit","at home","on"]
beneficiaries=["for the next pair of hands","for whoever comes next",
               "for the next watch","for us","for one another","for each other",
               "for the crew","for the late watch","for the people at the table",
               "for the voices at the table","until morning","at the end of the night",
               "as the water waits outside","until the sea turns blue",
               "after a long watch","after the last cup","by the window",""]
subjects_b=subjects+["the last light","the warm room"]
verbs_b=["stays","remains","waits","keeps","sits","glows","holds","shines","burns","is"]
states_b=["on","bright","lit","near the window","by the window","with us",
          "at the table","in the room","quiet","still here"]
termini=["the corridor has gone quiet","the night is almost finished",
         "the night is over","the sea has gone quiet","the last cup is empty",
         "we have finished our tea","the water is still","the last watch comes home",
         "the next watch comes in","the late crew goes home",
         "the voices have gone quiet","the first boat comes back",
         "the morning comes","the light is out","the room is empty",
         "the sea comes home","there is room for everyone",
         "the last mug is washed","the galley falls quiet","somebody sits down"]
def make_a(parts):
    return norm(" ".join(parts))
def make_b(parts):
    return norm(f"{parts[0]} {parts[1]} {parts[2]} until {parts[3]}")
assert n02==make_a(("a good watch","leaves","the room","ready",
                   "for the next pair of hands"))
assert n06==make_b(("the little lamp","stays","on","the corridor has gone quiet"))
plant=make_b(("the sea","waits","by the window","the night is over"))
planted_hash=digest(plant)
counts={"A":0,"B":0,"real":0,"N02":0,"N06":0,"synthetic":0}
unique=set()
for typ,items in [
    ("A",itertools.product(subjects,verbs,objects,states,beneficiaries)),
    ("B",itertools.product(subjects_b,verbs_b,states_b,termini))
]:
    for parts in items:
        s=make_a(parts) if typ=="A" else make_b(parts)
        counts[typ]+=1
        counts["N02"]+=int(s==n02)
        counts["N06"]+=int(s==n06)
        result=digest(s)
        counts["real"]+=int(result==target)
        counts["synthetic"]+=int(result==planted_hash)
        unique.add(s)
assert counts=={"A":471744,"B":28000,"real":0,"N02":1,"N06":1,"synthetic":1}
assert len(unique)==499744
print(json.dumps({"status":"NO_MATCH","unique_complete_captions":len(unique),
                  **counts},sort_keys=True))
