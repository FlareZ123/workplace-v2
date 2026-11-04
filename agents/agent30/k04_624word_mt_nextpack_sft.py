"""Exact 624 preserved H-17 source words as hypothetical MT19937 state.

A full original K04 commitment experiment from the next four MT outputs.
The selected copied printer coupon is excluded entirely from the 624 inputs.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
SHA_SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SHA_REC = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
U32 = 0xFFFFFFFF


def untemper(y: int) -> int:
    original = y
    for _ in range(5):
        y = original ^ (y >> 18)
    original = y
    for _ in range(5):
        y = original ^ ((y << 15) & 0xEFC60000)
    original = y
    for _ in range(5):
        y = original ^ ((y << 7) & 0x9D2C5680)
    original = y
    for _ in range(5):
        y = original ^ (y >> 11)
    return y & U32


def temper(y: int) -> int:
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & U32


def twist(a: int, b: int, c: int) -> int:
    value = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (c ^ (value >> 1) ^ (0x9908B0DF if value & 1 else 0)) & U32


def next4(native: list[int]) -> tuple[int, int, int, int]:
    assert len(native) == 624
    return tuple(temper(twist(native[i], native[i + 1], native[i + 397])) for i in range(4))


def source_groups() -> dict[str, list[list[bytes]]]:
    spool = (ROOT / "print/spool-reconstruction.log").read_bytes()
    rec = (ROOT / "recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SHA_SPOOL
    assert hashlib.sha256(rec).hexdigest() == SHA_REC
    assert len(rec) == 16 + 88 * 24
    printer = []
    selected = 0
    for line in spool.decode().splitlines():
        if "PAYLOAD=" not in line:
            continue
        if ("2026-10-03T18:02:00Z" in line
            and "JOB=PS-261003-0417" in line
            and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line):
            printer.append([])
            selected += 1
            continue
        raw = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
        printer.append([raw[i:i + 4] for i in range(0, 16, 4)])
    assert selected == 1 and len(printer) == 133
    recorder = [[rec[16 + i * 24 + 12:16 + i * 24 + 16]] for i in range(88)]
    ink = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
    proc = bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A")
    groups = {
        "P": printer,
        "R": recorder,
        "I": [[ink[i:i + 4]] for i in range(0, 16, 4)],
        "C": [[proc[i:i + 4]] for i in range(0, 16, 4)],
    }
    assert {name: sum(len(r) for r in rows) for name, rows in groups.items()} == {
        "P": 528, "R": 88, "I": 4, "C": 4
    }
    return groups


def state_words(rows: list[list[bytes]], endian: int, reverse_rows: int, reverse_words: int) -> list[int]:
    use = rows[::-1] if reverse_rows else rows
    chunks = (w for row in use for w in (row[::-1] if reverse_words else row))
    return [untemper(int.from_bytes(w, "little" if endian else "big")) for w in chunks]


def positive() -> None:
    rng = random.Random(6200417)
    observed = [rng.getrandbits(32) for _ in range(624)]
    actual = tuple(rng.getrandbits(32) for _ in range(4))
    assert next4([untemper(x) for x in observed]) == actual
    coupon = b"".join(w.to_bytes(4, "little") for w in actual)
    planted_target = hashlib.sha256(bytes(a ^ b for a, b in zip(coupon, MASK))).digest()
    assert planted_target != TARGET
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(
        b"".join(w.to_bytes(4, "little") for w in next4([untemper(x) for x in observed])), MASK
    ))).digest() == planted_target
    print("SYNTHETIC_MT624_TO_FULL_K04 PASS", flush=True)


def main() -> None:
    positive()
    groups = source_groups()
    variants = {}
    for name, rows in groups.items():
        variants[name] = []
        for endian, backwards, within in itertools.product(range(2), repeat=3):
            if name != "P" and within:
                continue
            variants[name].append(
                ((endian, backwards, within), state_words(rows, endian, backwards, within))
            )
    models = checks = 0
    hits = []
    predicted_quartets = set()
    for order in itertools.permutations("PRIC"):
        for config in itertools.product(*(variants[name] for name in order)):
            native = [word for _, group in config for word in group]
            assert len(native) == 624
            prediction = next4(native)
            predicted_quartets.add(prediction)
            models += 1
            for permutation in itertools.permutations(range(4)):
                for switches in range(16):
                    coupon = b"".join(
                        prediction[permutation[j]].to_bytes(
                            4, "big" if switches & (1 << j) else "little"
                        ) for j in range(4)
                    )
                    component = bytes(a ^ b for a, b in zip(coupon, MASK))
                    checks += 1
                    if hashlib.sha256(component).digest() == TARGET:
                        hits.append((order, permutation, switches, component.hex().upper()))
    assert (models, checks) == (12288, 4718592)
    print("ORIGINAL", {
        "hypotheses": models,
        "distinct_prediction_quartets": len(predicted_quartets),
        "full_K04_checks": checks,
        "original_matches": hits,
    }, flush=True)
    assert not hits


if __name__ == "__main__":
    main()
