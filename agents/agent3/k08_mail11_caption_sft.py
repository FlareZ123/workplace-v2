"""Source-pinned K08 whole-caption MAIL11 editor, stdlib single-file test.

From repo root run: python agents/agent3/k08_mail11_caption_sft.py
Evidence and acceptance are read only. This is a conjectural caption grammar.
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
PLACE = (
    "there is room for one more",
    "there is room for each other",
    "there is always room for one more",
    "there will always be room for one more",
    "there was still room for one more",
    "we made room for one another",
    "we made room for each other",
    "someone made room for one more",
    "someone saved a place for one more",
    "someone left a place for one more",
    "the night crew made room for each other",
    "the late crew made room for each other",
    "everybody made room for somebody else",
    "there was room at the table for one more",
    "there is room at the table for one more",
    "there is a place at the table for one more",
    "there is always a place for one more",
    "we kept a place at the table",
    "the last watch left room for the next",
    "we left room for the next watch",
)
WATER = (
    "with the water outside", "with the sea outside",
    "with the sea beyond the window", "with the water beyond the window",
    "with the sea at the window", "while the sea waited outside",
    "as the sea waited outside", "while the water waited outside",
    "and the sea was still outside", "as the sea turned light",
    "with the sea going silver", "with the water going silver",
    "with the sea beyond the glass", "under the dark sea sky",
    "looking out to sea", "beside the window and the sea",
    "with the sea on the other side of the glass",
    "while the sea was quiet", "while the water was quiet",
    "with the water turning light", "as the water turned to daylight",
    "and the sea outside", "and the water outside",
    "and the sea beyond the window",
)
WATCH = (
    "after a long watch", "after the long watch", "at the end of the night",
    "at the end of a long night", "as the night was nearly over",
    "when the night was almost finished", "with the night almost finished",
    "as the night was almost finished", "when the night was nearly over",
    "as the watch was almost over", "at the end of the watch",
    "when the watch was over", "as the last watch ended",
    "when the last watch ended", "before the morning watch",
    "at the edge of morning", "before the first light",
    "when the daylight came", "when morning came", "as the morning came",
    "after the night watch", "as night gave way to morning",
    "until the night was over", "after the last cup",
)
VOICES = (
    "and the voices at the table", "and voices at the table",
    "with the voices at the table", "with voices at the table",
    "and voices around the table", "with the crew at the table",
    "and somebody waiting at the table", "with everybody around the table",
    "and the last mugs on the table", "with mugs beside the window",
    "as the voices gathered at the table",
    "while the voices gathered at the table", "and nobody had to sit alone",
    "so nobody had to sit alone",
    "and nobody had to make their first cup alone",
    "with one more chair at the table", "and the little lamp still on",
    "with the little lamp still on", "and a place beside the lamp",
    "and the mugs at the window", "with the cups at the table",
    "and the cups at the table", "with tea for the next watch",
    "and tea for one more",
)
ORDERS = (
    ("PLACE", "WATER", "WATCH", "VOICES"),
    ("PLACE", "WATCH", "WATER", "VOICES"),
    ("WATCH", "WATER", "PLACE", "VOICES"),
    ("WATCH", "PLACE", "WATER", "VOICES"),
    ("WATER", "WATCH", "PLACE", "VOICES"),
    ("PLACE", "WATCH", "VOICES", "WATER"),
)
PARTS = dict(PLACE=PLACE, WATER=WATER, WATCH=WATCH, VOICES=VOICES)


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def slot(phrase: str, nonce: bytes) -> bytes:
    return hmac.new(nonce, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def main() -> None:
    evidence = ROOT / "resources" / "evidence"
    mail = (evidence / "mail" / "11.eml").read_bytes()
    notes = (evidence / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(mail).hexdigest() == MAIL11_SHA
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    assert "people making room for each other after a long watch" in " ".join(mail.decode("utf-8").split())
    assert "with the water outside and the night almost finished" in " ".join(mail.decode("utf-8").split())
    assert "the sea, the end of the night and the voices at the table" in notes.decode("utf-8")
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    goal = acceptance["slot_sha256"]["K08"]
    nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
    assert slot("A good watch leaves the room ready for the next pair of hands.", nonce).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    planted = " ".join(PARTS[n][0] for n in ORDERS[0])
    planted_target = hashlib.sha256(slot(planted, nonce)).hexdigest()
    total = hits = synthetic = 0
    first_hit = None
    for i, order in enumerate(ORDERS, 1):
        count = 0
        for chunks in itertools.product(*(PARTS[n] for n in order)):
            phrase = normalize(" ".join(chunks))
            digest = hashlib.sha256(slot(phrase, nonce)).hexdigest()
            count += 1
            if digest == planted_target:
                synthetic += 1
            if digest == goal:
                hits += 1
                first_hit = phrase
        total += count
        print(f"order{i}={order} complete_candidates={count}", flush=True)
    assert total == 1658880 and synthetic == 1
    print(json.dumps(dict(original_hits=hits, synthetic_hits=synthetic,
                          total_assignments=total, first_hit=first_hit), indent=2))


if __name__ == "__main__":
    main()
