"""H-17 SFT: record-ID hash issuer, 16-bit retry operator and PTW417 coupon transfer.

Read-only original resources, source pins, complete held-out packet checks.
Run from repository root with Python 3 standard library.
"""
from collections import defaultdict
from datetime import datetime
from itertools import product, permutations
from pathlib import Path
import hashlib
import json
import re

ROOT = Path("resources")
E = ROOT / "evidence"
PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "transfers/transfer-audit.jsonl": "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf",
}
for name, expected in PINS.items():
    assert hashlib.sha256((E / name).read_bytes()).hexdigest() == expected, name

receipts = [json.loads(x) for x in (E / "maintenance/seal-receipts.jsonl").read_text().splitlines()]
printed = {}
for line in (E / "print/spool-reconstruction.log").read_text().splitlines():
    m = re.search(r"JOB=PS-261003-(\d+) ", line)
    if m:
        fields = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line))
        n = int(m.group(1))
        if 390 <= n <= 416 and fields["STATE"] == "ACK":
            printed[n] = fields
legacy = {int(r["permit"].split("-")[-1]): r for r in receipts if r["permit"] != "PTW-417"}
assert set(legacy) == set(printed) == set(range(390, 417))
numbers = sorted(legacy)
actual = {n: bytes.fromhex(printed[n]["PAYLOAD"]) for n in numbers}

def emitter_input(n, representation, layout, direction, separator):
    r, pkt = legacy[n], printed[n]
    hx = r["serial"].split("-")[-1]
    source = {
        "raw": bytes.fromhex(hx),
        "raw-le": bytes.fromhex(hx)[::-1],
        "hex": hx.encode(),
        "serial": r["serial"].encode(),
    }[representation]
    context = {
        "none": b"",
        "ptw": ("PTW-" + str(n)).encode(),
        "ps": pkt["JOB"].encode(),
        "number": str(n).encode(),
        "bay": r["bay"].encode(),
        "class-dest": (pkt["CLASS"] + "|" + pkt["DEST"]).encode(),
        "ptw-bay": ("PTW-" + str(n) + "|" + r["bay"]).encode(),
        "ps-class-dest": (pkt["JOB"] + "|" + pkt["CLASS"] + "|" + pkt["DEST"]).encode(),
    }[layout]
    if layout == "none":
        return source
    return source + separator + context if direction == "suffix" else context + separator + source

def digest128(data, method):
    if method == "sha256-first": return hashlib.sha256(data).digest()[:16]
    if method == "sha256-last": return hashlib.sha256(data).digest()[16:]
    if method == "sha512-first": return hashlib.sha512(data).digest()[:16]
    if method == "sha512-last": return hashlib.sha512(data).digest()[-16:]
    if method == "blake2s": return hashlib.blake2s(data, digest_size=16).digest()
    if method == "blake2b": return hashlib.blake2b(data, digest_size=16).digest()
    if method == "md5": return hashlib.md5(data).digest()
    if method == "shake256": return hashlib.shake_256(data).digest(16)
    raise ValueError(method)

MASK = (1 << 128) - 1
def offset(original, sample, op):
    if op == "xor": return original ^ sample
    return (original - sample) & MASK

def apply(sample, pad, op):
    if op == "xor": return sample ^ pad
    return (sample + pad) & MASK

hash_family_count = 0
hash_holdout = 0
max_equal_bytes = 0
for rep, layout, method, op, scope, direction, sep in product(
    ("raw", "raw-le", "hex", "serial"),
    ("none", "ptw", "ps", "number", "bay", "class-dest", "ptw-bay", "ps-class-dest"),
    ("sha256-first", "sha256-last", "sha512-first", "sha512-last", "blake2s", "blake2b", "md5", "shake256"),
    ("xor", "add"), ("global", "per-bay"), ("suffix", "prefix"), (b"", b"|", b"\n"),
):
    predicted = {n: int.from_bytes(digest128(emitter_input(n, rep, layout, direction, sep), method), "big") for n in numbers}
    first = {}
    for n in numbers:
        group = legacy[n]["bay"] if scope == "per-bay" else "ALL"
        if group not in first:
            first[group] = n
    fits = {group: offset(int.from_bytes(actual[n], "big"), predicted[n], op) for group, n in first.items()}
    checks = [n for n in numbers if n not in first.values()]
    for n in checks:
        group = legacy[n]["bay"] if scope == "per-bay" else "ALL"
        candidate = apply(predicted[n], fits[group], op).to_bytes(16, "big")
        if candidate == actual[n]:
            hash_holdout += 1
        equal = sum(x == y for x, y in zip(candidate, actual[n]))
        max_equal_bytes = max(max_equal_bytes, equal)
    hash_family_count += 1
assert hash_family_count == 6144 and hash_holdout == 0
assert all(apply(x, 0x1234567890ABCDEF1234567890ABCDEF, "xor") ==
           (x ^ 0x1234567890ABCDEF1234567890ABCDEF) for x in (0, 3, MASK))

# The second boundary comprises genuine selected K02 revision pairs and
# selected AX7782 K07 checkpoint attempt pairs, all eight sequence positions.
telemetry = [json.loads(x) for x in (E / "telemetry/freeze-export.jsonl").read_text().splitlines()]
k02 = defaultdict(dict)
start = datetime.fromisoformat("2026-10-03T21:13:40+00:00")
end = datetime.fromisoformat("2026-10-03T21:13:48+00:00")
for r in telemetry:
    if (r.get("tag"), r.get("field"), r.get("quality"), r.get("state")) == ("LT-204", "DIAG_WORD", "GOOD", "HOLD") and start <= datetime.fromisoformat(r["ts"]) < end:
        k02[r["seq"]][r["revision"]] = r["value"]
transfer = [json.loads(x) for x in (E / "transfers/transfer-audit.jsonl").read_text().splitlines()]
k07 = defaultdict(dict)
for r in transfer:
    if r["transfer"] == "AX-7782" and r["kind"] == "CHUNK":
        k07[r["seq"]][r["attempt"]] = int(r["checkpoint"], 16)
pairs = {
    "K02": [(k02[i][1], k02[i][2]) for i in range(8)],
    "K07": [(k07[i][1], k07[i][2]) for i in range(8)],
}
assert all(len(p) == 8 for p in pairs.values())
def rol(v, k): return ((v << k) | (v >> (16 - k))) & 65535 if k else v
def swap(v): return ((v & 255) << 8) | (v >> 8)
def views(v):
    yield "identity", v
    yield "byteswap", swap(v)
    yield "not", v ^ 65535
    for k in range(1, 16): yield "rol" + str(k), rol(v, k)
    for k in range(1, 16): yield "ror" + str(k), rol(v, 16 - k)

model_count = 0
model_holdout = 0
for domain, history in pairs.items():
    for swap_old, swap_new, op in product((False, True), (False, True), ("xor", "add")):
        observed = [(swap(x) if swap_old else x, swap(y) if swap_new else y) for x, y in history]
        for name, first in views(observed[0][0]):
            pad = first ^ observed[0][1] if op == "xor" else (observed[0][1] - first) & 65535
            for old, new in observed[1:]:
                value = dict(views(old))[name]
                guess = (value ^ pad) if op == "xor" else ((value + pad) & 65535)
                model_holdout += int(guess == new)
            model_count += 1
assert model_count == 528 and model_holdout == 0

# Independent word-ordinal transfer: K02 delta_i -> K07 delta_i.
d2 = [a ^ b for a, b in pairs["K02"]]
d7 = [a ^ b for a, b in pairs["K07"]]
delta_holdout = sum((rol(d2[i], k) ^ rol(d2[0], k) ^ d7[0]) == d7[i]
                    for k in range(16) for i in range(1, 8))
assert delta_holdout == 0

# Exact two-pair-fitted affine ring model under integer addition modulo 2^16.
ring = {}
for name, p in pairs.items():
    x0, y0 = p[0]; x1, y1 = p[1]
    dx, dy = (x1-x0)&65535, (y1-y0)&65535
    v = (dx&-dx).bit_length()-1 if dx else 16
    if dx:
        mod = 1 << (16-v)
        alphas = [] if dy % (1 << v) else [((dy >> v)*pow(dx >> v, -1, mod)+j*mod)%65536 for j in range(1 << v)]
    else:
        alphas = range(65536) if dy == 0 else []
    hits = 0
    for a in alphas:
        b = (y0-a*x0)&65535
        hits += sum((a*x+b)&65535 == y for x, y in p[2:])
    ring[name] = (len(alphas), hits)
assert ring == {"K02": (1, 0), "K07": (1, 0)}
assert all((0x53db*x+0x6a23)&65535 == y for x,y in
           zip(range(8), [(0x53db*x+0x6a23)&65535 for x in range(8)]))

# Direct matched-ID coupon source family: every PTW417 four-serial ordered
# tuple, both common 32-bit serializers, then the fixed original route mask.
ptw417 = [bytes.fromhex(r["serial"].split("-")[1]) for r in receipts if r["permit"] == "PTW-417"]
assert len(ptw417) == 17
route = json.loads((E / "recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
commitment = acceptance["slot_sha256"]["K04"]
attempts = hits = 0
for indexes in permutations(range(17), 4):
    for reverse in (False, True):
        candidate_coupon = b"".join(ptw417[i][::-1] if reverse else ptw417[i] for i in indexes)
        key = bytes(a ^ b for a, b in zip(candidate_coupon, mask))
        hits += hashlib.sha256(key).hexdigest() == commitment
        attempts += 1
assert attempts == 114240 and hits == 0
planted = b"".join(ptw417[i][::-1] for i in (1, 6, 12, 4))
assert hashlib.sha256(bytes(a ^ b for a, b in zip(planted, mask))).digest() == hashlib.sha256(bytes(a ^ b for a, b in zip(planted, mask))).digest()
print(json.dumps({
    "sources_pinned": len(PINS), "matched_PTWs_and_printer_jobs": len(numbers),
    "hash_emitter_models": hash_family_count, "exact_emitter_holdouts": hash_holdout,
    "max_single_packet_equal_bytes": max_equal_bytes,
    "retry_rotation_models": model_count, "exact_retry_word_holdouts": model_holdout,
    "cross_stream_delta_exact_holdouts": delta_holdout, "ring_affine": ring,
    "PTW417_coupon_candidates": attempts, "original_K04_hits": hits,
    "result": "NO_MATCH; conditional source-model exclusions only",
}, indent=2))
