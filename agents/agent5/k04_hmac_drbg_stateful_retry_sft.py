"""Source-pinned, read-only K04 stateful HMAC_DRBG retry coupon test.

NIST SP800-90A Rev.1 (June 2015), sections 10.1.2.2 and 10.1.2.5.
The hypothetical issuer is not documented as real printer firmware.
"""
import hashlib
import hmac
import itertools
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = accept["slot_sha256"]["K04"]
assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
rows = []
for line in spool.decode().splitlines():
    if "PAYLOAD=" not in line:
        continue
    row = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line))
    row["time"] = line.split(" ", 1)[0]
    row["bytes"] = bytes.fromhex(row.pop("PAYLOAD"))
    rows.append(row)
assert len(rows) == 133
j17 = [r for r in rows if r["JOB"] == "PS-261003-0417"]
j20 = [r for r in rows if r["JOB"] == "PS-261003-0420"]
assert [(r["STATE"], r["ATTEMPT"], r["CLASS"]) for r in j17] == [
    ("ACK", "1", "LABEL"), ("REQUESTED", "1", "RECOVER"),
    ("ACK", "2", "RECOVER"), ("REQUESTED", "3", "RECOVER")]
assert [(r["STATE"], r["ATTEMPT"], r["CLASS"]) for r in j20] == [
    ("ACK", "1", "STORES"), ("ACK", "2", "RECOVER")]

def mac(key, message):
    return hmac.digest(key, message, "sha256")

class HmacDrbg:
    def __init__(self, seed):
        self.key = bytes(32)
        self.value = b"\x01" * 32
        self.update(seed)
    def update(self, provided=None):
        p = provided if provided is not None else b""
        self.key = mac(self.key, self.value + b"\x00" + p)
        self.value = mac(self.key, self.value)
        if provided is not None:
            self.key = mac(self.key, self.value + b"\x01" + p)
            self.value = mac(self.key, self.value)
    def generate(self, additional=None):
        if additional is not None:
            self.update(additional)
        self.value = mac(self.key, self.value)
        result = self.value[:16]
        self.update(additional)
        return result

def packet_context(row, style):
    if style == 0:
        return None
    if style == 1:
        return b""
    if style == 2:
        return row["JOB"].encode()
    if style == 3:
        return "|".join(row[k] for k in ("JOB", "ATTEMPT", "STATE", "CLASS", "DEST")).encode()
    if style == 4:
        return row["time"].encode()
    if style == 5:
        return (row["JOB"] + "|" + row["time"]).encode()
    if style == 6:
        return bytes([int(row["ATTEMPT"])])
    raise ValueError(style)

def seed_from(first, seed_style, nonce_style, personalization_style):
    raw = first["bytes"]
    if seed_style == 1:
        raw = hashlib.sha256(raw).digest()
    if seed_style == 2:
        raw = hashlib.sha512(raw).digest()
    if seed_style == 3:
        raw += first["JOB"].encode()
    if seed_style == 4:
        raw = first["JOB"].encode() + raw
    n = [
        b"", nonce, mask, first["JOB"].encode(), b"H17-IR-261003", b"2026-10-03"
    ][nonce_style]
    p = [
        b"", b"RECOVER", b"ESC-N", first["JOB"].encode(),
        b"IR-261003-H17", first["CLASS"].encode()
    ][personalization_style]
    return raw + n + p

# Functional positive: identical seed and exactly the same request sequence
# reproduce the 3 output blocks, including null-versus-empty additional data.
sample = HmacDrbg(b"TEST-ENTROPYTEST-NONCE")
blocks = (sample.generate(), sample.generate(b""), sample.generate(b"RECOVER"))
repeat = HmacDrbg(b"TEST-ENTROPYTEST-NONCE")
assert blocks == (repeat.generate(), repeat.generate(b""), repeat.generate(b"RECOVER"))
assert len(set(blocks)) == 3

# Plant a complete synthetic target BEFORE selecting the original issuer models.
fixture = (3, 1, 2, 4, 0)
model = HmacDrbg(seed_from(j17[0], *fixture[:3]))
fixture_output = [model.generate(packet_context(row, fixture[3])) for row in j17[1:]]
fixture_coupon = fixture_output[1]
planted_target = hashlib.sha256(bytes(x ^ y for x, y in zip(fixture_coupon, mask))).hexdigest()

counts = {
    "complete_selected_original_checks": 0,
    "original_K04_hits": 0,
    "source_0417_requested1_hits": 0,
    "source_0417_requested3_hits": 0,
    "source_0417_both_hits": 0,
    "source_0420_recov_ACK2_hits": 0,
    "synthetic_planted_positive_assignments": 0
}
coupons = set()
for s, n, p, extra, from_req1 in itertools.product(
    range(5), range(6), range(6), range(7), range(2)
):
    first = j17[1] if from_req1 else j17[0]
    later = j17[2:] if from_req1 else j17[1:]
    issuer = HmacDrbg(seed_from(first, s, n, p))
    out = [issuer.generate(packet_context(row, extra)) for row in later]
    if from_req1:
        coupon, predicted_req3 = out
        req1_ok = False
    else:
        predicted_req1, coupon, predicted_req3 = out
        req1_ok = predicted_req1 == j17[1]["bytes"]
    req3_ok = predicted_req3 == j17[3]["bytes"]
    counts["source_0417_requested1_hits"] += int(req1_ok)
    counts["source_0417_requested3_hits"] += int(req3_ok)
    counts["source_0417_both_hits"] += int(req1_ok and req3_ok)
    comparator = HmacDrbg(seed_from(j20[0], s, n, p))
    predicted_0420 = comparator.generate(packet_context(j20[1], extra))
    counts["source_0420_recov_ACK2_hits"] += int(predicted_0420 == j20[1]["bytes"])
    component = bytes(x ^ y for x, y in zip(coupon, mask))
    component_sha = hashlib.sha256(component).hexdigest()
    counts["complete_selected_original_checks"] += 1
    counts["original_K04_hits"] += int(component_sha == target)
    counts["synthetic_planted_positive_assignments"] += int(component_sha == planted_target)
    coupons.add(coupon)

assert counts["complete_selected_original_checks"] == 2520
assert len(coupons) == 2163
assert counts["synthetic_planted_positive_assignments"] == 1
assert counts["original_K04_hits"] == 0
print(json.dumps({"result": "NO_MATCH", "unique_coupons": len(coupons), **counts}, sort_keys=True))
