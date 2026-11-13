#!/usr/bin/env python3
"""Bounded K08 mug-as-person metonymy candidate test.

Run from repository root:
    python agents/agent4/k08_mug_metonymy_sft.py

Reads evidence and acceptance metadata only; never changes the verifier or route.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
MAIL12_SHA = "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd"
MAIL20_SHA = "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71"

CANDIDATES = (
    "There is always a mug for one more",
    "There is always another mug at the table",
    "A mug is waiting for you at the table",
    "Every mug has a place at the table",
    "The chipped blue mug has a place at the table",
    "We keep a mug for whoever comes next",
    "We keep a place for every mug",
    "A mug at the table means someone is home",
    "A mug tells you who has sat down",
    "A mug tells you who is here",
    "We count the mugs because everyone belongs",
    "The table is full of mugs and voices",
    "The last mug is never left alone",
    "There is room for one more mug",
    "A place for one more mug",
    "A mug for everyone at the table",
    "Every mug belongs to someone who expects to see it again",
    "A mug waits for the next watch",
    "A mug waits by the window for you",
    "The blue mug belongs at the table",
)


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def slot(phrase: str, nonce: bytes) -> bytes:
    return hmac.new(nonce, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def main() -> None:
    evidence = ROOT / "resources" / "evidence"
    notes = (evidence / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    mail11 = (evidence / "mail" / "11.eml").read_bytes()
    mail12 = (evidence / "mail" / "12.eml").read_bytes()
    mail20 = (evidence / "mail" / "20.eml").read_bytes()

    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    assert hashlib.sha256(mail11).hexdigest() == MAIL11_SHA
    assert hashlib.sha256(mail12).hexdigest() == MAIL12_SHA
    assert hashlib.sha256(mail20).hexdigest() == MAIL20_SHA

    notes_text = notes.decode("utf-8")
    mail11_text = " ".join(mail11.decode("utf-8").split())
    mail12_text = " ".join(mail12.decode("utf-8").split())
    mail20_text = " ".join(mail20.decode("utf-8").split())

    # Source-role pins: mug ownership / expected return; mugs as evidence
    # of people sitting down; end-of-night scene; explicit late-watch intent.
    for anchor in (
        "Even the chipped blue one belongs to someone who expects to see it again.",
        "Someone asked why I count mugs when I could count beds. A bed does not tell you whether anybody has sat down.",
        "At the end of the night the mugs stood beside the window",
        "the voices at the table",
    ):
        assert anchor in notes_text, anchor
    assert "They belong to two of the night crew and they know which ones they are." in mail12_text
    assert "people making room for each other after a long watch" in mail11_text
    assert "with the water outside and the night almost finished" in mail11_text
    assert "late crew making room for one another" in mail20_text
    assert "The words she finally chose matter, not our preferred paraphrase." in mail20_text

    route = json.loads((evidence / "recovery-routing.json").read_text())
    acceptance = json.loads((evidence / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    # Independent known-control check protects the normalization/HMAC path.
    assert slot(
        "A good watch leaves the room ready for the next pair of hands.",
        nonce,
    ).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    hits = []
    for phrase in CANDIDATES:
        component = slot(phrase, nonce)
        commitment = hashlib.sha256(component).hexdigest()
        if commitment == target:
            hits.append({"phrase": normalize(phrase), "component": component.hex().upper()})

    print(json.dumps({
        "model": "mug-as-person metonymy",
        "candidate_count": len(CANDIDATES),
        "hit_count": len(hits),
        "hits": hits,
        "source_hashes": {
            "noticeboard_and_desk_notes": NOTES_SHA,
            "mail11": MAIL11_SHA,
            "mail12": MAIL12_SHA,
            "mail20": MAIL20_SHA,
        },
    }, indent=2))
    assert not hits, "A candidate matched; preserve and independently verify it before promotion."


if __name__ == "__main__":
    main()
