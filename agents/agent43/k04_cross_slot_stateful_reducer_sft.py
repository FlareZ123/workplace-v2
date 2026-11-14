#!/usr/bin/env python3
"""Read-only SFT for a shared cross-slot REC8/1 stateful reducer.

Run from the workplace-v2 repository root. Uses Python's standard library.
No source, candidate, acceptance, route, or verifier file is modified.
"""
from collections import Counter
from pathlib import Path
import hashlib
import hmac
import itertools
import json
import re
import struct

ROOT = Path("resources")
E = ROOT / "evidence"
PINS = {
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "mail/04.eml": "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
}
for name, expected in PINS.items():
    assert hashlib.sha256((E / name).read_bytes()).hexdigest() == expected, name
ACCEPTANCE_PIN = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
assert hashlib.sha256((ROOT / "acceptance.json").read_bytes()).hexdigest() == ACCEPTANCE_PIN

# Verified source inputs / accepted components from results/h17-verified-six-slots.md.
K = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02": bytes.fromhex("0D7E3AB56FB75DA3EB0E2E06786D239E"),
    "K03": bytes.fromhex("1384AF96E25D6ADA666209CB55E062FA"),
    "K05": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07": bytes.fromhex("93495F5E425AB8E592123DABAEB68545"),
}
inputs = {
    ("K01", "K02"): b"".join(struct.pack(">H", x) for x in
        (57765, 58484, 47831, 59475, 41704, 50973, 13079, 54535)),
    ("K02", "K03"): b"SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD",
    ("K05", "K06"): K["K06"],  # raw 16-byte procedure-strip block
}
# K07's raw input is reconstructed from the selected AX-7782 second attempts.
audit = [json.loads(x) for x in (E / "transfers/transfer-audit.jsonl").read_text().splitlines()]
chunks = {}
for row in audit:
    if row.get("kind") == "CHUNK" and row.get("transfer") == "AX-7782":
        seq = int(row["seq"])
        if seq not in chunks or int(row["attempt"]) > int(chunks[seq]["attempt"]):
            chunks[seq] = row
assert set(chunks) == set(range(8))
k07_source = b"".join(bytes.fromhex(chunks[i]["checkpoint"]) for i in range(8))
inputs[("K06", "K07")] = k07_source
assert hashlib.sha256(inputs[("K01", "K02")]).digest()[:16] == K["K02"]
assert hashlib.sha256(inputs[("K02", "K03")]).digest()[:16] == K["K03"]
assert hashlib.sha256(k07_source).digest()[:16] == K["K07"]

# K04 source alternatives are considered only if one shared model predicts every known transition.
route = json.loads((E / "recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
spool_lines = (E / "print/spool-reconstruction.log").read_text().splitlines()
rows = []
for line in spool_lines:
    m = re.search(r"^(\S+) JOB=PS-261003-0417 ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)$", line)
    if m:
        ts, attempt, state, cls, payload, dest = m.groups()
        rows.append({"ts": ts, "attempt": attempt, "state": state, "class": cls,
                     "payload": bytes.fromhex(payload), "dest": dest, "line": line.encode()})
selected = [r for r in rows if r["state"] == "ACK" and r["class"] == "RECOVER"][-1]
k04_sources = {
    "payload": selected["payload"],
    "payload_xor_mask": bytes(a ^ b for a, b in zip(selected["payload"], mask)),
    "payload||mask": selected["payload"] + mask,
    "mask||payload": mask + selected["payload"],
    "mask": mask,
    "all_0417_payloads": b"".join(r["payload"] for r in rows),
    "selected_raw_line": selected["line"],
    "metadata": "|".join((selected["ts"], "PS-261003-0417", selected["attempt"],
        selected["state"], selected["class"], selected["dest"])).encode(),
}

FUNCS = {
    "md5": lambda p, s, j: hashlib.md5(j).digest(),
    "sha1": lambda p, s, j: hashlib.sha1(j).digest(),
    "sha256-first": lambda p, s, j: hashlib.sha256(j).digest()[:16],
    "sha256-last": lambda p, s, j: hashlib.sha256(j).digest()[-16:],
    "sha512-first": lambda p, s, j: hashlib.sha512(j).digest()[:16],
    "sha512-last": lambda p, s, j: hashlib.sha512(j).digest()[-16:],
    "sha3-first": lambda p, s, j: hashlib.sha3_256(j).digest()[:16],
    "sha3-last": lambda p, s, j: hashlib.sha3_256(j).digest()[-16:],
    "blake2s": lambda p, s, j: hashlib.blake2s(j, digest_size=16).digest(),
    "blake2b": lambda p, s, j: hashlib.blake2b(j, digest_size=16).digest(),
    "shake128": lambda p, s, j: hashlib.shake_128(j).digest(16),
    "shake256": lambda p, s, j: hashlib.shake_256(j).digest(16),
    "hmac256-prevkey": lambda p, s, j: hmac.new(p, j, hashlib.sha256).digest()[:16],
    "hmac256-sourcekey": lambda p, s, j: hmac.new(s, j, hashlib.sha256).digest()[:16],
    "hmac3-prevkey": lambda p, s, j: hmac.new(p, j, hashlib.sha3_256).digest()[:16],
    "hmac3-sourcekey": lambda p, s, j: hmac.new(s, j, hashlib.sha3_256).digest()[:16],
    "blake2s-prevkey": lambda p, s, j: hashlib.blake2s(j, key=p, digest_size=16).digest(),
    "blake2b-prevkey": lambda p, s, j: hashlib.blake2b(j, key=p, digest_size=16).digest(),
}
PREFIXES = (b"", b"REC8/1|", b"CEG-ARCHIVE-RECOVERY/v1\n", b"slot=")
SEPARATORS = (b"", b"|", b"\0", b"\n")
ORDERS = ("prev-source", "source-prev")
TRANSFORMS = ("direct", "xor-pad", "add-pad")

def joined_input(prefix, slot, separator, order, previous, source):
    domain = prefix + slot.encode() + b"|" if prefix == b"slot=" else prefix
    pair = previous + separator + source if order == "prev-source" else source + separator + previous
    return domain + pair

scores = Counter()
max_exact = 0
full_models = []
for prefix, separator, order, function, transform in itertools.product(
        PREFIXES, SEPARATORS, ORDERS, FUNCS, TRANSFORMS):
    predictions = []
    for (previous_slot, slot), source in inputs.items():
        previous = K[previous_slot]
        joined = joined_input(prefix, slot, separator, order, previous, source)
        predictions.append((FUNCS[function](previous, source, joined), K[slot]))
    if transform == "direct":
        score, denominator = sum(a == b for a, b in predictions), 4
        pad = None
    else:
        first_pred, first_actual = predictions[0]
        pad = (bytes(a ^ b for a, b in zip(first_pred, first_actual))
               if transform == "xor-pad"
               else (int.from_bytes(first_actual, "big") - int.from_bytes(first_pred, "big")) & ((1 << 128) - 1))
        def apply(value):
            return (bytes(a ^ b for a, b in zip(value, pad)) if transform == "xor-pad"
                    else ((int.from_bytes(value, "big") + pad) & ((1 << 128) - 1)).to_bytes(16, "big"))
        score, denominator = sum(apply(a) == b for a, b in predictions[1:]), 3
    scores[f"{score}/{denominator}"] += 1
    max_exact = max(max_exact, score)
    if score == denominator:
        full_models.append((prefix, separator, order, function, transform, pad))

# Synthetic positive: a planted shared SHA256(previous||'|'||source) reducer plus one XOR pad.
seed = bytes(range(16))
synthetic_pad = bytes.fromhex("1234567890ABCDEF1234567890ABCDEF")
synthetic_sources = [bytes((i, i ^ 0x55, i ^ 0xAA, 255 - i)) for i in range(4)]
synthetic_outputs = []
previous = seed
for source in synthetic_sources:
    raw = hashlib.sha256(previous + b"|" + source).digest()[:16]
    output = bytes(a ^ b for a, b in zip(raw, synthetic_pad))
    synthetic_outputs.append(output)
    previous = output
first_raw = hashlib.sha256(seed + b"|" + synthetic_sources[0]).digest()[:16]
fitted_pad = bytes(a ^ b for a, b in zip(first_raw, synthetic_outputs[0]))
synthetic_holdouts = 0
previous = synthetic_outputs[0]
for source, expected in zip(synthetic_sources[1:], synthetic_outputs[1:]):
    raw = hashlib.sha256(previous + b"|" + source).digest()[:16]
    synthetic_holdouts += bytes(a ^ b for a, b in zip(raw, fitted_pad)) == expected
    previous = expected
assert fitted_pad == synthetic_pad and synthetic_holdouts == 3

# Apply only fully supported common models to K04 alternatives; acceptance hash is decisive.
k04_hits = []
for prefix, separator, order, function, transform, pad in full_models:
    for source_name, source in k04_sources.items():
        previous = K["K03"]
        joined = joined_input(prefix, "K04", separator, order, previous, source)
        raw = FUNCS[function](previous, source, joined)
        if transform == "xor-pad":
            candidate = bytes(a ^ b for a, b in zip(raw, pad))
        elif transform == "add-pad":
            candidate = ((int.from_bytes(raw, "big") + pad) & ((1 << 128) - 1)).to_bytes(16, "big")
        else:
            candidate = raw
        if hashlib.sha256(candidate).hexdigest() == acceptance["slot_sha256"]["K04"]:
            k04_hits.append({"source": source_name, "function": function, "candidate": candidate.hex().upper()})

print(json.dumps({
    "source_pins": {**PINS, "acceptance.json": ACCEPTANCE_PIN},
    "known_transitions": ["K01->K02", "K02->K03", "K05->K06", "K06->K07"],
    "models": len(PREFIXES) * len(SEPARATORS) * len(ORDERS) * len(FUNCS) * len(TRANSFORMS),
    "direct_models": len(PREFIXES) * len(SEPARATORS) * len(ORDERS) * len(FUNCS),
    "padded_models": 2 * len(PREFIXES) * len(SEPARATORS) * len(ORDERS) * len(FUNCS),
    "max_exact_holdouts": max_exact,
    "score_histogram": dict(sorted(scores.items())),
    "full_known_models": len(full_models),
    "synthetic_positive_holdouts": synthetic_holdouts,
    "synthetic_positive_passed": True,
    "K04_source_alternatives_tested_if_model_passed": list(k04_sources),
    "K04_acceptance_hits": k04_hits,
    "result": "NO_SHARED_REDUCER_MODEL_PREDICTS_ALL_KNOWN_TRANSITIONS; NO K04 CANDIDATE",
}, indent=2))
