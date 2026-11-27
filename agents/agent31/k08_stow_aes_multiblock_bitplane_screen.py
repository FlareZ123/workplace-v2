#!/usr/bin/env python3
"""Local-only exact source-selected K08 AES/LOWBIT multiblock carrier screen.

No actual source caption, key, ciphertext, HMAC or candidate wording is printed.
Never reads selected ACK2, private sources, PDF, or public CI inputs.
Requires cryptography package and the untouched canonical original text export.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import hmac
import json
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
DATA = SOURCE.read_bytes()
assert sha256(DATA).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
notes = {
    int(m.group(1)): m.group(2) for m in re.finditer(
        r"^N(\d{2}) /[^\n]+\n([^\n]+)", DATA.decode("ascii"), re.M)
}
assert len(notes) == 24
words = lambda s: re.findall(r"[A-Za-z0-9]+", s)
fragments = (
    words(notes[9].split(":", 1)[-1])[0],
    words(notes[13])[0],
    words(notes[23])[0],
    words(notes[20])[18],
)
keys = (
    "".join(fragments).upper().encode("ascii"),
    "".join(fragments).lower().encode("ascii"),
    "".join(x.capitalize() for x in fragments).encode("ascii"),
)
assert all(len(key) == 16 for key in keys)

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
expected_sha = bytes.fromhex(json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K08"])

# Source-local paths, fixed before consulting original K08 commitment.
sequences = {
    "N09_13_23_20": [9, 13, 23, 20],
    "N09_12_13_23_20": [9, 12, 13, 23, 20],
    "STOW": [19, 20, 15, 23],
    "N09_12_23_20": [9, 12, 23, 20],
}


def decrypt(key, buf, mode, iv):
    if mode == "CBC":
        block_mode = modes.CBC(iv)
    elif mode == "CTR":
        block_mode = modes.CTR(iv)
    else:
        assert mode == "ECB"
        block_mode = modes.ECB()
    cipher = Cipher(algorithms.AES(key), block_mode).decryptor()
    return cipher.update(buf) + cipher.finalize()


def main():
    tally = Counter()
    for ids in sequences.values():
        for serialization in (
            "\n".join(notes[i] for i in ids),
            "".join(re.sub(r"\s+", "", notes[i]) for i in ids),
            "\n".join(notes[i].split(":", 1)[-1] for i in ids),
        ):
            bits = [ord(ch) & 1 for ch in serialization]
            for blocks in (2, 3, 4):
                nbits = 128 * blocks
                if len(bits) < nbits:
                    continue
                for phase in range(min(32, len(bits) - nbits + 1)):
                    selection = bits[phase:phase + nbits]
                    for bit_order in (False, True):
                        ciphertext = bytes(
                            sum(bit << (7 - j if bit_order else j)
                                for j, bit in enumerate(selection[i:i+8]))
                            for i in range(0, nbits, 8)
                        )
                        for key in keys:
                            for mode, iv in (
                                ("CBC", nonce), ("CTR", nonce),
                                ("CBC", bytes(16)), ("CTR", bytes(16)),
                                ("ECB", None),
                            ):
                                plain = decrypt(key, ciphertext, mode, iv)
                                tally["full_decryptions"] += 1
                                if not all(ch in (9, 10, 11, 12, 13) or 32 <= ch <= 126
                                           for ch in plain):
                                    continue
                                tally["fully_printable_candidates"] += 1
                                norm = " ".join(re.findall(r"[a-z0-9]+", plain.decode("ascii").lower()))
                                if not norm:
                                    continue
                                component = hmac.new(nonce, norm.encode("utf-8"), "sha256").digest()[:16]
                                tally["original_full_commitment_checks"] += 1
                                if sha256(component).digest() == expected_sha:
                                    tally["full_K08_matches"] += 1

    # Synthetic positive confirms complete 32-byte AES cipher and bitplane
    # serialization, with an independent key, IV and artificial cover.
    synthetic_key = bytes(range(16))
    synthetic_iv = bytes(range(16, 32))
    synthetic_plain = bytes(range(65, 97))  # synthetic 32 printable ASCII bytes
    for mode in ("CBC", "CTR", "ECB"):
        cryptomode = modes.CBC(synthetic_iv) if mode == "CBC" else (
            modes.CTR(synthetic_iv) if mode == "CTR" else modes.ECB())
        encoder = Cipher(algorithms.AES(synthetic_key), cryptomode).encryptor()
        ciphertext = encoder.update(synthetic_plain) + encoder.finalize()
        for high_first in (False, True):
            bits = [(byte >> (7-j if high_first else j)) & 1
                    for byte in ciphertext for j in range(8)]
            carrier = [1] * 7 + bits + [0] * 7
            unpacked = bytes(sum(carrier[7 + i*8 + j] << (7-j if high_first else j)
                                 for j in range(8)) for i in range(32))
            assert unpacked == ciphertext
            assert decrypt(synthetic_key, unpacked, mode,
                           synthetic_iv if mode != "ECB" else None) == synthetic_plain
            tally["synthetic_whole_cipher_controls"] += 1

    assert tally["synthetic_whole_cipher_controls"] == 6
    assert tally["full_decryptions"] == 20370
    # Never print encrypted source, guessed original plaintext or key.
    print(json.dumps({"source_cases": tally["full_decryptions"],
                      "fully_printable": tally["fully_printable_candidates"],
                      "full_commitment_checks": tally["original_full_commitment_checks"],
                      "full_K08_hits": tally["full_K08_matches"],
                      "synthetic_controls": tally["synthetic_whole_cipher_controls"],
                      "protected_pdf_read": False}, sort_keys=True))


if __name__ == "__main__":
    main()
