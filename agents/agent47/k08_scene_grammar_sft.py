"""H-17 K08 source-derived two- and three-scene free-clause SFT.

No original phrase is assumed. This is an exploratory finite syntactic family,
not a calibrated or attested historical writer. No evidence is modified.
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
EXPECTED_NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

SEA_SUBJECTS = (
    "the sea", "the water", "the sea outside", "the water outside",
    "the sea beyond the window", "the water beyond the window",
    "the sea outside the window", "the water past the window",
    "the night sea", "the horizon",
)
SEA_ACTIONS = (
    "goes quiet", "is quiet", "falls quiet", "turns quiet", "grows quiet",
    "is still", "waits outside", "turns pale", "begins to brighten",
    "keeps its own counsel", "is nearly still",
)
TIMES = (
    "", "at dawn", "at first light", "as the night ends",
    "at the end of the night", "when the night is almost finished",
    "before the first boat", "as morning comes", "after the last cup",
    "when the watch is nearly over",
)
PEOPLE_SUBJECTS = (
    "we", "the night crew", "the late watch", "the last watch",
    "the next watch", "the crew", "someone", "the voices at the table",
)
PEOPLE_ACTIONS = (
    "make room for each other", "leave room for each other",
    "leave a place for each other", "keep a place for each other",
    "leave room for the next watch", "make room for the next watch",
    "keep a place for the next watch", "make room for one another",
    "leave a place for one another", "keep room for the next pair of hands",
)
PEOPLE_PLACES = (
    "", "at the table", "by the window", "beside the window",
    "after a long watch", "after the last cup", "before morning",
    "while the lamp stays on",
)
LINKS = ("and", "while", "as", "when", "but", "so", "because", "until")
FRAMES = (
    "the little lamp stays on", "the lamp stays on",
    "the mugs wait by the window", "the voices are still at the table",
    "the corridor grows quiet",
)


def normalize(phrase):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", phrase.lower()).split())


def component(phrase, nonce):
    return hmac.digest(nonce, normalize(phrase).encode(), "sha256")[:16]


def main():
    notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == EXPECTED_NOTES_SHA
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert component("A good watch leaves the room ready for the next pair of hands.", nonce).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    planted = "the sea is quiet at dawn while we leave room for each other at the table"
    positive = hashlib.sha256(component(planted, nonce)).digest()
    sea = tuple((a + " " + b + " " + c).strip()
                for a, b, c in itertools.product(SEA_SUBJECTS, SEA_ACTIONS, TIMES))
    people = tuple((a + " " + b + " " + c).strip()
                   for a, b, c in itertools.product(PEOPLE_SUBJECTS, PEOPLE_ACTIONS, PEOPLE_PLACES))
    hits = []
    positives = 0
    n = 0
    for s, p, link in itertools.product(sea[:220], people[:240], LINKS):
        for phrase in (s + " " + link + " " + p, p + " " + link + " " + s):
            result = hashlib.sha256(component(phrase, nonce)).digest()
            n += 1
            if result == target:
                hits.append(phrase)
            if result == positive:
                positives += 1
    two_scene = n
    for s, p, link, frame in itertools.product(sea[:220], people[:240], LINKS[:4], FRAMES):
        for phrase in (s + " " + link + " " + p + " and " + frame,
                       p + " " + link + " " + s + " and " + frame):
            result = hashlib.sha256(component(phrase, nonce)).digest()
            n += 1
            if result == target:
                hits.append(phrase)
            if result == positive:
                positives += 1
    assert n == 2956800
    assert positives == 1
    print(json.dumps({
        "two_scene_complete_candidates": two_scene,
        "three_scene_complete_candidates": n - two_scene,
        "total_complete_candidates": n,
        "real_K08_matches": hits,
        "planted_positive_matches": positives,
    }, indent=2))


if __name__ == "__main__":
    main()
