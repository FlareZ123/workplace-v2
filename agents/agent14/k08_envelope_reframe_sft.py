"""K08 short inscription frames, original commitment and source-pinned synthetic control.

A retrospective hypothesized analogical editor for Emily's N17/N18 labels.
It reconstructs neither historic authorship nor the missing target by assumption.
"""
from hashlib import sha256
from hmac import digest as hmac_digest
from itertools import product
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTES = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert sha256(NOTES.read_bytes()).hexdigest() == SHA
notes = NOTES.read_text(encoding="utf-8")
assert "Standby envelope label: Leave the light on for the next watch." in notes
assert "Commissioning envelope label: Back before the first boat." in notes
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
want = bytes.fromhex(acceptance["slot_sha256"]["K08"])

def normalize(s):
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())

def derive(s):
    return hmac_digest(nonce, normalize(s).encode("utf-8"), "sha256")[:16]

assert derive("A good watch leaves the room ready for the next pair of hands.").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

VERBS = ("leave", "keep", "save", "hold", "make", "remember", "remember to leave", "remember to keep", "we leave", "we keep", "we made", "we saved", "someone left", "somebody kept", "there is", "there is always")
OBJECTS = ("the light", "the lamp", "the little lamp", "the room", "the table", "the last cup", "the chair", "a light", "a place", "a chair", "a seat", "a cup", "room", "room at the table", "a place at the table", "one more chair", "the window", "the voices")
STATES = ("on", "open", "ready", "warm", "waiting", "by the window", "at the window", "at the table", "for the next watch", "for one more", "for each other", "for whoever comes next", "till morning", "until morning", "when the night is done", "after the last cup", "after a long watch", "at the end of the night")
RECIPIENTS = ("the next watch", "whoever comes next", "one more", "the late crew", "the last watch", "the next pair of hands", "each other", "you", "us", "the room", "the table", "morning", "the sea", "the end of the night")
RETURN = ("back", "come back", "home", "come home", "here", "still here", "all here", "together", "back together", "come in", "stay", "stay awhile", "wait here", "we are here", "there is room", "there is always room")
TIME = ("before the first boat", "before the last boat", "before the first light", "before morning", "before the morning", "after the last cup", "after a long watch", "after the long watch", "after the last watch", "after the night watch", "at the end of the night", "by the first light", "until the next watch", "until the sea turns", "when the night is done", "when the sea is quiet", "while the sea waits", "when the water turns light")
SEA = ("the sea waits outside", "the water waits outside", "the sea is outside", "the water is outside", "the sea beyond the window", "the sea can wait", "the water can wait", "let the sea wait", "the sea will still be here", "the sea has not gone anywhere", "the night is almost finished", "the night is nearly over", "morning is almost here", "the water is turning to morning", "the sea is turning to morning", "the sea is still there")
COMPANY = ("there is room at the table", "there is always room at the table", "there is room for one more", "there is room for whoever comes next", "we have room for one more", "we make room for each other", "there is room for you", "leave room for one more", "leave a place at the table", "we left a place at the table", "someone kept a chair", "someone left a light on", "the mugs are by the window", "we are still here", "the voices are still here", "the table is still here", "the last cup is not finished", "the lamp is still on", "one more cup at the table", "the table has room for one more")
JOIN = ("and", "while", "but", "because", "as", "when")

def phrases():
    for verb, obj, state in product(VERBS, OBJECTS, STATES):
        yield f"{verb} {obj} {state}"
        for ending in ("after a long watch", "while the sea waits outside", "until morning"):
            yield f"{verb} {obj} {state} {ending}"
    for verb, obj, state, recipient in product(VERBS, OBJECTS, STATES, RECIPIENTS):
        yield f"{verb} {obj} {state} for {recipient}"
    for verb, obj, recipient in product(VERBS, OBJECTS, RECIPIENTS):
        yield f"{verb} {obj} for {recipient}"
    for verb, obj, time in product(VERBS, OBJECTS, TIME):
        yield f"{verb} {obj} {time}"
    for start, time in product(RETURN, TIME):
        yield f"{start} {time}"
    for start, time, obj in product(RETURN, TIME, ("at the table", "by the window", "for one more", "with the last cup")):
        yield f"{start} {time} {obj}"
    for sea, company, conjunction in product(SEA, COMPANY, JOIN):
        yield f"{sea} {conjunction} {company}"
        yield f"{company} {conjunction} {sea}"
    for sea, company in product(SEA, COMPANY):
        yield f"{sea}. {company}."
        yield f"{company}. {sea}."
    for company, time in product(COMPANY, TIME):
        yield f"{company} {time}"
        yield f"{time} {company}"

def main():
    count = duplicates = planted = 0
    first = None
    seen = set()
    category = {"3_6": 0, "7_10": 0, "11_14": 0, "15_plus": 0}
    proof = sha256()
    plant = normalize("the sea can wait and there is room for one more")
    plant_digest = sha256(derive(plant)).digest()
    for raw in phrases():
        s = normalize(raw)
        n = len(s.split())
        if not 3 <= n <= 18:
            continue
        if s in seen:
            duplicates += 1
            continue
        seen.add(s)
        count += 1
        category["3_6" if n <= 6 else "7_10" if n <= 10 else "11_14" if n <= 14 else "15_plus"] += 1
        proof.update(s.encode("ascii") + b"\n")
        d = sha256(derive(s)).digest()
        planted += d == plant_digest
        if d == want:
            first = {"phrase": s, "K08": derive(s).hex().upper(), "rank": count}
            break
    assert planted == 1
    print(json.dumps({"result": "MATCH" if first else "NO_MATCH", "match": first,
                      "unique_complete_candidates_checked": count, "duplicate_renders": duplicates,
                      "word_count_buckets": category, "synthetic_control_hits": planted,
                      "normalized_stream_sha256": proof.hexdigest()}, indent=2))

if __name__ == "__main__":
    main()
