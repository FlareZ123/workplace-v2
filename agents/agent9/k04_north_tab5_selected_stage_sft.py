"""North L-29/N five-tab print-source reconstruction, standard-library SFT.

Run from workplace-v2 root. Does not read or trust the copied 18:02 ACK2 coupon.
"""
import hashlib
import json
import random
import re
from pathlib import Path

E = Path("resources/evidence")
PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "h17-supplemental-office-files/print-fleet-retirement-note.txt": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
JOBS = (399, 386, 411, 404, 417)
TICKETS = (94, 81, 106, 99, 112)
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def mul(a, b, bits, modulus):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & (1 << bits):
            a ^= modulus
    return out


def power(a, n, bits, modulus):
    result = 1
    while n:
        if n & 1:
            result = mul(result, a, bits, modulus)
        a = mul(a, a, bits, modulus)
        n >>= 1
    return result


def interpolate(xs, values, dest, bits, modulus):
    assert len(xs) == len(values) and len(set(xs + (dest,))) == len(xs) + 1
    out = 0
    for i, xi in enumerate(xs):
        num = den = 1
        for j, xj in enumerate(xs):
            if i != j:
                num = mul(num, dest ^ xj, bits, modulus)
                den = mul(den, xi ^ xj, bits, modulus)
        weight = mul(num, power(den, (1 << bits) - 2, bits, modulus), bits, modulus)
        out ^= mul(values[i], weight, bits, modulus)
    return out


def coupon(xs, packets, dest, bits, poly, endian):
    if bits == 128:
        words = tuple(int.from_bytes(p, endian) for p in packets)
        return interpolate(xs, words, dest, bits, poly).to_bytes(16, endian)
    return bytes(interpolate(xs, tuple(p[i] for p in packets), dest, bits, poly)
                 for i in range(16))


def controls():
    rng = random.Random(20261109)
    fields = ((8, 0x11B, "big"), (8, 0x11D, "big"),
              (128, (1 << 128) | 0x87, "big"), (128, (1 << 128) | 0x87, "little"))
    xs = (1, 2, 3, 4, 5)
    for bits, poly, endian in fields:
        coeffs = [[rng.getrandbits(bits) for _ in range(5)]
                  for _ in range(16 if bits == 8 else 1)]
        def make(x, degree=4):
            lanes = []
            for lane in coeffs:
                value = 0
                for coefficient in reversed(lane[:degree + 1]):
                    value = mul(value, x, bits, poly) ^ coefficient
                lanes.append(value)
            return bytes(lanes) if bits == 8 else lanes[0].to_bytes(16, endian)
        samples = tuple(make(x) for x in xs)
        restored = coupon(xs, samples, 6, bits, poly, endian)
        assert restored == make(6)
        assert hashlib.sha256(bytes(a ^ b for a, b in zip(restored, MASK))).digest() == hashlib.sha256(
            bytes(a ^ b for a, b in zip(make(6), MASK))).digest()
        cubic = tuple(make(x, degree=3) for x in xs)
        for i in range(5):
            left = xs[:i] + xs[i + 1:]
            known = cubic[:i] + cubic[i + 1:]
            assert coupon(left, known, xs[i], bits, poly, endian) == cubic[i]


def main():
    for path, sha in PINS.items():
        assert hashlib.sha256((E / path).read_bytes()).hexdigest() == sha, path
    acceptance = Path("resources/acceptance.json")
    assert hashlib.sha256(acceptance.read_bytes()).hexdigest() == (
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f")
    assert json.loads(acceptance.read_text())["slot_sha256"]["K04"] == TARGET
    assert bytes.fromhex(json.loads((E / "recovery-routing.json").read_text())["K04"]["masked_component"]) == MASK
    rows = (E / "print/spool-reconstruction.log").read_text().splitlines()
    packets = []
    for job in JOBS:
        selected = [s for s in rows if f"JOB=PS-261003-{job:04d} " in s
                    and "ATTEMPT=1 STATE=ACK" in s]
        assert len(selected) == 1, job
        packets.append(bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1)))
    packets = tuple(packets)
    assert packets[-1] == bytes.fromhex("E1E60D5F6B6DD2225FA6D5A2A63AD932")
    assert len([s for s in rows if "JOB=PS-261003-0417 " in s
                and "ATTEMPT=2 STATE=ACK" in s]) == 1
    controls()

    forms = (
        ("tab", (1, 2, 3, 4, 5), 6),
        ("ticket", TICKETS, 113),
        ("job", JOBS, 418),
        ("minute", (915, 850, 975, 940, 1005), 1082),
    )
    fields = ((8, 0x11B, "big"), (8, 0x11D, "big"),
              (128, (1 << 128) | 0x87, "big"), (128, (1 << 128) | 0x87, "little"))
    holdouts = successes = 0
    candidates4, candidates5, hits = set(), set(), []
    for name, coordinates, destination in forms:
        for bits, poly, endian in fields:
            xs = tuple(x % (1 << bits) for x in coordinates)
            target_x = destination % (1 << bits)
            assert len(set(xs + (target_x,))) == 6
            for i in range(5):
                others = xs[:i] + xs[i + 1:]
                values = packets[:i] + packets[i + 1:]
                predicted = coupon(others, values, xs[i], bits, poly, endian)
                successes += predicted == packets[i]
                holdouts += 1
            for group, raw in (
                (candidates4, coupon(xs[:4], packets[:4], xs[4], bits, poly, endian)),
                (candidates5, coupon(xs, packets, target_x, bits, poly, endian)),
            ):
                for view in (raw, raw[::-1]):
                    component = bytes(a ^ b for a, b in zip(view, MASK))
                    group.add(component)
                    if hashlib.sha256(component).hexdigest() == TARGET:
                        hits.append((name, bits, hex(poly), endian, component.hex().upper()))
    result = {
        "jobs": JOBS, "ticket_tab_order": TICKETS,
        "historical_whole_packet_holdouts": holdouts,
        "historical_whole_packet_predictions_correct": successes,
        "distinct_four_to_five_candidates": len(candidates4),
        "distinct_five_to_six_candidates": len(candidates5),
        "original_K04_hits": hits, "synthetic_full_coupon_controls": 4,
    }
    print(json.dumps(result, indent=2))
    assert holdouts == 80 and successes == 0
    assert len(candidates4) == len(candidates5) == 32 and not hits


if __name__ == "__main__":
    main()
