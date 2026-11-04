"""H-17 K04 printer source: per-packet linear ECC rank, original-only SFT."""
import argparse
import hashlib
import random
import re
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def mul(a, b, poly):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        if a & 256:
            a ^= poly
        b >>= 1
    return out

def inv(x, poly):
    assert x
    out, power = 1, 254
    while power:
        if power & 1:
            out = mul(out, x, poly)
        x = mul(x, x, poly)
        power >>= 1
    return out

def rank256(vectors, poly):
    a = [bytearray(v) for v in vectors]
    rank = 0
    for c in range(16):
        pivot = next((i for i in range(rank, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = inv(a[rank][c], poly)
        for j in range(c, 16):
            a[rank][j] = mul(a[rank][j], scale, poly)
        for i in range(len(a)):
            if i == rank or not a[i][c]:
                continue
            scale = a[i][c]
            for j in range(c, 16):
                a[i][j] ^= mul(scale, a[rank][j], poly)
        rank += 1
    return rank

def rank2(vectors):
    basis = {}
    for value in vectors:
        x = int.from_bytes(value, "big")
        while x:
            col = x.bit_length() - 1
            if col in basis:
                x ^= basis[col]
            else:
                basis[col] = x
                break
    return len(basis)

def centered(values):
    return [bytes(a ^ b for a, b in zip(x, values[0])) for x in values]

def read_original(root):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = []
    for line in raw.decode().splitlines():
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(
            r"\S+ JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=\w+",
            line,
        )
        assert match, line
        job, attempt, state, cls, payload = match.groups()
        rows.append((job, int(attempt), state, cls, bytes.fromhex(payload)))
    assert len(rows) == 133
    assert rows[129][:4] == ("PS-261003-0417", 2, "ACK", "RECOVER")
    return rows

def synthetic_control(poly):
    rng = random.Random(20261104)
    source = []
    for _ in range(48):
        data = [rng.randrange(256) for _ in range(12)]
        parity = []
        for i in range(4):
            p = 0
            for j, val in enumerate(data):
                p ^= mul(val, (i + 1) * (j + 1), poly)
            parity.append(p)
        source.append(bytes(data + parity))
    assert (rank256(source, poly), rank256(centered(source), poly)) == (12, 12)
    damaged = source.copy()
    damaged[0] = damaged[0][:12] + bytes([damaged[0][12] ^ 1]) + damaged[0][13:]
    assert rank256(damaged, poly) == 13

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2] / "resources")
    rows = read_original(parser.parse_args().root)
    good = [r[4] for i, r in enumerate(rows) if i != 129 and r[2] == "ACK"]
    assert len(good) == 130
    print("original ACK GF2 linear, affine ranks:", rank2(good), rank2(centered(good)))
    assert (rank2(good), rank2(centered(good))) == (128, 127)
    for poly in (0x11B, 0x11D):
        synthetic_control(poly)
        for cls, count in (("RECOVER", 37), ("LABEL", 52), ("STORES", 41)):
            values = [r[4] for i, r in enumerate(rows) if i != 129 and r[2] == "ACK" and r[3] == cls]
            assert len(values) == count
            ranks = rank256(values, poly), rank256(centered(values), poly)
            print(f"GF({poly:#x}) {cls} n={count} linear, affine ranks: {ranks}")
            assert ranks == (16, 16)
    print("PASS: genuine ECC positive and corruption controls, source exclusions")

if __name__ == "__main__":
    main()
