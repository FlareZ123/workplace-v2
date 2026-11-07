"""Original-source H-17 K08 test: N02 aphorism-to-keeper-caption transformation.

Run as Python3 with --resources path/to/resources. Source files and original
acceptance are read-only. This model is an unsupported editorial hypothesis.
"""
import argparse
import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

NOTE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"

# An intentional N02 grammatical skeleton, unlike triptych / imperative editors.
# The small extra adjunct field is drawn from N20 and MAIL11.
SUBJECT = (
    "a good watch|a long watch|a late watch|a hard watch|a night watch|"
    "the last watch|the end of a long watch|the last hours of the night|"
    "the end of the night|a good night|a long night|the last cup|"
    "a shared cup|the early morning|the watch|one more cup|the sea at night"
).split("|")
VERB = (
    "leaves|keeps|makes|holds|gives|saves|finds|remembers|"
    "means leaving|is leaving|is keeping"
).split("|")
OBJECT = (
    "the room|the table|a place at the table|some room at the table|"
    "room at the table|one more place|one more cup|the light by the window|"
    "the lamp|a quiet place|the window|the galley|the last cup|space|"
    "a place|the night crew"
).split("|")
BENEFICIARY = (
    "ready for the next pair of hands|ready for the next person|"
    "ready for whoever comes next|ready for another voice|"
    "ready for one more cup|open for the next watch|open for another voice|"
    "there for the next watch|for one another|for the next person|"
    "for whoever needs it|for people who come after|"
    "for someone who has been awake|for another person|"
    "for everyone still awake|for somebody coming in|for one more pair of hands"
).split("|")
ADJUNCT = (
    "|with the water outside|with the sea outside|with the water still outside|"
    "with the sea still outside|while the sea is outside|"
    "while the sea is still outside|while the water is outside|"
    "while the water is still outside|as the night is almost over|"
    "as the night draws to a close|as the night comes to an end|"
    "at the end of the night|after a long watch|after the late watch|"
    "after the night watch|before the first boat|before the first light|"
    "when the night is nearly over|when the last watch ends|"
    "as morning comes|as the sea turns lighter|while the lamp is still on|"
    "with voices at the table|while voices gather at the table|"
    "with the night almost finished"
).split("|")


def normalize(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def phrase_component(nonce, text):
    return hmac.digest(nonce, normalize(text).encode("utf8"), "sha256")[:16]


def candidates():
    for subject, verb, obj, benefit in itertools.product(
        SUBJECT, VERB, OBJECT, BENEFICIARY
    ):
        base = f"{subject} {verb} {obj} {benefit}"
        yield base
        for adjunct in ADJUNCT[1:]:
            yield f"{base} {adjunct}"
            yield f"{adjunct} {base}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resources", type=Path,
        default=Path(__file__).resolve().parents[2] / "resources"
    )
    opts = parser.parse_args()
    root = opts.resources
    notes = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    mail = (root / "evidence/mail/11.eml").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == NOTE_SHA
    assert hashlib.sha256(mail).hexdigest() == MAIL11_SHA
    assert b"A good watch leaves the room ready for the next pair of hands." in notes
    assert b"people making room for each other after" in mail
    assert b"the water outside and the night almost finished" in mail
    assert b"the sea, the end of the night and the voices at the table" in notes
    routing = json.loads((root / "evidence/recovery-routing.json").read_text("utf8"))
    acceptance = json.loads((root / "acceptance.json").read_text("utf8"))
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    original = "a good watch leaves the room ready for the next pair of hands"
    assert phrase_component(nonce, original).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    synthetic = ("a long watch leaves a place at the table open for another voice "
                 "while the sea is outside")
    planted_sha = hashlib.sha256(phrase_component(nonce, synthetic)).digest()
    checks = original_hits = planted_hits = exact_n02 = 0
    for phrase in candidates():
        checks += 1
        if phrase == original:
            exact_n02 += 1
        digest = hashlib.sha256(phrase_component(nonce, phrase)).digest()
        if digest.hex() == target:
            original_hits += 1
            print("ORIGINAL_K08_HIT", repr(phrase))
        if digest == planted_sha:
            planted_hits += 1
            assert phrase == synthetic
    assert checks == (len(SUBJECT) * len(VERB) * len(OBJECT)
                      * len(BENEFICIARY) * (2 * len(ADJUNCT) - 1))
    assert checks == 2594064 and exact_n02 == 1 and planted_hits == 1
    print(json.dumps({"assignments": checks, "original_matches": original_hits,
                      "actual_N02_control": exact_n02,
                      "synthetic_complete_control": planted_hits}))


if __name__ == "__main__":
    main()
