"""H17 K04 hypothetical A9A9-framed 16-bit all-tap additive LFSR copier.
Read-only, no external dependencies. Run: python agents/agent49/k04_a9a9_lfsr_alltaps_sft.py
The A9A9 seed/feedback model is speculative and not a printer-firmware claim.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED = b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench"
P = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
SEED = int.from_bytes(P[:2], "big")

def stream(poly: int, reverse: bool, lsb: bool, reverse_bytes: bool) -> bytes:
    state = SEED
    bits: list[int] = []
    for _ in range(128):
        bits.append((state >> (0 if lsb else 15)) & 1)
        feedback = (state & poly).bit_count() & 1
        state = ((state >> 1) | (feedback << 15)) if reverse else (((state << 1) & 65535) | feedback)
    data = bytes(sum(bits[8 * i + j] << (7 - j) for j in range(8)) for i in range(16))
    return data[::-1] if reverse_bytes else data

def test() -> None:
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    assert spool.count(SELECTED) == 1
    assert SEED == 0xA9A9
    plant = bytes(a ^ b ^ c for a, b, c in zip(P, MASK, stream(0x1021, False, False, False)))
    plant_sha = hashlib.sha256(plant).digest()
    assignments = hits = synthetic = 0
    distinct: set[bytes] = set()
    witness = False
    for reverse in (False, True):
        for lsb in (False, True):
            for reverse_bytes in (False, True):
                for poly in range(65536):
                    keystream = stream(poly, reverse, lsb, reverse_bytes)
                    coupon = bytes(a ^ b ^ c for a, b, c in zip(P, MASK, keystream))
                    digest = hashlib.sha256(coupon).digest()
                    distinct.add(coupon)
                    assignments += 1
                    if digest == TARGET:
                        hits += 1
                        print("ORIGINAL_K04_HIT", poly, reverse, lsb, reverse_bytes, coupon.hex().upper())
                    if digest == plant_sha:
                        synthetic += 1
                        witness |= poly == 0x1021 and not reverse and not lsb and not reverse_bytes
    assert (assignments, len(distinct), hits, synthetic, witness) == (524288, 349487, 0, 4, True)
    print("K04_A9A9_LFSR_ALLTAPS", "assignments", assignments, "unique_complete", len(distinct),
          "original_hits", hits, "planted_assignments", synthetic)

if __name__ == "__main__":
    test()
