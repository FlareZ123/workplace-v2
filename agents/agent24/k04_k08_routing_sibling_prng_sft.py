"""Source-only H-17 source-pair PRNG test: K04 route mask versus K08 desk nonce.
Uses no printer coupon, acceptance commitments, verifier, or selected packet.
Python 3 standard library; override H17_RESOURCE_ROOT for extracted evidence.
"""
import hashlib
import itertools
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources/evidence")))
PIN = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
U32 = (1 << 32) - 1
U64 = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
M1 = 0xBF58476D1CE4E5B9
M2 = 0x94D049BB133111EB
XM = 2685821657736338717
A, C = 6364136223846793005, 1442695040888963407

def words(data, little, reverse):
    v = tuple(int.from_bytes(data[i:i + 4], "little" if little else "big")
              for i in (0, 4, 8, 12))
    return v[::-1] if reverse else v

def bytes4(v):
    return b"".join(x.to_bytes(4, "big") for x in v)

def unright(y, n, width):
    x = y
    for _ in range(8):
        x = y ^ (x >> n)
    return x & ((1 << width) - 1)

def unleft(y, n, width):
    x = y
    for _ in range(8):
        x = y ^ ((x << n) & ((1 << width) - 1))
    return x & ((1 << width) - 1)

def forward(s):
    a, b, c, d = s
    t = a ^ ((a << 11) & U32)
    return b, c, d, (d ^ (d >> 19) ^ t ^ (t >> 8)) & U32

def backward(s):
    a, b, c, d = s
    t = d ^ c ^ (c >> 19)
    return unleft(unright(t, 8, 32), 11, 32), a, b, c

def probe(mask, nonce, steps=200000):
    target = {words(nonce, le, reverse) for le in (0, 1)
              for reverse in (False, True)}
    hits = []
    checked = 0
    for le, reverse, direction in itertools.product(
            (0, 1), (False, True), (-1, 1)):
        s = words(mask, le, reverse)
        ring = [0] * 4
        for index in range(steps):
            s = forward(s) if direction == 1 else backward(s)
            ring[index % 4] = s[3] if direction == 1 else s[0]
            if index < 3:
                continue
            candidate = tuple(
                ring[(index - 3 + k) % 4] if direction == 1
                else ring[(index - k) % 4] for k in range(4))
            checked += 4
            if candidate in target:
                hits.append((le, reverse, direction, index))
    return checked, hits

def smix(x):
    x = ((x ^ (x >> 30)) * M1) & U64
    x = ((x ^ (x >> 27)) * M2) & U64
    return (x ^ (x >> 31)) & U64

def next64(label, output):
    if label == "splitmix":
        x = unright(output, 31, 64) * pow(M2, -1, 1 << 64) & U64
        x = unright(x, 27, 64) * pow(M1, -1, 1 << 64) & U64
        x = unright(x, 30, 64)
        return smix((x + GAMMA) & U64)
    if label == "xorshift64star":
        x = output * pow(XM, -1, 1 << 64) & U64
        x ^= x >> 12
        x ^= (x << 25) & U64
        x ^= x >> 27
        return x * XM & U64
    return (output * A + C) & U64

def pair64(data, reverse, swap, little):
    halves = [data[:8], data[8:]]
    if reverse:
        halves.reverse()
    if swap:
        halves = [h[4:] + h[:4] for h in halves]
    return tuple(int.from_bytes(h, "little" if little else "big") for h in halves)

def control():
    state = (0x829117AB, 0x5461CDAE, 0x08FBEE92, 0x17A7E089)
    first = []
    for _ in range(4):
        state = forward(state)
        first.append(state[3])
    for _ in range(57):
        state = forward(state)
    second = []
    for _ in range(4):
        state = forward(state)
        second.append(state[3])
    a, b = bytes4(first), bytes4(second)
    checks, hits = probe(a, b)
    assert checks == 6399904 and any(v[2:] == (1, 60) for v in hits)
    checks, hits = probe(b, a)
    assert checks == 6399904 and any(v[2:] == (-1, 60) for v in hits)
    for state in ((0, 1, 2, 3), (U32, 0, 12345, 76543)):
        assert backward(forward(state)) == state
        assert forward(backward(state)) == state
    for label in ("splitmix", "xorshift64star", "lcg64"):
        for seed in (0, 1, 0xDEADBEEFABCDEF23, U64):
            a = smix(seed) if label == "splitmix" else (
                seed * XM & U64 if label == "xorshift64star" else seed)
            b = next64(label, a)
            assert next64(label, pair64(
                a.to_bytes(8, "big") + b.to_bytes(8, "big"), False, False, False)[0]) == b
    print("PLANTED PASS: bidirectional 16byte source-pair donor, gap 57; 3 native 64bit producers")

def main():
    control()
    raw = (ROOT / "recovery-routing.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    info = json.loads(raw)
    mask = bytes.fromhex(info["K04"]["masked_component"])
    nonce = bytes.fromhex(info["K08"]["desk_nonce"])
    for label in ("splitmix", "xorshift64star", "lcg64"):
        matches = sum(next64(label, pair64(mask, r, w, le)[0])
                      == pair64(mask, r, w, le)[1]
                      for r, w, le in itertools.product((False, True), repeat=3))
        assert matches == 0
        print("ORIGINAL MASK HALF-PAIR:", label, "0/8 whole-source matches")
    checks, hits = probe(mask, nonce)
    assert checks == 6399904 and not hits
    print("SOURCE_PIN_PASS, xorshift128 6,399,904 full heldout nonce checks, 0 original matches")
    print("No K04 physical coupon bits or K08 author-final words recovered")

if __name__ == "__main__":
    main()
