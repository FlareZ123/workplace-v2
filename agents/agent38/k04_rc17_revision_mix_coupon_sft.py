#!/usr/bin/env python3
"""Bounded RC-17 cross-slot candidate test for the original K04 commitment.

This tests whether the 16-byte K04 coupon could be a concatenation of the four
RC-17 footer strips, including named service/standby ordering and revision mixes.
It does not assert that the source records historically define this relationship.
"""
from __future__ import annotations

import configparser
import hashlib
import itertools
import json
import os
import re
from pathlib import Path

SOURCE_ROOT = (
    Path(os.environ["H17_SOURCE_ROOT"])
    if "H17_SOURCE_ROOT" in os.environ
    else Path(__file__).resolve().parents[2]
)
if (SOURCE_ROOT / "evidence").is_dir():
    EVIDENCE = SOURCE_ROOT / "evidence"
    ACCEPTANCE = SOURCE_ROOT / "acceptance.json"
else:
    EVIDENCE = SOURCE_ROOT / "resources" / "evidence"
    ACCEPTANCE = SOURCE_ROOT / "resources" / "acceptance.json"

RC17_PATH = EVIDENCE / "procedures" / "RC-17-scans.txt"
LABELS_PATH = EVIDENCE / "archive-labels.ini"
ROUTING_PATH = EVIDENCE / "recovery-routing.json"

EXPECTED_SHA256 = {
    RC17_PATH.name: "a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d",
    LABELS_PATH.name: "146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad",
    ROUTING_PATH.name: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ACCEPTANCE.name: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path in (RC17_PATH, LABELS_PATH, ROUTING_PATH, ACCEPTANCE):
    actual = sha256_file(path)
    assert actual == EXPECTED_SHA256[path.name], (path, actual)

rc17 = RC17_PATH.read_text(encoding="utf-8")
strips = {
    (revision, section): bytes.fromhex(value)
    for revision, section, value in re.findall(
        r"DOCUMENT RC-17 / REV (B|C|D-draft) / SECTION (\w+).*?"
        r"Footer control strip: ([0-9A-F]{8})",
        rc17,
        re.S,
    )
}
assert len(strips) == 12
assert all(len(value) == 4 for value in strips.values())

labels = configparser.ConfigParser()
labels.read(LABELS_PATH, encoding="utf-8")
service_order = [x.strip() for x in labels["archive"]["service_order"].split(",")]
standby_order = [x.strip() for x in labels["archive"]["standby_order"].split(",")]
assert service_order == ["DRAIN", "ISOLATE", "PURGE", "VERIFY"]
assert standby_order == ["ISOLATE", "VERIFY", "DRAIN", "PURGE"]

routing = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]
assert len(mask) == 16
assert len(target) == 64


def candidate_digest(coupon: bytes) -> str:
    assert len(coupon) == 16
    component = bytes(a ^ b for a, b in zip(coupon, mask))
    return hashlib.sha256(component).hexdigest()


# Family A: all 24 C-strip section permutations, independent byte reversal
# within each four-byte strip, and whole-block reversal.
c_permutation_candidates: set[bytes] = set()
c_assignments = 0
for order in itertools.permutations(service_order):
    for flips in itertools.product((False, True), repeat=4):
        words = [
            strips[("C", section)][::-1] if flip else strips[("C", section)]
            for section, flip in zip(order, flips)
        ]
        coupon = b"".join(words)
        for whole_reverse in (False, True):
            c_assignments += 1
            c_permutation_candidates.add(coupon[::-1] if whole_reverse else coupon)

# Family B: all 3^4 B/C/D-draft revision selections by section in each of the
# two named orders, with the same byte-orientation variants.
revisions = ("B", "C", "D-draft")
mixed_revision_candidates: set[bytes] = set()
mixed_assignments = 0
for choices in itertools.product(revisions, repeat=4):
    for order in (service_order, standby_order):
        words_by_section = [
            strips[(revision, section)]
            for revision, section in zip(choices, order)
        ]
        for flips in itertools.product((False, True), repeat=4):
            words = [
                word[::-1] if flip else word
                for word, flip in zip(words_by_section, flips)
            ]
            coupon = b"".join(words)
            for whole_reverse in (False, True):
                mixed_assignments += 1
                mixed_revision_candidates.add(
                    coupon[::-1] if whole_reverse else coupon
                )

all_candidates = c_permutation_candidates | mixed_revision_candidates
original_hits = [
    coupon.hex().upper()
    for coupon in all_candidates
    if candidate_digest(coupon) == target
]

# Plant one complete positive from the tested set to validate the full
# mask/XOR/SHA256 acceptance path independently of the original target.
planted_coupon = min(all_candidates)
planted_component = bytes(a ^ b for a, b in zip(planted_coupon, mask))
planted_target = hashlib.sha256(planted_component).hexdigest()
planted_hits = [
    coupon for coupon in all_candidates if candidate_digest(coupon) == planted_target
]
assert planted_hits == [planted_coupon]
assert original_hits == []

candidate_set_sha256 = hashlib.sha256(
    b"\n".join(coupon.hex().upper().encode("ascii") for coupon in sorted(all_candidates))
).hexdigest()

print(f"c_permutation_assignments={c_assignments}")
print(f"c_permutation_unique={len(c_permutation_candidates)}")
print(f"mixed_revision_named_order_assignments={mixed_assignments}")
print(f"mixed_revision_named_order_unique={len(mixed_revision_candidates)}")
print(f"overlap_unique={len(c_permutation_candidates & mixed_revision_candidates)}")
print(f"union_unique={len(all_candidates)}")
print(f"original_k04_hits={len(original_hits)}")
print(f"planted_positive_hits={len(planted_hits)}")
print(f"candidate_set_sha256={candidate_set_sha256}")
