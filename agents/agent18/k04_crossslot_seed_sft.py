"""Read-only SFT: source-derived CPython seeds as an alternative K04 producer.

Original six accepted components, their raw prehash inputs and route constants
are treated as hypothesized seeding material. Exact original printer packets
are source controls; unchanged K04 commitment tests complete predictions.
No modification of the original evidence or verifier.
"""
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
values = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
for k, v in values.items():
    assert hashlib.sha256(bytes.fromhex(v)).hexdigest() == accept["slot_sha256"][k]
mask = bytes.fromhex(route["K04"]["masked_component"])
target = accept["slot_sha256"]["K04"]
rows = [m.group(1) for m in re.finditer(r"PAYLOAD=([0-9A-F]{32})", raw.decode())]
assert len(rows) == 133
actual = bytes.fromhex(rows[129])
intact = {bytes.fromhex(v) for i, v in enumerate(rows) if i != 129}
assert len(intact) == 132

source = {name: bytes.fromhex(v) for name, v in values.items()}
source.update({
    "SIX_ORDERED": b"".join(source[k] for k in values),
    "SIX_REVERSED": b"".join(source[k] for k in reversed(list(values))),
    "K02_PREHASH": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K03_PREHASH": bytes.fromhex("D7DAD6BC9714519B7DAD0AD4BE8E87FD"),
    "K04_MASK": mask,
    "K08_NONCE": bytes.fromhex(route["K08"]["desk_nonce"]),
})
assert len(source) == 12
seeds = {}
for name, b in source.items():
    seeds[name + ":BYTES"] = b
    seeds[name + ":HEX_TEXT"] = b.hex().upper()
    seeds[name + ":INT_LE"] = int.from_bytes(b, "little")
    seeds[name + ":INT_BE"] = int.from_bytes(b, "big")
    seeds[name + ":SHA256_BYTES"] = hashlib.sha256(b).digest()
assert len(seeds) == 60

def variants(words):
    chunks = [w.to_bytes(4, "little") for w in words]
    return (b"".join(chunks),
            b"".join(x[::-1] for x in chunks),
            b"".join(reversed(chunks)),
            b"".join(x[::-1] for x in reversed(chunks)))

def windows(seed, n):
    rng = random.Random(seed)
    buf = [rng.getrandbits(32) for _ in range(4)]
    for pos in range(n):
        yield pos, variants(buf)
        buf = buf[1:] + [rng.getrandbits(32)]

# A known source seed and a planted nonzero-offset coupon ensure the
# same full mask/XOR/SHA256 check detects an exact complete candidate.
pos = 173
rng = random.Random(source["K01"])
truth = [rng.getrandbits(32) for _ in range(pos + 4)]
planted = hashlib.sha256(bytes(a ^ b for a, b in zip(
    variants(truth[-4:])[0], mask))).digest()
assert any(hashlib.sha256(bytes(a ^ b for a, b in zip(
    payload, mask))).digest() == planted
    for p, group in windows(source["K01"], pos + 1)
    if p == pos for payload in group)

source_hits = []
target_hits = []
copy_hits = []
count = 0
for name, seed in sorted(seeds.items()):
    for pos, group in windows(seed, 4096):
        for view, payload in enumerate(group):
            count += 1
            if payload in intact:
                source_hits.append((name, pos, view))
            if payload == actual:
                copy_hits.append((name, pos, view))
            component = bytes(a ^ b for a, b in zip(payload, mask))
            if hashlib.sha256(component).hexdigest() == target:
                target_hits.append((name, pos, view, component.hex().upper()))
assert count == 60 * 4096 * 4
print(json.dumps({
    "source_blobs": len(source),
    "seed_interpretations": len(seeds),
    "draw_windows_per_seed": 4096,
    "complete_K04_candidates": count,
    "planted_positive": "PASS",
    "original_intact_source_packet_hits": source_hits,
    "copied_ACK2_packet_hits": copy_hits,
    "authentic_K04_slot_matches": target_hits
}, indent=2))
