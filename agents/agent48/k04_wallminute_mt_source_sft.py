"""H-17 K04: source-clock index MT19937 complete-packet holdout.
Read-only. Does not read selected 18:02 printer ACK2 or any commitment.
Run from repository checkout: python agents/agent48/k04_wallminute_mt_source_sft.py
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import random
import re
import struct

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROW = re.compile(r"^(\S+) JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$")
MASK = 0xFFFFFFFF


def untemper(value):
    value ^= value >> 18
    value ^= (value << 15) & 0xEFC60000
    fixed = value
    for _ in range(5):
        fixed = value ^ ((fixed << 7) & 0x9D2C5680)
    value = fixed
    for _ in range(3):
        fixed = value ^ (fixed >> 11)
    return fixed & MASK


def next_mt(x, y, z):
    w = (x & 0x80000000) | (y & 0x7FFFFFFF)
    return (z ^ (w >> 1) ^ (0x9908B0DF if w & 1 else 0)) & MASK


def check(coupons, mode):
    known = {}
    for minute, payload in coupons:
        words = list(struct.unpack("<4I" if mode % 2 == 0 else ">4I", payload))
        if mode >= 2:
            words.reverse()
        for offset, word in enumerate(words):
            index = minute + offset
            assert index not in known
            known[index] = untemper(word)
    checks = [(t, known[t + 624], next_mt(known[t], known[t + 1], known[t + 397]))
              for t in known if t + 624 in known and t + 397 in known and t + 1 in known]
    bad = tuple(t for t, actual, predicted in checks if actual != predicted)
    return len(known), len(checks), bad


def run():
    source = (Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(source).hexdigest() == PIN
    coupons = []
    for line in source.decode("ascii").splitlines():
        match = ROW.fullmatch(line)
        if match is None:
            continue
        timestamp, job, attempt, state, category, raw, destination = match.groups()
        job = int(job)
        if 300 <= job <= 427 and attempt == "1" and state == "ACK":
            when = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            minute = 60 * when.hour + when.minute
            assert minute == 420 + 5 * (job - 300)
            coupons.append((minute, bytes.fromhex(raw)))
    assert len(coupons) == 128
    assert sorted(minute for minute, _ in coupons) == list(range(420, 1056, 5))

    engine = random.Random(0x12345678)
    output = [engine.getrandbits(32) for _ in range(1100)]
    native = [untemper(word) for word in output]
    assert all(native[t + 624] == next_mt(native[t], native[t + 1], native[t + 397])
               for t in range(476))
    synthetic = [(minute, struct.pack("<4I", *output[minute:minute + 4]))
                 for minute, _ in coupons]
    assert check(synthetic, 0) == (512, 3, ())
    print("GENUINE_SYNTHETIC_MT19937 PASS (476/476 recurrence controls)")
    for mode in range(4):
        words, checked, failed = check(coupons, mode)
        assert words == 512 and checked == 3 and failed == (421, 426, 431)
        print("ORIGINAL", mode, "observed_words", words, "checked", checked,
              "contradictions", len(failed), "at", failed)
    print("RESULT: all four source-clock layouts contradicted; K04 not recovered")


if __name__ == "__main__":
    run()
