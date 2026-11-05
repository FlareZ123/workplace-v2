"""Read-only K04 categorical side-channel experiment, original source pinned.

Run Python 3 with optional evidence-root argument; test does not mutate evidence.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources/evidence"
SOURCE = ROOT / "print/spool-reconstruction.log"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")


def match(payload: bytes, target: bytes = TARGET) -> bool:
    return hashlib.sha256(bytes(a ^ b for a, b in zip(payload, MASK))).digest() == target


def source_codes() -> list[list[str]]:
    contents = SOURCE.read_bytes()
    assert hashlib.sha256(contents).hexdigest() == SOURCE_SHA
    lines = [x for x in contents.decode("ascii").splitlines() if " CLASS=" in x]
    assert len(lines) == 133
    assert lines[129].startswith(
        "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER"
    )
    first = lines[:128]
    return [[re.search(r"CLASS=(\S+)", s).group(1) for s in first],
            [re.search(r"DEST=(\S+)", s).group(1) for s in first]]


def to128(trits: tuple[int, ...], reverse: bool) -> bytes:
    n = 0
    for x in trits[::-1] if reverse else trits:
        n = 3 * n + x
    return (n & ((1 << 128) - 1)).to_bytes(16, "big")


def run() -> None:
    fields = source_codes()
    hits = []
    checks = 0
    unique = set()
    for fld, values in enumerate(fields):
        labels = sorted(set(values))
        assert len(labels) == 3
        for order in itertools.permutations((0, 1, 2)):
            lookup = dict(zip(labels, order))
            trits = tuple(lookup[v] for v in values)
            for n in (64, 81, 128):
                for start in range(len(trits) - n + 1):
                    source = trits[start:start + n]
                    for rev in (False, True):
                        base = to128(source, rev)
                        for orient in (False, True):
                            candidate = base[::-1] if orient else base
                            if n == 64:
                                bitseq = source[::-1] if rev else source
                                val = 0
                                for t in bitseq:
                                    val = (val << 2) | t
                                candidate = val.to_bytes(16, "big")
                                if orient:
                                    candidate = candidate[::-1]
                            checks += 1
                            unique.add(candidate)
                            if match(candidate):
                                hits.append((fld, order, n, start, rev, orient, candidate.hex()))

    assert checks == 2 * 6 * (65 + 48 + 1) * 4

    # A complete 41-row, 82-trit joint CLASS / DEST base-3 carrier.
    for class_order in itertools.permutations((0, 1, 2)):
        class_map = dict(zip(sorted(set(fields[0])), class_order))
        for dest_order in itertools.permutations((0, 1, 2)):
            dest_map = dict(zip(sorted(set(fields[1])), dest_order))
            for flip in (False, True):
                trits = tuple(
                    t
                    for pair in zip(
                        (class_map[x] for x in fields[0]),
                        (dest_map[x] for x in fields[1]),
                    )
                    for t in (pair[::-1] if flip else pair)
                )
                for start in range(88):
                    window = trits[2 * start:2 * (start + 41)]
                    for rev in (False, True):
                        base = to128(window, rev)
                        for orient in (False, True):
                            candidate = base[::-1] if orient else base
                            checks += 1
                            unique.add(candidate)
                            if match(candidate):
                                hits.append(("JOINT", class_order, dest_order, flip,
                                             start, rev, orient, candidate.hex()))

    assert checks == 30816
    assert len(unique) == checks
    planted = next(iter(unique))
    planted_target = hashlib.sha256(
        bytes(a ^ b for a, b in zip(planted, MASK))
    ).digest()
    assert sum(match(candidate, planted_target) for candidate in unique) == 1
    print({
        "class_counts": dict(collections.Counter(fields[0])),
        "dest_counts": dict(collections.Counter(fields[1])),
        "complete_checks": checks,
        "unique_coupons": len(unique),
        "original_K04_matches": hits,
        "planted_positive": 1,
    })


if __name__ == "__main__":
    run()
