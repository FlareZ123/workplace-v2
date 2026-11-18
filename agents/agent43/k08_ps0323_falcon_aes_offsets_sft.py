"""Frozen read-only H-17 K08 AES-128/Falcon word-offset complete-candidate test.

The ordinal N23 -> PS-0323 relation and AES/book hypothesis are conjectural.
They are never promoted to historical facts. The original acceptance, route,
printer stream, and official verifier remain immutable.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from filelock import FileLock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent3"))
import k08_ps0323_falcon_word_offsets as original  # noqa: E402

OUT = ROOT / "work" / "agent43-falcon-aes"
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + ".lock"):
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=".tmp-agent43-", delete=False,
        ) as fh:
            temp_path = Path(fh.name)
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, path)


def aes_transform(key: bytes, block: bytes, decrypt: bool) -> bytes:
    assert len(key) == 16 and len(block) == 16
    context = Cipher(algorithms.AES(key), modes.ECB())
    operation = context.decryptor() if decrypt else context.encryptor()
    return operation.update(block) + operation.finalize()


def run() -> int:
    assert aes_transform(
        bytes.fromhex("000102030405060708090A0B0C0D0E0F"),
        bytes.fromhex("00112233445566778899AABBCCDDEEFF"), False,
    ).hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"
    assert aes_transform(
        bytes.fromhex("000102030405060708090A0B0C0D0E0F"),
        bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a"), True,
    ).hex() == "00112233445566778899aabbccddeeff"

    route = json.loads((ROOT / "resources" / "evidence" / "recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    assert acceptance["slot_sha256"]["K08"] == TARGET
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    baseline = original.normalize_phrase("A good watch leaves the room ready for the next pair of hands.")
    assert hmac.new(nonce, baseline.encode(), hashlib.sha256).digest()[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    rows = original.spool_packets()
    raw_book, words = original.fetch_book()
    assert len(words) == 81392
    word_stream = " ".join(words)
    write_atomic(OUT / "falcon-normalized-wordstream.txt", word_stream + "\n")
    report = {
        "hypothesis": "AES-128-ECB(desk_nonce, PS-0323 or PS-0320 payload) as eight Falcon word offsets",
        "status": "NO_MATCH",
        "source_authentication": {
            "book_url": original.SOURCE_URL,
            "raw_book_sha256": hashlib.sha256(raw_book).hexdigest(),
            "word_stream_sha256": hashlib.sha256(word_stream.encode()).hexdigest(),
            "spool_sha256": original.SPOOL_SHA256,
            "word_count": len(words),
        },
        "candidate_count": 0,
        "candidates": [],
        "matches": [],
        "interpretation": "N23-to-PS-0323 has no independently verified source join; this is a hypothesis test only.",
    }
    for job in ("PS-261003-0323", "PS-261003-0320"):
        packet = bytes.fromhex(rows[job]["payload"])
        for decrypt in (False, True):
            transformed = aes_transform(nonce, packet, decrypt)
            for order in ("big", "little"):
                offsets = [int.from_bytes(transformed[i:i + 2], order) for i in range(0, 16, 2)]
                for base in (0, 1):
                    positions = [index - base for index in offsets]
                    if min(positions) < 0 or max(positions) >= len(words):
                        continue
                    phrase = " ".join(words[index] for index in positions)
                    normalized = original.normalize_phrase(phrase)
                    component = hmac.new(nonce, normalized.encode(), hashlib.sha256).digest()[:16]
                    digest = hashlib.sha256(component).hexdigest()
                    found = digest == TARGET
                    item = {
                        "job": job,
                        "aes": "decrypt" if decrypt else "encrypt",
                        "byte_order": order,
                        "base": base,
                        "offsets": offsets,
                        "phrase": phrase,
                        "component_hex": component.hex().upper(),
                        "sha256": digest,
                        "accepted": found,
                    }
                    report["candidates"].append(item)
                    report["candidate_count"] += 1
                    if found:
                        report["matches"].append(item)
    assert report["candidate_count"] == 16
    planted = report["candidates"][3]
    planted16 = bytes.fromhex(planted["component_hex"])
    assert hashlib.sha256(planted16).hexdigest() == planted["sha256"]
    assert len(planted16) == 16
    if report["matches"]:
        report["status"] = "K08_PASS"
    write_atomic(OUT / "aes-word-offset-report.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_sha256": report["source_authentication"]["raw_book_sha256"],
        "word_stream_sha256": report["source_authentication"]["word_stream_sha256"],
        "word_count": len(words),
        "complete_candidates": report["candidate_count"],
        "target_hits": len(report["matches"]),
        "status": report["status"],
    }, sort_keys=True))
    for item in report["matches"]:
        print("HISTORICAL_COMMITMENT_MATCH", json.dumps(item, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
