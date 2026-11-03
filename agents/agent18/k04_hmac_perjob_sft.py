"""H-17 K04 HMAC-SHA256 keyed-per-job coupon hypothesis, source-calibrated.

Read-only: python agents/agent18/k04_hmac_perjob_sft.py
No historical producer documentation asserts this HMAC mechanism.
"""
import hashlib
import hmac
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
for line in raw.decode().splitlines():
    if not line.startswith("2026-"):
        continue
    items = line.split(" ")
    row = {"timestamp": items[0]}
    row.update(dict(tok.split("=", 1) for tok in items[1:]))
    rows.append(row)
assert len(rows) == 133
selected = [r for r in rows if r["JOB"] == "PS-261003-0417"
            and r["ATTEMPT"] == "2" and r["STATE"] == "ACK"
            and r["CLASS"] == "RECOVER"]
assert len(selected) == 1
selected = selected[0]
acc = json.loads((ROOT / "acceptance.json").read_text())
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(acc["slot_sha256"]["K04"])
keys = {
    k: bytes.fromhex(value)
    for k, value in (
        ("K01", "049AAB2E1CDE7A82CD7C60234303C91A"),
        ("K02", "0D7E3AB56FB75DA3EB0E2E06786D239E"),
        ("K03", "1384AF96E25D6ADA666209CB55E062FA"),
        ("K05", "FF8B78200A56E8586DCDA00EF01E4572"),
        ("K06", "5DBF40EE52FAAED9A536D3326CF0D95A"),
        ("K07", "93495F5E425AB8E592123DABAEB68545"),
    )
}
keys["K04_MASK"] = mask
keys["K08_NONCE"] = bytes.fromhex(route["K08"]["desk_nonce"])
assert all(hashlib.sha256(v).hexdigest() == acc["slot_sha256"][k]
           for k, v in keys.items() if k.startswith("K0") and k
           not in ("K04_MASK", "K08_NONCE"))

def forms(row):
    t = row["timestamp"]
    job = row["JOB"]
    a = row["ATTEMPT"]
    state = row["STATE"]
    cls = row["CLASS"]
    dest = row["DEST"]
    suffix = job.rsplit("-", 1)[-1]
    iso = t.replace("+00:00", "Z")
    core = (job, a, state, cls, dest)
    basic = {
        "job": job,
        "job_attempt_colon": f"{job}:{a}",
        "job_attempt_dash": f"{job}-{a}",
        "job_class": f"{job}:{cls}",
        "job_dest": f"{job}:{dest}",
        "job_state": f"{job}:{state}",
        "job_attempt_class": f"{job}:{a}:{cls}",
        "job_attempt_dest": f"{job}:{a}:{dest}",
        "job_attempt_class_dest": f"{job}:{a}:{cls}:{dest}",
        "job_attempt_state_class": f"{job}:{a}:{state}:{cls}",
        "job_attempt_state_class_dest": f"{job}:{a}:{state}:{cls}:{dest}",
        "time": t,
        "time_iso": iso,
        "time_minute": iso[:16],
        "time_job_pipe": f"{iso}|{job}",
        "job_time_pipe": f"{job}|{iso}",
        "time_job_colon": f"{iso}:{job}",
        "job_time_colon": f"{job}:{iso}",
        "time_job_attempt_pipe": f"{iso}|{job}|{a}",
        "job_time_attempt_pipe": f"{job}|{iso}|{a}",
        "job_attempt_time_pipe": f"{job}|{a}|{iso}",
        "job_attempt_class_time_pipe": f"{job}|{a}|{cls}|{iso}",
        "job_attempt_state_class_dest_time_pipe": (
            f"{job}|{a}|{state}|{cls}|{dest}|{iso}"
        ),
        "suffix": suffix,
        "suffix_attempt": f"{suffix}:{a}",
        "suffix_class": f"{suffix}:{cls}",
        "suffix_attempt_class": f"{suffix}:{a}:{cls}",
        "suffix_iso": f"{suffix}:{iso}",
        "json_core": json.dumps(
            dict(zip(("job", "attempt", "state", "class", "dest"), core)),
            sort_keys=True, separators=(",", ":")
        ),
        "json_all": json.dumps(
            dict(zip(("job", "attempt", "state", "class", "dest", "timestamp"),
                     (*core, iso))),
            sort_keys=True, separators=(",", ":")
        ),
    }
    return {(label, prefix): (prefix + msg).encode()
            for label, msg in basic.items()
            for prefix in ("", "K04|", "H17|", "REC8|", "ESC-N|", "H-17/")}

formats = forms(rows[0])
assert len(formats) == 180
intact = [r for r in rows if r is not selected]
assert len(intact) == 132

source_hits, target_hits = [], []
checks = 0
for keyname, key in keys.items():
    for fmt in formats:
        for view in ("first", "last"):
            matched = []
            for i, row in enumerate(intact):
                digest = hmac.digest(key, forms(row)[fmt], "sha256")
                predicted = digest[:16] if view == "first" else digest[-16:]
                checks += 1
                if predicted == bytes.fromhex(row["PAYLOAD"]):
                    matched.append(i)
            if matched:
                source_hits.append((keyname, fmt, view, matched))
            digest = hmac.digest(key, forms(selected)[fmt], "sha256")
            predicted = digest[:16] if view == "first" else digest[-16:]
            candidate = bytes(a ^ b for a, b in zip(predicted, mask))
            if hashlib.sha256(candidate).digest() == target:
                target_hits.append((keyname, fmt, view, candidate.hex().upper()))
assert checks == 380160 and not source_hits and not target_hits

# Independent synthetic emitter with 132 calibration and heldout records:
test_key = bytes.fromhex("000102030405060708090A0B0C0D0E0F")
fmt = ("job_time_attempt_pipe", "H17|")
planted = [hmac.digest(test_key, forms(r)[fmt], "sha256")[:16]
           for r in rows]
assert planted[8] != planted[9]
assert all(hmac.digest(test_key, forms(rows[i])[fmt], "sha256")[:16]
           == planted[i] for i in (1, 17, 64, 127))
synthetic_commitment = hashlib.sha256(
    bytes(a ^ b for a, b in zip(planted[129], mask))
).digest()
assert synthetic_commitment != target
assert hashlib.sha256(bytes(a ^ b for a, b in zip(
    hmac.digest(test_key, forms(rows[129])[fmt], "sha256")[:16], mask
))).digest() == synthetic_commitment

print(json.dumps({
    "original_source_controls": len(intact),
    "keys": len(keys),
    "metadata_formats": len(formats),
    "truncated_digest_views": 2,
    "original_intact_packet_HMAC_checks": checks,
    "original_intact_full_packet_hits": source_hits,
    "original_selected_K04_commitment_checks": len(keys) * len(formats) * 2,
    "original_selected_K04_matches": target_hits,
    "synthetic_calibration_and_full_commitment": "PASS",
}, indent=2))
