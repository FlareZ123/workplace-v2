#!/usr/bin/env python3
"""Bounded K08 desk_nonce transcription-error screen.

Replays the supplied 4,871 normalized literal spans against the accepted
K08 commitment using the recorded nonce, every one-hex-nibble substitution,
and every distinct adjacent-nibble transposition. It does not attempt to
recover missing/nonliteral wording or authenticate the original nonce.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
SOURCE_HASHES = {
    "evidence/crew/noticeboard-and-desk-notes.txt":
        "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/crew/galley-and-stores.log":
        "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46",
    "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\\s]", " ", text.lower()).split())


def contiguous_spans(text: str):
    words = normalize(text).split()
    for length in range(1, min(64, len(words)) + 1):
        for start in range(len(words) - length + 1):
            yield " ".join(words[start:start + length])


def source_candidates() -> set[str]:
    note_path = RESOURCES / "evidence/crew/noticeboard-and-desk-notes.txt"
    galley_path = RESOURCES / "evidence/crew/galley-and-stores.log"
    lines = note_path.read_text(encoding="utf-8").splitlines()

    variants: list[str] = []
    note_count = 0
    for index, line in enumerate(lines):
        match = re.match(r"(N\\d{2}) / (.*)$", line)
        if not match:
            continue
        body = lines[index + 1].strip()
        author = match.group(2)
        variants.extend((body, author + " " + body))
        if ":" in body:
            variants.append(body.split(":", 1)[1].strip())
        note_count += 1

    galley_count = 0
    for line in galley_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        variants.append(line)
        if ":" in line:
            variants.append(line.split(":", 1)[1].strip())
        galley_count += 1

    assert note_count == 24, note_count
    assert galley_count == 7, galley_count
    candidates: set[str] = set()
    for variant in variants:
        candidates.update(contiguous_spans(variant))
    assert len(candidates) == 4871, len(candidates)
    return candidates


def nonce_variants(nonce_hex: str) -> set[str]:
    assert len(nonce_hex) == 32
    assert set(nonce_hex) <= set("0123456789ABCDEF")
    variants = {nonce_hex}
    alphabet = "0123456789ABCDEF"

    for position, original in enumerate(nonce_hex):
        for replacement in alphabet:
            if replacement != original:
                variants.add(
                    nonce_hex[:position] + replacement + nonce_hex[position + 1:]
                )

    for position in range(len(nonce_hex) - 1):
        if nonce_hex[position] == nonce_hex[position + 1]:
            continue
        variants.add(
            nonce_hex[:position]
            + nonce_hex[position + 1]
            + nonce_hex[position]
            + nonce_hex[position + 2:]
        )

    return variants


def main() -> None:
    for relative_path, expected_hash in SOURCE_HASHES.items():
        actual_hash = hashlib.sha256((RESOURCES / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, (relative_path, actual_hash)

    routing = json.loads((RESOURCES / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((RESOURCES / "acceptance.json").read_text())
    nonce_hex = routing["K08"]["desk_nonce"].upper()
    target = acceptance["slot_sha256"]["K08"]

    candidates = sorted(source_candidates())
    keys = sorted(nonce_variants(nonce_hex))
    hits: list[tuple[str, str]] = []

    for key_hex in keys:
        key = bytes.fromhex(key_hex)
        for message in candidates:
            component = hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()[:16]
            if hashlib.sha256(component).hexdigest() == target:
                hits.append((key_hex, message))

    print(f"literal normalized spans: {len(candidates)}")
    print(f"nonce variants: {len(keys)}")
    print(f"HMAC/commitment candidates: {len(candidates) * len(keys)}")
    print(f"exact K08 commitment hits: {len(hits)}")
    for key_hex, message in hits:
        print(f"HIT nonce={key_hex} phrase={message!r}")


if __name__ == "__main__":
    main()
