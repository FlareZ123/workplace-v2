"""SFT: original same-job payloads as 128-bit PRNG state snapshots.

Hypothetical 18:01 REQUESTED1 and 18:03 REQUESTED3 frames are snapshots
of a standard 128-bit linear state transition, with 1..256 state advances
in between. If they share a producer, an intermediate state may predict
the absent authentic ACK2. Test source-to-source first, then 20 complete
hypothetical one-transition coupons against the original K04 commitment.
No original file is changed.
"""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U32 = (1 << 32) - 1
U64 = (1 << 64) - 1

def rol(x, n, width):
    mask = (1 << width) - 1
    return ((x << n) | (x >> (width - n))) & mask

def next_state(state, kind):
    if kind == "xoshiro128":
        a, b, c, d = state
        t = (b << 9) & U32
        c ^= a
        d ^= b
        b ^= c
        a ^= d
        c ^= t
        return a, b, c, rol(d, 11, 32)
    if kind == "xorshift128":
        a, b, c, d = state
        t = (a ^ ((a << 11) & U32)) & U32
        return b, c, d, (d ^ (d >> 19) ^ t ^ (t >> 8)) & U32
    if kind in ("xoroshiro128", "xoroshiro128_old"):
        a, b = state
        b ^= a
        rot, shift, lastrot = ((24, 16, 37) if kind == "xoroshiro128"
                               else (55, 14, 36))
        return rol(a, rot, 64) ^ b ^ ((b << shift) & U64), rol(b, lastrot, 64)
    if kind == "xorshift128plus":
        a, b = state
        old_a = a
        a = b
        old_a ^= (old_a << 23) & U64
        old_a ^= old_a >> 17
        old_a ^= b
        old_a ^= b >> 26
        return a, old_a & U64
    raise ValueError(kind)

def read_same_job():
    original = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA
    rows = {}
    for line in original.decode("ascii").splitlines():
        if "JOB=PS-261003-0417 " not in line or "CLASS=RECOVER " not in line:
            continue
        fields = dict(field.split("=", 1) for field in line.split() if "=" in field)
        rows[int(fields["ATTEMPT"])] = (fields["STATE"], bytes.fromhex(fields["PAYLOAD"]))
    assert set(rows) == {1, 2, 3}
    assert rows[1][0] == rows[3][0] == "REQUESTED" and rows[2][0] == "ACK"
    return rows[1][1], rows[3][1]

def unpack(raw, width, endian, reverse):
    chunk = width // 8
    values = tuple(int.from_bytes(raw[i:i + chunk], endian)
                   for i in range(0, 16, chunk))
    return values[::-1] if reverse else values

def pack(values, width, endian, reverse):
    if reverse:
        values = values[::-1]
    return b"".join(value.to_bytes(width // 8, endian) for value in values)

def main():
    specs = [("xoshiro128", 32), ("xorshift128", 32),
             ("xoroshiro128", 64), ("xoroshiro128_old", 64),
             ("xorshift128plus", 64)]
    for kind, width in specs:
        seed = ((1, 3, 5, 7) if width == 32
                else (0x123456789ABCDEF, 0xFEDCBA9876543210))
        third = next_state(next_state(seed, kind), kind)
        assert third != seed
        assert next_state(next_state(seed, kind), kind) == third
    print("PASS synthetic two-stage recovery")
    p1, p3 = read_same_job()
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    accepted = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = accepted["slot_sha256"]["K04"]
    pairs, source_hits, target_hits = 0, [], []
    for kind, width in specs:
        for endian, reverse in itertools.product(("little", "big"), (False, True)):
            initial = unpack(p1, width, endian, reverse)
            final = unpack(p3, width, endian, reverse)
            predicted = pack(next_state(initial, kind), width, endian, reverse)
            component = bytes(x ^ y for x, y in zip(predicted, mask))
            if hashlib.sha256(component).hexdigest() == target:
                target_hits.append((kind, endian, reverse, component.hex().upper()))
            current = initial
            for gap in range(1, 257):
                current = next_state(current, kind)
                pairs += 1
                if current == final:
                    source_hits.append((kind, endian, reverse, gap))
    assert pairs == 5120
    assert not source_hits and not target_hits
    print("state transitions:", pairs, "P1-to-P3 matches:", source_hits)
    print("20 complete one-step candidate K04 components:", target_hits)
    print("Historical stage law: UNATTESTED")


if __name__ == "__main__":
    main()
