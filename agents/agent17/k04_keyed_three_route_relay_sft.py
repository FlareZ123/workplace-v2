"""Three-route keyed printer relay: source-calibrated K04 full-coupon candidates.

Read-only SFT for original H-17 repository resources. Historical printer family
is exploratory; no firmware evidence identifies such an issuer.
"""
from pathlib import Path
from itertools import product
import hashlib
import hmac
import json
import re

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "resources" / "evidence"
ACCEPT = json.loads((ROOT / "resources" / "acceptance.json").read_text())
ROUTE = json.loads((E / "recovery-routing.json").read_text())
CANDIDATE = json.loads((ROOT / "candidate.json").read_text())
MASK = bytes.fromhex(ROUTE["K04"]["masked_component"])
TARGET = ACCEPT["slot_sha256"]["K04"]

assert hashlib.sha256((E / "print/spool-reconstruction.log").read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256((E / "recovery-routing.json").read_bytes()).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
for slot in ("K01", "K02", "K03", "K05", "K06", "K07"):
    assert hashlib.sha256(bytes.fromhex(CANDIDATE[slot])).hexdigest() == ACCEPT["slot_sha256"][slot]

lines = (E / "print/spool-reconstruction.log").read_text().splitlines()
specs = (
    ("PS-261003-0417", 2, "ESC-N", "L-29/N", "FA-17", "H17-POL-17/A3"),
    ("PS-261003-0448", 1, "ESC-S", "L-29/S", "LV-42", "CS-18/5"),
    ("PS-261003-0420", 2, "WATCH-SPARE", "L-29/W", "ST-09", "STORES/FLT"),
)
records = []
for job, attempt, lane, ret, acct, filing in specs:
    rows = [s for s in lines if f"JOB={job} " in s and f"ATTEMPT={attempt} " in s]
    assert len(rows) == 1
    line = rows[0]
    f = dict(re.findall(r"(\w+)=(\S+)", line))
    assert f["STATE"] == "ACK" and f["CLASS"] == "RECOVER"
    records.append(dict(job=job, suffix=job[-4:], lane=lane, ret=ret,
                        acct=acct, filing=filing, timestamp=line.split()[0],
                        date=line[:10], attempt=str(attempt),
                        cls=f["CLASS"], dest=f["DEST"],
                        payload=bytes.fromhex(f["PAYLOAD"]) if lane != "ESC-N" else None))
north, south, watch = records
assert south["payload"] == bytes.fromhex("234BE186E97EE05830909790E336109E")
assert watch["payload"] == bytes.fromhex("432475F72A62DB39F3D5693E2C937FA4")

fields = (
    ("job",), ("suffix",), ("job", "attempt"), ("job", "timestamp"),
    ("lane", "job"), ("lane", "job", "attempt"), ("job", "lane", "acct"),
    ("lane", "ret", "acct", "filing"), ("job", "lane", "ret", "acct", "filing"),
    ("job", "attempt", "cls", "dest"), ("lane", "job", "attempt", "cls", "dest"),
    ("job", "acct", "filing"), ("job", "filing", "timestamp"),
    ("date", "job", "attempt"), ("lane", "filing"), ("ret", "job"),
    ("filing", "ret", "job"), ("acct", "job", "attempt"),
    ("cls", "dest", "job"), ("timestamp", "lane", "job"),
)
keys = {k: bytes.fromhex(CANDIDATE[k]) for k in ("K01", "K02", "K03", "K05", "K06", "K07")}
keys["mask"] = MASK
keys["nonce"] = bytes.fromhex(ROUTE["K08"]["desk_nonce"])
algorithms = ("hmac256", "hmac512", "blake2s", "blake2b", "sha-prefix", "sha-suffix", "shake128")
views = ("first", "last", "firstrev", "lastrev")


def digest(key, msg, method):
    if method == "hmac256":
        return hmac.new(key, msg, "sha256").digest()
    if method == "hmac512":
        return hmac.new(key, msg, "sha512").digest()
    if method == "blake2s":
        return hashlib.blake2s(msg, key=key).digest()
    if method == "blake2b":
        return hashlib.blake2b(msg, key=key).digest()
    if method == "sha-prefix":
        return hashlib.sha256(key + msg).digest()
    if method == "sha-suffix":
        return hashlib.sha256(msg + key).digest()
    return hashlib.shake_128(key + msg).digest(32)


def output(d, mode):
    b = d[:16] if mode.startswith("first") else d[-16:]
    return b[::-1] if mode.endswith("rev") else b


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


count = replays = hits = 0
for keyname, key in keys.items():
    for alg in algorithms:
        for names, sep, prefix, reverse, upper in product(
                fields, ("", "|", ":", "/", "-"), ("", "H17", "K04", "REC8", "ESC", "H-17"), (False, True), (False, True)):
            chosen = names[::-1] if reverse else names
            def message(record):
                parts = ([prefix] if prefix else []) + [record[n] for n in chosen]
                s = sep.join(parts)
                return (s.upper() if upper else s).encode("ascii")
            ds, dw, dn = (digest(key, message(r), alg) for r in (south, watch, north))
            for mode in views:
                ps, pw, pn = (output(d, mode) for d in (ds, dw, dn))
                pad = xor(south["payload"], ps)
                count += 1
                replays += xor(pw, pad) == watch["payload"]
                component = xor(xor(pn, pad), MASK)
                if hashlib.sha256(component).hexdigest() == TARGET:
                    hits += 1
                    print("TARGET MATCH", keyname, alg, chosen, sep, prefix, upper, mode, component.hex().upper())

for alg, mode in product(algorithms, views):
    key = b"synthetic-only-test-key"
    pad = bytes(range(16))
    d1, d2, d3 = (output(digest(key, s, alg), mode) for s in (b"S", b"W", b"N"))
    retained_s, retained_w, hidden_n = (xor(x, pad) for x in (d1, d2, d3))
    recovered_pad = xor(retained_s, d1)
    assert xor(d2, recovered_pad) == retained_w
    assert xor(d3, recovered_pad) == hidden_n

assert count == 537600
print(json.dumps(dict(models=count, complete_watch_replays=replays,
                      original_k04_hits=hits, planted_controls=28), sort_keys=True))
