"""Role-matched ACK2-only reverse xoroshiro128** K04 pilot.

Use only original 0420 ATTEMPT=2 RECOVER ACK payload to reconstruct a
possible preceding selected 0417 ACK2 coupon. Withhold the disputed 0417
copied bytes entirely. Check exact original K04 commitment; inspect separate
RECOVER/ACK/bench source controls. Requires only standard-library Python.
"""
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
assert sha256(SPOOL.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(acceptance["slot_sha256"]["K04"])

records = []
for line in SPOOL.read_text().splitlines():
    if not line.startswith("2026-"):
        continue
    match = re.fullmatch(
        r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) "
        r"CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)", line
    )
    assert match, line
    t, job, attempt, state, cls, value, dest = match.groups()
    records.append((t, job, int(attempt), state, cls, bytes.fromhex(value), dest))
assert len(records) == 133
ack2 = [r for r in records if r[2] == 2 and r[3:5] == ("ACK", "RECOVER")]
assert len(ack2) == 2
assert {r[1] for r in ack2} == {"PS-261003-0417", "PS-261003-0420"}
source = next(r for r in ack2 if r[1] == "PS-261003-0420")[5]
assert source.hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
assert next(r for r in ack2 if r[1] == "PS-261003-0417")[0] == "2026-10-03T18:02:00Z"
# Deliberately never inspect selected record's payload.

U64 = (1 << 64) - 1
INV5 = pow(5, -1, 1 << 64)
INV9 = pow(9, -1, 1 << 64)

def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & U64

def ror(x, n):
    return ((x >> n) | (x << (64 - n))) & U64

def emit(s):
    return (rol((s[0] * 5) & U64, 7) * 9) & U64

def next_state(s):
    a, b = s
    b ^= a
    return ((rol(a, 24) ^ b ^ (b << 16)) & U64, rol(b, 37))

def prev_state(s):
    a_next, b_next = s
    b = ror(b_next, 37)
    a = ror((a_next ^ b ^ (b << 16)) & U64, 24)
    return (a, b ^ a)

def state_from_outputs(first, second):
    a = (ror(first * INV9 & U64, 7) * INV5) & U64
    a_next = (ror(second * INV9 & U64, 7) * INV5) & U64
    u = a_next ^ rol(a, 24)
    b_xor_a = (u ^ (u << 16) ^ (u << 32) ^ (u << 48)) & U64
    s = (a, b_xor_a ^ a)
    assert emit(s) == first and emit(next_state(s)) == second
    assert prev_state(next_state(s)) == s
    return s

VIEWS = [(endian, order) for endian in ("little", "big") for order in (0, 1)]

def decode(packet, view):
    endian, reverse = view
    chunks = [packet[:8], packet[8:]]
    if reverse:
        chunks.reverse()
    return tuple(int.from_bytes(c, endian) for c in chunks)

def encode(words, view):
    endian, reverse = view
    if reverse:
        words = tuple(reversed(words))
    return b"".join(w.to_bytes(8, endian) for w in words)

def reduce_coupon(coupon):
    return bytes(a ^ b for a, b in zip(coupon, mask))

# Independent seeded synthetic control on both source inversion and original
# source-to-component reduction. The expected coupon is never an original.
synthetic = (0x1234567887654321, 0xAFFEEBABECAFEE11)
future = next_state(next_state(synthetic))
for view in VIEWS:
    packet = encode((emit(future), emit(next_state(future))), view)
    got = state_from_outputs(*decode(packet, view))
    assert prev_state(prev_state(got)) == synthetic
    expected = encode((emit(synthetic), emit(next_state(synthetic))), view)
    earlier = prev_state(prev_state(got))
    reconstructed = encode((emit(earlier), emit(next_state(earlier))), view)
    assert reconstructed == expected
    assert sha256(reduce_coupon(reconstructed)).digest() == sha256(reduce_coupon(expected)).digest()
print("SYNTHETIC_ACK2_BACKWARD_AND_MASKED_COMMITMENT: PASS")

controls = {
    r[5]: r[1] for r in records
    if r[3:5] == ("ACK", "RECOVER") and r[6] == "bench"
    and r[1] != "PS-261003-0417"
}
rows = []
for source_view in VIEWS:
    state = state_from_outputs(*decode(source, source_view))
    next_word = emit(state)
    match_count = 0
    matched_controls = []
    for distance in range(1, 100001):
        state = prev_state(state)
        earlier_word = emit(state)
        if distance >= 2:
            for coupon_view in VIEWS:
                coupon = encode((earlier_word, next_word), coupon_view)
                if coupon in controls:
                    matched_controls.append((distance, coupon_view, controls[coupon]))
                component = reduce_coupon(coupon)
                if sha256(component).digest() == target:
                    print("K04 PASS", source_view, distance, coupon_view, component.hex().upper())
                    match_count += 1
        next_word = earlier_word
    rows.append({
        "source_view": source_view,
        "candidates": 399996,
        "k04_hits": match_count,
        "other_original_bench_recover_ack_matches": matched_controls,
    })
print(json.dumps({"test": "reverse-ack2-only", "source_job": "PS-261003-0420", "results": rows}, indent=2))
assert all(row["k04_hits"] == 0 for row in rows)
