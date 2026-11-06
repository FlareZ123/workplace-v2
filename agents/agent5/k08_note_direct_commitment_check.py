"""Check whether any surviving N01-N24 caption directly matches K08.

The route normalizer and HMAC commitment are applied exactly as specified:
HMAC-SHA256(key=desk_nonce, message=normalized_caption)[:16], then SHA-256
of the 16-byte component compared with acceptance.json's K08 slot digest.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

PINS = {
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
}


def normalize(value: str) -> str:
    value = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root
    resources = root / "resources" if (root / "resources").is_dir() else root

    paths = {
        "acceptance.json": resources / "acceptance.json",
        "evidence/recovery-routing.json": resources / "evidence/recovery-routing.json",
        "evidence/crew/noticeboard-and-desk-notes.txt": resources / "evidence/crew/noticeboard-and-desk-notes.txt",
    }
    for name, path in paths.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == PINS[name], (name, actual)

    route = json.loads(paths["evidence/recovery-routing.json"].read_text("utf-8"))["K08"]
    acceptance = json.loads(paths["acceptance.json"].read_text("utf-8"))
    nonce = bytes.fromhex(route["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    note_text = paths["evidence/crew/noticeboard-and-desk-notes.txt"].read_text("utf-8")
    notes = re.findall(r"(?m)^N(\d{2})\s+(.+)$", note_text)
    assert len(notes) == 24, len(notes)

    checks = []
    for note_id, caption in notes:
        normalized = normalize(caption)
        component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        commitment = hashlib.sha256(component).hexdigest()
        checks.append({
            "note_id": f"N{note_id}",
            "normalized": normalized,
            "matches_k08": commitment == target,
        })

    print(json.dumps({
        "status": "COMPLETE",
        "tested_notes": len(checks),
        "exact_matches": [row for row in checks if row["matches_k08"]],
        "result": "NO_SURVIVING_NOTE_LINE_MATCH" if not any(row["matches_k08"] for row in checks) else "MATCH_FOUND",
        "source_sha256": PINS,
        "normalization": "lowercase; replace non-ASCII-alphanumeric/non-whitespace with spaces; collapse whitespace; trim",
        "commitment": "SHA256(HMAC-SHA256(desk_nonce, normalized_caption)[:16])",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
