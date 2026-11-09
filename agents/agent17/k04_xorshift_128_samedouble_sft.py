"""Whole-block 128-bit xorshift same-job retry inversion gate.

Source-pinned original two-step REQUESTED1 -> missing ACK2 -> REQUESTED3
PS-261003-0417 event bracket; excludes disputed selected ACK2 copy.
Python standard library only; run from repo root.
"""
from pathlib import Path
import hashlib
import itertools
import re
import time

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
FULL = (1 << 128) - 1


def xs(x, pattern, a, b, c):
    for side, shift in zip(pattern, (a, b, c)):
        x ^= (x << shift) & FULL if side else x >> shift
    return x


def source_bracket():
    original = SPOOL.read_bytes()
    assert hashlib.sha256(original).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    stages = {}
    for line in original.decode("ascii").splitlines():
        if "JOB=PS-261003-0417" not in line:
            continue
        head = re.search(r"ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)", line)
        if head is None or head.group(3) != "RECOVER":
            continue
        attempt = int(head.group(1))
        if attempt == 2:
            stages[2] = (head.group(2), None)  # selected bytes never parsed
            continue
        payload = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert payload is not None
        stages[attempt] = (head.group(2), bytes.fromhex(payload.group(1)))
    assert sorted(stages) == [1, 2, 3]
    assert stages[1][0] == stages[3][0] == "REQUESTED"
    assert stages[2] == ("ACK", None)
    return stages[1][1], stages[3][1]


def view(value, layout):
    if layout & 1:
        value = value[::-1]
    if layout & 2:
        value = b"".join(value[i:i + 4][::-1] for i in range(0, 16, 4))
    if layout & 4:
        value = b"".join(value[i:i + 4] for i in (12, 8, 4, 0))
    return value


def main():
    first, third = source_bracket()
    started = time.perf_counter()
    n, holdouts, hits = 0, 0, []
    for layout in range(8):
        first_native = int.from_bytes(view(first, layout), "little")
        third_native = int.from_bytes(view(third, layout), "little")
        for pattern in itertools.product((0, 1), repeat=3):
            for shifts in itertools.product(range(1, 64), repeat=3):
                middle = xs(first_native, pattern, *shifts)
                survives = xs(middle, pattern, *shifts) == third_native
                holdouts += survives
                if survives:
                    # One complete source-verified middle would immediately
                    # provide a whole 16-byte coupon, then a real K04 hash test.
                    coupon = view(middle.to_bytes(16, "little"), layout)
                    k04 = bytes(x ^ y for x, y in zip(coupon, MASK))
                    if hashlib.sha256(k04).hexdigest() == TARGET:
                        hits.append((layout, pattern, shifts))
                n += 1
    assert n == 8 * 8 * 63**3
    assert holdouts == 0 and not hits
    seed = 0x37429A0871FAB1983ECC492F0788B32D
    for layout in range(8):
        for pattern in itertools.product((0, 1), repeat=3):
            shifts = (11, 19, 8)
            planted = xs(seed, pattern, *shifts)
            last = xs(planted, pattern, *shifts)
            assert xs(xs(seed, pattern, *shifts), pattern, *shifts) == last
            assert view(view(planted.to_bytes(16, "little"), layout), layout) == planted.to_bytes(16, "little")
    print("Original source two-step models:", n)
    print("Original whole third-packet predictions:", holdouts)
    print("Original source-qualified K04 hash hits:", len(hits))
    print("Genuine planted 64 whole-state controls: PASS")
    print("Seconds:", round(time.perf_counter() - started, 2))


if __name__ == "__main__":
    main()
