"""Original H17 author-final K08 first/last text-line margin carrier pilot.

No free-form caption phrases: only contiguous 2..40-word windows of first/last
physical-line words and two original numbered-note edge columns. Read-only.
"""
from hashlib import sha256
from hmac import new as hmac_new
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2] / "resources/evidence"
crew=ROOT / "crew/noticeboard-and-desk-notes.txt"
assert sha256(crew.read_bytes()).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
nonce=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
target=bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+",s.lower()))
def hashed(s):
    return sha256(hmac_new(nonce,norm(s).encode(),"sha256").digest()[:16]).digest()
assert hmac_new(nonce,norm("A good watch leaves the room ready for the next pair of hands.").encode(),"sha256").hexdigest()[:32].upper()=="BF889359B0303F2B2B2FD96AE841210B"
texts={str(p.relative_to(ROOT)):p.read_text(errors="replace") for p in (ROOT/"mail").glob("*.eml")}
texts["crew/noticeboard-and-desk-notes.txt"]=crew.read_text()
phrases=set()
channels=[]
for name,full in sorted(texts.items()):
    if name.endswith(".eml"):
        full=full.split("\n\n",1)[1]
    for pi,par in enumerate(full.split("\n\n")):
        lines=[line for line in par.splitlines() if re.search(r"[A-Za-z0-9]",line)]
        if len(lines)<2:
            continue
        first=[]
        last=[]
        for line in lines:
            words=re.findall("[a-z0-9]+",line.lower())
            if words:
                first.append(words[0])
                last.append(words[-1])
        for label,stream in (("first",first),("last",last)):
            channels.append((name,pi,label,stream))
            for direction in (stream,stream[::-1]):
                for i in range(len(direction)):
                    for j in range(i+2,min(i+41,len(direction)+1)):
                        phrases.add(" ".join(direction[i:j]))
notes=[re.findall("[a-z0-9]+",b.lower()) for b in re.findall(r"N\d\d /[^\n]+\n([^\n]+)",crew.read_text())]
assert len(notes)==24
for tag,docs in (("all",notes),("emily",[notes[i-1] for i in (2,6,10,13,17,18,20,23)])):
    for loc in ("first","last"):
        stream=[v[0] if loc=="first" else v[-1] for v in docs]
        channels.append(("Nseries",tag,loc,stream))
        for direction in (stream,stream[::-1]):
            for i in range(len(direction)):
                for j in range(i+2,len(direction)+1):
                    phrases.add(" ".join(direction[i:j]))
hits=[v for v in sorted(phrases) if hashed(v)==target]
source_caption="A good watch leaves the room ready for the next pair of hands"
lines=[w+" witness" for w in norm(source_caption).split()]
planted=" ".join(re.findall("[a-z0-9]+",line)[0] for line in lines)
assert planted==norm(source_caption) and hashed(planted)==hashed(source_caption)
assert len(channels)==170 and len(phrases)==2446 and not hits
print(f"CREW_SHA_PASS channels={len(channels)} candidate_phrases={len(phrases)} "
      f"original_K08_hits={len(hits)} planted_caption_pass=True")
