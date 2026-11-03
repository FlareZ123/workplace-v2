"""H-17 original-source serial differential coupon copy/serialization hypothesis.

Read-only; source does not attest a differential codec.
python agents/agent18/k04_differential_codec_sft.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected = [r for r in raw.decode().splitlines()
            if "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in r]
assert len(selected) == 1
payload = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", selected[0]).group(1))
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
acc = json.loads((ROOT / "acceptance.json").read_text())
target = bytes.fromhex(acc["slot_sha256"]["K04"])
assert hashlib.sha256(bytes(a ^ b for a, b in zip(payload, mask))).digest() != target

def reverse_bits(value, width):
    return int(f"{value:0{width}b}"[::-1], 2)

def transform(data, width, from_right, reverse_symbols, op, decode, initial, origin):
    n = 128 // width
    limit = (1 << width) - 1
    value = int.from_bytes(data, "big")
    values = [(value >> (width * (n - 1 - i))) & limit for i in range(n)]
    if reverse_symbols:
        values = [reverse_bits(x, width) for x in values]
    indices = [(origin + (-k if from_right else k)) % n for k in range(n)]
    previous = values[indices[-1]] if initial else 0
    result = values.copy()
    for i in indices:
        x = values[i]
        if decode:
            y = ((x + previous) & limit) if op == "add" else x ^ previous
            previous = y
        else:
            y = ((x - previous) & limit) if op == "add" else x ^ previous
            previous = x
        result[i] = y
    if reverse_symbols:
        result = [reverse_bits(x, width) for x in result]
    out = 0
    for x in result:
        out = (out << width) | x
    return out.to_bytes(16, "big")

sources = {
    "payload": payload,
    "mask": mask,
    "reduced": bytes(a ^ b for a, b in zip(payload, mask))
}
def component(stage, updated):
    if stage == "reduced":
        return updated
    if stage == "payload":
        return bytes(a ^ b for a, b in zip(updated, mask))
    return bytes(a ^ b for a, b in zip(payload, updated))

# Planted genuinely nonidentity byte-additive differential, with full SHA256.
control = ("payload", 8, True, False, "add", True, True, 5)
planted = component(control[0], transform(sources[control[0]], *control[1:]))
planted_hash = hashlib.sha256(planted).digest()
assert planted_hash != target

checks, matches, controls = 0, [], []
seen = set()
for stage, data in sources.items():
    for width in (1, 2, 4, 8, 16, 32):
        n = 128 // width
        for from_right in (False, True):
            for reverse_symbols in (False, True):
                for op in ("xor", "add"):
                    for decode in (False, True):
                        for initial in (False, True):
                            for origin in range(n):
                                args = (
                                    stage, width, from_right, reverse_symbols,
                                    op, decode, initial, origin
                                )
                                result = component(
                                    stage, transform(data, width, from_right,
                                    reverse_symbols, op, decode, initial, origin)
                                )
                                checks += 1
                                digest = hashlib.sha256(result).digest()
                                if digest == planted_hash:
                                    controls.append(args)
                                if digest == target:
                                    matches.append((args, result.hex().upper()))
                                seen.add(result)
assert checks == 3 * sum(128 // w for w in (1, 2, 4, 8, 16, 32)) * 32
assert control in controls and not matches
print(json.dumps({
    "symbol_widths": [1, 2, 4, 8, 16, 32],
    "copy_stages": list(sources),
    "complete_original_K04_SHA256_checks": checks,
    "distinct_full_components": len(seen),
    "synthetic_control_recovered": control in controls,
    "synthetic_control_assignments": len(controls),
    "authentic_K04_matches": matches,
}, indent=2))
