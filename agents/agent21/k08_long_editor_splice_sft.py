"""Original-source K08 15+-word literal editorial splice (single-file read-only test).

Windows/Linux: python k08_long_editor_splice_sft.py [evidence-root]
This tests an exploratory source-derived model, not an authenticated final quote.
"""
from __future__ import annotations
import hashlib
import hmac
import itertools
import re
import sys
import time
from pathlib import Path

NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")

def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

def note(text: str, number: int) -> list[str]:
    match = re.search(rf"(?m)^N{number:02d} / [^\n]+\n([^\n]+)", text)
    assert match, f"Missing N{number:02d}"
    return tokens(match.group(1).split(":", 1)[-1])

def spans(words: list[str], lo: int, hi: int, anchors: set[str]) -> list[str]:
    return [" ".join(words[i:i+n]) for n in range(lo, hi + 1)
            for i in range(len(words)-n+1) if anchors.intersection(words[i:i+n])]

def component(phrase: str) -> bytes:
    return hmac.digest(NONCE, phrase.encode("utf-8"), "sha256")[:16]

def run(root: Path) -> None:
    started = time.perf_counter()
    note_data = (root / "crew/noticeboard-and-desk-notes.txt").read_bytes()
    mail_data = (root / "mail/11.eml").read_bytes()
    assert hashlib.sha256(note_data).hexdigest() == NOTES_SHA
    assert hashlib.sha256(mail_data).hexdigest() == MAIL_SHA
    notes, mail = note_data.decode("utf-8"), mail_data.decode("utf-8")
    n02 = " ".join(note(notes, 2))
    assert component(n02).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    assert hashlib.sha256(component(n02)).digest() != TARGET

    n13 = note(notes, 13)
    n20 = note(notes, 20)
    assert (len(n13), len(n20)) == (22, 30)
    m = re.search(r"For this envelope\s+I wanted(.*?)\n\s*Emily\s*$", mail, re.S)
    assert m, "MAIL11's original caption description is missing"
    description = tokens("I wanted" + m.group(1))
    assert len(description) == 39

    scene = spans(n13, 9, 23, {"mugs", "window", "lamp"})
    sea = spans(n20, 3, 9, {"sea"})
    people = spans(description, 3, 9, {"room", "people"})
    assert (len(scene), len(sea), len(people)) == (105, 41, 55)
    pools = (scene, sea, people)
    joins = (" ", " and ")
    planted = scene[0] + " and " + sea[0] + " " + people[0]
    planted_digest = hashlib.sha256(component(planted)).digest()
    checks = matches = planted_matches = 0
    min_words, max_words = 999, 0

    for order in itertools.permutations((0, 1, 2)):
        for a, b, c in itertools.product(*(pools[i] for i in order)):
            for x, y in itertools.product(joins, repeat=2):
                phrase = a + x + b + y + c
                n = len(phrase.split())
                min_words, max_words = min(min_words, n), max(max_words, n)
                digest = hashlib.sha256(component(phrase)).digest()
                checks += 1
                if digest == planted_digest:
                    planted_matches += 1
                if digest == TARGET:
                    matches += 1
                    print("ORIGINAL_K08_HIT", phrase, component(phrase).hex().upper(), flush=True)
    assert checks == 5_682_600
    assert planted_matches == 1
    assert (min_words, max_words) == (15, 42)
    print(f"K08_LONG_EDITOR checks={checks} original_hits={matches} "
          f"planted_hits={planted_matches} min_words={min_words} "
          f"max_words={max_words} elapsed_s={time.perf_counter()-started:.3f}")

if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else
        Path(__file__).resolve().parents[2] / "resources/evidence")
