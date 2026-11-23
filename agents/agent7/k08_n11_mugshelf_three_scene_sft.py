#!/usr/bin/env python3
"""K08 N11 mug-shelf ordered-subsequence plus three-scene full-caption test.

Run with three original read-only paths:
    python agents/agent7/k08_n11_mugshelf_three_scene_sft.py CREW ROUTING ACCEPTANCE
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

SOURCE_SHA = {
    "crew": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
N11_BODY = "Even the chipped blue one belongs to someone who expects to see it again."
N02_BODY = "A good watch leaves the room ready for the next pair of hands."
CUES = ("the sea", "at the end of the night", "the voices at the table")
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
ASSIGNMENTS = 2224128


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def component(text: str, nonce: bytes) -> bytes:
    return hmac.digest(nonce, normalize(text).encode("utf-8"), "sha256")[:16]


def note_body(source: str, number: int) -> str:
    match = re.search(rf"(?m)^N{number:02d} / [^\n]*\n([^\n]+)$", source)
    if match is None:
        raise ValueError(f"Missing N{number:02d}")
    return match.group(1).split(": ", 1)[-1]


def generate(base: list[str], cues: list[list[str]]):
    # Every order-preserving subsequence of N11, including the empty one.
    # Three literal N20 sea/night/table motifs are inserted in that order.
    for mask in range(1 << len(base)):
        kept = [word for index, word in enumerate(base) if (mask >> index) & 1]
        for a in range(len(kept) + 1):
            for b in range(a, len(kept) + 1):
                for c in range(b, len(kept) + 1):
                    yield " ".join(
                        kept[:a] + cues[0] + kept[a:b] + cues[1]
                        + kept[b:c] + cues[2] + kept[c:]
                    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("crew", type=Path)
    parser.add_argument("routing", type=Path)
    parser.add_argument("acceptance", type=Path)
    args = parser.parse_args()

    paths = {"crew": args.crew, "routing": args.routing, "acceptance": args.acceptance}
    source = {name: path.read_bytes() for name, path in paths.items()}
    observed = {name: hashlib.sha256(data).hexdigest() for name, data in source.items()}
    assert observed == SOURCE_SHA, observed
    notes = source["crew"].decode("utf-8")
    route = json.loads(source["routing"])
    acceptance = json.loads(source["acceptance"])
    assert note_body(notes, 11) == N11_BODY
    assert note_body(notes, 2) == N02_BODY

    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    assert component(N02_BODY, nonce).hex().upper() == N02_HMAC16

    base = normalize(N11_BODY).split()
    cues = [normalize(cue).split() for cue in CUES]
    assert len(base) == 14
    planted_phrase = " ".join(
        base[:5] + cues[0] + base[5:9] + cues[1]
        + base[9:11] + cues[2] + base[11:]
    )
    planted_target = hashlib.sha256(component(planted_phrase, nonce)).hexdigest()

    count = planted = original = 0
    first_hit = None
    for phrase in generate(base, cues):
        count += 1
        token = component(phrase, nonce)
        digest = hashlib.sha256(token).hexdigest()
        if digest == planted_target:
            planted += 1
        if digest == target:
            original += 1
            if first_hit is None:
                first_hit = {"phrase": phrase, "component_hex": token.hex().upper()}
    assert count == ASSIGNMENTS
    assert planted >= 1
    print(json.dumps({
        "source_sha256": observed,
        "base": "N11 Mug shelf",
        "base_words": len(base),
        "motifs": CUES,
        "complete_assignments": count,
        "original_k08_hits": original,
        "planted_complete_hits": planted,
        "original_hit": first_hit,
    }, indent=2))


if __name__ == "__main__":
    main()
