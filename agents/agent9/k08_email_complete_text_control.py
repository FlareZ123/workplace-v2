#!/usr/bin/env python3
"""Source-pinned complete-text HMAC control over all 20 surviving email records.

Tests whole messages, subjects, bodies, paragraphs, lines, and sentences only.
It deliberately does not assemble arbitrary fragments or invent caption wording.
"""
from __future__ import annotations

import email
import hashlib
import hmac
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources" / "evidence"
ACCEPTANCE = ROOT / "resources" / "acceptance.json"

EXPECTED_ACCEPTANCE = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
EXPECTED_ROUTING = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
EXPECTED_MAIL = {
    "01.eml": "df0729237a3d6d5e90bcaffa95b396d54e511007ec4b0c7e5e8490280aa1d698",
    "02.eml": "a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11",
    "03.eml": "3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889",
    "04.eml": "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
    "05.eml": "29d6d60c6addc16b6f3fd1803b582481a22ce0e757e0a1601a3dc7e116730272",
    "06.eml": "6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3",
    "07.eml": "ee0830aba2e08cc862179aeca034e075f76a08914e5ee6d604ad17f4b806ac22",
    "08.eml": "2da71346103454b6743698103f4d80d79bc0b6013046646e4611c08e8d5f0937",
    "09.eml": "1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c",
    "10.eml": "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    "11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "12.eml": "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    "13.eml": "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    "14.eml": "9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5",
    "15.eml": "249ec45e7c21b66faf0d3310cc742ffdc70e88396a10272932ce821649b7c9e2",
    "16.eml": "02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    "17.eml": "67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014",
    "18.eml": "7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0",
    "19.eml": "caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd",
    "20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    routing_path = EVIDENCE / "recovery-routing.json"
    if sha256(ACCEPTANCE) != EXPECTED_ACCEPTANCE:
        raise SystemExit("acceptance.json hash mismatch")
    if sha256(routing_path) != EXPECTED_ROUTING:
        raise SystemExit("recovery-routing.json hash mismatch")

    acceptance = json.loads(ACCEPTANCE.read_text())
    routing = json.loads(routing_path.read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    candidates: dict[str, list[dict[str, str | int]]] = {}
    raw_count = Counter()
    source_hashes = {}
    for filename, expected in EXPECTED_MAIL.items():
        path = EVIDENCE / "mail" / filename
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"{filename} hash mismatch: {actual}")
        source_hashes[filename] = actual

        raw = path.read_text(errors="replace")
        msg = email.message_from_string(raw)
        parts = re.split(r"\r?\n\r?\n", raw, maxsplit=1)
        body = parts[1] if len(parts) == 2 else raw
        texts = [
            ("full-message", raw),
            ("subject", msg.get("Subject", "")),
            ("body", body),
        ]
        texts.extend(("paragraph", value) for value in re.split(r"\r?\n\s*\r?\n", body) if value.strip())
        texts.extend(("line", value) for value in body.splitlines() if value.strip())
        texts.extend(("sentence", value) for value in re.split(r"(?<=[.!?])\s+", body) if value.strip())

        for kind, value in texts:
            raw_count[kind] += 1
            normalized = normalize(value)
            if normalized:
                candidates.setdefault(normalized, []).append({
                    "source": filename,
                    "kind": kind,
                    "excerpt": value[:160],
                })

    hits = []
    for normalized, origins in candidates.items():
        digest16 = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
        if hashlib.sha256(digest16).hexdigest() == target:
            hits.append({"normalized": normalized, "origins": origins})

    output = {
        "scope": "20 complete surviving email records; no arbitrary fragment assembly",
        "normalization": "lowercase; non-ASCII-alphanumeric/non-whitespace to spaces; collapse whitespace; trim",
        "hmac": "HMAC-SHA256(key=desk_nonce, message=normalized UTF-8); retain first 16 bytes; SHA256 compare to K08 commitment",
        "source_hashes": {
            "acceptance.json": sha256(ACCEPTANCE),
            "recovery-routing.json": sha256(routing_path),
            "mail": source_hashes,
        },
        "raw_candidate_counts_by_kind": dict(raw_count),
        "unique_normalized_candidate_count": len(candidates),
        "hit_count": len(hits),
        "hits": hits,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
