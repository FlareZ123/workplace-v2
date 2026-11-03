"""Source-pinned full-rewrite K08 caption grammar, with a synthetic positive.

This models Emily's late-watch motifs through independent predicative clauses.
It deliberately does not preserve literal source spans or use edit windows.
Only a commitment match would make a historical recovery claim.
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SHA = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "evidence/mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}

# Four independent semantic roles visible in original N02/N06/N13/N20
# and MAIL-11, not text copied from one original sentence.
TIME = (
    "at the end of the night", "after a long watch", "after the last watch",
    "when the night is almost over", "when the night is nearly done",
    "at the end of a long night", "before the night is over",
    "before the first light", "as the night comes to an end",
    "when the watch is finished", "when the last cup is empty",
    "by the time morning comes", "when the night turns toward morning",
)
SEA = (
    "the sea waits outside", "the sea is outside the window",
    "the sea is waiting beyond the window", "the water is outside",
    "the water is beyond the window", "the sea is turning light",
    "the sea can wait", "the sea is still outside",
    "the sea is there beyond the glass", "the sea looks different by daylight",
    "the sea is quiet outside", "the water is slowly turning light",
    "the sea is almost morning", "the sea comes back into view",
)
ROOM = (
    "the little lamp stays on", "the lamp is still on",
    "the lamp stays on by the window", "the mugs are beside the window",
    "the mugs are waiting at the table", "the last mugs are by the window",
    "the voices are still at the table", "the voices are quiet at the table",
    "there are voices around the table", "the table still has voices",
    "the last cup is still warm", "the room has not gone quiet",
    "there is still light at the window", "the table is still full of voices",
)
PEOPLE = (
    "there is room for one more", "there is room at the table",
    "there is still room at the table", "we make room for each other",
    "we keep a place for whoever comes next", "there is always room for another cup",
    "someone has left a place at the table", "no one has to sit alone",
    "there is still a chair for one more", "the next watch will have a place",
    "there is room for the next pair of hands", "someone has kept the lamp on for us",
    "there is a place for the late crew", "we leave a place for the next watch",
)
JOIN = ("and", "while", "but", "as", "because", "when")


# Alternative N10/N13 version hypothesis: caption describes the photograph
# after the room has emptied, hence completed/past-tense image rather than
# a living scene or source-quote splice.
PAST_TIME = (
    "after the last cup", "after the last cup was finished",
    "when the long watch was over", "after the watch was finished",
    "when the room had gone quiet", "at the end of the long night",
    "when the voices had gone", "when the last people had left",
    "by the time the night was over", "before the first boat came",
    "after everyone had found a place", "when the table was empty",
)
PAST_ROOM = (
    "the mugs were still beside the window", "the mugs were still at the table",
    "the little lamp was still on", "someone had left the lamp on",
    "the last cup stood by the window", "the empty bench was still warm",
    "the chairs were still pulled up", "the room still held the last voices",
    "the table was still waiting", "the table was finally quiet",
    "there was still a chair at the table", "the window still held the little light",
)
PAST_SEA = (
    "the sea was outside", "the sea was still beyond the window",
    "the sea had turned pale", "the water had begun to lighten",
    "the sea waited outside", "the sea looked different by daylight",
    "the water was turning toward morning", "the sea was there beyond the glass",
    "the sea had not gone anywhere", "the sea was coming into morning",
    "the water was still out there", "the sea was quiet at the window",
)
PAST_PEOPLE = (
    "the voices had only just gone", "the last voices were still in the room",
    "somebody had made room for one more", "someone had kept a place for the next watch",
    "there was still room for one more", "nobody had been left alone",
    "someone had remembered the next pair of hands", "the table still had room for another cup",
    "the place belonged to everybody", "somebody had left the light on for them",
    "the next watch would find room at the table", "they had made room for each other",
)

def normalize(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())


def scenarios():
    # Original notes don't say the final was a collage; test complete
    # sentence-level reconstructions in three distinct layouts.
    for t, sea, room, people, bridge in itertools.product(TIME, SEA, ROOM, PEOPLE, JOIN):
        yield f"{t}, {sea} {bridge} {people}."
        yield f"{t}, {room} {bridge} {people}, and {sea}."
        yield f"{sea}, and {room} {bridge} {people} {t}."
    for t, sea, room, people in itertools.product(TIME, SEA, ROOM, PEOPLE):
        yield f"{t}, {sea}; {room}; {people}."
        yield f"{t}, {sea}. {room}, and {people}."
        yield f"{sea} {t}; {room}; {people}."


    for t, room, sea, people, bridge in itertools.product(
        PAST_TIME, PAST_ROOM, PAST_SEA, PAST_PEOPLE, JOIN
    ):
        yield f"{t}, {room}, {sea}, and {people}."
        yield f"{t}, {room} {bridge} {sea}, and {people}."
        yield f"{sea} {t}, {room}, and {people}."


def component(key: bytes, phrase: str) -> bytes:
    return hmac.digest(key, normalize(phrase).encode("utf-8"), "sha256")[:16]


def main():
    for name, expected in SHA.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acc = json.loads((ROOT / "acceptance.json").read_text())
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = bytes.fromhex(acc["slot_sha256"]["K08"])
    # Known, original-source reduction control independent of candidate family.
    original_n02 = "A good watch leaves the room ready for the next pair of hands."
    assert component(key, original_n02).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    synthetic_phrase = f"{TIME[2]}, {SEA[1]} and {PEOPLE[2]}."
    fake_target = hashlib.sha256(component(key, synthetic_phrase)).digest()
    assert fake_target != target
    synthetic_recovered = False
    count = 0
    unique = set()
    streamhash = hashlib.sha256()
    for candidate in scenarios():
        norm = normalize(candidate)
        if not 10 <= len(norm.split()) <= 32:
            continue
        if len(norm) <= 38 or norm in unique:
            continue
        unique.add(norm)
        count += 1
        streamhash.update(norm.encode("ascii") + b"\n")
        c = component(key, norm)
        digest = hashlib.sha256(c).digest()
        if digest == fake_target and norm == normalize(synthetic_phrase):
            synthetic_recovered = True
        if digest == target:
            print(json.dumps({"outcome":"FOUND","phrase":norm,"K08":c.hex().upper(),"tested":count}))
            return
    assert synthetic_recovered, "Synthetic selected-withheld caption not recovered from grammar"
    print(json.dumps({"outcome":"NO_MATCH","distinct_candidates":count,
                      "candidate_stream_sha256":streamhash.hexdigest(),
                      "time_variants":len(TIME),"sea_variants":len(SEA),
                      "room_variants":len(ROOM),"inclusion_variants":len(PEOPLE),
                      "synthetic_HMAC_control":"PASS","source_HMAC_control":"PASS"}))


if __name__ == "__main__":
    main()
