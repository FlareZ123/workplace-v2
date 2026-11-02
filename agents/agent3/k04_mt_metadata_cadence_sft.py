"""SFT: MT19937 producer with bounded class/dest-conditioned metadata draw cadence.

Hypothesis: the 128 original ordinary printer coupons are four contiguous
tempered MT19937 outputs each, with extra draws per row according to source
CLASS and DEST labels. Test actual MT cross-cycle recurrences on intact
records. Selected 18:02 ACK2, K04 mask and commitments are never read.
Run: python agents/agent3/k04_mt_metadata_cadence_sft.py
"""
import hashlib
import itertools
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = (1 << 32) - 1

def unright(v, shift):
    x = v
    for _ in range(6):
        x = v ^ (x >> shift)
    return x & U

def unleft(v, shift, mask):
    x = v
    for _ in range(7):
        x = v ^ ((x << shift) & mask)
    return x & U

def untemper(y):
    y = unright(y, 18)
    y = unleft(y, 15, 0xEFC60000)
    y = unleft(y, 7, 0x9D2C5680)
    return unright(y, 11)

def twist(x, y):
    z = (x & 0x80000000) | (y & 0x7FFFFFFF)
    return ((z >> 1) ^ (0x9908B0DF if z & 1 else 0)) & U

def source_rows():
    data = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    rows = []
    for line in data.decode("ascii").splitlines():
        m = re.search(
            r"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK "
            r"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", line)
        if m and 300 <= int(m.group(1)) <= 427:
            rows.append((m.group(2), m.group(4), bytes.fromhex(m.group(3))))
    assert len(rows) == 128
    return rows

def packet_positions(rows, base, clabel, dlabel, before):
    positions = []
    offset = 0
    for category, dest, _ in rows:
        positions.append((offset + before, offset + before + 1,
                          offset + before + 2, offset + before + 3))
        offset += 4 + base + clabel[category] + dlabel[dest]
    return positions, offset

def recurrence_test(index):
    checks = matches = 0
    for position, value in index.items():
        if position < 624:
            continue
        prior = (position - 227, position - 624, position - 623)
        if not all(p in index for p in prior):
            continue
        checks += 1
        if value == (index[prior[0]] ^ twist(index[prior[1]], index[prior[2]])):
            matches += 1
    return checks, matches

def main():
    rows = source_rows()
    rng = random.Random(20261003)
    full = [untemper(rng.getrandbits(32)) for _ in range(1200)]
    assert all(full[p] == (full[p - 227] ^
                twist(full[p - 624], full[p - 623]))
               for p in range(624, 1200))

    clabel = {"LABEL": 0, "RECOVER": 1, "STORES": 2}
    dlabel = {"bench": 0, "desk": 1, "store": 2}
    synthetic_positions, width = packet_positions(rows, 2, clabel, dlabel, 1)
    rng = random.Random(98232)
    synthetic = [untemper(rng.getrandbits(32)) for _ in range(width)]
    synthetic_index = {p: synthetic[p] for four in synthetic_positions for p in four}
    checks, matches = recurrence_test(synthetic_index)
    assert checks == matches == 43
    print(f"PASS synthetic known-cadence cross-cycle MT checks: {checks}")

    views = {}
    for endian, reverse in itertools.product(("little", "big"), (False, True)):
        packets = []
        for category, dest, raw in rows:
            words = [untemper(int.from_bytes(raw[k:k + 4], endian))
                     for k in (0, 4, 8, 12)]
            packets.append(words[::-1] if reverse else words)
        views[endian, reverse] = packets

    tested = with_checks = no_checks = total = matched = 0
    max_checks = 0
    survivors = []
    for base in range(5):
        for cvals in itertools.product(range(3), repeat=2):
            classes = {"LABEL": 0, "RECOVER": cvals[0], "STORES": cvals[1]}
            for dvals in itertools.product(range(3), repeat=2):
                dests = {"bench": 0, "desk": dvals[0], "store": dvals[1]}
                for before in range(base + 1):
                    positions, _ = packet_positions(rows, base, classes, dests, before)
                    for orientation, packets in views.items():
                        observed = {position: value
                            for four, packet in zip(positions, packets)
                            for position, value in zip(four, packet)}
                        count, hits = recurrence_test(observed)
                        tested += 1
                        total += count
                        matched += hits
                        max_checks = max(max_checks, count)
                        if count == 0:
                            no_checks += 1
                        else:
                            with_checks += 1
                            if count == hits:
                                survivors.append((base, cvals, dvals, before, orientation))
    assert tested == 4860
    assert with_checks == 4764 and no_checks == 96
    assert total == 169220 and matched == 0 and max_checks == 77
    assert not survivors
    print(f"original metadata-cadence models {tested}: with equations {with_checks}, "
          f"no equations {no_checks}; exact recurrence checks {total}, matches {matched}")
    print("zero source models pass; selected K04 coupon, mask and hash: UNREAD")

if __name__ == "__main__":
    main()
