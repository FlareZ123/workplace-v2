"""Original K08 collective-voice caption hypothesis, read-only source-pinned probe."""
import argparse
import hashlib
import hmac
import itertools
import re
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--resources", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
args = parser.parse_args()
root = args.resources
note = root / "evidence/crew/noticeboard-and-desk-notes.txt"
nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
target = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
assert hashlib.sha256((root / "acceptance.json").read_bytes()).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
assert hashlib.sha256(note.read_bytes()).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = note.read_text()
for anchor in (
    "The sea looks different when you have finally finished your tea",
    "A good watch leaves the room ready for the next pair of hands",
    "At the end of the night the mugs stood beside the window",
    "I wanted the line to hold the sea, the end of the night and the voices at the table",
):
    assert anchor in notes

def normalize(s: str) -> str:
    return " ".join(re.findall("[a-z0-9]+", s.lower()))

fixture = normalize("A good watch leaves the room ready for the next pair of hands.")
assert hmac.digest(nonce, fixture.encode("utf-8"), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

# A deliberately bounded collective narrator, separate from third-person scene or imperative grammars.
crew = (
    "we leave room at the table", "we make room for one another",
    "we always make room at the table", "we keep a place at the table",
    "we keep a chair for the next watch", "we keep a chair for each other",
    "we leave a place for whoever comes next", "we save a place for one more",
    "we come back to the table", "we gather at the table",
    "we stay a little longer at the table", "we find each other at the table",
    "we know who has come off watch", "we know when the last watch is over",
    "we remember to leave the light on", "we leave the little lamp on",
    "we remember the next pair of hands", "we leave the room ready for one another",
    "there is still room for us at the table", "there is a place for us at the table",
    "we can hear the voices at the table", "we hear each other across the table",
    "our voices fill the room", "our voices stay around the table",
    "our mugs are waiting by the window", "our mugs are still beside the window",
    "our first cup is never alone", "our last cup belongs to everyone",
    "we all find a place at the table", "we leave a little room for the next person",
    "we take turns leaving the light on", "we wait until everyone has a seat",
)
sea = (
    "the sea is outside", "the sea waits outside", "the sea stays outside",
    "the sea is still outside", "the sea is beyond the window",
    "the sea is outside the window", "the sea is on the other side of the window",
    "the water is outside", "the water waits beyond the window",
    "the water is outside the window", "the water is still outside",
    "the sea is there when the watch is over", "the water is there at the end of the night",
    "the sea does not mind", "the sea keeps its own watch",
    "the sea has its own watch", "the sea is dark beyond the window",
    "the sea gives back the daylight", "the water gives back the light",
    "the sea looks different after the last cup",
)
night = (
    "the night is almost over", "the night is nearly finished",
    "the night is nearly over", "the night is coming to an end",
    "the watch is almost done", "the watch is almost over",
    "the last watch is over", "the long watch is over",
    "the last cup is finished", "the last cup is empty",
    "the night has almost ended", "the night is giving way to morning",
    "the watch has come to an end", "the night has finally ended",
    "the night is almost finished", "the morning is almost here",
    "daylight is coming", "the next watch is near",
    "the lamp is still on", "the little lamp stays on",
)
connectors = (" and ", " while ", " as ", " when ", " but ", " with ")
planted = "we leave room at the table and the sea is outside while the night is almost over"
planted_digest = hashlib.sha256(hmac.digest(nonce, planted.encode("utf-8"), "sha256")[:16]).hexdigest()
original_hits: list[str] = []
synthetic_hits = 0
count = 0
started = time.monotonic()
for order in itertools.permutations((crew, sea, night)):
    for a in order[0]:
        for b in order[1]:
            for c in order[2]:
                for first in connectors:
                    left = a + first + b
                    for second in connectors:
                        phrase = left + second + c
                        component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
                        digest = hashlib.sha256(component).hexdigest()
                        count += 1
                        if digest == planted_digest:
                            synthetic_hits += 1
                            assert phrase == planted
                        if digest == target:
                            original_hits.append(phrase)
                            print("RECOVERED_K08", phrase, flush=True)
assert count == 2_764_800
assert count == 6 * len(crew) * len(sea) * len(night) * len(connectors) ** 2
assert synthetic_hits == 1
print("K08_COLLECTIVE", count, synthetic_hits, len(original_hits), round(time.monotonic() - started, 3))
