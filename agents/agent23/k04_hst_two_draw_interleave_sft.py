"""Source-pinned K04 MT19937 two-word historian PV interleave pilot.

Ordinary spool jobs 0300..0427 each expose four consecutive native words.
Historian PV seq100..211 conjecturally consumes two consecutive hidden words
in one of five locations of jobs 0300..0411. This explicitly rejects any
stronger unobserved per-job draw chronology as outside the tested model.
Run from repository root: python agents/agent23/k04_hst_two_draw_interleave_sft.py
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources/evidence"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
PV_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
MASK = 0xFFFFFFFF


def unt_right(y, shift):
    x = y
    for _ in range(5):
        x = y ^ (x >> shift)
    return x & MASK


def unt_left(y, shift, mask):
    x = y
    for _ in range(7):
        x = y ^ ((x << shift) & mask)
    return x & MASK


def untemper(y):
    y = unt_right(y, 18)
    y = unt_left(y, 15, 0xEFC60000)
    y = unt_left(y, 7, 0x9D2C5680)
    return unt_right(y, 11)


def recurrence(values):
    pass_count = 0
    fail_count = 0
    for i in range(len(values) - 624):
        quartet = [values[j] for j in (i, i + 1, i + 397, i + 624)]
        if any(x is None for x in quartet):
            continue
        a, b, c, d = quartet
        combination = (a & 0x80000000) | (b & 0x7FFFFFFF)
        predicted = c ^ (combination >> 1)
        if combination & 1:
            predicted ^= 0x9908B0DF
        if predicted == d:
            pass_count += 1
        else:
            fail_count += 1
    return pass_count, fail_count


def insert_pv(words, offset):
    output = []
    for i, row in enumerate(words):
        if i < 112:
            output += row[:offset] + [None, None] + row[offset:]
        else:
            output += row
    assert len(output) == 736
    return output


def source():
    source_bytes = (ROOT / "print/spool-reconstruction.log").read_bytes()
    pv_bytes = (ROOT / "telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == SPOOL_SHA
    assert hashlib.sha256(pv_bytes).hexdigest() == PV_SHA
    printer = []
    for line in source_bytes.decode("ascii").splitlines():
        if line.startswith("2026-"):
            _, *tokens = line.split()
            printer.append(dict(token.split("=", 1) for token in tokens))
    assert len(printer) == 133
    for i, row in enumerate(printer[:128]):
        assert row["JOB"] == f"PS-261003-{i+300:04d}"
    telemetry = [json.loads(line) for line in pv_bytes.decode().splitlines()]
    pv = {entry["seq"]: entry["value"] for entry in telemetry if entry["field"] == "PV"}
    assert len(pv) == 112 and sorted(pv) == list(range(100, 212))
    return printer[:128]


def synthetic():
    seeded = random.Random(202611180517)
    samples = [seeded.getrandbits(32) for _ in range(736)]
    for offset in range(5):
        observed = []
        index = 0
        for i in range(128):
            size = 6 if i < 112 else 4
            data = samples[index:index + size]
            if i < 112:
                observed.append(data[:offset] + data[offset + 2:])
            else:
                observed.append(data)
            index += size
        assert index == 736
        recovered = insert_pv(observed, offset)
        good, bad = recurrence([None if w is None else untemper(w) for w in recovered])
        assert good >= 55 and bad == 0, (offset, good, bad)
    print("SYNTHETIC_MT_TWO_DRAW_CONTROLS_PASS", flush=True)


def original():
    rows = source()
    totals = []
    for endian in ("big", "little"):
        for reverse in (False, True):
            packets = []
            for row in rows:
                payload = bytes.fromhex(row["PAYLOAD"])
                words = [int.from_bytes(payload[i:i + 4], endian) for i in range(0, 16, 4)]
                packets.append([untemper(w) for w in (words[::-1] if reverse else words)])
            for offset in range(5):
                good, bad = recurrence(insert_pv(packets, offset))
                totals.append((endian, reverse, offset, good, bad))
                print(json.dumps({"endian": endian, "reverse_words": reverse,
                                  "pv_insertion": offset, "matches": good,
                                  "violations": bad}), flush=True)
                assert good + bad >= 55
    assert len(totals) == 20
    assert all(good == 0 and bad >= 55 for _, _, _, good, bad in totals)
    print("SOURCE_TWO_DRAW_INTERLEAVING_20_LAYOUTS_REJECTED", flush=True)


if __name__ == "__main__":
    synthetic()
    original()
