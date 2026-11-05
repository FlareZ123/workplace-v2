"""Detect a literal H17 K08 inscription serialized at a non-byte-aligned bit offset.

Original sources, K08 nonce and official acceptance digest are read-only.
Run: python agents/agent3/k08_original_bitserial_literal_sft.py
"""
import hashlib
import hmac
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
REVERSE = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))
DRAFT = b"a good watch leaves the room ready for the next pair of hands"

def source_streams():
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        yield str(path.relative_to(EVIDENCE)), raw
        for found in re.finditer(rb"(?<![0-9a-fA-F])[0-9a-fA-F]{16,}(?![0-9a-fA-F])", raw):
            if len(found.group()) % 2 == 0:
                yield f"{path.relative_to(EVIDENCE)}:hex:{found.start()}", bytes.fromhex(found.group().decode("ascii"))

def transform(raw, offset):
    return bytes(((raw[i] << offset) & 255) | (raw[i+1] >> (8-offset)) for i in range(len(raw)-1))

def phrases(raw, offset, output_reversed):
    moved = transform(raw, offset)
    if output_reversed:
        moved = moved.translate(REVERSE)
    for found in re.finditer(rb"[\x20-\x7e]{16,}", moved):
        normalized = re.sub(rb"[^a-z0-9\s]", b" ", found.group().lower())
        words = normalized.split()
        for i in range(len(words)):
            for n in range(2, min(32,len(words)-i)+1):
                phrase = b" ".join(words[i:i+n])
                if len(phrase) >= 9:
                    yield phrase

def reduction(phrase):
    return hashlib.sha256(hmac.new(NONCE,phrase,hashlib.sha256).digest()[:16]).digest()

def insert_shifted(plain, offset):
    bits = "1" * offset + "".join(f"{x:08b}" for x in plain) + "0" * (8-offset)
    return bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8))

def main():
    assert hashlib.sha256((EVIDENCE/"crew"/"noticeboard-and-desk-notes.txt").read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    assert hmac.new(NONCE,DRAFT,hashlib.sha256).digest()[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    for offset,flip in ((3,0),(5,1)):
        encoded = insert_shifted(DRAFT.translate(REVERSE) if flip else DRAFT,offset)
        assert transform(encoded,offset).translate(REVERSE if flip else bytes(range(256))) == DRAFT
        positives = sum(p == DRAFT and reduction(p) == reduction(DRAFT) for p in phrases(encoded,offset,flip))
        assert positives == 1, (offset,flip,positives)
    print("SYNTHETIC_COMPLETE_CAPTION_CONTROLS=2 PASS",flush=True)

    source = list(source_streams())
    assert len(source) == 189 and sum(len(b) for _,b in source) == 114964
    unique = set()
    matches = []
    started = time.monotonic()
    for name,raw in source:
        if len(raw) < 33:
            continue
        for source_reversed,view in ((0,raw),(1,raw.translate(REVERSE))):
            for offset in range(1,8):
                for output_reversed in (0,1):
                    for phrase in phrases(view,offset,output_reversed):
                        if phrase in unique:
                            continue
                        unique.add(phrase)
                        if reduction(phrase) == TARGET:
                            matches.append((name,source_reversed,offset,output_reversed,phrase.decode("ascii")))
    assert len(unique) == 749, len(unique)
    assert not matches, matches
    print("SOURCE_STREAMS",len(source),"UNIQUE_ORIGINAL_COMPLETE_K08_CHECKS",len(unique),"ORIGINAL_MATCHES",len(matches),"SECONDS",round(time.monotonic()-started,2))

if __name__ == "__main__":
    main()
