"""Read-only SplitMix64 state-spacing test for H-17 16-byte source objects."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
EVIDENCE = ROOT / "evidence"
MASK64 = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
C1 = 0xBF58476D1CE4E5B9
C2 = 0x94D049BB133111EB
INV_C1 = pow(C1, -1, 1 << 64)
INV_C2 = pow(C2, -1, 1 << 64)
INV_GAMMA = pow(GAMMA, -1, 1 << 64)
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def unxor(y: int, n: int) -> int:
    x, s = y, n
    while s < 64:
        x ^= x >> s
        s *= 2
    return x & MASK64

def unmix(value: int) -> int:
    x = unxor(value, 31)
    x = (x * INV_C2) & MASK64
    x = unxor(x, 27)
    x = (x * INV_C1) & MASK64
    return unxor(x, 30)

def mix(state: int) -> int:
    z = (state ^ (state >> 30)) * C1 & MASK64
    z = (z ^ (z >> 27)) * C2 & MASK64
    return z ^ (z >> 31)

for i in range(1024):
    x = (0xACEDBADD5EEDC0DE + i * GAMMA) & MASK64
    assert unmix(mix(x)) == x
assert mix(0x9E3779B97F4A7C15) == 0xE220A8397B1DCDAF

spool = (EVIDENCE / "print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
objects: dict[str, bytes] = {}
for line in spool.decode().splitlines():
    m = re.search(r"JOB=(\\S+) ATTEMPT=(\\d+) STATE=(\\S+) CLASS=(\\S+) PAYLOAD=([0-9A-F]{32})", line)
    if m:
        job, attempt, state, cls, payload = m.groups()
        name = f"spool:{job}:attempt{attempt}:{state}:{cls}:{line.split()[0]}"
        objects[name] = bytes.fromhex(payload)
route = json.loads((EVIDENCE / "recovery-routing.json").read_text())
objects["route:K04:masked_component"] = bytes.fromhex(route["K04"]["masked_component"])
objects["route:K08:desk_nonce"] = bytes.fromhex(route["K08"]["desk_nonce"])
objects.update({
    "K01:ink": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02:reduced": bytes.fromhex("0D7E3AB56FB75DA3EB0E2E06786D239E"),
    "K02:source": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K03:reduced": bytes.fromhex("1384AF96E25D6ADA666209CB55E062FA"),
    "K05:latches": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06:service": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07:reduced": bytes.fromhex("93495F5E425AB8E592123DABAEB68545"),
    "K07:source": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
})
assert len(objects) == 143
views: list[tuple[str, str, int, int]] = []
for name, payload in objects.items():
    for endian in ("big", "little"):
        for half in range(2):
            word = int.from_bytes(payload[8*half:8*half+8], endian)
            views.append((name, endian, half, unmix(word)))

LIMIT = 65536
hits = []
for a in range(len(views)):
    name_a, endian_a, half_a, state_a = views[a]
    for b in range(a + 1, len(views)):
        name_b, endian_b, half_b, state_b = views[b]
        n = ((state_b - state_a) * INV_GAMMA) & MASK64
        signed = n if n < (1 << 63) else n - (1 << 64)
        if 0 < abs(signed) <= LIMIT:
            hits.append((signed, name_a, endian_a, half_a, name_b, endian_b, half_b))

state = 0x123456789ABCDEF0
w1, w2 = mix((state + GAMMA) & MASK64), mix((state + 123 * GAMMA) & MASK64)
recovered = ((unmix(w2) - unmix(w1)) * INV_GAMMA) & MASK64
assert recovered == 122
within = [x for x in hits if x[1] == x[4] and x[2] == x[5] and x[3] != x[6] and abs(x[0]) == 1]
print(json.dumps({
    "spool_sha256": SPOOL_SHA,
    "objects": len(objects),
    "observed_64bit_views": len(views),
    "pair_comparisons": len(views) * (len(views)-1)//2,
    "state_gap_limit": LIMIT,
    "state_gap_hits": len(hits),
    "intra_packet_consecutive_hits": len(within),
    "example_hits": hits[:25],
    "positive_mix_inverse": True,
    "positive_122_draw_spacing": True,
}, indent=2))
