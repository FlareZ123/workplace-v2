"""K08 crib-key cancellation: read-only source decoder and complete HMAC check."""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
ACCEPTANCE = ROOT / "resources/acceptance.json"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
# Exact contiguous original-source snippets from crew notes or MAIL11/20.
CRIBS = (
    "end of the night", "at the end of the night", "the voices at the table",
    "people making room for each other", "room for one another",
    "after a long watch", "the water outside", "the night almost finished",
    "the last cup", "the little lamp", "the corridor has gone quiet",
    "the next pair of hands", "the next watch", "before the first boat",
    "the sea looks different", "the water gives back",
    "nobody should have to make their first cup alone",
    "leave the light on for the next watch", "back before the first boat",
    "a good watch leaves the room ready for the next pair of hands",
    "the little lamp stays on until the corridor has gone quiet",
)
ALLOWED = frozenset(range(32,127)) | {9,10,11,12,13}
WORD = re.compile(r"[a-z0-9]+")


def norm(value: str) -> bytes:
    return " ".join(WORD.findall(value.lower())).encode("utf-8")


def component(value: str) -> bytes:
    return hmac.new(NONCE, norm(value), "sha256").digest()[:16]


def digest(value: str) -> str:
    return hashlib.sha256(component(value)).hexdigest()


def decode_byte(b: int, key: int, op: str) -> int:
    return b ^ key if op == "xor" else (b-key)&255


def possible_window(raw: bytes, start: int, crib: bytes, p: int, op: str) -> bytes | None:
    if op == "xor":
        if any((raw[start+j]^raw[start+j-p]) != (crib[j]^crib[j-p]) for j in range(p,len(crib))):
            return None
        return bytes(raw[start+j]^crib[j] for j in range(p))
    if any((raw[start+j]-raw[start+j-p])%256 != (crib[j]-crib[j-p])%256 for j in range(p,len(crib))):
        return None
    return bytes((raw[start+j]-crib[j])&255 for j in range(p))


def expand(raw: bytes, start: int, crib: bytes, key: bytes, op: str, limit: int=160) -> str:
    p=len(key)
    l=start
    while l>0 and start-l<limit and decode_byte(raw[l-1],key[(l-1-start)%p],op) in ALLOWED:
        l-=1
    r=start+len(crib)
    while r<len(raw) and r-start<len(crib)+limit and decode_byte(raw[r],key[(r-start)%p],op) in ALLOWED:
        r+=1
    return bytes(decode_byte(raw[j],key[(j-start)%p],op) for j in range(l,r)).decode("ascii")


def scan(raw: bytes, source: str, target: str=TARGET, max_period: int=8, max_length: int=160):
    hits=[]
    matches=0
    candidate_count=0
    target_hits=[]
    cribs={v for phrase in CRIBS for v in (phrase.encode(),phrase.lower().encode(),phrase.upper().encode(),phrase.capitalize().encode())}
    for p in range(1,max_period+1):
        if len(raw)<p+2:
            continue
        for op in ("xor","subtract"):
            # A lag-p difference cancels ANY repeating key of period p.
            # This permits fast key-independent needle lookup without
            # generating a guessed terminal keeper caption.
            if op=="xor":
                differences=bytes(raw[i+p]^raw[i] for i in range(len(raw)-p))
            else:
                differences=bytes((raw[i+p]-raw[i])&255 for i in range(len(raw)-p))
            for crib in cribs:
                if len(crib)<2*p:
                    continue
                if op=="xor":
                    needle=bytes(crib[i+p]^crib[i] for i in range(len(crib)-p))
                else:
                    needle=bytes((crib[i+p]-crib[i])&255 for i in range(len(crib)-p))
                at=differences.find(needle)
                while at>=0:
                    key=possible_window(raw,at,crib,p,op)
                    assert key is not None
                    if any(key):
                        matches+=1
                        expanded=expand(raw,at,crib,key,op,max_length)
                        words=WORD.findall(expanded.lower())
                        if len(words)>1:
                            candidates={norm(" ".join(words[i:j])).decode() for i in range(len(words)) for j in range(i+2,min(len(words)+1,i+33))}
                            candidate_count+=len(candidates)
                            for cand in candidates:
                                if digest(cand)==target:
                                    target_hits.append((source,op,p,at,crib.decode(),key.hex(),cand))
                        if len(hits)<12:
                            hits.append((source,op,p,at,crib.decode(),key.hex(),expanded[:160]))
                    at=differences.find(needle,at+1)
    return matches,candidate_count,hits,target_hits


def main():
    assert hashlib.sha256((EVIDENCE/"crew/noticeboard-and-desk-notes.txt").read_bytes()).hexdigest()==NOTES_SHA
    assert json.loads(ACCEPTANCE.read_text(encoding="utf-8"))["slot_sha256"]["K08"]==TARGET
    assert component("A good watch leaves the room ready for the next pair of hands.").hex().upper()=="BF889359B0303F2B2B2FD96AE841210B"
    total=[0,0,0]
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():
            continue
        m,n,hits,accepted=scan(path.read_bytes(),str(path.relative_to(EVIDENCE)))
        if m or accepted:
            print("SOURCE",path.relative_to(EVIDENCE),"periodic_matches",m,"candidate_checks",n,
                  "examples",hits[:4],"ACCEPTED",accepted,flush=True)
        total[0]+=m;total[1]+=n;total[2]+=len(accepted)
    print("ORIGINAL_TOTAL",total,"TARGET_MATCHES",total[2])
    assert total==[8,30,0],total
    phrase="At the end of the night there was always room for one another at the table."
    key=b"SAVE"
    for op in ("xor","subtract"):
        data=phrase.encode()
        encrypted=bytes(b^key[i%4] if op=="xor" else (b+key[i%4])&255 for i,b in enumerate(data))
        m,n,hits,accepted=scan(encrypted,"SYNTHETIC",target=digest(phrase))
        assert any(v[-1]==norm(phrase).decode() and v[1]==op for v in accepted),(op,m,n,accepted)
        print("SYNTHETIC",op,"PASS","target_hits",len(accepted))


if __name__=="__main__":
    main()
