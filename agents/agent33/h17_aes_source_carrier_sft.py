"""Source-wide AES full-object carrier probe for the historical H17 archive.

Requires cryptography. Run with the untouched h17-archive-dump.zip as sole
argument. Makes no writes to evidence or acceptance. The source does not
attest AES; this is an exploratory candidate-construction model.
"""
from collections import Counter
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
import zipfile

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEY_HEX = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "nonce": "5F933DA6A1BD03C32DA5CBC25344F497",
    "mask": "8556C8CB6140A7F9A5123AC7571BEE1C",
}
KEYS = {name: bytes.fromhex(value) for name, value in KEY_HEX.items()}
NONCE, MASK = KEYS["nonce"], KEYS["mask"]
K04 = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
K08 = bytes.fromhex("285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747")


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def plausible_text(block: bytes) -> bytes | None:
    valid = lambda v: bool(v) and all(32 <= x <= 126 for x in v)
    if valid(block):
        return block.strip()
    last = block[-1]
    if 1 <= last <= 15 and block.endswith(bytes([last]) * last) and valid(block[:-last]):
        return block[:-last]
    trimmed = block.rstrip(b"\x00")
    if len(trimmed) >= 5 and len(trimmed) < len(block) and valid(trimmed):
        return trimmed
    return None


def k08_hash(text: bytes) -> bytes:
    normalized = " ".join(re.sub(r"[^a-z0-9\s]", " ", text.decode("ascii").lower()).split())
    return hashlib.sha256(hmac.digest(NONCE, normalized.encode(), "sha256")[:16]).digest()


def main(archive: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        notes = z.read("evidence/crew/noticeboard-and-desk-notes.txt")
        spool = z.read("evidence/print/spool-reconstruction.log")
        assert hashlib.sha256(notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
        assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
        commitments = json.loads(z.read("acceptance.json"))["slot_sha256"]
        assert bytes.fromhex(commitments["K04"]) == K04
        assert bytes.fromhex(commitments["K08"]) == K08
        for name in ("K01", "K02", "K03", "K05", "K06", "K07"):
            assert hashlib.sha256(KEYS[name]).hexdigest() == commitments[name]
        sources = []
        for name in z.namelist():
            if not name.startswith("evidence/") or name.endswith("/"):
                continue
            raw = z.read(name)
            sources.append((name, raw))
            for match in re.finditer(rb"[0-9a-fA-F]{64,}", raw):
                s = match.group()
                sources.append((name + ":hex", bytes.fromhex(s[:len(s) // 2 * 2].decode())))

    assert hmac.digest(NONCE, b"a good watch leaves the room ready for the next pair of hands",
                       "sha256")[:16].hex() == "bf889359b0303f2b2b2fd96ae841210b"
    counts = Counter()
    hits = []
    for key_name, key in KEYS.items():
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        decrypt, encrypt = cipher.decryptor(), cipher.encryptor()
        for source_name, raw in sources:
            for offset in range(len(raw) - 15):
                block = raw[offset:offset + 16]
                d, e = decrypt.update(block), encrypt.update(block)
                candidates = [("ECB-decrypt", d), ("ECB-encrypt", e)]
                counts["ECB-decrypt"] += 1
                counts["ECB-encrypt"] += 1
                ivs = [("zero-IV", bytes(16)), ("nonce-IV", NONCE), ("mask-IV", MASK)]
                if offset >= 16:
                    ivs.append(("preceding-IV", raw[offset - 16:offset]))
                for iv_name, iv in ivs:
                    candidates.append(("CBC-" + iv_name, xor(d, iv)))
                    counts["CBC-decrypt"] += 1
                for mode, plain in candidates:
                    for component in (plain, xor(plain, MASK)):
                        counts["K04-hashes"] += 1
                        if hashlib.sha256(component).digest() == K04:
                            hits.append(("K04", source_name, offset, key_name, mode, component.hex()))
                    text = plausible_text(plain)
                    if text is not None:
                        counts["K08-phrases"] += 1
                        if k08_hash(text) == K08:
                            hits.append(("K08", source_name, offset, key_name, mode, text.decode()))
        decrypt.finalize()
        encrypt.finalize()

    # Exact block decryption and 3-block CBC synthetic checks, never H17 claims.
    planted_coupon = b"0123456789ABCDEF"
    key = KEYS["K01"]
    ecb = Cipher(algorithms.AES(key), modes.ECB())
    assert ecb.decryptor().update(ecb.encryptor().update(planted_coupon)) == planted_coupon
    planted_phrase = b"the sea is outside and voices fill the room".ljust(48, b" ")
    cbc = Cipher(algorithms.AES(key), modes.CBC(NONCE))
    assert cbc.decryptor().update(cbc.encryptor().update(planted_phrase)) == planted_phrase
    assert k08_hash(planted_phrase) == k08_hash(cbc.decryptor().update(cbc.encryptor().update(planted_phrase)))
    assert len(sources) == 51 and sum(len(raw) for _, raw in sources) == 112756
    assert counts == {"ECB-decrypt": 895928, "ECB-encrypt": 895928,
                      "CBC-decrypt": 3577184, "K04-hashes": 10738080}
    assert hits == [], hits
    print("ORIGINAL_K04_K08_NO_MATCH:", dict(counts))
    print("HISTORICAL_N02_AND_SYNTHETIC_AES_CONTROLS_PASS")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
