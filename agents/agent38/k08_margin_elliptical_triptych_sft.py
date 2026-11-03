"""H17 original K08 keeper-caption elliptical three-motif source-conditioned SFT.

Distinctive model: author-final may be an elliptical photographic caption,
an ordered group of three nominal scenes, rather than a full 3/4-clause
sentence or a contiguous source excerpt. Speculative, not historically attested.
26 sea, 26 watch-time, 41 community motifs, all 6 orders and 8 connectors.
No source sentence or target commitment is changed.
"""
from pathlib import Path
import hashlib,hmac,itertools,json,re,time

ROOT=Path(__file__).resolve().parents[2]/"resources"
def read(n):return (ROOT/n).read_bytes()
SOURCE_HASHES={
 "evidence/crew/noticeboard-and-desk-notes.txt":"13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
 "evidence/mail/11.eml":"f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
 "evidence/mail/20.eml":"e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71"}
for n,v in SOURCE_HASHES.items():assert hashlib.sha256(read(n)).hexdigest()==v

routing=json.loads(read("evidence/recovery-routing.json"))
accept=json.loads(read("acceptance.json"))
nonce=bytes.fromhex(routing["K08"]["desk_nonce"])
want=bytes.fromhex(accept["slot_sha256"]["K08"])

def normal(s):return " ".join(re.sub(r"[^a-z0-9\s]"," ",s.lower()).split())
def k08(s):return hmac.digest(nonce,normal(s).encode(),"sha256")[:16]
assert k08("A good watch leaves the room ready for the next pair of hands.").hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
SEA=(
 "the sea outside","the sea outside the window","the water outside","the water beyond the window",
 "the sea beyond the glass","the water beyond the glass","the sea just outside","the water at the window",
 "the sea beyond the room","the sea past the window","the sea beyond the light","the water past the window",
 "the sea in the morning","the sea at the end of the night","the sea waiting outside","the water waiting outside",
 "the sea outside in the dark","the sea under the last light","the dark sea outside","the sea at first light",
 "the water at the edge of morning","the sea still outside","the water still outside","the sea under the window",
 "the first light on the water","the water returning in the morning",
)
TIME=(
 "the end of the night","the night almost over","the night nearly over","the night nearly finished",
 "the last of the night","the end of a long night","the end of the watch","the last of the watch",
 "the end of a long watch","the last hour of the watch","the last hour of the night",
 "the night almost finished","the watch almost done","the watch nearly done","the watch finished",
 "the long watch over","after the last cup","the last cup of the night","the first light of morning",
 "morning almost here","before the first boat","after a long watch","the end of another watch",
 "the quiet end of the night","the last quiet minutes of the night","the night finally quiet",
)
PEOPLE=(
 "room for one more","room for one more at the table","room for whoever comes next",
 "room for the next watch","room for the next pair of hands","room for each other",
 "a place for one more","a place for one more at the table","a place for whoever comes next",
 "a chair for the next watch","a chair for the next pair of hands","a place for everyone",
 "one more place at the table","one more chair at the table","an empty chair at the table",
 "the voices at the table","the last voices at the table","people making room for each other",
 "people making room for one another","everyone making room for each other",
 "somebody making room for one more","someone saving a place at the table",
 "one more cup at the table","one more mug at the table","the last cup at the table",
 "a mug waiting for the next watch","the last mugs beside the window","the little lamp still on",
 "the lamp still on for the next watch","the table waiting for the next watch",
 "the room ready for the next watch","the table full of voices","the room ready for the next pair of hands",
 "a place for the late watch","a place for everyone at the table",
 "somebody remembering the next watch","the next watch always welcome",
 "a place left for the next watch","the little light left on","the cups left out for the next watch",
 "the voices that are still at the table",
)
BRIDGES=(("","and"),("and","and"),("with","and"),("","with"),("and","with"),("and",""),("",""),("with","with"))
def captions():
 for sea,time,people in itertools.product(SEA,TIME,PEOPLE):
  for a,b in BRIDGES:
   yield " ".join(x for x in (sea,a,time,b,people) if x)
   yield " ".join(x for x in (time,a,sea,b,people) if x)
   yield " ".join(x for x in (time,a,people,b,sea) if x)
   yield " ".join(x for x in (people,a,sea,b,time) if x)
   yield " ".join(x for x in (sea,a,people,b,time) if x)
   yield " ".join(x for x in (people,a,time,b,sea) if x)
def main():
 t0=time.monotonic()
 seen=set()
 positive=normal(" ".join([SEA[0],"and",TIME[1],"and",PEOPLE[2]]))
 planted=hashlib.sha256(k08(positive)).digest()
 assert planted!=want
 synthetic=0;assignments=0
 for raw in captions():
  assignments+=1;s=normal(raw)
  if s in seen:continue
  seen.add(s)
  component=k08(s)
  digest=hashlib.sha256(component).digest()
  if digest==planted:synthetic+=1
  if digest==want:
   print(json.dumps({"result":"ORIGINAL_FOUND","phrase":s,"K08":component.hex().upper(),"assignments":assignments}))
   return
 assert synthetic==1
 print(json.dumps({"result":"NO_MATCH","assignments":assignments,"distinct":len(seen),"synthetic":synthetic,
                   "seconds":round(time.monotonic()-t0,2),"sea_forms":len(SEA),"time_forms":len(TIME),"people_forms":len(PEOPLE)}))
if __name__=="__main__":main()
