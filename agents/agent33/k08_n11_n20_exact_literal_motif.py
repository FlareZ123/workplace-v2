#!/usr/bin/env python3
"""Source-exact N20 motif correction for the bounded N11 K08 caption model.

Run with the original read-only source files:
  python agents/agent33/k08_n11_n20_exact_literal_motif.py \
    resources/evidence/crew/noticeboard-and-desk-notes.txt \
    resources/evidence/recovery-routing.json resources/acceptance.json

This is a bounded hypothesis test only. It does not modify candidate.json,
acceptance.json, routing, or the original verifier.
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
N20_BODY = (
    "I wanted the line to hold the sea, the end of the night and the voices at "
    "the table. Do not use the standby label just because it is shorter."
)
N13_BODY = (
    "At the end of the night the mugs stood beside the window, and somebody "
    "had remembered to leave the little lamp on."
)
N02_BODY = "A good watch leaves the room ready for the next pair of hands."
CUES = ("the sea", "the end of the night", "the voices at the table")
N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"
EXPECTED_ASSIGNMENTS = 2_224_128


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\\s]", " ", text.lower()).split())


def component(text: str, nonce: bytes) -> bytes:
    return hmac.digest(nonce, normalize(text).encode("utf-8"), "sha256")[:16]


def note_body(source: str, number: int) -> str:
    match = re.search(rf"(?m)^N{number:02d} / [^\\n]*\\n([^\\n]+)$", source)
    if match is None:
        raise ValueError(f"Missing N{number:02d}")
    return match.group(1).split(": ", 1)[-1]


def generate(base: list[str], cues: list[list[str]]):
    # All order-preserving N11 subsequences, with exactly three N20 motifs
    # inserted in the source's semantic order at nondecreasing word gaps.
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
    if observed != SOURCE_SHA:
        raise ValueError(f"Source fingerprints differ: {observed}")

    notes = source["crew"].decode("utf-8")
    routing = json.loads(source["routing"])
    acceptance = json.loads(source["acceptance"])
    n02, n11, n13, n20 = (note_body(notes, n) for n in (2, 11, 13, 20))
    if (n02, n11, n13, n20) != (N02_BODY, N11_BODY, N13_BODY, N20_BODY):
        raise ValueError("Pinned note text differs from the source export")

    # N20 says exactly "the end of the night"; the added "at" belongs to N13.
    n20_normalized = normalize(n20)
    n13_normalized = normalize(n13)
    if not all(cue in n20_normalized for cue in CUES):
        raise AssertionError("A cue is not present in N20's exact wording")
    if "at the end of the night" in n20_normalized:
        raise AssertionError("Unexpected N20 wording")
    if "at the end of the night" not in n13_normalized:
        raise AssertionError("The N13 source attribution check failed")

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    if component(n02, nonce).hex().upper() != N02_HMAC16:
        raise AssertionError("Original N02 known-answer control failed")

    base = normalize(n11).split()
    cues = [normalize(cue).split() for cue in CUES]
    if len(base) != 14:
        raise AssertionError(f"Expected 14 N11 words, got {len(base)}")

    planted_phrase = " ".join(
        base[:5] + cues[0] + base[5:9] + cues[1]
        + base[9:11] + cues[2] + base[11:]
    )
    planted_target = hashlib.sha256(component(planted_phrase, nonce)).hexdigest()

    count = planted = original = 0
    for phrase in generate(base, cues):
        count += 1
        token = component(phrase, nonce)
        digest = hashlib.sha256(token).hexdigest()
        if digest == planted_target:
            planted += 1
        if digest == target:
            original += 1

    if count != EXPECTED_ASSIGNMENTS:
        raise AssertionError(f"Assignment count mismatch: {count}")
    if planted != 1:
        raise AssertionError(f"Planted full-caption control mismatch: {planted}")
    if original:
        raise AssertionError(f"Unexpected original K08 hits: {original}")

    print(json.dumps({
        "source_sha256": observed,
        "base": "N11 Mug shelf",
        "n20_exact_motifs": CUES,
        "n13_contains_added_at": "at the end of the night" in n13_normalized,
        "complete_assignments": count,
        "original_k08_hits": original,
        "planted_complete_hits": planted,
        "n02_known_answer": N02_HMAC16,
        "result": "NO_HIT",
    }, indent=2))


if __name__ == "__main__":
    main()
