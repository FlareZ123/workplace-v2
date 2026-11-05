"""Source-pinned exact old-code-page K08 plaintext screen.

Reads the original supplied ZIP at H17_ZIP; standard-library only.
"""
from hashlib import sha256
import hmac
import os
import re
from zipfile import ZipFile

NONCE=bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET=bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
CODECS=("cp037","cp500","cp1026","cp1140")

def candidates(text):
    for match in re.finditer("[A-Za-z0-9 ,.;:!'\"()?!/-]{14,}",text):
        words=re.findall("[A-Za-z0-9]+",match.group().lower())
        for i in range(len(words)):
            for j in range(i+2,min(len(words),i+24)+1):
                v=" ".join(words[i:j]).encode("ascii")
                if len(v)>=14:
                    yield v

def main():
    with ZipFile(os.environ.get("H17_ZIP","h17-archive-dump.zip")) as z:
        assert sha256(z.read("evidence/crew/noticeboard-and-desk-notes.txt")).hexdigest()=="13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
        originals=[z.read(n) for n in z.namelist() if n.startswith("evidence/") and not n.endswith("/")]
    phrase=b"leave the light on for the next watch"
    assert phrase in set(candidates(phrase.decode("ascii").encode("cp500").decode("cp500")))
    found=set()
    per_codec={}
    for codec in CODECS:
        texts=set()
        for blob in originals:
            texts.update(candidates(blob.decode(codec,"strict")))
        per_codec[codec]=len(texts)
        found.update(texts)
    hits=[x for x in found if sha256(hmac.new(NONCE,x,sha256).digest()[:16]).digest()==TARGET]
    assert len(originals)==42 and not hits and not found
    print("synthetic_cp500_original_label PASS, evidence_files",len(originals))
    print("candidate_counts",per_codec,"authentic_hits",len(hits))

if __name__=="__main__":main()
