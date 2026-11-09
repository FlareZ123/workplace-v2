"""Original-source K08 Sea-Fever quotation/reframing hypothesis, read-only SFT.
Run: python agents/agent8/k08_seafever_literal_sft.py
Public-domain poem: https://poets.org/poem/sea-fever
"""
from __future__ import annotations

import hashlib
import hmac
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POEM = """I must go down to the seas again, to the lonely sea and the sky,
And all I ask is a tall ship and a star to steer her by,
And the wheel’s kick and the wind’s song and the white sail’s shaking,
And a grey mist on the sea’s face, and a grey dawn breaking,

I must go down to the seas again, for the call of the running tide
Is a wild call and a clear call that may not be denied;
And all I ask is a windy day with the white clouds flying,
And the flung spray and the blown spume, and the sea-gulls crying.

I must go down to the seas again, to the vagrant gypsy life,
To the gull’s way and the whale’s way where the wind’s like a whetted knife;
And all I ask is a merry yarn from a laughing fellow-rover,
And quiet sleep and a sweet dream when the long trick’s over."""

HEADS = (
    "", "we leave", "leave", "we leave room for each other",
    "there is room for each other", "there is always room for one another",
    "after the long watch", "after the late watch", "the night crew",
    "our late watch", "all we ask is", "when the long trick s over",
    "at the end of the night", "at the end of a long watch",
)
BODIES = (
    "", "a merry yarn", "a merry yarn from a laughing fellow rover",
    "a merry yarn from a laughing fellow rover and quiet sleep",
    "quiet sleep and a sweet dream", "a sweet dream when the long trick s over",
    "room for each other", "somebody remembering to leave the little lamp on",
    "a good watch leaves the room ready for the next pair of hands",
    "the little lamp stays on until the corridor has gone quiet",
    "the sea outside and voices at the table",
    "mugs beside the window and the water outside",
)
TAILS = (
    "", "when the long trick s over", "at the end of the night",
    "after the long watch", "before the first boat", "when the sea goes quiet",
    "while the sea waits outside", "for the next watch",
    "for the next pair of hands", "and a grey dawn breaking",
    "as dawn breaks over the water", "when the late watch is done",
    "with the water outside", "for those who follow",
)


def normalize(s: str) -> str:
    return " ".join(re.findall("[a-z0-9]+", s.lower()))


def main() -> None:
    evidence = ROOT / "resources" / "evidence"
    notes = (evidence / "crew" / "noticeboard-and-desk-notes.txt").read_bytes()
    routing = (evidence / "recovery-routing.json").read_bytes()
    acceptance = (ROOT / "resources" / "acceptance.json").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
    assert hashlib.sha256(routing).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
    assert hashlib.sha256(acceptance).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
    nonce = bytes.fromhex(json.loads(routing)["K08"]["desk_nonce"])
    target = json.loads(acceptance)["slot_sha256"]["K08"]

    def component(phrase: str) -> bytes:
        return hmac.digest(nonce, normalize(phrase).encode("utf-8"), "sha256")[:16]

    assert component("A good watch leaves the room ready for the next pair of hands.").hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    lines = [normalize(line) for line in POEM.splitlines() if line.strip()]
    assert len(lines) == 12
    words = " ".join(lines).split()
    assert len(words) > 120

    seen: set[str] = set()
    hits: list[dict[str, str]] = []
    synthetic = normalize(lines[-1])
    synthetic_digest = hashlib.sha256(component(synthetic)).digest()
    synthetic_hits = 0

    def test(raw_phrase: str) -> None:
        nonlocal synthetic_hits
        phrase = normalize(raw_phrase)
        if not phrase or phrase in seen:
            return
        seen.add(phrase)
        value = component(phrase)
        digest = hashlib.sha256(value).digest()
        if digest == synthetic_digest:
            synthetic_hits += 1
            assert phrase == synthetic
        if digest.hex() == target:
            hits.append({"phrase": phrase, "component": value.hex().upper()})

    for i in range(len(words)):
        for j in range(i + 1, len(words) + 1):
            test(" ".join(words[i:j]))
    for mask in range(1, 1 << len(lines)):
        test(" ".join(lines[i] for i in range(len(lines)) if mask & (1 << i)))
    for h, b, t in itertools.product(HEADS, BODIES, TAILS):
        test(" ".join((h, b, t)))

    assert synthetic_hits == 1
    assert len(seen) == 20836
    print(json.dumps({
        "distinct_normalized_complete_candidates": len(seen),
        "synthetic_full_reducer_positive": "PASS",
        "original_K08_SHA256_matches": hits,
        "source_or_verifier_modified": False,
    }, indent=2))


if __name__ == "__main__":
    main()
