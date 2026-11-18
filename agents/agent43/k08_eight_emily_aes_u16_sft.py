#!/usr/bin/env python3
"""Bounded K08 AES-u16 test over the eight Emily note jobs.

Conjectural inputs: the desk nonce is not source-attested as an AES key, and
the note-to-spool sequence alignment is a locator rather than a documented
cryptographic instruction. The finite test covers eight mapped ACK packets,
AES-128-ECB decryption, unsigned u16 offsets into the pinned book text, two
byte orders, zero/one index bases, and a source-indexed cross-note matrix
reading. It does not scan other spool jobs or invent further transforms.

Requires the local openssl executable.
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

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
BOOK_WORD_COUNT = 81_392
BOOK_JOINED_SHA256 = "36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66"

# Finite note-to-job crosswalk documented in
# results/h17-k08-full-note-spool-sequence-crosswalk-20261118.md.
NOTE_JOBS = (
    ("N02", "0302"),
    ("N06", "0306"),
    ("N10", "0310"),
    ("N13", "0313"),
    ("N17", "0317"),  # standby-label negative control
    ("N18", "0318"),  # commissioning-label negative control
    ("N20", "0320"),  # earlier authoring-brief control
    ("N23", "0323"),  # final-margin locator candidate
)
# Active phrase-source rows only; explicit controls above are not used here.
ACTIVE_NOTES = ("N02", "N06", "N10", "N13", "N23")


def normalize_phrase(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
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
            rf"\s+CLASS=([^\s]+)\s+PAYLOAD=([0-9A-Fa-f]{{32}})"
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

    spool_sha = hashlib.sha256(SPOOL.read_bytes()).hexdigest()
    if spool_sha != SPOOL_SHA256:
        raise ValueError(f"Unexpected pinned spool: sha256={spool_sha}")

    # Known-answer control: the exact N02 draft phrase is independently
    # recorded in the K08 route evidence and must reproduce its HMAC16.
    known_n02 = "a good watch leaves the room ready for the next pair of hands"
    known_n02_mac = hmac.new(nonce, normalize_phrase(known_n02).encode("utf-8"), hashlib.sha256).digest()[:16]
    if known_n02_mac.hex().upper() != "BF889359B0303F2B2B2FD96AE841210B":
        raise ValueError("N02 HMAC known-answer control failed")

    payloads = load_ack_payloads()
    plaintexts: dict[str, bytes] = {}
    offsets_by_note: dict[str, dict[str, list[int]]] = {}
    candidates = []

    def add_candidate(kind: str, notes: list[str], jobs: list[str], selector: str,
                      endian: str, base: int, offsets: list[int], phrase_words: list[str]) -> None:
        phrase = normalize_phrase(" ".join(phrase_words))
        mac16 = hmac.new(nonce, phrase.encode("utf-8"), hashlib.sha256).digest()[:16]
        digest = hashlib.sha256(mac16).hexdigest()
        candidates.append(
            {
                "kind": kind,
                "notes": notes,
                "jobs": jobs,
                "source_rows": [
                    {
                        "note": note,
                        "job": f"PS-261003-{dict(NOTE_JOBS)[note]}",
                        "class": payloads[note][0],
                        "dest": payloads[note][1],
                    }
                    for note in notes
                ],
                "selector": selector,
                "endian": endian,
                "base": base,
                "u16_offsets": offsets,
                "phrase": phrase,
                "hmac16": mac16.hex().upper(),
                "slot_sha256": digest,
                "match": digest == target,
            }
        )

    for note, job in NOTE_JOBS:
        class_name, dest, ciphertext = payloads[note]
        plaintext = decrypt_aes_ecb(ciphertext, nonce)
        plaintexts[note] = plaintext
        offsets_by_note[note] = {}
        for endian in ("big", "little"):
            offsets = [
                int.from_bytes(plaintext[i : i + 2], endian, signed=False)
                for i in range(0, 16, 2)
            ]
            offsets_by_note[note][endian] = offsets
            for base in (0, 1):
                indices = [offset - base for offset in offsets]
                if not all(0 <= index < len(raw_words) for index in indices):
                    raise ValueError(f"{note}/PS-{job}: offset outside pinned text")
                add_candidate(
                    "single-row",
                    [note],
                    [f"PS-261003-{job}"],
                    "all eight u16 offsets from one packet",
                    endian,
                    base,
                    offsets,
                    [raw_words[index] for index in indices],
                )

    # Cross-record hypothesis: one common column across the five active
    # Emily note rows yields one word per note. This is a bounded matrix
    # transpose, not a source-authenticated selection rule.
    for endian in ("big", "little"):
        for base in (0, 1):
            for column in range(8):
                offsets = [offsets_by_note[note][endian][column] for note in ACTIVE_NOTES]
                indices = [offset - base for offset in offsets]
                if not all(0 <= index < len(raw_words) for index in indices):
                    raise ValueError(f"active column {column + 1}: offset outside pinned text")
                add_candidate(
                    "cross-note-column",
                    list(ACTIVE_NOTES),
                    [f"PS-261003-{dict(NOTE_JOBS)[note]}" for note in ACTIVE_NOTES],
                    f"same column {column + 1} across active note rows",
                    endian,
                    base,
                    offsets,
                    [raw_words[index] for index in indices],
                )

            for selector, columns in (
                ("active ordinal diagonal", list(range(len(ACTIVE_NOTES)))),
                ("active reverse diagonal", list(range(7, 7 - len(ACTIVE_NOTES), -1))),
            ):
                offsets = [
                    offsets_by_note[note][endian][column]
                    for note, column in zip(ACTIVE_NOTES, columns)
                ]
                indices = [offset - base for offset in offsets]
                if not all(0 <= index < len(raw_words) for index in indices):
                    raise ValueError(f"{selector}: offset outside pinned text")
                add_candidate(
                    "cross-note-diagonal",
                    list(ACTIVE_NOTES),
                    [f"PS-261003-{dict(NOTE_JOBS)[note]}" for note in ACTIVE_NOTES],
                    selector,
                    endian,
                    base,
                    offsets,
                    [raw_words[index] for index in indices],
                )

    print(
        json.dumps(
            {
                "test": "eight-Emily-job AES-ECB unsigned-u16 whole-book and cross-note candidates",
                "spool_sha256": spool_sha,
                "book_word_count": len(raw_words),
                "N02_HMAC16_control": known_n02_mac.hex().upper(),
                "book_joined_sha256": joined_sha,
                "candidate_count": len(candidates),
                "match_count": sum(row["match"] for row in candidates),
                "target_K08_sha256": target,
                "plaintexts": {note: value.hex().upper() for note, value in plaintexts.items()},
                "candidates": candidates,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
