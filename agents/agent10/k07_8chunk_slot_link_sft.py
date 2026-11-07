"""Read-only original-source AX-7782 chunk -> REC8 component link SFT.

Run from repo root: python agents/agent10/k07_8chunk_slot_link_sft.py
Only intact source slots 1, 5 and 6 are model-fitting controls.
"""
import binascii
import hashlib
import hmac
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
ACCEPTANCE_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
PREHASH = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
KNOWN = {
    1: bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    5: bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    6: bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
}
VARIANTS = (
    "repeat", "md5", "sha256-first", "sha256-last", "sha512-first",
    "blake2s", "hmac-nonce", "hmac-mask", "sha256-prefix", "sha256-suffix",
    "hmac-prefix", "hmac-suffix",
)
CRC = (
    ("ccitt0", 0x1021, 0, False, 0),
    ("ccittffff", 0x1021, 0xffff, False, 0),
    ("x25", 0x8408, 0xffff, True, 0xffff),
    ("kermit", 0x8408, 0, True, 0),
    ("ibm0", 0xa001, 0, True, 0),
    ("modbus", 0xa001, 0xffff, True, 0),
    ("dnp", 0xa6bc, 0, True, 0xffff),
)


def source_checkpoints():
    raw = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFER_SHA
    records = [json.loads(x) for x in raw.splitlines()]
    receipts = [r for r in records if r["kind"] == "COMMIT" and r["transfer"] == "AX-7782"]
    assert len(receipts) == 1 and receipts[0]["dry_run"] is False and receipts[0]["chunks"] == 8
    chosen = {}
    for r in records:
        if r["kind"] == "CHUNK" and r["transfer"] == "AX-7782":
            seq = r["seq"]
            if seq not in chosen or r["attempt"] > chosen[seq]["attempt"]:
                chosen[seq] = r
    assert sorted(chosen) == list(range(8))
    assert all(chosen[i]["attempt"] == 2 for i in range(8))
    out = tuple(bytes.fromhex(chosen[i]["checkpoint"]) for i in range(8))
    assert b"".join(out) == PREHASH
    return out


def expand(data, slot, variant):
    label = f"K{slot:02d}".encode()
    if variant == "repeat":
        return data * 8
    if variant == "md5":
        return hashlib.md5(data).digest()
    if variant == "sha256-first":
        return hashlib.sha256(data).digest()[:16]
    if variant == "sha256-last":
        return hashlib.sha256(data).digest()[16:]
    if variant == "sha512-first":
        return hashlib.sha512(data).digest()[:16]
    if variant == "blake2s":
        return hashlib.blake2s(data, digest_size=16).digest()
    if variant == "hmac-nonce":
        return hmac.digest(NONCE, data, "sha256")[:16]
    if variant == "hmac-mask":
        return hmac.digest(MASK, data, "sha256")[:16]
    if variant == "sha256-prefix":
        return hashlib.sha256(label + data).digest()[:16]
    if variant == "sha256-suffix":
        return hashlib.sha256(data + label).digest()[:16]
    if variant == "hmac-prefix":
        return hmac.digest(NONCE, label + data, "sha256")[:16]
    if variant == "hmac-suffix":
        return hmac.digest(NONCE, data + label, "sha256")[:16]
    raise ValueError(variant)


def crc16(data, poly, init, reflected):
    reg = init
    for byte in data:
        reg ^= byte if reflected else byte << 8
        for _ in range(8):
            if reflected:
                reg = ((reg >> 1) ^ (poly if reg & 1 else 0)) & 0xffff
            else:
                reg = ((reg << 1) ^ (poly if reg & 0x8000 else 0)) & 0xffff
    return reg


def pos(slot, phase, inverse):
    return ((1 - slot if inverse else slot - 1) + phase) % 8


def check_full(chain, expected):
    comparisons, hits = 0, []
    for variant in VARIANTS:
        for phase in range(8):
            for inverse in (False, True):
                for flip in (False, True):
                    for slot, known in expected.items():
                        raw = chain[pos(slot, phase, inverse)]
                        if flip:
                            raw = raw[::-1]
                        comparisons += 1
                        if expand(raw, slot, variant) == known:
                            hits.append((variant, phase, inverse, flip, slot))
    return comparisons, hits


def check_crc(chain, expected):
    comparisons, hits = 0, []
    for name, poly, init, reflected, xorout in CRC:
        for phase in range(8):
            for inverse in (False, True):
                for flip in (False, True):
                    for slot, known in expected.items():
                        raw = chain[pos(slot, phase, inverse)]
                        if flip:
                            raw = raw[::-1]
                        comparisons += 1
                        if (crc16(known, poly, init, reflected) ^ xorout).to_bytes(2, "big") == raw:
                            hits.append((name, phase, inverse, flip, slot))
    return comparisons, hits


def main():
    assert hashlib.sha256((ROOT / "acceptance.json").read_bytes()).hexdigest() == ACCEPTANCE_SHA
    original = source_checkpoints()
    full_n, full_hits = check_full(original, KNOWN)
    crc_n, crc_hits = check_crc(original, KNOWN)
    assert full_n == 1152 and not full_hits
    assert crc_n == 672 and not crc_hits
    assert crc16(b"123456789", 0x1021, 0xffff, False) == 0x29b1
    assert crc16(b"123456789", 0xa001, 0xffff, True) == 0x4b37

    # Plant source-selected whole target values independently via hashlib.
    fake = [bytes((i, 200 + i)) for i in range(8)]
    expected_full = {
        slot: hashlib.sha256(fake[pos(slot, 2, False)][::-1] + f"K{slot:02d}".encode()).digest()[:16]
        for slot in KNOWN
    }
    _, planted_full_hits = check_full(fake, expected_full)
    assert all(("sha256-suffix", 2, False, True, slot) in planted_full_hits for slot in KNOWN)

    # Plant an independently binascii-derived CRC chain.
    crc_fake = [bytes((i, 220 + i)) for i in range(8)]
    for slot, known in KNOWN.items():
        crc_fake[pos(slot, 3, True)] = binascii.crc_hqx(known, 0).to_bytes(2, "big")
    _, planted_crc_hits = check_crc(crc_fake, KNOWN)
    assert all(("ccitt0", 3, True, False, slot) in planted_crc_hits for slot in KNOWN)

    print(json.dumps({
        "source": "PASS", "original_selected": "AX-7782",
        "complete_16byte_predictions": full_n, "full_matches": len(full_hits),
        "crc16_fingerprint_predictions": crc_n, "crc_matches": len(crc_hits),
        "planted_complete_control": "PASS", "planted_crc_control": "PASS",
        "original_missing_components_recovered": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
