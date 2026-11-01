"""Read-only H-17 K04 two-gap single-file test.

Read original incident ZIP; selected row129 payload and acceptance are withheld.
Frozen row-start coordinates originate from:
workplace-v1/agents/agent5/k04_crosssource_six_vectors.json
"""
from __future__ import annotations

import argparse
import hashlib
import random
import re
import struct
import zipfile
from pathlib import Path

SPOOL_PATH = "evidence/print/spool-reconstruction.log"
SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CHRONOLOGIES = (
    # selected p, row43 start, row44 start, row96 start, row97 start
    (950, 323, 334, 716, 728),
    (951, 324, 335, 717, 729),
    (952, 325, 336, 718, 730),
    (953, 326, 337, 719, 731),
    (954, 327, 338, 720, 732),
    (955, 328, 339, 721, 733),
)
SEEDS = (0, 17, 20261003, 314159, 0xC0FFEE)
FULL = 0xFFFFFFFF
MAGIC = 0x9908B0DF


def untemper(value: int) -> int:
    result = value
    for _ in range(6):
        result = value ^ (result >> 18)
    value = result & FULL
    result = value
    for _ in range(7):
        result = value ^ ((result << 15) & 0xEFC60000)
    value = result & FULL
    result = value
    for _ in range(7):
        result = value ^ ((result << 7) & 0x9D2C5680)
    value = result & FULL
    result = value
    for _ in range(6):
        result = value ^ (result >> 11)
    return result & FULL


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & FULL


def twist(a: int, b: int) -> int:
    mixed = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return ((mixed >> 1) ^ (MAGIC if b & 1 else 0)) & FULL


def verify_source(archive: Path) -> None:
    with zipfile.ZipFile(archive) as source:
        blob = source.read(SPOOL_PATH)
    digest = hashlib.sha256(blob).hexdigest()
    assert digest == SPOOL_SHA256
    rows = [line for line in blob.decode("ascii").splitlines() if "PAYLOAD=" in line]
    assert len(rows) == 133
    print("ORIGINAL_SPOOL_SHA256", digest, "ROWS", len(rows))
    anchors = {
        43: ("2026-10-03T10:35:00+00:00", "PS-261003-0343"),
        44: ("2026-10-03T10:40:00+00:00", "PS-261003-0344"),
        96: ("2026-10-03T15:00:00+00:00", "PS-261003-0396"),
        97: ("2026-10-03T15:05:00+00:00", "PS-261003-0397"),
    }
    for i, (timestamp, job) in anchors.items():
        assert rows[i].startswith(timestamp + " JOB=" + job + " ")
        print("ANCHOR", i, timestamp, job)
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in rows[129]
    print("SELECTED", "row129 metadata only; bytes withheld")
    original43 = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", rows[43]).group(1)
    last_word = struct.unpack("<4I", bytes.fromhex(original43))[3]
    assert temper(untemper(last_word)) == last_word
    assert untemper(last_word) == 0x59E4D0B9
    print("INTACT_SOURCE_WORD", "row43.word3", f"{last_word:08X}")


def test_cuts() -> None:
    for p, a, b, c, d in CHRONOLOGIES:
        assert (a, b, c, d) == (p - 627, p - 616, p - 234, p - 222)
        assert a + 3 == p - 624
        assert all(a + 4 <= j < b for j in range(p - 623, p - 619))
        assert all(c + 4 <= j < d for j in range(p - 227, p - 223))
        print("CONDITIONAL_MODEL", p, "known=", p - 624,
              "early_gap=", list(range(p - 623, p - 619)),
              "middle_gap=", list(range(p - 227, p - 223)))
    print("SIX_WAY_CAUSAL_CUT_PASS", len(CHRONOLOGIES))


def test_mt() -> None:
    total = 0
    for seed in SEEDS:
        mt = random.Random(seed)
        states = [untemper(mt.getrandbits(32)) for _ in range(960)]
        for p, *_ in CHRONOLOGIES:
            predicted = [
                states[p - 227 + i] ^ twist(states[p - 624 + i], states[p - 623 + i])
                for i in range(4)
            ]
            assert predicted == states[p:p + 4], (seed, p)
            for j in range(4):
                printed = temper(states[p + j])
                parity = ((printed >> 30) ^ (printed >> 15)) & 1
                donor = ((states[p - 227 + j] >> 30) ^ (states[p - 624 + j] >> 31)) & 1
                assert parity == donor, (seed, p, j, parity, donor)
            total += 1
        print("SYNTHETIC_MT_PASS", seed, "six complete four-word predictions")
    print("TOTAL_FULL_COUPON_SYNTHETIC_CONTROLS", total)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    verify_source(args.archive)
    test_cuts()
    test_mt()
    print("K04_SELECTED_AUTHENTICATED_BITS", 0, "K08_EXACT_FINAL_WORDS", 0)


if __name__ == "__main__":
    main()
