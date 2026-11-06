"""Source-pinned, read-only H-17 K08 anthropomorphic-caretaker caption SFT."""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
notes = (ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
mail11 = (ROOT/"evidence/mail/11.eml").read_bytes()
assert hashlib.sha256(notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert hashlib.sha256(mail11).hexdigest() == "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
assert all(p in notes.lower() for p in [b"good watch leaves the room ready for the next pair of hands", b"little lamp stays on until the corridor has gone quiet", b"voices at the table"])
assert b"water outside and the night almost finished" in mail11.lower()
route = json.loads((ROOT/"evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT/"acceptance.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target = accept["slot_sha256"]["K08"]
assert target == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"

def norm(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def component(s):
    return hmac.digest(nonce, norm(s).encode(), "sha256")[:16]

assert component("A good watch leaves the room ready for the next pair of hands.").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

SUBJECTS = [
    "the sea", "the water", "the water outside", "the sea outside",
    "the little lamp", "the lamp", "the lamp by the window",
    "the light", "the light by the window", "the last cup",
    "the mugs", "the window", "a good watch", "the night",
    "the last light", "the quiet room",
]
PREDICATES = ["leaves", "keeps", "holds", "saves", "remembers",
              "makes", "keeps open", "leaves open", "keeps ready", "leaves ready"]
OBJECTS = [
    "a place", "a place at the table", "room", "the room",
    "room at the table", "the table", "a cup", "one more cup",
    "a seat", "one more seat", "the light on", "the lamp on",
    "the mugs", "the voices", "a space", "a place by the window",
]
BENEFICIARIES = [
    "", "for us", "for everyone", "for one another", "for each other",
    "for the next watch", "for the late watch", "for the last watch",
    "for the late crew", "for the next pair of hands",
    "for whoever comes next", "for someone coming in", "for another cup",
    "for the people at the table", "for the voices at the table",
]
TEMPORAL = [
    "", "after the long watch", "after a long watch", "after the last cup",
    "at the end of the night", "as the night ends", "while the sea is outside",
    "while the water is outside", "while the night is almost finished",
    "when the night is nearly over", "before the morning", "before dawn",
    "until the corridor has gone quiet", "until the night is over",
    "until the night is almost finished", "until the last watch is over",
    "until we are all home", "as the water turns blue",
]
planted = "the sea keeps room at the table for the late crew after a long watch"
planted_hash = hashlib.sha256(component(planted)).hexdigest()
seen = set()
matches = []
controls = 0
assignments = 0
for args in itertools.product(SUBJECTS, PREDICATES, OBJECTS, BENEFICIARIES, TEMPORAL):
    assignments += 1
    candidate = norm(" ".join(x for x in args if x))
    if candidate in seen:
        continue
    seen.add(candidate)
    digest = hashlib.sha256(component(candidate)).hexdigest()
    if digest == target:
        matches.append(candidate)
    if digest == planted_hash:
        controls += 1
assert assignments == len(seen) == 691200
assert controls == 1
print(json.dumps({"original_matches":matches, "unique":len(seen), "synthetic_hits":controls, "source":"original"}))
