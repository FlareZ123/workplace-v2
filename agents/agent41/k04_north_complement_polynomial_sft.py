"""H17 K04: finite North ticket-complement five-packet polynomial hypothesis.
The proposed ST -> PS map is structural only; no historical issuer is asserted.
Pure-Python read-only SFT. From repository: python agents/agent41/k04_north_complement_polynomial_sft.py
"""
from pathlib import Path
from functools import lru_cache
import hashlib
import os
import re

root = Path(os.environ["H17_SOURCE_ROOT"]) if "H17_SOURCE_ROOT" in os.environ else Path(__file__).resolve().parents[2] / "resources"
spool = root / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(spool.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = {}
for line in spool.read_text().splitlines():
    m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=ACK CLASS=(\w+) PAYLOAD=([0-9A-F]{32})", line)
    if m:
        job, attempt, label, payload = m.groups()
        if attempt == "1":
            rows[int(job)] = (label, bytes.fromhex(payload))
tickets = [94, 81, 106, 99, 112]
jobs = [417 - number for number in tickets]
assert jobs == [323, 336, 311, 318, 305]
packets = [rows[job][1] for job in jobs]
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
goal = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def multiply(a, b, degree, polynomial):
    result = 0
    top = 1 << degree
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= polynomial
    return result

@lru_cache(maxsize=None)
def power(a, exponent, degree, polynomial):
    result = 1
    while exponent:
        if exponent & 1:
            result = multiply(result, a, degree, polynomial)
        a = multiply(a, a, degree, polynomial)
        exponent //= 2
    return result

def interpolate(coordinates, values, target, degree, polynomial):
    result = 0
    for i in range(len(coordinates)):
        weight = 1
        for j in range(len(coordinates)):
            if i == j:
                continue
            denominator = coordinates[i] ^ coordinates[j]
            assert denominator
            inverse = power(denominator, (1 << degree) - 2, degree, polynomial)
            weight = multiply(weight, multiply(target ^ coordinates[j], inverse, degree, polynomial), degree, polynomial)
        result ^= multiply(values[i], weight, degree, polynomial)
    return result

for degree, polynomial in ((8, 0x11B), (8, 0x11D), (128, (1 << 128) | 0x87)):
    for coefficients in ((1, 2, 3, 4), (11, 7, 3, 5, 13)):
        def polynomial_value(x):
            result, exponent = 0, 1
            for coefficient in coefficients:
                result ^= multiply(coefficient, exponent, degree, polynomial)
                exponent = multiply(exponent, x, degree, polynomial)
            return result
        controls = list(range(1, len(coefficients) + 2))
        actual = [polynomial_value(x) for x in controls]
        assert interpolate(controls[:-1], actual[:-1], controls[-1], degree, polynomial) == actual[-1]
print("Synthetic degree-3 withheld and degree-4 next-object controls: 6/6 PASS")

checks = 0
holdout_hits = 0
target_hits = []
models = 0
for name, coordinates, target in (
    ("ticket", tickets, 0),
    ("job", jobs, 417),
    ("ordinal", [1, 2, 3, 4, 5], 6),
):
    for degree, polynomial in ((8, 0x11B), (8, 0x11D), (128, (1 << 128) | 0x87)):
        coords = [x & ((1 << degree) - 1) for x in coordinates]
        target &= (1 << degree) - 1
        lanes = 16 if degree == 8 else 1
        serialize = lambda values: bytes(values) if degree == 8 else values[0].to_bytes(16, "big")
        def values_for(items, lane):
            return [item[lane] if degree == 8 else int.from_bytes(item, "big") for item in items]
        for missing in range(5):
            train_coords = [x for j, x in enumerate(coords) if j != missing]
            train_rows = [packet for j, packet in enumerate(packets) if j != missing]
            predicted = serialize([
                interpolate(train_coords, values_for(train_rows, lane), coords[missing], degree, polynomial)
                for lane in range(lanes)
            ])
            holdout_hits += predicted == packets[missing]
        candidate = serialize([
            interpolate(coords, values_for(packets, lane), target, degree, polynomial)
            for lane in range(lanes)
        ])
        models += 1
        print(f"{name} / {hex(polynomial)}: predicted complete physical coupon {candidate.hex().upper()}")
        for coupon in (candidate, candidate[::-1]):
            for component in (coupon, bytes(a ^ b for a, b in zip(coupon, mask))):
                checks += 1
                if hashlib.sha256(component).hexdigest() == goal:
                    target_hits.append((name, hex(polynomial), coupon.hex(), component.hex()))
assert models == 9 and checks == 36
print(f"Models={models}, original complete withheld packets={5*models}, exact withheld={holdout_hits}, original full K04 hash checks={checks}, hits={target_hits}")
