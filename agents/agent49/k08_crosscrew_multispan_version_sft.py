"""K08 N13 two-role editorial replacement using original crew photo and galley captions.

Source-only vocabulary and full original HMAC/SHA commitment; no archive writes.
Run: python agents/agent49/k08_crosscrew_multispan_version_sft.py
"""
from __future__ import annotations
import hashlib
import hmac
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")

def note(src: str, n: int) -> tuple[str, ...]:
    match = re.search(r"(?m)^N%02d /[^\n]+\n([^\n]+)" % n, src)
    assert match
    return tuple(re.findall(r"[a-z0-9]+", match.group(1).split(":", 1)[-1].lower()))

def fragments(src: str, ids: tuple[int, ...], anchors: set[str]) -> list[tuple[str, ...]]:
    return sorted({tokens[i:i+n]
                   for ident in ids for tokens in [note(src, ident)]
                   for n in range(2, 8)
                   for i in range(len(tokens)-n+1)
                   if anchors.intersection(tokens[i:i+n])})

def digest(phrase: str) -> bytes:
    return hashlib.sha256(hmac.digest(NONCE, phrase.encode("ascii"), "sha256")[:16]).digest()

def run() -> None:
    blob = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == NOTES_SHA
    source = blob.decode("utf-8")
    n13 = note(source, 13)
    assert len(n13) == 22 and n13[:6] == ("at", "the", "end", "of", "the", "night")
    assert hmac.digest(NONCE, " ".join(note(source, 2)).encode("ascii"), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    sea = fragments(source, (1, 8, 14), {"sea", "water", "daylight", "horizon", "rain", "window", "outside", "night", "boat"})
    care = fragments(source, (3, 4, 9, 11, 19), {"cup", "mugs", "chair", "head", "heads", "someone", "somebody", "alone", "sat", "down", "blue", "belongs", "bed", "needs", "one"})
    cuts = [(a, b, c, d) for a in range(6, 9) for b in range(10, 15)
            for c in range(12, 17) for d in range(19, 23) if a < b <= c < d]
    assert (len(sea), len(care), len(cuts)) == (88, 183, 264)
    a, b, c, d = cuts[3]
    plant = " ".join(n13[:a] + sea[16] + n13[b:c] + care[53] + n13[d:])
    planted_target = digest(plant)
    total = original = positive = 0
    for a, b, c, d in cuts:
        for s in sea:
            left = n13[:a] + s + n13[b:c]
            for p in care:
                phrase = " ".join(left + p + n13[d:])
                out = digest(phrase)
                total += 1
                if out == TARGET:
                    original += 1
                    print("ORIGINAL_K08_HIT", repr(phrase), flush=True)
                if out == planted_target:
                    assert phrase == plant
                    positive += 1
    assert (total, positive, original) == (4251456, 1, 0)
    print("K08_CROSSCREW_MULTISPAN assignments", total, "original_matches", original,
          "synthetic_positive", positive)

if __name__ == "__main__":
    run()
