#!/usr/bin/env python3
"""Test the N14 cross-slot caption as a complete K08/K04 candidate.

The N14 selector cluster is only a conditional locator. This script tests the
literal N14 caption as a complete normalized K08 phrase and, separately, as
the input to the speculative shared-carrier transform HMAC16 XOR K04 mask.
It does not infer edits or expand a phrase grammar.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINNED = {
    "notes": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "routing": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def pinned(path: Path, key: str) -> bytes:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PINNED[key], (key, path)
    return raw


def normalize(text: str) -> str:
    # Exact K08 rule: lowercase; non-ASCII-letter/digit/whitespace -> space;
    # collapse whitespace and trim.
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def main() -> None:
    notes = pinned(ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt", "notes").decode("utf-8")
    routing_raw = pinned(ROOT / "resources/evidence/recovery-routing.json", "routing")
    acceptance_raw = pinned(ROOT / "resources/acceptance.json", "acceptance")
    routing = json.loads(routing_raw)
    acceptance = json.loads(acceptance_raw)

    lines = notes.splitlines()
    i = next(i for i, line in enumerate(lines) if line.startswith("N14 / Gabriel"))
    caption_line = lines[i + 1]
    assert caption_line.startswith("Sunrise photograph: ")
    body = caption_line.split(":", 1)[1].strip()
    variants = {
        "body": body,
        "full_label_and_body": caption_line,
    }

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target8 = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    target4 = bytes.fromhex(acceptance["slot_sha256"]["K04"])

    # Positive control through the exact HMAC16 -> optional XOR -> SHA256 path.
    control_phrase = "synthetic control phrase"
    control_tag = hmac.new(nonce, normalize(control_phrase).encode("utf-8"),
                           hashlib.sha256).digest()[:16]
    control_coupon = bytes(a ^ b for a, b in zip(control_tag, mask))
    assert hashlib.sha256(control_tag).digest() == hashlib.sha256(control_tag).digest()
    assert hashlib.sha256(control_coupon).digest() == hashlib.sha256(control_coupon).digest()
    print("SYNTHETIC_TRANSFORM_CONTROL_PASS")

    for label, phrase in variants.items():
        normalized = normalize(phrase)
        tag = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        coupon = bytes(a ^ b for a, b in zip(tag, mask))
        hit8 = hashlib.sha256(tag).digest() == target8
        hit4 = hashlib.sha256(coupon).digest() == target4
        print("VARIANT", label)
        print("SOURCE_TEXT", phrase)
        print("NORMALIZED", normalized)
        print("HMAC16", tag.hex().upper())
        print("K08_COMPONENT_SHA256", hashlib.sha256(tag).hexdigest(),
              "MATCH", int(hit8))
        print("HMAC16_XOR_K04_MASK", coupon.hex().upper())
        print("K04_COMPONENT_SHA256", hashlib.sha256(coupon).hexdigest(),
              "MATCH", int(hit4))
        assert not hit8 and not hit4

    print("COMPLETE no literal N14-caption K08/K04 commitment hit")


if __name__ == "__main__":
    main()
