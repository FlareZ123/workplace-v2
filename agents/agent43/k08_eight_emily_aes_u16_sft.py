#!/usr/bin/env python3
"""Bounded K08 AES-u16 candidate test over the eight Emily note jobs.

This is explicitly conjectural: the desk nonce is not source-attested as an
AES key, and the note-to-spool sequence alignment is a locator rather than a
documented cryptographic instruction. The test is finite: eight mapped jobs,
AES-128-ECB decryption, unsigned u16 offsets, two byte orders, and zero/one
index bases. It does not scan other spool jobs or invent further transforms.

Requires the local `openssl` executable.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources/evidence/print/spool-reconstruction.log"
ROUTING = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"
BOOK = ROOT / "work/h17_falcon_1889_normalized_words.txt"

BOOK_WORD_COUNT = 81_392
BOOK_JOINED_SHA256 = "36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66"

# The finite note-to-job crosswalk documented in
# results/h17-k08-full-note-spool-sequence-crosswalk-20261118.md.
NOTE_JOBS = (
    ("N02", "0302"),
    ("N06", "0306"),
    ("N10", "0310"),
    ("N13", "0313"),
    ("N17", "0317"),  # explicit standby-label negative control
    ("N18", "0318"),  # explicit commissioning-label negative control
    ("N20", "0320"),  # earlier authoring-brief control
    ("N23", "0323"),  # final-margin locator candidate
)


def normalize_phrase(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def decrypt_aes_ecb(ciphertext: bytes, key: bytes) -> bytes:
    if len(ciphertext) != 16 or len(key) != 16:
        raise ValueError("AES-128-ECB candidate must be exactly one 16-byte block")
    with tempfile.TemporaryDirectory(prefix="h17-k08-aesu16-") as tmp:
        source = Path(tmp) / "cipher.bin"
        target = Path(tmp) / "plain.bin"
        source.write_bytes(ciphertext)
        subprocess.run(
            [
                "openssl", "enc", "-aes-128-ecb", "-d", "-nosalt", "-nopad",
                "-K", key.hex(), "-in", str(source), "-out", str(target),
            ],
            check=True,
            capture_output=True,
        )
        plaintext = target.read_bytes()
    if len(plaintext) != 16:
        raise ValueError(f"OpenSSL returned {len(plaintext)} bytes, expected 16")
    return plaintext


def load_ack_payloads() -> dict[str, tuple[str, str, bytes]]:
    text = SPOOL.read_text(encoding="utf-8")
    found: dict[str, tuple[str, str, bytes]] = {}
    for note, job in NOTE_JOBS:
        pattern = re.compile(
            rf"JOB=PS-261003-{job}\s+ATTEMPT=(\d+)\s+STATE=ACK"
            rf"\s+CLASS=([^\s]+)\s+PAYLOAD=([0-9A-Fa-f]{32})"
            rf"\s+DEST=([^\s]+)"
        )
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            raise ValueError(f"{note}/PS-{job}: expected exactly one ACK row, found {len(matches)}")
        m = matches[0]
        found[note] = (m.group(2), m.group(4), bytes.fromhex(m.group(3)))
    return found


def main() -> int:
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]

    raw_words = BOOK.read_text(encoding="utf-8").split()
    joined = " ".join(raw_words)
    joined_sha = hashlib.sha256(joined.encode("ascii")).hexdigest()
    if len(raw_words) != BOOK_WORD_COUNT or joined_sha != BOOK_JOINED_SHA256:
        raise ValueError(
            f"Unexpected pinned book text: words={len(raw_words)}, sha256={joined_sha}"
        )

    payloads = load_ack_payloads()
    rows = []
    for note, job in NOTE_JOBS:
        class_name, dest, ciphertext = payloads[note]
        plaintext = decrypt_aes_ecb(ciphertext, nonce)
        for endian in ("big", "little"):
            offsets = [
                int.from_bytes(plaintext[i : i + 2], endian, signed=False)
                for i in range(0, 16, 2)
            ]
            for base in (0, 1):
                indices = [offset - base for offset in offsets]
                if not all(0 <= index < len(raw_words) for index in indices):
                    raise ValueError(f"{note}/PS-{job}: offset outside pinned text")
                phrase = " ".join(raw_words[index] for index in indices)
                normalized = normalize_phrase(phrase)
                mac16 = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
                digest = hashlib.sha256(mac16).hexdigest()
                rows.append(
                    {
                        "note": note,
                        "job": f"PS-261003-{job}",
                        "class": class_name,
                        "dest": dest,
                        "ciphertext": ciphertext.hex().upper(),
                        "aes_plaintext": plaintext.hex().upper(),
                        "endian": endian,
                        "base": base,
                        "u16_offsets": offsets,
                        "phrase": normalized,
                        "hmac16": mac16.hex().upper(),
                        "slot_sha256": digest,
                        "match": digest == target,
                    }
                )

    print(
        json.dumps(
            {
                "test": "eight-Emily-job AES-ECB unsigned-u16 whole-book candidates",
                "book_word_count": len(raw_words),
                "book_joined_sha256": joined_sha,
                "candidate_count": len(rows),
                "match_count": sum(row["match"] for row in rows),
                "target_K08_sha256": target,
                "candidates": rows,
            },
            indent=2,
        )
    )
    return 0 if not any(row["match"] for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
