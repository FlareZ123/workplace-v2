"""H-17 K08 short keeper inscription, source-conditioned semantic compression.

Read-only exploratory constructor, not a historical quotation.
Run: python agents/agent15/k08_keeper_short_inscription_sft.py
"""
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MASKED_N02 = "a good watch leaves the room ready for the next pair of hands"


def norm(text):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def generate():
    # Three motifs explicitly named by original N20; one dependent inscription
    # rather than four separately formed scene clauses.
    sea = ("the sea", "the water", "the waves", "the tide")
    sea_state = (
        "waits outside", "is still outside", "waits beyond the window",
        "is waiting outside", "can wait", "is still there",
        "is beyond the window", "turns toward morning", "turns to morning",
        "is turning toward morning", "is turning pale",
        "looks different in the morning", "has not gone anywhere",
        "keeps moving outside", "comes in with the morning",
    )
    people = (
        "there is room at the table", "there is still room at the table",
        "there is room for one more", "there is always room for one more",
        "we make room for one another", "we make room at the table",
        "we leave room for one more", "someone saves a chair",
        "nobody has to sit alone", "the last chair is never empty",
        "the voices are still at the table", "the table is still full of voices",
        "there are still voices at the table",
        "the last voices remain at the table",
        "the last cup is still warm", "there is a place for everyone",
    )
    time = (
        "when the night is over", "when the watch is done",
        "at the end of the night", "after the long watch",
        "after the last watch", "before the first light",
        "when the night is nearly over", "as the night ends",
        "when morning comes", "as the night turns to morning",
        "when the last cup is empty", "when the night is almost finished",
        "after the last cup", "when the long night ends",
        "by the time the night is done",
    )
    bridge = ("and", "while", "when", "because", "as", "until", "but", "so", "even when")
    for s, state, p, t, b in itertools.product(sea, sea_state, people, time, bridge):
        yield f"{p} {b} {s} {state} {t}"
        yield f"{t} {p} {b} {s} {state}"
        yield f"{s} {state} {t} {b} {p}"
        yield f"{s} {state} {b} {p} {t}"

    # A water predicate taking a communal action as its complement.
    water_subject = ("the sea", "the water", "the tide", "the waves")
    water_pred = ("can wait", "will wait", "is waiting", "waits", "is still there", "can stay outside")
    human_event = (
        "we have made room for one more", "we make room for one more",
        "there is room at the table", "the last cup has been shared",
        "the last voices have gone quiet", "everyone has a place at the table",
        "we have finished the last cup", "we have pulled up another chair",
        "someone has found a place at the table", "no one is left alone",
    )
    until = ("until", "while", "as", "because", "when", "after")
    for s, w, h, b, t in itertools.product(water_subject, water_pred, human_event, until, time):
        yield f"{s} {w} {b} {h} {t}"
        yield f"{t} {s} {w} {b} {h}"
        yield f"{s} {w} {t} {b} {h}"

    # Elliptical labels, retaining the historical N17/N18 style distinction.
    short_time = (
        "after the last watch", "at the end of the night",
        "before the first light", "after the last cup",
        "when the night is almost over", "when the night ends",
    )
    short_sea = (
        "sea outside", "water outside", "sea at the window",
        "water beyond the glass", "sea beyond the window", "tide beyond the window",
    )
    short_people = (
        "room for one more", "a chair for one more", "voices at the table",
        "room at the table", "a place for each other",
        "a place for everyone", "one more cup at the table",
        "the last voice at the table",
    )
    for t, s, p, b in itertools.product(short_time, short_sea, short_people, bridge):
        yield f"{t} {s} {b} {p}"
        yield f"{p} {b} {s} {t}"
        yield f"{s} {t} {b} {p}"


def main():
    notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == NOTES_SHA
    text = notes.decode("utf-8")
    assert "N20 / Emily" in text
    assert "sea, the end of the night and the voices at the table" in text
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acc = json.loads((ROOT / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    want = bytes.fromhex(acc["slot_sha256"]["K08"])

    def component(phrase):
        return hmac.digest(nonce, phrase.encode("ascii"), "sha256")[:16]

    assert component(MASKED_N02).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    first = norm(next(generate()))
    planted = hashlib.sha256(component(first)).digest()
    assert planted != want
    n = 0
    positive = 0
    seen = set()
    hit = None
    for phrase in generate():
        phrase = norm(phrase)
        if phrase in seen or not 7 <= len(phrase.split()) <= 30:
            continue
        seen.add(phrase)
        n += 1
        d = hashlib.sha256(component(phrase)).digest()
        if d == planted:
            positive += 1
        if d == want:
            hit = {"phrase": phrase, "K08": component(phrase).hex().upper()}
            break
    assert positive == 1
    print(json.dumps({
        "result": "MATCH" if hit else "NO_MATCH", "candidates": n,
        "authentic_hit": hit, "planted_control": positive,
        "source_control": "PASS", "notes_sha256": NOTES_SHA
    }, indent=2))


if __name__ == "__main__":
    main()
