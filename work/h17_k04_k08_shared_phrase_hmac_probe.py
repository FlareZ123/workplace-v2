#!/usr/bin/env python3
"""Probe a shared-phrase K04/K08 construction against the surviving H-17 export.

Hypothesis:
  - one normalized keeper phrase is the message for both slots;
  - K08 = HMAC-SHA256(desk_nonce, phrase)[:16];
  - the PS-0417 attempt-2 RECOVER ACK payload is HMAC-SHA256(K04_mask, phrase)[:16];
  - the K04 component remains ACK_payload XOR K04_mask.

This is an exploratory cross-slot model, not an accepted reduction rule.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import zipfile
from email import policy
from email.parser import BytesParser
from pathlib import Path


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def add_spans(target: dict[str, set[str]], source: str, text: str,
              max_words: int = 24) -> None:
    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^(>+|\*+)\s*", "", line)
        chunks.append(line)
        chunks.extend(x.strip() for x in re.split(r"(?<=[.!?])\s+", line)
                      if x.strip())
    for chunk in chunks:
        words = chunk.split()
        for start in range(len(words)):
            for end in range(start + 1, min(len(words), start + max_words) + 1):
                phrase = normalize(" ".join(words[start:end]))
                if phrase:
                    target.setdefault(phrase, set()).add(source)


def hmac16(key: bytes, message: bytes) -> bytes:
    return hmac.new(key, message, hashlib.sha256).digest()[:16]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    args = parser.parse_args()

    acceptance = json.loads(args.acceptance.read_text(encoding="utf-8"))
    targets = {slot: bytes.fromhex(value)
               for slot, value in acceptance["slot_sha256"].items()}

    with zipfile.ZipFile(args.zip) as archive:
        route = json.loads(archive.read("evidence/recovery-routing.json"))
        mask = bytes.fromhex(route["K04"]["masked_component"])
        nonce = bytes.fromhex(route["K08"]["desk_nonce"])
        spool = archive.read("evidence/print/spool-reconstruction.log").decode(
            "utf-8", errors="replace")
        notes = archive.read(
            "evidence/crew/noticeboard-and-desk-notes.txt").decode(
                "utf-8", errors="replace")
        galley = archive.read(
            "evidence/crew/galley-and-stores.log").decode(
                "utf-8", errors="replace")

        selected_payload = None
        for line in spool.splitlines():
            if ("JOB=PS-261003-0417" in line and "ATTEMPT=2" in line
                    and "STATE=ACK" in line and "CLASS=RECOVER" in line):
                match = re.search(r"PAYLOAD=([0-9A-Fa-f]{32})", line)
                if match:
                    selected_payload = bytes.fromhex(match.group(1))
                    break
        if selected_payload is None:
            raise RuntimeError("selected PS-0417 attempt-2 RECOVER ACK not found")

        candidates: dict[str, set[str]] = {}
        add_spans(candidates, "crew_notes", notes)
        add_spans(candidates, "galley_log", galley)
        for name in archive.namelist():
            if name.startswith("evidence/mail/") and name.endswith(".eml"):
                message = BytesParser(policy=policy.default).parsebytes(
                    archive.read(name))
                body = message.get_body(preferencelist=("plain",))
                if body is not None:
                    add_spans(candidates, name, body.get_content())

    hits = {
        "K08_exact_HMAC": [],
        "K04_payload_is_HMAC": [],
        "K04_component_is_HMAC": [],
        "K04_reverse_HMAC": [],
        "K08_reverse_HMAC": [],
    }
    for phrase in candidates:
        message = phrase.encode("utf-8")
        k08_value = hmac16(nonce, message)
        if hashlib.sha256(k08_value).digest() == targets["K08"]:
            hits["K08_exact_HMAC"].append(phrase)

        k04_value = hmac16(mask, message)
        if k04_value == selected_payload:
            hits["K04_payload_is_HMAC"].append(phrase)
        k04_component = bytes(a ^ b for a, b in zip(k04_value, mask))
        if hashlib.sha256(k04_component).digest() == targets["K04"]:
            hits["K04_component_is_HMAC"].append(phrase)

        reverse_k04 = hmac16(message, mask)
        if reverse_k04 == selected_payload:
            hits["K04_reverse_HMAC"].append(phrase)
        reverse_k08 = hmac16(message, nonce)
        if hashlib.sha256(reverse_k08).digest() == targets["K08"]:
            hits["K08_reverse_HMAC"].append(phrase)

    print(json.dumps({
        "unique_normalized_spans": len(candidates),
        "source_files": len({s for owners in candidates.values() for s in owners}),
        "selected_payload_hex": selected_payload.hex().upper(),
        "K04_mask_hex": mask.hex().upper(),
        "K08_nonce_hex": nonce.hex().upper(),
        "hits": {name: values for name, values in hits.items()},
        "interpretation": (
            "No match rejects this shared-phrase HMAC construction for the "
            "enumerated retained-export text; it does not reject a phrase "
            "present only in missing envelope/photo-caption records."
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
