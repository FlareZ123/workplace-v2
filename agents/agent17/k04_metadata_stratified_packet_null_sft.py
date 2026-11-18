"""Source-preserving conditional permutation null for native MT printer witnesses.

Reads only an unchanged original H-17 spool text file. Excludes selected ACK2
before decoding, and never imports K04 acceptance or mask. Entire packet objects
are shuffled within frozen original metadata categories, without altering words.
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from random import Random
import re
import struct
import sys

PIN = '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
TRIALS = 200_000
SEED = 20261118004


def untemper(y):
    x = y
    for shift, mask, iterations, direction in (
        (18, 0, 2, 'r'), (15, 0xEFC60000, 3, 'l'),
        (7, 0x9D2C5680, 6, 'l'), (11, 0, 5, 'r')
    ):
        previous = x
        for _ in range(iterations):
            x = (previous ^ (x >> shift if direction == 'r'
                             else (x << shift) & mask)) & 0xFFFFFFFF
    return x


def mix(a, b):
    z = (a & 0x80000000) | (b & 0x7FFFFFFF)
    return (z >> 1) ^ (0x9908B0DF if z & 1 else 0)


def parse(path):
    original = path.read_bytes()
    assert sha256(original).hexdigest() == PIN
    lines = [line for line in original.decode('ascii').splitlines()
             if 'PAYLOAD=' in line]
    assert len(lines) == 133
    assert 'JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER' in lines[129]
    packets, metadata = [], []
    for index, line in enumerate(lines):
        m = re.search(r'CLASS=(\w+).*?PAYLOAD=([0-9A-F]{32}) DEST=(\w+)', line)
        assert m
        metadata.append((m[1], m[3]))
        if index == 129:
            packets.append([])
        else:
            packets.append([untemper(w) for w in
                            struct.unpack('<4I', bytes.fromhex(m[2]))])
    return packets, metadata


def constraints(packets):
    locations = defaultdict(list)
    words = []
    for row, block in enumerate(packets):
        for position, word in enumerate(block):
            words.append((row, position, word))
            locations[word].append((row, position))
    triples = set()
    matches = 0
    for antecedent, packet in enumerate(packets):
        for j in range(len(packet) - 1):
            xor = mix(packet[j], packet[j+1])
            for middle, ci, value in words:
                for end, dj in locations.get(xor ^ value, ()):
                    if (middle, ci) < (end, dj) and len({antecedent, middle, end}) == 3:
                        triples.add((antecedent, middle, end))
                        matches += 1
    assert (matches, len(triples)) == (25, 18)
    assert all(a < c and a < d for a, c, d in triples)
    return tuple(sorted(triples))


def shuffle_control(packets, metadata, triples, mode):
    groups = defaultdict(list)
    for i, packet in enumerate(packets):
        if not packet:
            continue
        cls, dest = metadata[i]
        key = ((cls, dest) if mode == 'class_dest' else cls if mode == 'class'
               else dest if mode == 'dest' else 'global')
        groups[key].append(i)
    strata = list(groups.values())
    rng = Random(SEED)
    positions = list(range(len(packets)))
    histogram = [0] * (len(triples) + 1)
    for _ in range(TRIALS):
        for group in strata:
            destinations = group[:]
            rng.shuffle(destinations)
            for original, shuffled in zip(group, destinations):
                positions[original] = shuffled
        forward = sum(positions[a] < positions[c] and positions[a] < positions[d]
                      for a, c, d in triples)
        histogram[forward] += 1
    return histogram


def main(source):
    packets, metadata = parse(source)
    triples = constraints(packets)
    print('SOURCE_SHA256', PIN)
    print('ORIGINAL_INTACT_PACKETS', 132)
    print('FULLWORD_MATCHES', 25)
    print('DISTINCT_TRIPLES_ALL_FORWARD', len(triples))
    for mode, expected_sum, expected_max in (
        ('class_dest', 1483424, 16), ('class', 1290626, 16),
        ('dest', 1227365, 16), ('none', 1198727, 15)
    ):
        histogram = shuffle_control(packets, metadata, triples, mode)
        forward_sum = sum(i * count for i, count in enumerate(histogram))
        maximum = max(i for i, count in enumerate(histogram) if count)
        assert forward_sum == expected_sum, (mode, forward_sum)
        assert maximum == expected_max, (mode, maximum)
        assert histogram[-1] == 0
        print('STRATUM', mode, 'N', TRIALS, 'mean', forward_sum / TRIALS,
              'max', maximum, 'all18', histogram[-1], 'histogram', histogram)
    print('PASS: source-pinned, packet-intact, category-stratified chronology null')


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] /
         'resources/evidence/print/spool-reconstruction.log')
