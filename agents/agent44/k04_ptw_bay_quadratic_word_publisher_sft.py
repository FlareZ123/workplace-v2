#!/usr/bin/env python3
"""Source-paired PTW/PS quadratic word-publisher falsifier.

The candidate join pairs PTW-390..416 with same-suffix PS-261003-0390..0416
ACK1 records. The selected PS-0417 ACK2 payload, K04 mask and commitments
are excluded. Run from the repository root, optionally passing a resources
directory as the first argument.
"""
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
SEAL = ROOT / "evidence/maintenance/seal-receipts.jsonl"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
PINS = {
    SEAL: "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}


def read_source(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PINS[path], path
    return raw


def m8(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
    return out


def p8(a, n):
    out = 1
    while n:
        if n & 1:
            out = m8(out, a)
        a = m8(a, a)
        n >>= 1
    return out


def fit8(xs, ys):
    assert len(xs) == len(ys) == 3 and len(set(xs)) == 3
    aa = bb = cc = 0
    for i in range(3):
        j, k = [q for q in range(3) if q != i]
        scale = m8(ys[i], p8(m8(xs[i] ^ xs[j], xs[i] ^ xs[k]), 254))
        aa ^= scale
        bb ^= m8(scale, xs[j] ^ xs[k])
        cc ^= m8(scale, m8(xs[j], xs[k]))
    return aa, bb, cc


def e8(coeff, x):
    a, b, c = coeff
    return m8(m8(a, x) ^ b, x) ^ c


POLY32 = 0x8D  # x^32 + x^7 + x^3 + x^2 + 1
MASK32 = 0xFFFFFFFF


def m32(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 0x100000000:
            a ^= 0x100000000 | POLY32
    return out & MASK32


def p32(a, n):
    out = 1
    while n:
        if n & 1:
            out = m32(out, a)
        a = m32(a, a)
        n >>= 1
    return out


def fit32(xs, ys):
    assert len(xs) == len(ys) == 3 and len(set(xs)) == 3
    aa = bb = cc = 0
    for i in range(3):
        j, k = [q for q in range(3) if q != i]
        den = m32(xs[i] ^ xs[j], xs[i] ^ xs[k])
        scale = m32(ys[i], p32(den, (1 << 32) - 2))
        aa ^= scale
        bb ^= m32(scale, xs[j] ^ xs[k])
        cc ^= m32(scale, m32(xs[j], xs[k]))
    return aa, bb, cc


def e32(coeff, x):
    a, b, c = coeff
    return m32(m32(a, x) ^ b, x) ^ c


def load_pairs():
    seals = [json.loads(x) for x in read_source(SEAL).decode().splitlines() if x.strip()]
    packets = defaultdict(list)
    pat = re.compile(
        r"JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) "
        r"CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)"
    )
    for line in read_source(SPOOL).decode().splitlines():
        match = pat.search(line)
        if match:
            n, attempt, state, cls, payload, dest = match.groups()
            packets[int(n)].append((int(attempt), state, bytes.fromhex(payload)))
    pairs = []
    for n in range(390, 417):
        sr = [r for r in seals if r["permit"] == f"PTW-{n}"]
        assert len(sr) == 1
        pr = packets[n]
        assert len(pr) == 1 and pr[0][0] == 1 and pr[0][1] == "ACK"
        pairs.append({
            "id": n,
            "bay": sr[0]["bay"],
            "serial": bytes.fromhex(sr[0]["serial"].split("-", 1)[1]),
            "packet": pr[0][2],
        })
    assert Counter(x["bay"] for x in pairs) == {"A": 8, "B": 4, "C": 9, "D": 6}
    return pairs


def synthetic_controls():
    rng = random.Random(20261107)
    for _ in range(20):
        xs = [rng.getrandbits(32) for _ in range(8)]
        c = tuple(rng.getrandbits(32) for _ in range(3))
        ys = [e32(c, x) for x in xs]
        recovered = fit32(xs[:3], ys[:3])
        assert recovered == c and all(e32(recovered, x) == y for x, y in zip(xs[3:], ys[3:]))
    for _ in range(20):
        xs = [rng.randrange(256) for _ in range(8)]
        if len(set(xs[:3])) < 3:
            continue
        c = tuple(rng.randrange(256) for _ in range(3))
        ys = [e8(c, x) for x in xs]
        recovered = fit8(xs[:3], ys[:3])
        assert recovered == c and all(e8(recovered, x) == y for x, y in zip(xs[3:], ys[3:]))
    assert m32(0x12345678, p32(0x12345678, (1 << 32) - 2)) == 1


def run8(pairs):
    models = predictions = exact = byte_hits = 0
    for bay in "ABCD":
        group = sorted((x for x in pairs if x["bay"] == bay), key=lambda x: x["id"])
        train, hold = group[:3], group[3:]
        for w in range(4):
            for ir in (False, True):
                for outrev in (False, True):
                    xs = [x["serial"][::-1] if ir else x["serial"] for x in train]
                    ys = []
                    for x in train:
                        word = x["packet"][4*w:4*w+4]
                        ys.append(word[::-1] if outrev else word)
                    if any(len({xs[k][j] for k in range(3)}) < 3 for j in range(4)):
                        continue
                    coeff = [fit8([v[j] for v in xs], [v[j] for v in ys]) for j in range(4)]
                    models += 1
                    for x in hold:
                        source = x["serial"][::-1] if ir else x["serial"]
                        actual = x["packet"][4*w:4*w+4]
                        actual = actual[::-1] if outrev else actual
                        pred = bytes(e8(coeff[j], source[j]) for j in range(4))
                        exact += pred == actual
                        byte_hits += sum(a == b for a, b in zip(pred, actual))
                        predictions += 1
    assert (models, predictions, exact, byte_hits) == (64, 240, 0, 6)
    return {"models": models, "holdout_words": predictions, "exact_words": exact, "matching_bytes": byte_hits}


def run32(pairs):
    modes = ("serial", "xor_id", "add_id", "sub_id")
    models = predictions = exact = byte_hits = bit_errors = 0
    for bay in "ABCD":
        group = sorted((x for x in pairs if x["bay"] == bay), key=lambda x: x["id"])
        train, hold = group[:3], group[3:]
        for w in range(4):
            for ir in (False, True):
                for outrev in (False, True):
                    for mode in modes:
                        def xval(row):
                            raw = row["serial"][::-1] if ir else row["serial"]
                            value = int.from_bytes(raw, "big")
                            if mode == "xor_id":
                                value ^= row["id"]
                            elif mode == "add_id":
                                value = (value + row["id"]) & MASK32
                            elif mode == "sub_id":
                                value = (value - row["id"]) & MASK32
                            return value
                        xs = [xval(x) for x in train]
                        ys = []
                        for x in train:
                            word = x["packet"][4*w:4*w+4]
                            ys.append(int.from_bytes(word[::-1] if outrev else word, "big"))
                        if len(set(xs)) < 3:
                            continue
                        coeff = fit32(xs, ys)
                        models += 1
                        for x in hold:
                            word = x["packet"][4*w:4*w+4]
                            actual = word[::-1] if outrev else word
                            pred = e32(coeff, xval(x)).to_bytes(4, "big")
                            exact += pred == actual
                            byte_hits += sum(a == b for a, b in zip(pred, actual))
                            bit_errors += sum((a ^ b).bit_count() for a, b in zip(pred, actual))
                            predictions += 1
    assert (models, predictions, exact, byte_hits, bit_errors) == (256, 960, 0, 15, 15348)
    return {
        "models": models, "holdout_words": predictions, "exact_words": exact,
        "matching_bytes": byte_hits, "bit_errors": bit_errors,
    }


def main():
    synthetic_controls()
    pairs = load_pairs()
    print(json.dumps({
        "source_sha256": {str(k): v for k, v in PINS.items()},
        "candidate_join": "PTW-n with PS-261003-0n by equal suffix, n=390..416",
        "training": "three lowest-numbered permits per bay",
        "pairs": len(pairs),
        "holdouts_by_bay": {"A": 5, "B": 1, "C": 6, "D": 3},
        "GF256_bytewise_quadratic": run8(pairs),
        "GF2_32_word_quadratic_with_serial_id_inputs": run32(pairs),
        "synthetic_controls": "PASS",
        "selected_K04_payload_read": False,
        "K04_mask_or_commitment_read": False,
        "result": "NO_SOURCE_HOLDOUT_PREDICTIONS",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
