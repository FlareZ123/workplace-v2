"""Source-stage-free MT19937 precursor search across intact printer and AX checkpoints.

Run from a workplace-v2 checkout with Python 3. Requires only standard library.
All original sources are read-only. The disputed selected K04 ACK2, its mask,
acceptance commitment, candidate and verifier are never used.
"""
from collections import defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import random
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MAG = 0x9908B0DF
BIT30_OMIT = 0xBFFFFFFF
U32 = 0xFFFFFFFF


def pinned(path, digest):
    data = (ROOT / path).read_bytes()
    assert sha256(data).hexdigest() == digest
    return data


def untemper(value):
    for shift, left, mask in (
        (18, False, U32), (15, True, 0xEFC60000),
        (7, True, 0x9D2C5680), (11, False, U32)
    ):
        original = value
        for _ in range(6):
            value = original ^ (((value << shift) & mask) if left else (value >> shift))
        value &= U32
    return value


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    value ^= value >> 18
    return value & U32


def precursor_options(early, late):
    """Return both possible tempered X[t+1] from intact X[t+397],X[t+624]."""
    difference = (early ^ late) & BIT30_OMIT
    parity = difference >> 31
    lower31 = (((difference ^ (MAG if parity else 0)) & 0x3FFFFFFF) << 1) | parity
    assert ((((lower31 & 0x7FFFFFFF) >> 1) ^ ((lower31 & 1) * MAG)) & BIT30_OMIT) == difference
    return (temper(lower31), temper(lower31 | 0x80000000))


def printer_rows():
    data = pinned("evidence/print/spool-reconstruction.log", SPOOL_SHA)
    payloads = [bytes.fromhex(b.decode("ascii")) for b in re.findall(rb"PAYLOAD=([0-9A-F]{32})", data)]
    assert len(payloads) == 133
    # Only intact observations: exclude row129 without decoding any of its bytes.
    return {i: [untemper(int.from_bytes(p[j:j + 4], "little")) for j in (0, 4, 8, 12)]
            for i, p in enumerate(payloads) if i != 129}


def triples(rows):
    """Index source-constrained 3x16bit sampler candidates, no MT stages."""
    bycode = defaultdict(list)
    specifications = 0
    for ra, rb in combinations(sorted(rows), 2):
        for start in (0, 1):
            possibilities = [precursor_options(rows[ra][start + lane], rows[rb][start + lane])
                             for lane in range(3)]
            for selected in product((0, 1), repeat=3):
                complete = [possibilities[i][selected[i]] for i in range(3)]
                for view in ("high16", "low16"):
                    sequence = tuple((v >> 16) if view == "high16" else (v & 0xFFFF)
                                     for v in complete)
                    bycode[sequence].append((ra, rb, start, selected, view))
                    specifications += 1
    return bycode, specifications


def original_transfer_windows(bycode, rows):
    data = pinned("evidence/transfers/transfer-audit.jsonl", TRANSFER_SHA)
    source = [json.loads(line) for line in data.decode("ascii").splitlines()]
    source = [item for item in source if item["kind"] == "CHUNK"]
    assert len(source) == 64
    hits = []
    checked = 0
    for transfer in sorted({x["transfer"] for x in source}):
        selected = [x for x in source if x["transfer"] == transfer]
        assert len(selected) == 16
        for order in ("seq", "attempt"):
            ordered = sorted(selected, key=lambda x: (x["seq"], x["attempt"])
                             if order == "seq" else (x["attempt"], x["seq"]))
            for endian in ("little", "big"):
                values = [int.from_bytes(bytes.fromhex(x["checkpoint"]), endian)
                          for x in ordered]
                for start in range(14):
                    checked += 1
                    for ra, rb, offset, selected_bits, view in bycode.get(tuple(values[start:start + 3]), ()):
                        next_options = ()
                        heldout = None
                        if offset == 0:
                            options = precursor_options(rows[ra][3], rows[rb][3])
                            next_options = tuple((v >> 16) if view == "high16" else (v & 0xFFFF)
                                                 for v in options)
                            heldout = values[start + 3] in next_options
                        hits.append((transfer, order, endian, start, ra, rb, offset,
                                     selected_bits, view, next_options, values[start + 3], heldout))
    return checked, hits


def controls(bycode, rows):
    rng = random.Random(0x81723)
    stream = [untemper(rng.getrandbits(32)) for _ in range(900)]
    for t in range(20, 24):
        assert temper(stream[t + 1]) in precursor_options(stream[t + 397], stream[t + 624])
    for _ in range(40):
        synthetic = tuple(random.Random(rng.getrandbits(64)).randrange(65536) for _ in range(3))
        assert synthetic not in bycode
    expected = [0x35AE, 0x78FE, 0x42DD, 0xFD35]
    for lane, observed in enumerate(expected):
        assert observed in [v >> 16 for v in precursor_options(rows[34][lane], rows[64][lane])]


def main():
    rows = printer_rows()
    assert len(rows) == 132
    bycode, assignments = triples(rows)
    checked, hits = original_transfer_windows(bycode, rows)
    controls(bycode, rows)
    assert assignments == 276672 and len(bycode) == 276672
    assert checked == 224 and len(hits) == 2
    assert [(h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[8]) for h in hits] == [
        ("AX-7778", "seq", "little", 11, 34, 64, 0, "high16"),
        ("AX-7778", "seq", "little", 12, 34, 64, 1, "high16")]
    assert hits[0][9] == (0x7525, 0xFD35) and hits[0][10] == 0xFD35 and hits[0][11] is True
    assert hits[1][11] is None
    print(json.dumps({"source_packet_pairs": 8646, "source_triple_specs": assignments,
                      "independent_transfer_window_checks": checked,
                      "source_three_word_matches": len(hits), "heldout_fourth_exact": 1,
                      "matched_original_transfer": "AX-7778", "matched_printer_rows": [34, 64],
                      "matched_byteswapped_hex": ["35AE", "78FE", "42DD", "FD35"],
                      "genuine_prng_and_random_negative_controls": "PASS",
                      "original_selected_K04_bits_recovered": 0}, indent=2))


if __name__ == "__main__":
    main()
