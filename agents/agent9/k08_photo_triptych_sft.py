"""H17 K08 cross-author photo-caption triptych.

Original final Emily caption was developed from desk and photograph captions.
This candidate grammar joins one 2..5-word motif-anchored weather/sea image,
one care/tea/mug image and one watch/night image, preserving literal words.
Motif groups are from N01/N08/N14, N03/N09/N11/N19, and Emily
N02/N06/N13/N20. Previous two-photo-splice and three-Emily-anchor
experiments do not cover these three source groups simultaneously.

Run twice with command argument SCW and WCS, using same source and
original K08 HMAC/commitment. Each branch has 8,164,800 assignments.
No historical authenticity or original final word is inferred from grammar.
"""
from itertools import product
from pathlib import Path
import hashlib
import hmac
import json
import re
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[2] / "resources"
path = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = raw.decode("utf-8")
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
key = bytes.fromhex(routing["K08"]["desk_nonce"])
target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
sea = {"N01":{"sea"},"N08":{"water","daylight","overnight"},"N14":{"horizon","rain"}}
care = {"N03":{"teaspoons"},"N09":{"cup","alone"},"N11":{"blue","belongs"},"N19":{"mugs","beds"}}
watch = {"N02":{"watch","room","hands"},"N06":{"lamp","quiet","corridor"},"N13":{"night","lamp","mugs"},"N20":{"sea","voices","table","night"}}
joiners = (" "," and "," while "," when ")

def spans(source):
    out = set()
    for note_id, motif in source.items():
        m = re.search(r"^"+note_id+r" /[^\n]*\n(.*)$", notes, re.M)
        assert m, note_id
        line = m.group(1).split(":",1)[-1]
        words = re.findall(r"[a-z0-9]+", line.lower())
        out.update(" ".join(words[i:i+k])
                   for i in range(len(words))
                   for k in range(2,6)
                   if i+k <= len(words) and not motif.isdisjoint(words[i:i+k]))
    return sorted(out)

a, b, c = spans(sea), spans(care), spans(watch)
assert (len(a),len(b),len(c)) == (50,81,126)
def slot(s):
    return hmac.digest(key, s.encode(), "sha256")[:16]
assert slot("a good watch leaves the room ready for the next pair of hands").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
plant = a[3]+" and "+b[7]+" while "+c[17]
positive = hashlib.sha256(slot(plant)).digest()
orientation = sys.argv[1] if len(sys.argv)>1 else "SCW"
assert orientation in ("SCW","WCS")
left,right = (a,c) if orientation=="SCW" else (c,a)
count=hits=controls=0
started = monotonic()
for one,mid,other in product(left,b,right):
    for j1,j2 in product(joiners,repeat=2):
        phrase=one+j1+mid+j2+other
        digest=hashlib.sha256(slot(phrase)).digest()
        count+=1
        if digest==positive:
            assert phrase==plant
            controls+=1
        if digest==target:
            print("ORIGINAL_MATCH",repr(phrase),slot(phrase).hex().upper())
            hits+=1
assert count==8164800 and controls==(1 if orientation=="SCW" else 0)
print("K08_TRIPTYCH",orientation,"tested",count,"original_matches",hits,"planted_hits",controls,"seconds",round(monotonic()-started,2))
