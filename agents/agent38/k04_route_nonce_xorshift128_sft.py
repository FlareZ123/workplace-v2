"""H-17: K04 route-mask / K08 desk-nonce seeded xorshift128 producer.

Exploratory shared-token PRNG channel (not historically asserted). The two
original constant tokens form possible 128-bit initial states; their forward
and inverse Marsaglia xorshift128 state trajectories yield complete K04
candidate coupons and possible intact printer packet positive controls.
The original selected ACK2 is excluded from producer calibration.
"""
from hashlib import sha256
from pathlib import Path
import json
import re
import sys
from zipfile import ZipFile

U32 = (1 << 32) - 1
MAX_STEPS = 8192
SP_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def fetch(path):
    if len(sys.argv) > 1:
        with ZipFile(sys.argv[1]) as z:
            return z.read(path)
    return (Path(__file__).resolve().parents[2] / "resources" / path).read_bytes()

def left_unxor(v, n):
    x = v
    for k in range(1, 32 // n + 2):
        x ^= (v << (n * k)) & U32
    return x & U32

def right_unxor(v, n):
    x = v
    for k in range(1, 32 // n + 2):
        x ^= v >> (n * k)
    return x & U32

def forward(v):
    a, b, c, d = v
    t = (a ^ ((a << 11) & U32)) & U32
    return (b, c, d, (d ^ (d >> 19) ^ t ^ (t >> 8)) & U32)

def backward(v):
    b, c, d, e = v
    t = right_unxor(e ^ d ^ (d >> 19), 8)
    a = left_unxor(t, 11)
    return (a, b, c, d)

def state_bytes(v, endian, reverse):
    words = v[::-1] if reverse else v
    return b"".join(x.to_bytes(4, endian) for x in words)

def parse_state(value, endian, reverse):
    out = tuple(int.from_bytes(value[i:i+4], endian) for i in range(0, 16, 4))
    return out[::-1] if reverse else out

def stream_bytes(state, endian, reverse):
    words = []
    for _ in range(4):
        state = forward(state)
        words.append(state[3])
    return state_bytes(tuple(words), endian, reverse)

def scan(inputs, mask, target, intact, planted_digest):
    count, planted, target_hits, intact_hits = 0, [], [], []
    for label, token in inputs.items():
        for endian in ("big", "little"):
            for reverse in (False, True):
                seed = parse_state(token, endian, reverse)
                for direction, update in (("forward", forward), ("backward", backward)):
                    state = seed
                    for step in range(MAX_STEPS + 1):
                        for codec, coupon in (("state", state_bytes(state, endian, reverse)),
                                              ("four_outputs", stream_bytes(state, endian, reverse))):
                            count += 1
                            component = bytes(x ^ y for x, y in zip(coupon, mask))
                            digest = sha256(component).digest()
                            if digest == target:
                                target_hits.append((label, endian, reverse, direction, step, codec, component.hex().upper()))
                            if digest == planted_digest:
                                planted.append((label, endian, reverse, direction, step, codec))
                            if coupon in intact:
                                intact_hits.append((label, endian, reverse, direction, step, codec))
                        state = update(state)
    return count, planted, target_hits, intact_hits

raw = fetch("evidence/print/spool-reconstruction.log")
assert sha256(raw).hexdigest() == SP_SHA
packet_hex = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
assert len(packet_hex) == 133
intact = {bytes.fromhex(x.decode()) for i,x in enumerate(packet_hex) if i != 129}
assert len(intact) == 132
routing = json.loads(fetch("evidence/recovery-routing.json"))
accepted = json.loads(fetch("acceptance.json"))
mask = bytes.fromhex(routing["K04"]["masked_component"])
nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
assert len(mask) == len(nonce) == 16
inputs = {"K04_MASK":mask, "K08_NONCE":nonce}
original = bytes.fromhex(accepted["slot_sha256"]["K04"])
# Genuine positive with disjoint source seed and nonzero forward step;
# the scan must reconstruct the full masked component exactly.
seed = parse_state(nonce, "little", True)
for _ in range(137):
    seed = forward(seed)
planted_coupon = state_bytes(seed,"little",True)
planted_digest = sha256(bytes(x ^ y for x,y in zip(planted_coupon,mask))).digest()
assert planted_digest != original
for v in ((0,0,0,1),(0x12345678,0x9abcdef0,0x10203040,0xfedcba98), (U32,U32,U32,U32)):
    assert backward(forward(v)) == v and forward(backward(v)) == v
count, planted, hits, source_matches = scan(inputs,mask,original,intact,planted_digest)
assert ("K08_NONCE","little",True,"forward",137,"state") in planted
assert count == 2 * 2 * 2 * 2 * (MAX_STEPS + 1) * 2
print(json.dumps({"source_sha256":SP_SHA, "route_sources":list(inputs),
                  "states_and_fourword_emissions_evaluated":count,
                  "planted_exact_full_coupon_positive":len(planted),
                  "original_K04_commitment_hits":hits,
                  "original_intact_printer_packet_matches":source_matches},indent=2))
