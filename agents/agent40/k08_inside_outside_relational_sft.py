"""K08 inside/outside relational-caption model. Source-pinned complete candidates.

Hypothesis: the late-watch caption uses a foreground/background contrast between
sea outside and people making room together inside. This speculative model
differs from literal word-span editing and independent four-clause collage.
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
PINS = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "evidence/mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}
SEA = (
    "the sea was still outside", "the sea was outside the window",
    "the sea waited outside", "the sea waited beyond the window",
    "the sea was quiet beyond the glass", "the sea was still there",
    "the sea was turning pale", "the sea was coming into morning",
    "the sea held the last of the night", "the sea was beyond the window",
    "the sea was waiting for morning", "the sea was just beyond the glass",
    "the sea had not gone anywhere", "the sea turned toward the morning",
    "the sea looked different at first light", "the sea was already there",
    "the sea was beginning to brighten", "the sea had begun to lighten",
    "the water was still outside", "the water waited beyond the window",
    "the water was turning light", "the water was still there",
    "the water waited for the morning", "the water was just outside",
    "the night sea was beyond the window", "outside the sea was still there",
    "outside the water was turning light", "outside the sea waited for morning",
    "beyond the window the sea waited", "beyond the glass the water was quiet",
    "the sea kept the last of the night", "the sea was almost morning",
)
TIME = (
    "at the end of the night", "at the end of a long night",
    "at the end of the watch", "at the end of a long watch",
    "after the last watch", "after a long watch",
    "after the last cup", "after the last cup of tea",
    "when the long watch was over", "when the night was almost done",
    "when the night was nearly finished", "when the night was nearly over",
    "as the night came to an end", "as the night was ending",
    "before morning came", "before the first light",
    "as the first light came", "as morning came",
    "before the first boat", "before the first boat arrived",
    "when the corridor had gone quiet", "when the last cup was empty",
    "while the last light was coming", "as the night gave way to morning",
)
INSIDE = (
    "inside there was room at the table", "inside there was room for one more",
    "inside there was still room for one more", "inside someone had made room for another",
    "inside we made room for one more", "inside we made room for each other",
    "inside someone had left a place at the table", "inside the table still had room",
    "inside there were voices around the table", "inside the voices were still at the table",
    "inside the late crew made room for each other", "inside a place was kept for the next watch",
    "inside the mugs were still beside the window", "inside the little lamp was still on",
    "inside the last voices were still at the table", "inside we kept a place for the next watch",
    "at the table there was still room for one more", "at the table there was always room",
    "at the table they had made room for one more", "at the table we made room for each other",
    "at the table someone had left a place for the next watch", "at the table the voices were still there",
    "at the table the last voices stayed", "at the table somebody made room for one more",
    "by the window there was room for one more", "by the window someone kept the little lamp on",
    "by the window the mugs were still waiting", "by the window the crew kept a place for one more",
    "there was still room at the table", "there was always room at the table",
    "there was room for the next pair of hands", "someone had kept a place for the next watch",
    "someone left room for one more", "someone made room for one more",
    "we left room for the next watch", "we left a place for each other",
    "we kept a place at the table", "the voices made room for the next watch",
    "no one had to take the last cup alone", "nobody had to make the first cup alone",
)
CONNECT = ("and", "but", "while", "as", "even as", "though")

def normalize(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def component(key: bytes, phrase: str) -> bytes:
    return hmac.digest(key, phrase.encode("utf-8"), "sha256")[:16]

def candidates():
    for sea, time, inside, conn in itertools.product(SEA, TIME, INSIDE, CONNECT):
        yield normalize(f"{time}, {sea}, {conn} {inside}.")
        yield normalize(f"{time}, {inside}, {conn} {sea}.")
        yield normalize(f"{sea}, {conn} {inside} {time}.")
        yield normalize(f"{inside}, {conn} {sea} {time}.")
        yield normalize(f"{sea}. {inside} {time}.")
        yield normalize(f"{inside}. {sea} {time}.")
        yield normalize(f"{sea}; {time}, {inside}.")
        yield normalize(f"{inside}; {time}, {sea}.")

def main():
    for path, pin in PINS.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == pin, path
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acc = json.loads((ROOT / "acceptance.json").read_text())
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acc["slot_sha256"]["K08"])
    assert component(key, normalize("A good watch leaves the room ready for the next pair of hands.")).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    planted = normalize(f"{TIME[2]}, {SEA[4]}, and {INSIDE[5]}.")
    plant_target = hashlib.sha256(component(key, planted)).digest()
    tested = 0
    plant_hits = 0
    for phrase in candidates():
        tested += 1
        c = component(key, phrase)
        digest = hashlib.sha256(c).digest()
        if digest == plant_target:
            assert phrase == planted
            plant_hits += 1
        if digest == target:
            print(json.dumps({"result":"FOUND", "phrase":phrase, "K08":c.hex().upper(), "tested":tested}))
            return
    assert plant_hits == 1, plant_hits
    print(json.dumps({"result":"NO_MATCH", "tested_complete_assignments":tested,
        "synthetic_positive_hits":plant_hits,
        "distinct_source_clause_counts":[len(SEA),len(TIME),len(INSIDE),len(CONNECT)],
        "templates":8}))

if __name__ == "__main__":
    main()
