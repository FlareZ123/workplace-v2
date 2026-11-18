"""Sensitivity null preserving CLASS, DEST, STATE and ATTEMPT categories.

Narrow extension of Agent17's 2026-11-18 CLASS/DEST whole-packet permutation
test. Uses only the pinned original spool text, excludes selected ACK2 before
decoding its payload, and preserves complete packets.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
from random import Random
import re
import struct
import sys

SOURCE_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET_INDEX = 129  # index among PAYLOAD rows, not physical text line number
TRIALS = 200_000
SEED = 20261118005


def untemper(y):
    x = y
    for shift, mask, iterations, direction in (
        (18, 0, 2, "r"), (15, 0xEFC60000, 3, "l"),
        (7, 0x9D2C5680, 6, "l"), (11, 0, 5, "r")
    ):
        previous = x
        for _ in range(iterations):
            x = (previous ^ (x >> shift if direction == "r"
                             else (x << shift) & mask)) & 0xFFFFFFFF
    return x


def mix(a, b):
    z = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (z >> 1) ^ (0x9908B0DF if z & 1 else 0)


def parse(path):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == SOURCE_SHA256, digest
    payload_lines = [line for line in raw.decode("ascii").splitlines()
                     if "PAYLOAD=" in line]
    assert len(payload_lines) == 133
    assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in payload_lines[TARGET_INDEX]

    packets, metadata = [], []
    meta_re = re.compile(r"ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+).*?DEST=(\w+)")
    payload_re = re.compile(r"PAYLOAD=([0-9A-F]{32})")
    for index, line in enumerate(payload_lines):
        m = meta_re.search(line)
        assert m, (index, line)
        attempt, state, cls, dest = int(m[1]), m[2], m[3], m[4]
        metadata.append((cls, dest, state, attempt))
        if index == TARGET_INDEX:
            # Do not extract/decode the selected ACK2 payload at all.
            packets.append([])
            continue
        p = payload_re.search(line)
        assert p, (index, line)
        packets.append([untemper(w) for w in struct.unpack("<4I", bytes.fromhex(p[1]))])
    return packets, metadata


def find_triples(packets):
    locations = defaultdict(list)
    words = []
    for row, packet in enumerate(packets):
        for position, word in enumerate(packet):
            words.append((row, position, word))
            locations[word].append((row, position))
    triples = set()
    occurrences = 0
    for antecedent, packet in enumerate(packets):
        for j in range(len(packet) - 1):
            twisted = mix(packet[j], packet[j + 1])
            for middle, ci, value in words:
                for end, dj in locations.get(twisted ^ value, ()):
                    if (middle, ci) < (end, dj) and len({antecedent, middle, end}) == 3:
                        triples.add((antecedent, middle, end))
                        occurrences += 1
    assert (occurrences, len(triples)) == (25, 18)
    assert all(a < c and a < d for a, c, d in triples)
    assert all(TARGET_INDEX not in triple for triple in triples)
    return tuple(sorted(triples)), occurrences


def run(packets, metadata, triples):
    groups = defaultdict(list)
    for index, packet in enumerate(packets):
        if packet:
            groups[metadata[index]].append(index)
    strata = list(groups.values())
    group_hist = Counter(map(len, strata))
    rng = Random(SEED)
    histogram = [0] * (len(triples) + 1)
    for _ in range(TRIALS):
        position = list(range(len(packets)))
        for group in strata:
            permutation = group[:]
            rng.shuffle(permutation)
            # Map each original packet identity to its new slot.
            for slot, packet_id in zip(group, permutation):
                position[packet_id] = slot
        forward = sum(position[a] < position[c] and position[a] < position[d]
                      for a, c, d in triples)
        histogram[forward] += 1
    forward_sum = sum(i * count for i, count in enumerate(histogram))
    maximum = max(i for i, count in enumerate(histogram) if count)
    all_forward = histogram[-1]
    upper95 = 1.0 - 0.05 ** (1.0 / TRIALS) if all_forward == 0 else None
    return group_hist, histogram, forward_sum / TRIALS, maximum, all_forward, upper95


def main(path):
    packets, metadata = parse(path)
    triples, occurrences = find_triples(packets)
    group_hist, histogram, mean, maximum, all_forward, upper95 = run(packets, metadata, triples)
    print("SOURCE_SHA256", SOURCE_SHA256)
    print("INTACT_PACKETS", sum(bool(p) for p in packets))
    print("WITNESS_OCCURRENCES", occurrences)
    print("UNIQUE_TRIPLES", len(triples))
    print("ALL_ORIGINAL_TRIPLES_FORWARD", all(a < c and a < d for a, c, d in triples))
    print("FULL_METADATA_FIELDS", "CLASS,DEST,STATE,ATTEMPT")
    print("GROUP_SIZE_HISTOGRAM", dict(sorted(group_hist.items())))
    print("TRIALS", TRIALS, "SEED", SEED)
    print("MEAN_FORWARD", f"{mean:.6f}", "MAX", maximum, "ALL18", all_forward)
    print("HISTOGRAM_0_TO_18", histogram)
    print("ZERO_SUCCESS_UPPER_95", f"{upper95:.12g}" if upper95 is not None else "n/a")
    assert (round(mean * TRIALS), maximum, all_forward) == (1489293, 16, 0)
    print("PASS: full four-field categorical metadata sensitivity null")


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources/evidence/print/spool-reconstruction.log")
    main(source)
