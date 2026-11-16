"""Conditional K08 time-adjunct plus two-scene complete-caption constructor.

The source asserts no historical final inscription. Test the unaltered
K08 nonce and commitment for a defined normalized candidate family.
"""
from __future__ import annotations
import hashlib
import hmac
import itertools
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2] / "resources"
TIMES = (
    "at the end of the night", "by the end of the night",
    "after a long watch", "after the long watch", "after the last cup",
    "before the first boat", "when the night was almost finished",
    "with the night almost finished", "when the night was nearly over",
    "as the night came to an end", "as the night was ending",
    "at first light", "as the first light came",
    "while the last watch ended", "after the last watch",
)
WATER = (
    "the sea was outside", "the sea was still outside", "the water was outside",
    "the water was still outside", "the sea waited outside",
    "the water waited outside", "the sea stayed outside",
    "the sea went on outside", "the water went on outside",
    "the sea kept moving outside", "the water kept moving outside",
    "the sea was there beyond the window",
    "the water was there beyond the window",
    "the sea lay beyond the window", "the water lay beyond the window",
    "the sea stayed beyond the window", "the water stayed beyond the window",
    "the sea looked different", "the sea looked different from the window",
    "the water gave back the daylight", "the water gave back the colors",
    "the sea beyond the glass", "the water beyond the window",
    "the sea outside the window", "the water outside the window",
    "the sea was still there", "the sea was still there outside",
    "the sea was turning silver", "the water was turning silver",
    "the sea kept its own watch", "the water kept its own watch",
    "the sea beyond the window was still there",
)
PEOPLE = (
    "there was room for one more at the table",
    "there was room at the table",
    "there was room for one another at the table",
    "there was room for each other",
    "there was room for one more cup",
    "there was room for one more voice",
    "there was always room at the table", "there was room for everyone",
    "there was room for the next watch",
    "there was always room for one more",
    "we made room for each other", "we made room for one another",
    "we left room for each other", "we left room for one another",
    "we kept room for one more", "we kept room at the table",
    "we kept a place for each other", "we kept a place for one another",
    "we kept a place for the next watch",
    "we left a place for the next watch",
    "we saved a place at the table", "we left room for the next watch",
    "we made room for the next pair of hands",
    "the voices at the table went on",
    "the voices at the table carried on",
    "the voices at the table stayed",
    "the voices at the table were still there",
    "the voices at the table kept going",
    "the voices at the table made room",
    "the table made room for another",
    "the table made room for one more",
    "the table had room for one more",
    "the table had room for everyone",
    "the table still had room for one more",
    "the table had room for each other",
    "the people at the table made room for each other",
    "the people at the table made room for one another",
    "somebody made room at the table",
    "somebody left room at the table",
    "somebody remembered to make room",
    "somebody remembered to leave room",
    "somebody remembered to leave a place at the table",
    "someone had left room for another",
    "someone made room for another",
    "no one had to sit alone", "nobody had to sit alone",
    "nobody had to drink alone", "no one had to drink alone",
    "we all found room at the table",
    "the next watch found room at the table",
    "the next pair of hands found room",
    "a good watch made room for another",
)
JOIN = ("and", "but", "while", "as", "when", "because", "so", "and still", "with")

def normalize(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def digest(s: str, nonce: bytes) -> bytes:
    component = hmac.digest(nonce, normalize(s).encode("utf-8"), "sha256")[:16]
    return hashlib.sha256(component).digest()

def candidates():
    for clock, sea, people, join in itertools.product(TIMES, WATER, PEOPLE, JOIN):
        yield f"{clock} {sea} {join} {people}"
        yield f"{clock} {people} {join} {sea}"
        yield f"{sea} {join} {people} {clock}"
        yield f"{people} {join} {sea} {clock}"
        yield f"{sea} {clock} {join} {people}"
        yield f"{people} {clock} {join} {sea}"

def main() -> None:
    crew = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    mail11 = (ROOT / "evidence/mail/11.eml").read_bytes()
    assert hashlib.sha256(crew).hexdigest() == (
        "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    )
    assert hashlib.sha256(mail11).hexdigest() == (
        "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
    )
    original = (crew + mail11).decode("utf-8").lower()
    assert all(s in original for s in (
        "end of the night", "sea looks different", "voices at the table",
        "making room for each other after", "night almost finished",
    ))
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    known = "a good watch leaves the room ready for the next pair of hands"
    assert hmac.digest(nonce, known.encode(), "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    synthetic_digest = digest(next(candidates()), nonce)
    synthetic = 0
    matches = []
    count = 0
    for caption in candidates():
        observed = digest(caption, nonce)
        count += 1
        synthetic += observed == synthetic_digest
        if observed == target:
            matches.append({
                "phrase": normalize(caption),
                "component": hmac.digest(nonce, normalize(caption).encode(), "sha256")[:16].hex().upper(),
            })
    assert count == len(TIMES)*len(WATER)*len(PEOPLE)*len(JOIN)*6
    assert count == 1347840 and synthetic == 1
    print(json.dumps({"complete_assignments":count,
                      "synthetic_positive":synthetic,
                      "original_K08_hits":matches}, indent=2))

if __name__ == "__main__":
    main()
