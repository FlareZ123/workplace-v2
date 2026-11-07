"""H17 K08: source nonce copied with one dropped and one extra hex nibble.

A transcription may move hex-nibble alignment across most of the 128-bit
route nonce while yielding another syntactically valid 32-hex field. Test
the FULL K08 HMAC16 -> SHA256 commitment against 281 genuinely preserved
whole-text source candidates. This is a conditional copied-key model, not
an attestation that the route nonce is wrong or source text is author-final.

Single portable test: python agents/agent36/k08_nonce_nibble_indel_sft.py
Runs read-only from the complete original repository checkout.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import hmac
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
TARGET = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")
N02 = "a good watch leaves the room ready for the next pair of hands"


def norm(s: str) -> str:
    return " ".join(re.findall("[a-z0-9]+", s.lower()))


def reduced(key: bytes, phrase: str) -> bytes:
    h = hmac.new(key, phrase.encode("utf8"), hashlib.sha256).digest()[:16]
    return hashlib.sha256(h).digest()


def source_texts(original_notes: bytes) -> set[str]:
    texts: dict[str, str] = {}
    lines = original_notes.decode("utf8").splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"N(\d{2}) /", line)
        if match:
            note = "N" + match.group(1)
            body = lines[index + 1].strip()
            texts[note] = body
            if ":" in body:
                texts[note + " caption"] = body.split(":", 1)[1].strip()
    for p in sorted((ROOT / "resources/evidence/mail").glob("*.eml")):
        body = p.read_text(encoding="utf8").split("\n\n", 1)[-1].strip()
        texts[p.stem] = body
        for j, value in enumerate(re.split(r"\n\s*\n", body)):
            if len(value.strip()) > 15:
                texts[f"{p.stem}p{j}"] = " ".join(value.split())
        for j, value in enumerate(
            re.split(r"(?<=[.!?])\s+", body.replace("\n", " "))
        ):
            if len(value.strip()) > 18:
                texts[f"{p.stem}s{j}"] = value.strip()
    phrases = {norm(value) for value in texts.values()} - {""}
    assert len(phrases) == 281
    assert N02 in phrases
    return phrases


def keys_from_hex(hextext: str) -> set[bytes]:
    assert len(hextext) == 32
    assert all(char in "0123456789ABCDEF" for char in hextext)
    return {
        bytes.fromhex(short[:j] + digit + short[j:])
        for i in range(32)
        for short in [hextext[:i] + hextext[i + 1:]]
        for j in range(32)
        for digit in "0123456789ABCDEF"
    }


def main() -> None:
    notes = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    route = (ROOT / "resources/evidence/recovery-routing.json").read_bytes()
    accept = (ROOT / "resources/acceptance.json").read_bytes()
    assert hashlib.sha256(notes).hexdigest() == SOURCE_SHA
    assert hashlib.sha256(route).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(accept).hexdigest() == ACCEPT_SHA
    official = json.loads(route)["K08"]["desk_nonce"].upper()
    genuine_nonce = bytes.fromhex(official)
    assert official == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert hmac.new(genuine_nonce, N02.encode(), hashlib.sha256).digest()[:16].hex() == (
        "bf889359b0303f2b2fd96ae841210b"
    )
    phrases = source_texts(notes)
    keys = keys_from_hex(official)
    assert len(keys) == 14368
    short = official[:4] + official[5:]
    planted_key = bytes.fromhex(short[:25] + "A" + short[25:])
    assert planted_key != genuine_nonce and planted_key in keys
    planted_target = reduced(planted_key, N02)
    assert planted_target != TARGET
    actual_hits: list[tuple[str, str]] = []
    plant_hits = 0
    for key in keys:
        for phrase in phrases:
            digest = reduced(key, phrase)
            if digest == TARGET:
                actual_hits.append((key.hex(), phrase))
            if digest == planted_target:
                plant_hits += 1
    assert len(actual_hits) == 0 and plant_hits == 1
    print(
        "K08_ORIGINAL_NONCE_SINGLE_NIBBLE_DROP_PLUS_INSERT "
        f"distinct_fullkeys={len(keys)} intact_source_texts={len(phrases)} "
        f"original_full_commitment_checks={len(keys)*len(phrases)} "
        f"authentic_hits={len(actual_hits)} planted_full_positive={plant_hits}"
    )
    print("K04_K08_UNRECOVERED SIX_ORIGINAL_SLOTS_UNCHANGED")


if __name__ == "__main__":
    main()
