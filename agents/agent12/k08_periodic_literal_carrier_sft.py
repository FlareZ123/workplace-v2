"""Source-driven K08 search for literal envelope text under short repeating-byte encoders.

Reads the untouched H17 evidence; no candidate or commitment files are modified.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import re
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2] if (Path(__file__).resolve().parents[2] / 'resources/evidence').is_dir() else Path(__file__).resolve().parent
EVIDENCE = ROOT / 'resources/evidence' if (ROOT / 'resources/evidence').is_dir() else ROOT / 'evidence'
ACCEPTANCE = ROOT / 'resources/acceptance.json' if (ROOT / 'resources/acceptance.json').exists() else ROOT / 'acceptance.json'
NONCE = bytes.fromhex('5F933DA6A1BD03C32DA5CBC25344F497')
EXPECTED = '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
KNOWN = [
    b'Leave the light on for the next watch.',
    b'Back before the first boat.',
    b'A good watch leaves the room ready for the next pair of hands.',
    b'The little lamp stays on until the corridor has gone quiet.'
]

def normalize(s: str) -> str:
    return ' '.join(re.sub(r'[^a-z0-9\s]', ' ', s.lower()).split())

def check(text: str) -> bool:
    norm=normalize(text)
    return len(norm.split())>=2 and hashlib.sha256(hmac.new(NONCE,norm.encode('utf-8'),hashlib.sha256).digest()[:16]).hexdigest()==EXPECTED

def source_files() -> list[tuple[str,bytes]]:
    return [(str(x.relative_to(ROOT)),x.read_bytes()) for x in sorted(EVIDENCE.rglob('*')) if x.is_file()]

def match_repeat(raw: bytes, known: bytes, max_period: int=16):
    """Detect all bytewise XOR or subtraction periodic encodings, including exact copies."""
    dat=np.frombuffer(raw,dtype=np.uint8)
    pt=np.frombuffer(known,dtype=np.uint8)
    n=len(pt)
    if len(dat)<n: return
    for operation in ('xor','subtract'):
        for period in range(1,min(max_period,n-12)+1):
            diffs=(np.bitwise_xor(dat[period:],dat[:-period]) if operation=='xor' else dat[period:]-dat[:-period])
            keydif=(np.bitwise_xor(pt[period:],pt[:-period]) if operation=='xor' else pt[period:]-pt[:-period])
            # All n-period equalities of repeat keys must hold at the same start.
            candidates=np.ones(len(dat)-n+1,dtype=np.bool_)
            for i,k in enumerate(keydif):
                candidates &= diffs[i:i+len(candidates)]==k
                if not candidates.any():break
            for pos in np.flatnonzero(candidates):
                raw_key=dat[pos:pos+period]
                key=np.bitwise_xor(raw_key,pt[:period]) if operation=='xor' else raw_key-pt[:period]
                yield operation,period,int(pos),key.tobytes()

# Allowed decoded natural caption chars: letters/digits/space and standard sentence punctuation.
ALLOWED=bytes(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.!?;:'\"()-")
PRINTABLE=set(range(32,127)) | {9,10,13}
KEYMASK={op:{b:sum(1 << k for k in range(256) if (b^k if op=='xor' else (b-k)&255) in ALLOWED) for b in range(256)} for op in ('xor','subtract')}

def find_encoded_windows(raw:bytes, min_length:int=64, max_period:int=8, operation:str='xor'):
    """Find long windows permitting repeating XOR/additive plaintext in caption alphabet.
    This is independent of a proposed wording; every possible per-lane key is allowed.
    Require at least one ciphertext byte outside ASCII printables, to avoid trivial
    source prose and to make the scope of this binary-carrier screen explicit.
    """
    for start in range(len(raw)-min_length+1):
        block=raw[start:start+min_length]
        # Avoid spending time on unencoded plain original prose.
        if all(b in PRINTABLE for b in block):continue
        for p in range(1,max_period+1):
            keys=[]
            for r in range(p):
                mask=(1<<256)-1
                for b in block[r::p]:
                    mask &= KEYMASK[operation][b]
                    if not mask:break
                if not mask:break
                keys.append(mask)
            if len(keys)==p:
                # Reconstruct one candidate using ordinary letter/space plausibility.
                key=[]
                for r,mask in enumerate(keys):
                    choices=[k for k in range(256) if (mask>>k)&1]
                    # Typical English symbols: letters and space win, but preserve other candidates.
                    def score(k):
                        d=[b^k if operation=='xor' else (b-k)&255 for b in block[r::p]]
                        return sum(5 if x==32 else 4 if x in b'etaoinshrdluETAOINSHRDLU' else 1 if x in b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' else -2 for x in d)
                    key.append(max(choices,key=score))
                yield start,p,bytes(key),bytes(b^key[i%p] if operation=='xor' else (b-key[i%p])&255 for i,b in enumerate(block))

def main():
    assert hashlib.sha256((EVIDENCE/'crew/noticeboard-and-desk-notes.txt').read_bytes()).hexdigest()=='13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
    assert json.loads(ACCEPTANCE.read_text(encoding='utf-8'))['slot_sha256']['K08']==EXPECTED
    assert check('A good watch leaves the room ready for the next pair of hands.') is False
    sources=source_files()
    print('SOURCE_FILES',len(sources),'BYTES',sum(len(x) for _,x in sources))
    known_hits=[]
    for name,raw in sources:
        for phrase in KNOWN:
            for op,p,pos,key in match_repeat(raw,phrase):
                known_hits.append((name,phrase.decode(),op,p,pos,key.hex()))
    distinct={ (n,t,op,off,k) for n,t,op,p,off,k in known_hits }
    print('KNOWN_LABEL_MATCHES',len(known_hits),'distinct',len(distinct), 'nonzero_pad', sum(int(any(bytes.fromhex(v[5]))) for v in known_hits))
    for item in known_hits[:4]:print('KNOWN_CONTROL',item)
    unknown_hits=[]; accepted=[]; scanned=0
    for operation in ('xor','subtract'):
        for min_length,period in ((48,4),(64,8)):
            sub=0
            for name,raw in sources:
                for pos,p,key,plain in find_encoded_windows(raw,min_length,period,operation):
                    scanned+=1; sub+=1
                    text=plain.decode('ascii')
                    if text.count(' ')<5:continue
                    unknown_hits.append((name,operation,min_length,pos,p,key.hex(),text))
                    if check(text): accepted.append((name,operation,min_length,pos,p,key.hex(),text))
            print('FEASIBLE_ENCODED_WINDOWS',operation,min_length,period,sub)
    print('TOTAL_FEASIBLE',scanned,'english_like',len(unknown_hits),'original_K08_hits',len(accepted))
    for hit in unknown_hits[:30]:print('WINDOW',hit)
    for hit in accepted:print('K08_PASS',hit)
    # Genuine encoded original label inserted into binary with a nonzero period-4 key.
    planted=bytes((c^b'ABCD'[i%4]) for i,c in enumerate(KNOWN[0]))
    positives=[m for m in match_repeat(b'\x01\x00'+planted+b'\x01',KNOWN[0]) if m[0]=='xor' and m[1]==4 and m[2]==2 and m[3]==b'ABCD']
    assert positives, 'known-caption encoded control was not detected'
    print('PLANTED_PERIOD4_KNOWN_POSITIVE',len(positives))
    long_phrase=KNOWN[2]+b' The little lamp stays on until the corridor has gone quiet.'
    planted_long=bytes(c^b'ABCD'[i%4] for i,c in enumerate(long_phrase))
    probe=b'\x00\x01\x02'*9+planted_long+b'\x00\x01'
    long_hits=[h for h in find_encoded_windows(probe,64,8,'xor') if h[0]==27 and h[1]==4 and h[2]==b'ABCD' and h[3]==long_phrase[:64]]
    assert long_hits, 'arbitrary-plaintext periodic decoder did not detect positive'
    print('PLANTED_PERIOD4_UNKNOWN_POSITIVE',len(long_hits))
    add_planted=bytes((c+b'ABCD'[i%4])&255 for i,c in enumerate(long_phrase))
    add_probe=b'\x00\x01\x02'*9+add_planted+b'\x00\x01'
    add_hits=[h for h in find_encoded_windows(add_probe,64,8,'subtract') if h[0]==27 and h[1]==4 and h[2]==b'ABCD' and h[3]==long_phrase[:64]]
    assert add_hits,'additive unknown-caption detector failed planted positive'
    print('PLANTED_PERIOD4_ADD_UNKNOWN_POSITIVE',len(add_hits))

if __name__=='__main__':main()
