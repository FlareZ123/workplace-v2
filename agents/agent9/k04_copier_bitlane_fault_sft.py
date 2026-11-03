"""K04 read-only selected-ACK fault-family tester, original source pinned.

Tests independently applied one-byte bitlane/nibble faults and permutations
within each 32-bit copied word. Uses the original K04 route XOR and SHA-256.
Synthetic complete-hash positives validate searching, independently of source.
"""
from pathlib import Path
import hashlib
import itertools
import json
import re

root = Path(__file__).resolve().parents[2] / "resources"
spool = root / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(spool.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected = [
    s for s in spool.read_text().splitlines()
    if "JOB=PS-261003-0417" in s and "ATTEMPT=2" in s
    and "STATE=ACK" in s and "CLASS=RECOVER" in s
]
assert len(selected) == 1
payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1))
route = json.loads((root / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = json.loads((root / "acceptance.json").read_text())["slot_sha256"]["K04"]

def digest(data: bytes) -> str:
    return hashlib.sha256(bytes(a ^ b for a, b in zip(data, mask))).hexdigest()

def family_functions():
    return {
        "byte_nibble_exchange": lambda v: ((v & 15) << 4) | (v >> 4),
        "byte_full_bit_reverse": lambda v: int(f"{v:08b}"[::-1], 2),
        "byte_bit_complement": lambda v: v ^ 255,
        "byte_high_nibble_complement": lambda v: v ^ 240,
        "byte_low_nibble_complement": lambda v: v ^ 15,
        "byte_bit_rotate_left_1": lambda v: ((v << 1) | (v >> 7)) & 255,
        "byte_bit_rotate_right_1": lambda v: ((v >> 1) | (v << 7)) & 255,
    }

def enumerate_byte_masks(data: bytes, transform, commitment: str):
    hits = []
    effects = [b ^ transform(b) for b in data]
    for bitmask in range(65536):
        restored = bytes(b ^ (effects[i] if bitmask >> i & 1 else 0) for i, b in enumerate(data))
        if digest(restored) == commitment:
            hits.append((bitmask, restored.hex().upper()))
    return hits

def enumerate_words(data: bytes, commitment: str):
    perms = list(itertools.permutations(range(4)))
    hits = []
    for indexes in itertools.product(range(24), repeat=4):
        restored = b"".join(
            bytes(data[j * 4 + perms[k][i]] for i in range(4))
            for j, k in enumerate(indexes)
        )
        if digest(restored) == commitment:
            hits.append((indexes, restored.hex().upper()))
    return hits

def positives():
    planted = digest(payload)
    cases = (
        ("nibble", lambda b: ((b & 15) << 4) | (b >> 4), 0xA35D),
        ("bit_reverse", lambda b: int(f"{b:08b}"[::-1], 2), 0xB397),
        ("bit7", lambda b: b ^ 128, 0x9713),
    )
    for name, transform, bitmask in cases:
        corrupted = bytes(
            b ^ ((b ^ transform(b)) if bitmask >> i & 1 else 0)
            for i, b in enumerate(payload)
        )
        hits = enumerate_byte_masks(corrupted, transform, planted)
        assert bitmask in {value for value, _ in hits}
        print("synthetic SHA positive", name, "PASS", len(hits))
    perms = list(itertools.permutations(range(4)))
    indexes = (5, 12, 21, 9)
    corrupted = b"".join(
        bytes(payload[j * 4 + perms[k][i]] for i in range(4))
        for j, k in enumerate(indexes)
    )
    hits = enumerate_words(corrupted, planted)
    assert any(original == payload.hex().upper() for _, original in hits)
    print("synthetic SHA positive four-word permutation PASS", len(hits))

def main():
    assert digest(payload) != target
    print("source SHA pinned; selected event:", selected[0])
    positives()
    count = 0
    hits = []
    for name, transform in family_functions().items():
        found = enumerate_byte_masks(payload, transform, target)
        count += 65536
        hits.extend((name, v) for v in found)
    for bit in range(8):
        name = f"one_bitplane_{bit}_independent_per_byte"
        found = enumerate_byte_masks(payload, lambda b, bit=bit: b ^ (1 << bit), target)
        count += 65536
        hits.extend((name, v) for v in found)
    found = enumerate_words(payload, target)
    count += 24 ** 4
    hits.extend(("independent_four_byte_word_permutation", v) for v in found)
    assert count == 1314816
    print("complete candidates", count, "matching original K04 commitment", hits)

if __name__ == "__main__":
    main()
