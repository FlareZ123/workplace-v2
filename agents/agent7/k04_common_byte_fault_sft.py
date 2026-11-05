"""H-17 K04: complete source-pinned correlated byte-fault corrections.

Test all nonempty damaged-position subsets for an unknown *shared* XOR
byte, modular-add byte, or byte-rotation fault in the retained copied ACK2.
Reduction with the untouched route mask takes place after each repair.
Requires only the Python standard library and original repository resources.
"""

import hashlib
import json
import re
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA256 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
SELECTED_COPY = "A9A9DC5731A5E2AE879C47215C2559D5"


def trial(base: bytes, mask: bytes, target: bytes, transforms):
    """Return number of SHA256 checks and first complete matching fault."""
    attempts = 0
    for label, f in transforms:
        candidate = bytearray(a ^ b for a, b in zip(base, mask))
        # Gray-code traversal flips one position at a time.
        for step in range(1, 1 << 16):
            pos = (step & -step).bit_length() - 1
            bitset = step ^ (step >> 1)
            candidate[pos] = (f(base[pos]) if bitset & (1 << pos) else base[pos]) ^ mask[pos]
            attempts += 1
            if hashlib.sha256(candidate).digest() == target:
                return attempts, (label, bitset, candidate)
    return attempts, None


def rotate_left(x: int, count: int) -> int:
    return ((x << count) | (x >> (8 - count))) & 0xFF


def transforms():
    for value in range(1, 256):
        yield ("xor", value), lambda x, n=value: x ^ n
    for value in range(1, 256):
        yield ("add", value), lambda x, n=value: (x + n) & 0xFF
    for value in range(1, 8):
        yield ("rol", value), lambda x, n=value: rotate_left(x, n)


def main():
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA256
    matches = [line for line in spool.decode("utf-8").splitlines()
               if "JOB=PS-261003-0417" in line
               and "ATTEMPT=2" in line and "STATE=ACK" in line
               and "CLASS=RECOVER" in line]
    assert len(matches) == 1
    copied = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", matches[0]).group(1))
    assert copied.hex().upper() == SELECTED_COPY
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA256
    target = bytes.fromhex(K04_SHA256)
    assert len(copied) == len(mask) == 16

    started = perf_counter()
    original_count, original_hit = trial(copied, mask, target, transforms())
    expected = (255 + 255 + 7) * ((1 << 16) - 1)
    assert original_count == expected or original_hit is not None
    print(f"Original source: pinned SHA, selected row, mask, commitment PASS")
    print(f"Original full K04 candidates: {original_count:,}")
    print(f"Original K04 match: {original_hit}")

    # Three independent positives, ten damaged copied-payload positions each.
    # A synthetic physical coupon is corrupted before the mask is applied.
    actual = bytes.fromhex("73893BD77A50E4B261EF09C5AC8D4F23")
    indices = (0, 1, 3, 4, 5, 8, 10, 12, 14, 15)
    desired_bits = sum(1 << i for i in indices)
    digest = hashlib.sha256(bytes(x ^ y for x, y in zip(actual, mask))).digest()
    for label, forward, inverse in (
        ("xor", lambda x: x ^ 0xA9, lambda x: x ^ 0xA9),
        ("add", lambda x: (x - 0x39) & 255, lambda x: (x + 0x39) & 255),
        ("rol", lambda x: rotate_left(x, 3), lambda x: rotate_left(x, 5)),
    ):
        damaged = bytearray(actual)
        for i in indices:
            damaged[i] = forward(actual[i])
        positive_count, hit = trial(bytes(damaged), mask, digest, [((label, "planted"), inverse)])
        assert hit is not None and hit[1] == desired_bits
        assert hit[2] == bytes(x ^ y for x, y in zip(actual, mask))
        print(f"Synthetic 10-byte {label} repair: PASS, checks={positive_count}")
    print(f"Elapsed seconds: {perf_counter() - started:.3f}")
    print("Scope: one uniform fault operation and parameter across arbitrary copied-byte subset")


if __name__ == "__main__":
    main()
