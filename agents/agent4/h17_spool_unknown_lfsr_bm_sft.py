"""H17 source-first Berlekamp–Massey test of a common unknown-order printer LFSR.
Read-only; no selected ESC-N coupon is used. Agent4, 5 November 2026.
"""
from pathlib import Path
from hashlib import sha256
import os
import random
import re

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
src = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert sha256(src).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
lines = [line for line in src.decode().splitlines() if "PAYLOAD=" in line]
assert len(lines) == 133
assert all("STATE=ACK" in line and f"JOB=PS-261003-{300+i:04d}" in line
           for i, line in enumerate(lines[:128]))
packets = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1))
           for line in lines[:128]]

def berlekamp_massey(bits):
    polynomial = prior = 1
    degree = 0
    last_change = -1
    previous_bits = 0
    for index, bit in enumerate(bits):
        previous_bits = (previous_bits << 1) | bit
        if ((previous_bits & polynomial).bit_count() & 1) == 0:
            continue
        old = polynomial
        polynomial ^= prior << (index - last_change)
        if 2 * degree <= index:
            degree = index + 1 - degree
            prior = old
            last_change = index
    return degree, polynomial

def bit_sequence(blocks, forward_bytes, msb_first):
    for packet in blocks:
        for byte in (packet if forward_bytes else packet[::-1]):
            for position in (range(7, -1, -1) if msb_first else range(8)):
                yield (byte >> position) & 1

def predict(polynomial, training, length):
    history = 0
    for bit in training:
        history = (history << 1) | bit
    for _ in range(length):
        next_bit = ((polynomial >> 1) & history).bit_count() & 1
        yield next_bit
        history = (history << 1) | next_bit

# True arbitrary nontrivial 127-bit additive LFSR with a full independent
# holdout. A fixed-polynomial/seed brute-force test is not used.
rng = random.Random(0xA481)
original_polynomial = (1 << 127) | (1 << 1) | 1
synthetic = [rng.getrandbits(1) for _ in range(127)]
for _ in range(3000):
    history = 0
    for bit in synthetic[-127:]:
        history = (history << 1) | bit
    synthetic.append(((original_polynomial >> 1) & history).bit_count() & 1)
known_degree, known_polynomial = berlekamp_massey(synthetic[:600])
assert known_degree == 127
assert list(predict(known_polynomial, synthetic[:600], len(synthetic) - 600)) == synthetic[600:]
print("POSITIVE seeded LFSR degree", known_degree, "full unseen bits recovered", len(synthetic)-600)

# Source-only: all 16,384 original bits are copied intact from 128 retained
# ordinary ACKs. No selected K04, desk phrase or acceptance hash is read.
for forward in (True, False):
    for msb in (True, False):
        bits = list(bit_sequence(packets, forward, msb))
        assert len(bits) == 16384
        degree, polynomial = berlekamp_massey(bits)
        train = bits[:12800]  # 100 source packets
        heldout = bits[12800:]  # 28 genuine subsequent packets
        train_degree, train_poly = berlekamp_massey(train)
        errors = sum(a != b for a, b in zip(heldout,
                      predict(train_poly, train, len(heldout))))
        assert (degree, train_degree, errors) == {
            (True, True): (8192, 6401, 1781),
            (True, False): (8192, 6401, 1830),
            (False, True): (8192, 6399, 1780),
            (False, False): (8194, 6399, 1831),
        }[(forward, msb)]
        print("ORIGINAL", "forward" if forward else "reverse_bytes",
              "MSB" if msb else "LSB", "minimum_binary_recurrence_order", degree,
              "first100_packet_model_degree", train_degree,
              "next28_packet_bit_errors", errors, "of", len(heldout))
print("NO_SHARED_SHORT_LFSR original K04/K08 remain missing")
