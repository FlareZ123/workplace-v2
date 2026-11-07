#!/usr/bin/env python3
"""Source-pinned K08 test for the N12 workshop-card wording.

Run from the repository root:
    python agents/agent18/k08_n12_workshop_card_candidate_sft.py
"""
from __future__ import annotations
import hashlib, hmac, json, re
from pathlib import Path

EXPECTED = {
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}

def source_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    if (root / "resources" / "evidence").is_dir():
        return root
    if (root / "evidence").is_dir():
        return root
    raise FileNotFoundError("resources/evidence not found")

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()

def component(text: str, key: bytes) -> tuple[str, bytes, str]:
    normalized = normalize(text)
    hmac16 = hmac.new(key, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    return normalized, hmac16, hashlib.sha256(hmac16).hexdigest()

def main() -> None:
    root = source_root()
    paths = {name: root / name for name in EXPECTED}
    for name, path in paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == EXPECTED[name], (name, actual)

    notes = paths["evidence/crew/noticeboard-and-desk-notes.txt"].read_text(encoding="utf-8")
    route = json.loads(paths["evidence/recovery-routing.json"].read_text(encoding="utf-8"))
    acceptance = json.loads(paths["acceptance.json"].read_text(encoding="utf-8"))
    key = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    entries = {}
    for match in re.finditer(r"^N(\d{2})\s*/[^\n]*\n(.*?)(?=\nN\d{2}\s*/|\Z)", notes, flags=re.MULTILINE | re.DOTALL):
        note_id = int(match.group(1))
        body = match.group(2).strip()
        if ":" in body:
            body = body.split(":", 1)[1].strip()
        entries[note_id] = body

    n02_norm, n02_hmac, n02_commit = component(entries[2], key)
    n12_norm, n12_hmac, n12_commit = component(entries[12], key)
    assert n02_hmac.hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    assert n02_commit != target
    assert n12_commit != target

    print(json.dumps({
        "target_k08_sha256": target,
        "positive_control": {
            "note": "N02",
            "normalized": n02_norm,
            "hmac16": n02_hmac.hex().upper(),
            "component_sha256": n02_commit,
            "matches_k08": n02_commit == target,
        },
        "candidate": {
            "note": "N12",
            "normalized": n12_norm,
            "hmac16": n12_hmac.hex().upper(),
            "component_sha256": n12_commit,
            "matches_k08": n12_commit == target,
        },
    }, indent=2))

if __name__ == "__main__":
    main()
