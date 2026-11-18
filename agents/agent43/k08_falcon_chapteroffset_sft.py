"""Complete K08 source-only Falcon 15-chapter / 12-bit-word indexed caption SFT.

This is a conjectural 4+12-bit address coder for actual PS-0323 or PS-0320
historical packet bytes. N23 to PS-0323 is NOT source-authenticated.
Requires only the frozen public-domain Falcon 81,392-word text in this repo.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2]
WORD_PIN = "36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66"
SPOOL_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
CHAPTERS = ("ii", "iii", "iv", "v", "vi", "vii", "viii", "ix",
            "x", "xi", "xii", "xiii", "xiv", "xv")
ORIGINAL_JOBS = ("PS-261003-0323", "PS-261003-0320")


def offsets_as_words(
    values: list[int], boundaries: list[int], words: list[str],
    orientation: str, chapter_base: int, word_base: int,
) -> str | None:
    positions = []
    for value in values:
        if orientation == "high":
            chapter = (value >> 12) - chapter_base
            index = (value & 4095) - word_base
        else:
            chapter = (value & 15) - chapter_base
            index = (value >> 4) - word_base
        if not 0 <= chapter < 15 or not 0 <= index < boundaries[chapter + 1] - boundaries[chapter]:
            return None
        positions.append(boundaries[chapter] + index)
    return " ".join(words[i] for i in positions)


def main() -> None:
    wordpath = ROOT / "work/h17_falcon_1889_normalized_words.txt"
    wordraw = wordpath.read_bytes()
    assert wordraw.endswith(b"\n")
    assert hashlib.sha256(wordraw[:-1]).hexdigest() == WORD_PIN
    words = wordraw[:-1].decode("ascii").split()
    assert len(words) == 81392
    boundaries = [0]
    for i, word in enumerate(words[:-1]):
        if word == "chapter" and words[i + 1] in CHAPTERS:
            boundaries.append(i)
    boundaries.append(len(words))
    assert boundaries == [
        0, 3278, 8236, 14403, 20871, 28053, 33145, 40292,
        44696, 49818, 56233, 61762, 67997, 74086, 79441, 81392,
    ]
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_PIN
    routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    key = bytes.fromhex(routing["K08"]["desk_nonce"])
    assert acceptance["slot_sha256"]["K08"] == TARGET
    assert key.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert hmac.digest(
        key, b"a good watch leaves the room ready for the next pair of hands",
        "sha256",
    )[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    test_key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
    test_block = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    sample = Cipher(algorithms.AES(test_key), modes.ECB()).encryptor()
    assert (sample.update(test_block) + sample.finalize()).hex() == (
        "69c4e0d86a7b0430d8cdb78070b4c55a"
    )

    planted_values = [((i + 1) << 12) | (i + 20) for i in range(8)]
    expected = " ".join(words[boundaries[i] + 20 + i] for i in range(8))
    assert offsets_as_words(planted_values, boundaries, words, "high", 1, 0) == expected
    planted_digest = hashlib.sha256(hmac.digest(key, expected.encode(), "sha256")[:16]).hexdigest()
    control_decoded = offsets_as_words(planted_values, boundaries, words, "high", 1, 0)
    assert hashlib.sha256(hmac.digest(key, control_decoded.encode(), "sha256")[:16]).hexdigest() == planted_digest

    packet_rows = {}
    for line in spool.decode().splitlines():
        for job in ORIGINAL_JOBS:
            if f"JOB={job} " in line:
                assert job not in packet_rows
                assert "ATTEMPT=1 STATE=ACK CLASS=RECOVER" in line
                packet_rows[job] = bytes.fromhex(line.split("PAYLOAD=")[1].split()[0])
    assert set(packet_rows) == set(ORIGINAL_JOBS)
    attempts = valid = 0
    hits = []
    for job, packet in packet_rows.items():
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        enc = cipher.encryptor()
        dec = cipher.decryptor()
        for transform, raw in (
            ("raw", packet),
            ("aes_encrypt", enc.update(packet) + enc.finalize()),
            ("aes_decrypt", dec.update(packet) + dec.finalize()),
        ):
            for endian in ("big", "little"):
                values = [int.from_bytes(raw[i:i + 2], endian) for i in range(0, 16, 2)]
                for orientation in ("high", "low"):
                    for chapter_base in (0, 1):
                        for word_base in (0, 1):
                            attempts += 1
                            phrase = offsets_as_words(
                                values, boundaries, words,
                                orientation, chapter_base, word_base,
                            )
                            if phrase is None:
                                continue
                            valid += 1
                            component = hmac.digest(key, phrase.encode(), "sha256")[:16]
                            if hashlib.sha256(component).hexdigest() == TARGET:
                                hits.append({
                                    "job": job, "transform": transform, "endian": endian,
                                    "orientation": orientation, "chapter_base": chapter_base,
                                    "word_base": word_base, "phrase": phrase,
                                    "component_hex": component.hex().upper(),
                                })
    assert (attempts, valid) == (96, 32)
    print(json.dumps({
        "original_bounded_hypotheses": attempts,
        "all_8_words_source_in_range": valid,
        "original_k08_hits": hits,
        "control": "N02_HMAC_AES_VECTOR_SYNTHETIC_CHAPTER_WORD_PASS",
        "status": "K08_MISSING" if not hits else "EXPERIMENTAL_K08_MATCH",
    }, indent=2))


if __name__ == "__main__":
    main()
