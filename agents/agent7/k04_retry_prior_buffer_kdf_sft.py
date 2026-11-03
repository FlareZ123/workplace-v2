"""Source-pinned H-17 attempt-2 ACK emitter test; read-only SFT.

Tests a prior-same-job-buffer hash/HMAC KDF on the only later intact
attempt-2 RECOVER ACK control, then original K04 full-component candidates.
No observed attempt-2 payload participates in constructing a candidate.
Run with Python 3 from any working directory.
"""
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(source).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
acceptance = json.loads((ROOT / "acceptance.json").read_text())
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
assert acceptance["slot_sha256"]["K04"] == (
    "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
)
rows = []
for line in source.decode().splitlines():
    if "PAYLOAD=" not in line:
        continue
    item = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line))
    item["ts"] = line.split(" ")[0]
    rows.append(item)
assert len(rows) == 133


def row(job, attempt, state, category):
    x = [r for r in rows if r["JOB"].endswith(job)
         and r["ATTEMPT"] == str(attempt)
         and r["STATE"] == state and r["CLASS"] == category]
    assert len(x) == 1
    return x[0]


prior_control = row("0420", 1, "ACK", "STORES")
control = row("0420", 2, "ACK", "RECOVER")
prior_label = row("0417", 1, "ACK", "LABEL")
prior_request = row("0417", 1, "REQUESTED", "RECOVER")
selected = row("0417", 2, "ACK", "RECOVER")
assert control["PAYLOAD"] == "432475F72A62DB39F3D5693E2C937FA4"
assert prior_control["PAYLOAD"] == "31C9714DD36DB2677BB9006670A9DFFD"
assert prior_request["PAYLOAD"] == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
assert selected["ts"] == "2026-10-03T18:02:00Z"


def headers(previous, current):
    m = {
        "empty": "",
        "job": current["JOB"],
        "suffix": current["JOB"].split("-")[-1],
        "time": current["ts"],
        "date": current["ts"][:10],
        "attempt": current["ATTEMPT"],
        "class": current["CLASS"],
        "dest": current["DEST"],
        "job+attempt": current["JOB"] + ":" + current["ATTEMPT"],
        "job/class/dest": current["JOB"] + "|" + current["CLASS"] + "|" + current["DEST"],
        "time/attempt": current["ts"] + "|" + current["ATTEMPT"],
        "full_header": " ".join(f"{k}={current[k]}" for k in
                               ("JOB", "ATTEMPT", "STATE", "CLASS", "DEST")),
        "delta_header": "|".join((previous["CLASS"], previous["DEST"],
                                   current["CLASS"], current["DEST"], current["ATTEMPT"])),
        "json": json.dumps({k: current[k] for k in
                            ("JOB", "ATTEMPT", "STATE", "CLASS", "DEST", "ts")},
                           sort_keys=True, separators=(",", ":")),
        "line_no_payload": (f'{current["ts"]} JOB={current["JOB"]} '
                            f'ATTEMPT={current["ATTEMPT"]} STATE={current["STATE"]} '
                            f'CLASS={current["CLASS"]} DEST={current["DEST"]}'),
    }
    assert len(m) == 15
    return {k: v.encode() for k, v in m.items()}


HASHES = {
    name: getattr(hashlib, name)
    for name in ("md5", "sha1", "sha256", "sha512", "sha3_256", "blake2s", "blake2b")
}
DOMAINS = (b"", b"H17|", b"K04|", b"RECOVER|", b"ESC-N|", b"retry|")


def emit(previous, current):
    """Frozen family of 24,300 KDF assignments using prior payload only."""
    raw = bytes.fromhex(previous["PAYLOAD"])
    previous_forms = (("raw", raw), ("hex", raw.hex().upper().encode()),
                      ("raw-reversed", raw[::-1]))
    for form, part in previous_forms:
        for field, message in headers(previous, current).items():
            for domain in DOMAINS:
                data = domain + message
                values = (("prior||meta", part + data),
                          ("meta||prior", data + part),
                          ("prior||meta||prior", part + data + part))
                for order, material in values:
                    for algorithm, hash_fn in HASHES.items():
                        digest = hash_fn(material).digest()
                        for view, output in (("first16", digest[:16]),
                                             ("last16", digest[-16:]),
                                             ("revfirst16", digest[:16][::-1])):
                            yield (("HASH", form, field, domain.decode(),
                                    order, algorithm, view), output)
                for key_form, key in (("raw16", raw),
                                      ("sha32", hashlib.sha256(raw).digest()),
                                      ("rev16", raw[::-1])):
                    for algorithm in ("sha1", "sha256", "sha512"):
                        digest = hmac.digest(key, data, algorithm)
                        for view, output in (("first16", digest[:16]),
                                             ("last16", digest[-16:]),
                                             ("revfirst16", digest[:16][::-1])):
                            yield (("HMAC", key_form, field, domain.decode(),
                                    algorithm, view), output)


controls = list(emit(prior_control, control))
assert len(controls) == 24300
control_hits = [cfg for cfg, v in controls if v.hex().upper() == control["PAYLOAD"]]
assert control_hits == []
# Synthetic, source-input-only positive from within the frozen family.
planted_config = ("HMAC", "raw16", "full_header", "H17|", "sha256", "first16")
planted = next(v for cfg, v in controls if cfg == planted_config)
assert [cfg for cfg, v in controls if v == planted and cfg == planted_config] == [
    planted_config
]

mask = bytes.fromhex(routing["K04"]["masked_component"])
assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
target_digest = acceptance["slot_sha256"]["K04"]
target_count = 0
target_hits = []
for context, previous in (("prior LABEL ACK1", prior_label),
                          ("prior RECOVER REQUESTED1", prior_request)):
    for cfg, payload in emit(previous, selected):
        target_count += 1
        key = bytes(x ^ y for x, y in zip(payload, mask))
        if hashlib.sha256(key).hexdigest() == target_digest:
            target_hits.append((context, cfg, key.hex().upper()))
assert target_count == 48600
print(json.dumps({
    "source_sha256": hashlib.sha256(source).hexdigest(),
    "heldout_control": "PS-261003-0420 attempt2 RECOVER ACK",
    "heldout_full_coupon_checks": len(controls),
    "heldout_exact_matches": len(control_hits),
    "selected_event": "PS-261003-0417 attempt2 RECOVER ACK",
    "selected_full_K04_checks": target_count,
    "original_K04_matches": target_hits,
    "synthetic_KDF_positive": True,
    "selected_copied_payload_used_for_generation": False
}, indent=2))
