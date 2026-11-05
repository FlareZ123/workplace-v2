"""K08 source-wide literal-carrier search under one-byte XOR/add and ROT13.

Read-only 42-file original evidence scan. Fixed normalized text windows,
2..24 words, each checked against unchanged K08 nested HMAC/SHA256 target.
"""
from __future__ import annotations

import codecs
from collections import Counter
import hashlib
import hmac
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
PINS = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
PRINTABLE = re.compile(rb"[\x20-\x7e]{8,}")
TOKENS = re.compile(rb"[a-z0-9]+")
CONTROLS = {
    b"a good watch leaves the room ready for the next pair of hands": "N02",
    b"leave the light on for the next watch": "N17",
    b"back before the first boat": "N18",
}

def main() -> None:
    for filename, expected in PINS.items():
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected

    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    accepted = json.loads((ROOT / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(accepted["slot_sha256"]["K08"])
    assert hmac.digest(nonce, next(iter(CONTROLS)), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    def digest(candidate: bytes) -> bytes:
        return hashlib.sha256(hmac.digest(nonce, candidate, "sha256")[:16]).digest()

    seen = set()
    recovered_controls = set()
    stats = Counter()
    original_matches = []

    def search(data: bytes, name: str, transform: str) -> None:
        for run in PRINTABLE.finditer(data):
            words = TOKENS.findall(run.group().lower())
            if len(words) < 2:
                continue
            stats["runs"] += 1
            for left in range(len(words)):
                for width in range(2, min(24, len(words) - left) + 1):
                    phrase = b" ".join(words[left:left + width])
                    if len(phrase) < 7 or phrase in seen:
                        continue
                    seen.add(phrase)
                    if phrase in CONTROLS:
                        recovered_controls.add(CONTROLS[phrase])
                    if digest(phrase) == target:
                        original_matches.append((name, transform, phrase.decode()))
                        print("ORIGINAL_MATCH", original_matches[-1], flush=True)

    paths = sorted(x for x in (ROOT / "evidence").rglob("*") if x.is_file())
    assert len(paths) == 42
    for filename in paths:
        raw = filename.read_bytes()
        for mode in ("xor", "add"):
            for key in range(256):
                table = bytes((n ^ key if mode == "xor" else (n - key) & 255) for n in range(256))
                search(raw.translate(table), str(filename.relative_to(ROOT)), f"{mode}:{key}")
        text = codecs.encode(raw.decode("latin1"), "rot_13").encode("latin1")
        search(text, str(filename.relative_to(ROOT)), "rot13")

    original_count = len(seen)
    assert original_count == 7164804, original_count
    assert recovered_controls == {"N02", "N17", "N18"}
    assert not original_matches
    planted = b"sea and voices at the table before morning"
    planted_commitment = digest(planted)
    ciphertext = bytes(x ^ 0x93 for x in planted)
    synthetic_hits = 0
    for key in range(256):
        decoded = bytes(x ^ key for x in ciphertext)
        for run in PRINTABLE.finditer(decoded):
            words = TOKENS.findall(run.group().lower())
            for left in range(len(words)):
                for width in range(2, min(24, len(words) - left) + 1):
                    candidate = b" ".join(words[left:left + width])
                    synthetic_hits += digest(candidate) == planted_commitment
    assert synthetic_hits >= 1
    print(json.dumps({
        "files": len(paths), "decoded_runs": stats["runs"],
        "original_unique_candidates": original_count, "original_hits": len(original_matches),
        "old_full_text_controls": sorted(recovered_controls),
        "synthetic_xor_key_0x93_hits": synthetic_hits,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
