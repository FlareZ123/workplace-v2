"""H-17 source-pinned original printer clock seed + unknown initial MT draws.

CPython random.Random(integer_seed).getrandbits(32), with 0..max_prefix
unobserved generator draws and four source packet byte/word layouts.
The disputed original selected ACK row129 and K04 commitment are withheld.
This is a source-calibrated hypothetical writer, not evidenced firmware.
"""
import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]


def decode(payload, endian, reverse):
    raw = bytes.fromhex(payload)
    values = tuple(int.from_bytes(raw[i:i + 4], endian) for i in range(0, 16, 4))
    return values[::-1] if reverse else values


def check_all_rows(seed, prefix, layout, payloads):
    """Freeze candidate on first packet; validate other 131 intact packets."""
    endian, reverse = layout
    rng = random.Random(seed)
    current = 0
    compared = 0
    for row, pos in enumerate(STARTS):
        if row == 129:
            continue
        until = prefix + pos
        for _ in range(until - current):
            rng.getrandbits(32)
        actual = tuple(rng.getrandbits(32) for _ in range(4))
        current = until + 4
        if actual != decode(payloads[row], endian, reverse):
            return compared
        compared += 1
    return compared


def scan(seed_min, seed_max, max_prefix, source):
    original = source.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA
    payloads = [x.decode() for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", original)]
    assert len(payloads) == len(STARTS) == 133
    assert payloads[0] == "FBBBC54356483F5864BB3F06794518A5"
    assert payloads[1] == "64176B6C3A91BD06B12FC0D90B3A7DB4"
    patterns = {
        decode(payloads[0], endian, reverse)[0]: (endian, reverse)
        for endian in ("little", "big") for reverse in (False, True)
    }
    assert len(patterns) == 4
    firstword_hits, packet_hits = [], []
    started = time.monotonic()
    for seed in range(seed_min, seed_max):
        rng = random.Random(seed)
        for offset in range(max_prefix + 1):
            out = rng.getrandbits(32)
            layout = patterns.get(out)
            if layout is None:
                continue
            state = rng.getstate()
            rest = tuple(rng.getrandbits(32) for _ in range(3))
            rng.setstate(state)
            if rest == decode(payloads[0], *layout)[1:]:
                intact = check_all_rows(seed, offset, layout, payloads)
                packet_hits.append(dict(seed=seed, offset=offset,
                                        endian=layout[0], reverse=layout[1],
                                        matching_original_packets=intact))
                print("FOURWORD SOURCE MATCH", packet_hits[-1], flush=True)
            firstword_hits.append(dict(seed=seed, offset=offset,
                                       endian=layout[0], reverse=layout[1]))
    draws = (seed_max - seed_min) * (max_prefix + 1)
    return dict(seed_min=seed_min, seed_max=seed_max,
                max_prefix=max_prefix, seed_count=seed_max - seed_min,
                generator_outputs=draws, firstword_tests=draws * 4,
                firstword_matches=firstword_hits,
                full_packet_matches=packet_hits,
                elapsed_seconds=round(time.monotonic() - started, 3))


def synthetic_controls():
    for seed in (1, 5489, 1791010800):
        for prefix in (0, 17, 625, 4095):
            rng = random.Random(seed)
            for _ in range(prefix):
                rng.getrandbits(32)
            native = tuple(rng.getrandbits(32) for _ in range(4))
            for endian in ("little", "big"):
                for reverse in (False, True):
                    raw = native[::-1] if reverse else native
                    packet = b"".join(word.to_bytes(4, endian) for word in raw).hex()
                    assert decode(packet, endian, reverse) == native
    seed, prefix = 20261103, 57
    rng = random.Random(seed)
    for _ in range(prefix):
        rng.getrandbits(32)
    expected = tuple(rng.getrandbits(32) for _ in range(4))
    found = []
    for test_seed in range(seed - 3, seed + 4):
        trial = random.Random(test_seed)
        for test_prefix in range(72):
            output = trial.getrandbits(32)
            if output != expected[0]:
                continue
            state = trial.getstate()
            other = tuple(trial.getrandbits(32) for _ in range(3))
            trial.setstate(state)
            if other == expected[1:]:
                found.append((test_seed, test_prefix))
    assert found == [(seed, prefix)]
    return "48 layout controls and one planted hidden-prefix recovery PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-min", type=int, required=True)
    parser.add_argument("--seed-max", type=int, required=True)
    parser.add_argument("--max-prefix", type=int, default=8192)
    parser.add_argument("--source", type=Path, default=(
        Path(__file__).resolve().parents[2] /
        "resources/evidence/print/spool-reconstruction.log"
    ))
    args = parser.parse_args()
    assert 0 <= args.seed_min < args.seed_max and args.max_prefix >= 0
    print(synthetic_controls(), flush=True)
    print(json.dumps(scan(args.seed_min, args.seed_max,
                          args.max_prefix, args.source), sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
