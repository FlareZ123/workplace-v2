"""Original H-17 source-only printer parity-code falsifier.

A fixed affine GF2/GF256 code shared by every intact ordinary printer
packet must yield rank <128 / <16 after centering packets.
Target ACK row129, route mask, acceptance and verifier are never opened.
"""
import hashlib
import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
packets = []
for line in raw.decode().splitlines():
    if not line or line.startswith("#"):
        continue
    if line.startswith("2026-10-03T18:02:00Z JOB=PS-261003-0417 "):
        continue
    fields = dict(item.split("=", 1) for item in line.split()[1:])
    packets.append(bytes.fromhex(fields["PAYLOAD"]))
assert len(packets) == 132 and all(len(p) == 16 for p in packets)


def binary_rank(values):
    basis = {}
    for value in values:
        v = int.from_bytes(value, "big") if isinstance(value, bytes) else value
        while v:
            b = v.bit_length() - 1
            if b not in basis:
                basis[b] = v
                break
            v ^= basis[b]
    return len(basis)


def multiply(a, b):
    out = 0
    for _ in range(8):
        if b & 1:
            out ^= a
        a <<= 1
        if a & 256:
            a ^= 0x11B
        b >>= 1
    return out


def power(v, p):
    out = 1
    while p:
        if p & 1:
            out = multiply(out, v)
        v = multiply(v, v)
        p >>= 1
    return out


def byte_rank(values):
    matrix = [list(row) for row in values]
    r = 0
    for column in range(16):
        pivot = next((i for i in range(r, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[r], matrix[pivot] = matrix[pivot], matrix[r]
        inv = power(matrix[r][column], 254)
        matrix[r] = [multiply(x, inv) for x in matrix[r]]
        for i in range(len(matrix)):
            if i != r and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = [a ^ multiply(factor, b)
                             for a, b in zip(matrix[i], matrix[r])]
        r += 1
        if r == 16:
            break
    return r


# Independent synthetic parity-code tests.
rng = Random(20261102)
parity_data = []
binary_parity_data = []
for _ in range(200):
    values = [rng.randrange(256) for _ in range(14)]
    parity_data.append(values + [values[0] ^ values[1], values[2] ^ values[3]])
    v = rng.getrandbits(127)
    binary_parity_data.append(v << 1 | (v.bit_count() % 2))
assert byte_rank(parity_data) == 14
assert binary_rank(binary_parity_data) == 127

centered = [bytes(a ^ b for a, b in zip(p, packets[0]))
            for p in packets[1:]]
observed = {
    "intact_original_packet_count": len(packets),
    "gf256_linear_rank": byte_rank(packets),
    "gf256_affine_rank": byte_rank(centered),
    "gf2_linear_rank": binary_rank(packets),
    "gf2_affine_rank": binary_rank(centered),
    "synthetic_gf256_parity_positive_rank": 14,
    "synthetic_gf2_parity_positive_rank": 127,
}
assert observed["gf256_affine_rank"] == 16
assert observed["gf2_affine_rank"] == 128
print(json.dumps(observed, indent=2))
