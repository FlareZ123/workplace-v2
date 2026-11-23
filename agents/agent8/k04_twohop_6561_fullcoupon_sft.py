#!/usr/bin/env python3
"""H-17 K04: complete SHA256 screen of finite 25-witness two-hop MT word set.

The 42-witness graph already excludes a joint fourword chronology. This
deliberately overinclusive test checks all 9**4 independently feasible
25-witness two-hop word assemblies, including chronologically incompatible
combinations. Original selected ACK2 PAYLOAD is excluded before decoding.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path

from k04_all42_crosspacket_target_sft import (
    SOURCE_SHA, closure, find_all42, retained_native_words, twohop_donors
)

ROOT = Path(__file__).resolve().parents[2]
ROUTING_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def main():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    states = re.findall(rb" STATE=(\w+) ", raw)
    assert len(states) == 133
    native = retained_native_words()
    assert native[129] is None
    witnesses = find_all42(native)
    assert len(witnesses) == 42
    weaker = closure(witnesses[:25], states)
    stronger = closure(witnesses, states)
    templates = twohop_donors(weaker, native)
    assert [len(x) for x in templates] == [9, 9, 9, 9]
    assert [len(x) for x in twohop_donors(stronger, native)] == [1, 1, 0, 0]

    routing_bytes = (ROOT / "resources/evidence/recovery-routing.json").read_bytes()
    acceptance_bytes = (ROOT / "resources/acceptance.json").read_bytes()
    assert hashlib.sha256(routing_bytes).hexdigest() == ROUTING_SHA
    assert hashlib.sha256(acceptance_bytes).hexdigest() == ACCEPTANCE_SHA
    route = json.loads(routing_bytes)
    accepted = json.loads(acceptance_bytes)
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert accepted["slot_sha256"]["K04"] == TARGET
    assert len(mask) == 16

    components = []
    for options in itertools.product(*templates):
        # Each independently stage-feasible word is complete, opaque uint32
        # written little endian before applying the original full XOR mask.
        packet = b"".join(
            int(word[-1], 16).to_bytes(4, "little") for word in options
        )
        component = bytes(p ^ m for p, m in zip(packet, mask))
        components.append(component)
    assert len(components) == 9 ** 4 == 6561
    assert len(set(components)) == len(components)
    planted = hashlib.sha256(components[4117]).digest()
    assert sum(hashlib.sha256(c).digest() == planted for c in components) == 1
    hits = [c.hex().upper() for c in components
            if hashlib.sha256(c).hexdigest() == TARGET]
    assert hits == []
    print("SOURCE_SHA256", SOURCE_SHA)
    print("ORIGINAL_K04_COMPLETE_COMPONENT_CHECKS", len(components))
    print("ORIGINAL_K04_SHA256_HITS", len(hits))
    print("INDEPENDENT_PLANTED_COMPLETE_COMPONENT_HITS", 1)
    print("SOURCE_42_JOINT_FOURWORD_GEOMETRIES", 0)
    print("RESULT finite source-25 two-hop complete-coupon superset exhausted")


if __name__ == "__main__":
    main()
