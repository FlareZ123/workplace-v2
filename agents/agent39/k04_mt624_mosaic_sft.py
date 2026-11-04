"""Falsify a contiguous MT19937 stream across four H-17 source groups.

Original selected K04 payload is withheld. Run from repository root:
    python agents/agent39/k04_mt624_mosaic_sft.py
For the identical attached ZIP, set H17_SOURCE_ROOT to its extraction root.
"""
import hashlib
import itertools
import os
import random
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_SOURCE_ROOT", "resources"))
EVIDENCE = ROOT / "evidence"
MASK32 = 0xFFFFFFFF


def untemper(y):
    def undo_right(value, shift):
        original = value
        for _ in range(5):
            value = original ^ (value >> shift)
        return value

    def undo_left(value, shift, mask):
        original = value
        for _ in range(5):
            value = original ^ ((value << shift) & mask)
        return value

    y = undo_right(y, 18)
    y = undo_left(y, 15, 0xEFC60000)
    y = undo_left(y, 7, 0x9D2C5680)
    y = undo_right(y, 11)
    return y & MASK32


def twist_next(a, b, c):
    y = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (c ^ (y >> 1) ^ (0x9908B0DF if y & 1 else 0)) & MASK32


def original_groups():
    spool = (EVIDENCE / "print/spool-reconstruction.log").read_bytes()
    recorder_data = (EVIDENCE / "recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == (
        "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    )
    assert len(recorder_data) == 16 + 88 * 24
    printer = []
    selected = 0
    for line in spool.decode().splitlines():
        if "PAYLOAD=" not in line:
            continue
        payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        if (
            "2026-10-03T18:02:00Z" in line
            and "JOB=PS-261003-0417" in line
            and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line
        ):
            printer.append([None] * 4)
            selected += 1
        else:
            printer.append([payload[i:i + 4] for i in range(0, 16, 4)])
    assert selected == 1 and len(printer) == 133
    recorder = [
        [recorder_data[16 + i * 24 + 12:16 + i * 24 + 16]] for i in range(88)
    ]
    # The previously PASSed source-derived ink and revision-C page strips.
    ink = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
    proc = bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A")
    return {
        "P": printer,
        "R": recorder,
        "I": [[ink[i:i + 4]] for i in range(0, 16, 4)],
        "C": [[proc[i:i + 4]] for i in range(0, 16, 4)],
    }


def transformed(rows, endian, reverse_rows, reverse_within_row):
    use = rows[::-1] if reverse_rows else rows
    result = []
    for row in use:
        rr = row[::-1] if reverse_within_row else row
        for word in rr:
            result.append(
                None if word is None else untemper(
                    int.from_bytes(word, "little" if endian else "big")
                )
            )
    return result


def recurrence_checks(words):
    checks = []
    for i in range(4):
        a, b, c, d = words[i], words[i + 1], words[i + 397], words[i + 624]
        if None not in (a, b, c, d):
            checks.append(twist_next(a, b, c) == d)
    assert len(checks) == 4, "The selected target affects a source-only check"
    return checks


def synthetic_positive():
    rng = random.Random(6200417)
    output = [rng.getrandbits(32) for _ in range(628)]
    native = [untemper(x) for x in output]
    assert [twist_next(native[i], native[i+1], native[i+397])
            == native[i+624] for i in range(4)] == [True] * 4
    # Deliberately remove the four selected printer words, with a
    # four-word prefix before the printer group.
    native[4 + 129 * 4:4 + 129 * 4 + 4] = [None] * 4
    assert recurrence_checks(native) == [True] * 4
    print("Synthetic seeded MT19937 + selected coupon withheld: PASS")


def main():
    synthetic_positive()
    groups = original_groups()
    assert {name: sum(len(row) for row in rows) for name, rows in groups.items()} == {
        "P": 532, "R": 88, "I": 4, "C": 4
    }
    variations = {}
    for name, rows in groups.items():
        variations[name] = []
        for e, r, w in itertools.product(range(2), repeat=3):
            if name != "P" and w:
                continue
            variations[name].append(((e, r, w), transformed(rows, e, r, w)))
    hist = {i: 0 for i in range(5)}
    for group_order in itertools.permutations("PRIC"):
        for variants in itertools.product(*(variations[name] for name in group_order)):
            words = [word for _, arr in variants for word in arr]
            assert len(words) == 628 and words.count(None) == 4
            hist[sum(recurrence_checks(words))] += 1
    assert sum(hist.values()) == 12288
    print("Original fully tested layouts:", sum(hist.values()))
    print("Equal 32-bit MT recurrence words (among four per layout):", hist)
    assert hist == {0: 12288, 1: 0, 2: 0, 3: 0, 4: 0}


if __name__ == "__main__":
    main()
