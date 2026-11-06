"""K08 two-role multiword replacement in original Emily N13; no source writes.
Usage: python agents/agent49/k08_two_role_multispan_editor_sft.py resources
"""
from __future__ import annotations
import hashlib
import hmac
import re
import sys
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")

def words(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", text.lower()))

def note(src: str, index: int) -> tuple[str, ...]:
    m = re.search(r"(?m)^N%02d /[^\n]+\n([^\n]+)" % index, src)
    assert m
    return words(m.group(1).split(":", 1)[-1])

def pool(sources: tuple[tuple[str, ...], ...], anchors: frozenset[str]) -> list[tuple[str, ...]]:
    out = set()
    for source in sources:
        for n in range(2, 10):
            for i in range(len(source) - n + 1):
                w = source[i:i+n]
                if anchors.intersection(w):
                    out.add(w)
    return sorted(out)

def component(phrase: str) -> bytes:
    return hmac.digest(NONCE, phrase.encode("ascii"), "sha256")[:16]

def run(root: Path) -> None:
    nb = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    mb = (root / "evidence/mail/11.eml").read_bytes()
    assert hashlib.sha256(nb).hexdigest() == NOTES_SHA
    assert hashlib.sha256(mb).hexdigest() == MAIL_SHA
    notes, mail = nb.decode(), mb.decode()
    assert component(" ".join(note(notes, 2))).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    n13, n20 = note(notes, 13), note(notes, 20)
    assert len(n13) == 22 and len(n20) == 30
    assert n13[:6] == ("at", "the", "end", "of", "the", "night")
    assert n13[6:12] == ("the", "mugs", "stood", "beside", "the", "window")
    assert n13[12:] == ("and", "somebody", "had", "remembered", "to", "leave", "the", "little", "lamp", "on")
    match = re.search(r"For this envelope\s+I wanted(.*?)\n\s*Emily\s*$", mail, re.S)
    assert match
    purpose = words("I wanted" + match.group(1))
    assert all(x in purpose for x in ("people", "water", "outside"))
    n20_scene = n20[:19]
    assert n20_scene[-5:] == ("the", "voices", "at", "the", "table")
    source = (n20_scene, purpose)
    sea = pool(source, frozenset(("sea", "water", "outside")))
    people = pool(source, frozenset(("voices", "table", "people", "room", "each", "other")))
    assert len(sea) == 95 and len(people) == 114
    boundaries = [(a, b, c, d) for a in range(6, 9) for b in range(10, 15)
                  for c in range(12, 17) for d in range(19, 23) if a < b <= c < d]
    assert len(boundaries) == 264
    a, b, c, d = boundaries[11]
    planted = " ".join(n13[:a] + sea[13] + n13[b:c] + people[27] + n13[d:])
    planted_hash = hashlib.sha256(component(planted)).digest()
    unique: set[str] = set()
    original_hits = positives = checks = 0
    for a, b, c, d in boundaries:
        for s in sea:
            left = n13[:a] + s + n13[b:c]
            for p in people:
                phrase = " ".join(left + p + n13[d:])
                unique.add(phrase)
                digest = hashlib.sha256(component(phrase)).digest()
                checks += 1
                if digest == TARGET:
                    original_hits += 1
                    print("ORIGINAL_K08_HIT", repr(phrase), component(phrase).hex().upper(), flush=True)
                if digest == planted_hash:
                    positives += 1
                    assert phrase == planted
    assert checks == 2859120 and positives == 1
    assert len(unique) == 2215036
    fingerprint = hashlib.sha256()
    for phrase in sorted(unique):
        fingerprint.update(phrase.encode("ascii") + b"\n")
    assert fingerprint.hexdigest() == "42f32d94a966fe623fbf0df897d585cff3f8c177372915f1cec5eff678769105"
    print("K08_TWO_ROLE_MULTISPAN_EDITOR", "assignments", checks,
          "unique_normalized", len(unique), "source_set_sha256", fingerprint.hexdigest(),
          "original_hits", original_hits, "synthetic_positive", positives)

if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources")
