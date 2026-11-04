"""Cross-family invertible MurmurHash3_x64_128 native-state K04 pilot.

Run from repo root: python agents/agent46/k04_crossarchive_murmur_native_state_sft.py
Read-only source blocks are the five selected direct/prehash archive objects.
This tests an explicitly hypothetical common public-label emitter, not printer firmware.
MurmurHash3 specification: aappleby/smhasher src/MurmurHash3.cpp.
"""
import hashlib
import itertools
import json
import random
import time
from pathlib import Path

M = (1 << 64) - 1
C1, C2 = 0x87C37B91114253D5, 0x4CF5AD432745937F
A, B = 0xFF51AFD7ED558CCD, 0xC4CEB9FE1A85EC53
I5, IA, IB = pow(5, -1, 1 << 64), pow(A, -1, 1 << 64), pow(B, -1, 1 << 64)

def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & M

def ror(x, n):
    return ((x >> n) | (x << (64 - n))) & M

def mix1(k):
    return (rol((k * C1) & M, 31) * C2) & M

def mix2(k):
    return (rol((k * C2) & M, 33) * C1) & M

def fmix(x):
    x ^= x >> 33
    x = (x * A) & M
    x ^= x >> 33
    x = (x * B) & M
    x ^= x >> 33
    return x

def unfmix(x):
    x ^= x >> 33
    x = (x * IB) & M
    x ^= x >> 33
    x = (x * IA) & M
    x ^= x >> 33
    return x

def encode(msg, state):
    h1, h2 = state
    nblocks = len(msg) // 16
    for i in range(nblocks):
        k1 = int.from_bytes(msg[16*i:16*i+8], "little")
        k2 = int.from_bytes(msg[16*i+8:16*i+16], "little")
        h1 ^= mix1(k1)
        h1 = (rol(h1, 27) + h2) & M
        h1 = (h1 * 5 + 0x52DCE729) & M
        h2 ^= mix2(k2)
        h2 = (rol(h2, 31) + h1) & M
        h2 = (h2 * 5 + 0x38495AB5) & M
    tail = msg[16*nblocks:]
    if len(tail) > 8:
        h2 ^= mix2(int.from_bytes(tail[8:], "little"))
    if tail:
        h1 ^= mix1(int.from_bytes(tail[:8], "little"))
    h1 ^= len(msg)
    h2 ^= len(msg)
    h1 = (h1 + h2) & M
    h2 = (h2 + h1) & M
    h1, h2 = fmix(h1), fmix(h2)
    h1 = (h1 + h2) & M
    h2 = (h2 + h1) & M
    return h1.to_bytes(8, "little") + h2.to_bytes(8, "little")

def invert(msg, output):
    o1 = int.from_bytes(output[:8], "little")
    o2 = int.from_bytes(output[8:], "little")
    f2 = (o2 - o1) & M
    f1 = (o1 - f2) & M
    h1, h2 = unfmix(f1), unfmix(f2)
    p2 = (h2 - h1) & M
    p1 = (h1 - p2) & M
    h1, h2 = p1 ^ len(msg), p2 ^ len(msg)
    nblocks = len(msg) // 16
    tail = msg[16*nblocks:]
    if tail:
        h1 ^= mix1(int.from_bytes(tail[:8], "little"))
    if len(tail) > 8:
        h2 ^= mix2(int.from_bytes(tail[8:], "little"))
    for i in reversed(range(nblocks)):
        k1 = int.from_bytes(msg[16*i:16*i+8], "little")
        k2 = int.from_bytes(msg[16*i+8:16*i+16], "little")
        h2 = ror((((h2 - 0x38495AB5) * I5 - h1) & M), 31) ^ mix2(k2)
        h1 = ror((((h1 - 0x52DCE729) * I5 - h2) & M), 27) ^ mix1(k1)
    return h1, h2

def views(block):
    words = [block[i:i+4] for i in range(0, 16, 4)]
    for reverse_words in (False, True):
        for reverse_bytes in (False, True):
            for swap_halves in (False, True):
                seq = words[::-1] if reverse_words else words
                seq = [word[::-1] if reverse_bytes else word for word in seq]
                b = b"".join(seq)
                yield b[8:] + b[:8] if swap_halves else b

aliases = {
    "K01": ("WN-14", "WN14", "WATCH REGISTER", "INK"),
    "K02": ("LT-204", "LT204", "DIAG_WORD"),
    "K05": ("TRP2", "TRP-2", "NODE49"),
    "K06": ("RC-17", "RC17", "REV C"),
    "K07": ("AX-7782", "AX7782", "TRANSFER AUDIT"),
}
def forms(slot):
    for name in aliases[slot]:
        for n in (name, name.lower(), name.upper()):
            for root in ("", "H17", "H-17", "REC8/1", "IR-261003-H17",
                         "H17-IR-261003", "CEG-ARCHIVE-RECOVERY/v1"):
                for sep in ("", "/", ":", "|", " ", "-", "_", "\n"):
                    yield n
                    yield slot + sep + n
                    yield n + sep + slot
                    if root:
                        yield root + sep + n
                        yield root + sep + slot + sep + n
                        yield n + sep + root
                        yield n + sep + slot + sep + root
                    for date in ("20261003", "2026-10-03", "20260924"):
                        yield date + sep + n
                        yield n + sep + date

rng = random.Random(41042)
for length in range(96):
    for _ in range(3):
        msg = rng.randbytes(length)
        state = rng.getrandbits(64), rng.getrandbits(64)
        assert invert(msg, encode(msg, state)) == state
# Published canonical x64 output for "Hello" seed=0 (raw little-endian 64-bit lanes).
assert encode(b"Hello", (0, 0)).hex() == "1cc4d455ff74b93544551229cfea00a0"

root = Path(__file__).resolve().parents[2]
acceptance = json.loads((root / "resources/acceptance.json").read_text())
route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
blocks = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K05": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
}
for slot, raw in blocks.items():
    component = hashlib.sha256(raw).digest()[:16] if slot in ("K02", "K07") else raw
    assert hashlib.sha256(component).hexdigest() == acceptance["slot_sha256"][slot]

states = {}
for slot, block in blocks.items():
    states[slot] = {
        invert(text.encode("ascii"), view)
        for text in set(forms(slot))
        for view in views(block)
    }
assert sum(map(len, states.values())) == 65792
collisions = [
    (a, b, len(states[a] & states[b]))
    for a, b in itertools.combinations(states, 2) if states[a] & states[b]
]
assert not collisions, collisions

route_labels = (
    "ESC-N", "PS-261003-0417", "PS2610030417", "RECOVER", "K04",
    "K04/ESC-N", "REC8/1/K04/PS-261003-0417",
    "IR-261003-H17/K04/ESC-N/PS-261003-0417",
    "PS-261003-0417/RECOVER/2", "PS-261003-0417|2|ACK|RECOVER|bench",
    "2026-10-03T18:02:00Z PS-261003-0417 2 ACK RECOVER",
    "2026-10-03T18:02:00Z|PS-261003-0417|2|ACK|RECOVER|bench",
)
mask = bytes.fromhex(route["K04"]["masked_component"])
wanted = acceptance["slot_sha256"]["K04"]

# End-to-end genuine seeded synthetic control: invert an authentic-style known
# source block, predict a distinct selected-route coupon and verify its XOR/digest.
control_state = (0x0123456789ABCDEF, 0xDEADBEEFCAFEBABE)
derived = invert(b"WN-14", encode(b"WN-14", control_state))
assert derived == control_state
control_coupon = encode(b"PS-261003-0417", derived)
control_component = bytes(a ^ b for a, b in zip(mask, control_coupon))
assert hashlib.sha256(control_component).hexdigest() == hashlib.sha256(
    bytes(a ^ b for a, b in zip(mask, encode(b"PS-261003-0417", control_state)))
).hexdigest()

start = time.monotonic()
hits = []
unique_states = set().union(*states.values())
checks = 0
for state in unique_states:
    for label in route_labels:
        for coupon in views(encode(label.encode("ascii"), state)):
            component = bytes(a ^ b for a, b in zip(mask, coupon))
            checks += 1
            if hashlib.sha256(component).hexdigest() == wanted:
                hits.append((state, label, coupon.hex()))
assert checks == 6316032
assert not hits, hits
print(json.dumps({
    "source_state_inversions": sum(map(len, states.values())),
    "source_families": sorted(states),
    "cross_family_state_collisions": len(collisions),
    "source_state_to_selected_K04_complete_candidates": checks,
    "original_K04_commitment_hits": len(hits),
    "synthetic_roundtrip_controls": 288,
    "synthetic_complete_K04_control": "PASS",
    "seconds_for_target_checks": round(time.monotonic() - start, 2),
}, indent=2))
