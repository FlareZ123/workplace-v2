"""K08 alternate envelope genre: short second-person invitation captions.

A speculative author/editor mechanism: Emily's old labels N17 and N18 use a
short direct-address/imperative voice, whereas N20 gives sea/night/people
imagery for the final line. Original final words are unobserved.
Run from repo root: python agents/agent18/k08_direct_address_editor_sft.py.
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
assert hashlib.sha256(notes).hexdigest() == (
    "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
)
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acc = json.loads((ROOT / "acceptance.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(acc["slot_sha256"]["K08"])

def norm(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def component(s):
    return hmac.digest(nonce, norm(s).encode("utf-8"), "sha256")[:16]

assert component("A good watch leaves the room ready for the next pair of hands.").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

INVITE = (
    "there is room for you at the table",
    "there is always room for one more at the table",
    "we made room for you at the table",
    "we have kept a place at the table for you",
    "we have saved you a place by the window",
    "we kept a light on for you",
    "someone has saved you the last chair",
    "somebody has kept your cup warm",
    "there is still a chair for you",
    "come in and take a seat",
    "come and sit with us",
    "pull up a chair and stay awhile",
    "there is a place for you among us",
    "you are welcome at this table",
    "the table is waiting for you",
    "we are waiting for you at the table",
    "you will always find room here",
    "you are never too late for a cup",
    "make yourself room at the table",
    "there is still room for your voice",
    "the last chair is for you",
    "this place was kept for you",
    "we leave the last light on for you",
    "there is room for whoever comes next",
)
TIME = (
    "when the night is almost over",
    "as the night is nearly done",
    "at the end of a long watch",
    "after a long watch",
    "when the long watch has ended",
    "before the first light",
    "after the last cup",
    "when morning is almost here",
    "at the end of the night",
    "while the night is nearly finished",
    "after the night watch",
    "when the late watch comes home",
    "when the watch is done",
    "before the first boat",
)
SEA = (
    "the sea is still outside",
    "the water is outside the window",
    "the sea is beyond the window",
    "the sea is waiting for morning",
    "the sea can wait until morning",
    "the water is turning toward daylight",
    "the sea is quiet beyond the glass",
    "the water has begun to lighten",
    "the sea is turning pale",
    "the sea is there beyond the window",
    "the sea has not gone anywhere",
    "the water is still dark outside",
)
VOICES = (
    "we are still here",
    "the voices are still at the table",
    "you can hear the last voices",
    "the last voices have gone quiet",
    "we can still hear each other",
    "you can hear the people at the table",
    "there are voices by the window",
    "there is still a voice beside yours",
    "we are here to listen",
    "the mugs are still warm",
    "the light is still on",
    "someone is still at the table",
)

def phrases():
    for a,t,s,v in itertools.product(INVITE,TIME,SEA,VOICES):
        yield f"{t}, {a}, while {s} and {v}."
        yield f"{a} {t}; {s} and {v}."
        yield f"{s} {t}, and {a} while {v}."
        yield f"{v} {t}; {a} while {s}."
        yield f"{a} as {s}, and {v} {t}."
    for a,t,s in itertools.product(INVITE,TIME,SEA):
        yield f"{a} {t}, while {s}."
        yield f"{s}, and {a} {t}."
        yield f"{t}, {a} because {s}."
        yield f"{a}. {s} {t}."

planted = norm(next(phrases()))
planted_commitment = hashlib.sha256(component(planted)).digest()
assert planted_commitment != target
unique = set()
count = positive = 0
hits = []
for phrase in phrases():
    n = norm(phrase)
    if not 10 <= len(n.split()) <= 30 or n in unique:
        continue
    unique.add(n)
    count += 1
    digest = hashlib.sha256(component(n)).digest()
    positive += digest == planted_commitment
    if digest == target:
        hits.append({"phrase":n, "K08":component(n).hex().upper()})
assert count == 254266 and positive == 1
print(json.dumps({
    "genre":"second-person short envelope invitation",
    "unique_complete_candidates":count,
    "planted_HMAC_control_hits":positive,
    "authentic_K08_matches":hits,
    "authentic_source_HMAC_control":"PASS"
}, indent=2))
