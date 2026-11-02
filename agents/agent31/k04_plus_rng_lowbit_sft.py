"""H17 source-only PLUS-family PRNG low-bit test. Python 3 standard library.

Run: python agents/agent31/k04_plus_rng_lowbit_sft.py
Or: python agents/agent31/k04_plus_rng_lowbit_sft.py path/to/original.zip
Use --quick for a small smoke test, otherwise execute full source-only schedule search.
Selected ACK attempt2, route mask, acceptance commitments and verifier are never used.
"""
from __future__ import annotations

from itertools import product
from pathlib import Path
import hashlib
import re
import sys
import time
import zipfile

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CONFIGS = [("xoshiro128+", None, 32, 4),
           ("xoroshiro128+ 2016", (55, 14, 36), 64, 2),
           ("xoroshiro128+ 1.0", (24, 16, 37), 64, 2)]


def read_original(archive: str | None):
    if archive:
        with zipfile.ZipFile(archive) as z:
            data = z.read("evidence/print/spool-reconstruction.log")
    else:
        base = Path(__file__).resolve().parents[2]
        data = (base / "resources" / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA256
    lines = [line for line in data.decode("utf-8").splitlines() if "PAYLOAD=" in line]
    assert len(lines) == 133
    records = []
    for line in lines[:128]:
        fields = dict(part.split("=", 1) for part in line.split() if "=" in part)
        assert re.fullmatch("[0-9A-F]{32}", fields["PAYLOAD"])
        records.append(fields)
    return records


def rol(masks: list[int], shift: int):
    return masks[-shift:] + masks[:-shift]


def symbolic_seed(width: int, nwords: int):
    return tuple([[1 << (k * width + i) for i in range(width)] for k in range(nwords)])


def symbolic_step(state, name: str, rot):
    if name == "xoshiro128+":
        a, b, c, d = state
        output = a[0] ^ d[0]
        t = [0] * 9 + b[:23]
        c = [u ^ v for u, v in zip(c, a)]
        d = [u ^ v for u, v in zip(d, b)]
        b = [u ^ v for u, v in zip(b, c)]
        a = [u ^ v for u, v in zip(a, d)]
        c = [u ^ v for u, v in zip(c, t)]
        return output, (a, b, c, rol(d, 11))
    a, b = state
    output = a[0] ^ b[0]
    r0, left, r1 = rot
    temp = [u ^ v for u, v in zip(a, b)]
    a2 = [u ^ v ^ w for u, v, w in zip(rol(a, r0), temp, [0] * left + temp[:64-left])]
    return output, (a2, rol(temp, r1))


def concrete_step(state, name, rot):
    if name == "xoshiro128+":
        mask = (1 << 32) - 1
        a, b, c, d = state
        output = (a + d) & mask
        t = (b << 9) & mask
        c ^= a
        d ^= b
        b ^= c
        a ^= d
        c ^= t
        d = ((d << 11) | (d >> 21)) & mask
        return output, (a, b, c, d)
    mask = (1 << 64) - 1
    a, b = state
    output = (a + b) & mask
    t = a ^ b
    r0, left, r1 = rot
    a = (((a << r0) | (a >> (64-r0))) ^ t ^ (t << left)) & mask
    b = ((t << r1) | (t >> (64-r1))) & mask
    return output, (a, b)


def decode(payload, endianness, reverse, width):
    raw = bytes.fromhex(payload)
    width_bytes = width // 8
    words = [int.from_bytes(raw[i:i+width_bytes], endianness)
             for i in range(0, 16, width_bytes)]
    return words[::-1] if reverse else words


def insert_equation(mask, bit, pivots):
    while mask:
        pivot = mask.bit_length() - 1
        if pivot not in pivots:
            pivots[pivot] = (mask, bit)
            return True
        row, rhs = pivots[pivot]
        mask ^= row
        bit ^= rhs
    return bit == 0


def run_fit(records, schedule, name, rot, width, nwords, endianness, reverse):
    state = symbolic_seed(width, nwords)
    pivots = {}
    for rowno, (record, extra) in enumerate(zip(records, schedule)):
        for word in decode(record["PAYLOAD"], endianness, reverse, width):
            expression, state = symbolic_step(state, name, rot)
            if not insert_equation(expression, word & 1, pivots):
                return False, len(pivots), rowno
        for _ in range(extra):
            _, state = symbolic_step(state, name, rot)
    return True, len(pivots), len(records)


def labels_to_gaps(records, coefficients, next_label):
    base, stores, recover, desk, store = coefficients
    cc = {"LABEL": 0, "STORES": stores, "RECOVER": recover}
    dd = {"bench": 0, "desk": desk, "store": store}
    return [base
            + cc[(records[min(i+1, len(records)-1)] if next_label else row)["CLASS"]]
            + dd[(records[min(i+1, len(records)-1)] if next_label else row)["DEST"]]
            for i, row in enumerate(records)]


def synthetic_control(original, name, rot, width, nwords):
    state = (0x12345ABF, 0x88776655, 0x1F2B3C4D, 0xDD6EEAB7) if width == 32 else (
        0x12345ABF88776655, 0x1F2B3C4DDD6EEAB7)
    schedule = labels_to_gaps(original, (1, 2, 0, 1, 2), False)
    fixture = []
    for row, extra in zip(original, schedule):
        output = []
        for _ in range(nwords):
            word, state = concrete_step(state, name, rot)
            output.append(word)
        for _ in range(extra):
            _, state = concrete_step(state, name, rot)
        fixture.append({
            "PAYLOAD": b"".join(word.to_bytes(width//8, "little")
                                for word in output).hex().upper(),
            "CLASS": row["CLASS"], "DEST": row["DEST"]})
    success, rank, _ = run_fit(fixture, schedule, name, rot, width, nwords, "little", False)
    assert success and rank == 128, (name, success, rank)
    wrong, _, _ = run_fit(fixture, [0]*len(fixture), name, rot, width, nwords,
                          "little", False)
    assert not wrong, "Incorrect schedule unexpectedly fitted"
    return rank


def main(archive, quick=False):
    original = read_original(archive)
    print("PINNED SPOOL SHA256", SOURCE_SHA256,
          "ordinary source rows", len(original), "selected ACK2 excluded")
    started = time.monotonic()
    total = 0
    max_coeff = 2 if quick else 3
    for name, rot, width, nwords in CONFIGS:
        rank = synthetic_control(original, name, rot, width, nwords)
        print("SYNTHETIC POSITIVE", name, "rank", rank, "PASS", flush=True)
        for endianness, reverse in product(("little", "big"), (False, True)):
            for skip in range(65):
                valid, _, _ = run_fit(original, [skip]*len(original), name, rot,
                                      width, nwords, endianness, reverse)
                assert not valid, ("Fixed-gap original match", name, endianness,
                                  reverse, skip)
                total += 1
            for next_label in (False, True):
                farthest = 0
                for coeff in product(range(max_coeff), repeat=5):
                    valid, _, last = run_fit(
                        original, labels_to_gaps(original, coeff, next_label),
                        name, rot, width, nwords, endianness, reverse)
                    assert not valid, ("Metadata original match", name,
                                      endianness, reverse, next_label, coeff)
                    farthest = max(farthest, last)
                    total += 1
                print("ORIGINAL", name, endianness,
                      "reversed" if reverse else "forward",
                      "next-label" if next_label else "current-label",
                      f"{max_coeff**5}/{max_coeff**5} impossible",
                      "latest contradiction row", farthest, flush=True)
        print("ORIGINAL", name, "fixed gap 0..64 in four serializations: no fit",
              flush=True)
    print("NO SOURCE GENERATOR SURVIVED", total,
          "schedule/serializer/variant attempts; elapsed",
          round(time.monotonic()-started, 2), "s")
    print("New authentic K04 bits 0/128; K08 exact final words 0; REC8 incomplete")


if __name__ == "__main__":
    main(next((arg for arg in sys.argv[1:] if arg != "--quick"), None),
         quick="--quick" in sys.argv[1:])
