"""Source-pinned K08 N13-free editorial rewrite grammar (exploratory, not authenticated)."""
import hashlib
import hmac
import itertools
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_ROOT", Path(__file__).resolve().parents[2] / "resources"))
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")


def normalize(s):
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return " ".join(s.split())


def component(s):
    return hmac.new(NONCE, normalize(s).encode(), hashlib.sha256).digest()[:16]


def accepted(s):
    return hashlib.sha256(component(s)).digest() == TARGET


def families():
    # Rewrites starting from N02's "good watch ... room ... next pair of hands".
    intro = ("a good watch", "the good watch", "the last watch", "the late watch",
             "the night watch", "a long watch", "the end of the watch")
    action = ("leaves", "left", "keeps", "kept", "makes", "made", "finds", "found")
    object_ = ("room", "a room", "space", "a space", "a place", "one more place",
               "a chair", "an empty chair", "a seat", "an empty seat")
    where = ("at the table", "around the table", "by the window",
             "beside the window", "for the next watch", "for another voice",
             "for the next pair of hands", "for the next person", "for one more")
    while_ = ("as the night ends", "at the end of the night",
              "when the night is almost over", "as the night is ending",
              "while the sea waits outside", "with the sea outside",
              "while the water is dark", "after the last cup",
              "when the sea is quiet", "as the last cup is finished")
    endings = ("", " and the lamp is still on", " and the little lamp stays on",
               " and the voices are still there", " and we hear each other",
               " and there is still a voice at the table",
               " and the sea is still beyond the window")
    for a,b,c,d,e,f in itertools.product(intro,action,object_,where,while_,endings):
        yield f"{a} {b} {c} {d} {e}{f}"
        yield f"{e} {a} {b} {c} {d}{f}"
        yield f"{a} {b} {c} {d}{f} {e}"

    # N06 structural scene recast into N20 sea/table setting.
    light = ("the lamp", "the little lamp", "our little lamp", "the light",
             "the small lamp", "the last light", "one little lamp")
    action2 = ("stays on", "stayed on", "is still on", "was still on",
               "keeps burning", "kept burning", "waits", "was left on")
    temporal = ("at the end of the night", "until the night is quiet",
                "when the night is nearly over", "after the last cup",
                "as the night ends", "when the watch is over",
                "after a long watch", "before morning", "as the sky gets light")
    seaview = ("with the sea outside", "while the sea waits outside",
               "with the water beyond the window", "beside the sea",
               "as the sea goes quiet", "and the sea is still there",
               "with the sea at the window", "with the last of the night outside")
    people = ("for the next pair of hands", "for the next watch",
              "for the next voice at the table", "while we make room at the table",
              "while there is room for one more", "for the voices around the table",
              "until everyone has had their tea", "until the last voice is heard",
              "while the mugs are still on the table", "as everyone makes room")
    for a,b,c,d,e in itertools.product(light,action2,temporal,seaview,people):
        yield f"{a} {b} {c} {d} {e}"
        yield f"{c} {a} {b} {d} {e}"
        yield f"{a} {b} {e} {d} {c}"

    # No N13 quotation base: full N20 sea/night/voices/table recomposition.
    night = ("at the end of the night", "when the night is almost over",
             "as the night comes to an end", "as the night ends",
             "at the last hour of the watch", "after the long watch",
             "when the last watch is done", "when the night gives way to morning")
    sea = ("the sea is still outside", "the sea waits beyond the window",
           "the sea is there beyond the glass", "the water is still there",
           "we can hear the sea", "we look out at the sea",
           "the sea holds the last light", "the sea takes the last of the night")
    voices = ("the voices are at the table", "there are voices around the table",
              "someone is still talking at the table",
              "we are still talking at the table", "the last voices gather at the table",
              "there is always one more voice at the table",
              "the voices are still here", "the table is full of voices")
    welcome = ("and there is room for one more",
               "and we leave a place for the next watch",
               "and the lamp is still on", "and we make room for each other",
               "and everyone makes room for the next",
               "and someone has left a light on",
               "and there is a place for the next pair of hands",
               "and the last cup is never taken alone")
    connect = (", and ", "; ", ", while ", ", but ", " as ", " with ", ". ", " and ")
    for a,b,c,d,con in itertools.product(night,sea,voices,welcome,connect):
        yield f"{a}, {b}{con}{c}, {d}"
        yield f"{b}{con}{a}, {c}, {d}"
        yield f"{a}, {c}{con}{b}, {d}"


def main():
    note_bytes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(note_bytes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    note = note_bytes.decode("utf-8")
    assert all(x in note for x in ("N02 / Emily", "N06 / Emily", "N13 / Emily", "N20 / Emily", "N23 / Emily"))
    assert normalize("A-good WATCH!") == "a good watch"
    test_phrase = next(families())
    test_target = hashlib.sha256(component(test_phrase)).digest()
    assert hashlib.sha256(component(next(families()))).digest() == test_target
    seen = set()
    count = 0
    for s in families():
        msg = normalize(s)
        if msg in seen:
            continue
        seen.add(msg)
        count += 1
        if accepted(msg):
            print(json.dumps({"result":"PASS","checked":count,"caption":msg,"K08":component(msg).hex().upper()}))
            return
    print(json.dumps({"result":"NO_MATCH","unique_checked":count,
          "family":"N02/N06/N20 version rewrite; no N13 base",
          "scope":"source-inspired speculative full-caption grammar; not an exclusion of unseen final wording"}))


if __name__ == "__main__":
    main()
