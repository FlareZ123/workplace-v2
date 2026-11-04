"""Read-only H17 K04 128-job batch emitter/late-control SFT. Python 3 stdlib."""
from __future__ import annotations
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
evidence = root / "evidence"
spool = (evidence / "print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
routing = json.loads((evidence / "recovery-routing.json").read_text())
targets = json.loads((root / "acceptance.json").read_text())
known = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
for name, value in known.items():
    assert hashlib.sha256(bytes.fromhex(value)).hexdigest() == targets["slot_sha256"][name]
mask = bytes.fromhex(routing["K04"]["masked_component"])
keys = {name: bytes.fromhex(value) for name, value in known.items()}
keys.update({
    "mask": mask,
    "nonce": bytes.fromhex(routing["K08"]["desk_nonce"]),
    "K02pre": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K07pre": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
})
pattern = re.compile(r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$")
rows = []
for line in spool.decode().splitlines():
    match = pattern.match(line)
    if match:
        utc, job, attempt, state, klass, payload, dest = match.groups()
        rows.append(dict(utc=utc, job=job, attempt=int(attempt), state=state,
                         klass=klass, payload=bytes.fromhex(payload), dest=dest))
assert len(rows) == 133
regular, late = rows[:128], rows[128:]
assert [int(x["job"].rsplit("-", 1)[-1]) for x in regular] == list(range(300, 428))
assert len(late) == 5
selected = [x for x in late if x["utc"] == "2026-10-03T18:02:00Z"
            and x["job"] == "PS-261003-0417" and x["attempt"] == 2
            and x["state"] == "ACK" and x["klass"] == "RECOVER"]
assert len(selected) == 1
selected = selected[0]
spare = next(x for x in late if x["job"].endswith("-0420") and x["attempt"] == 2 and x["state"] == "ACK")
south = next(x for x in late if x["job"].endswith("-0448") and x["attempt"] == 1 and x["state"] == "ACK")
assert spare["payload"].hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
assert south["payload"].hex().upper() == "234BE186E97EE05830909790E336109E"
groups = {
    "all": regular, "reverse": list(reversed(regular)),
    "by-class": sorted(regular, key=lambda x: (x["klass"], x["job"])),
    "by-destination": sorted(regular, key=lambda x: (x["dest"], x["job"])),
}
for field in ("klass", "dest"):
    for value in sorted({x[field] for x in regular}):
        groups[field + "=" + value] = [x for x in regular if x[field] == value]
assert len(groups) == 10
batches = {name: b"".join(x["payload"] for x in group) for name, group in groups.items()}
algorithms = ("md5", "sha1", "sha256", "sha512", "sha3_256", "sha3_512", "blake2s", "blake2b")

def labels(x):
    utc, job = x["utc"], x["job"]
    suffix = job.rsplit("-", 1)[-1]
    return (b"", job.encode(), suffix.encode(), utc.encode(), (job + "|" + utc).encode(),
            (job + "|" + x["klass"] + "|" + x["state"] + "|" + str(x["attempt"])).encode(),
            "|".join((utc, job, str(x["attempt"]), x["state"], x["klass"], x["dest"])).encode(),
            "|".join((job, x["klass"], x["dest"], str(x["attempt"]), utc)).encode(),
            int(suffix).to_bytes(4, "little"), int(suffix).to_bytes(4, "big"),
            ("H-17|" + job + "|RECOVER").encode(),
            ("REC8/1|" + job + "|" + str(x["attempt"])).encode())

def emit(x):
    for batch in batches.values():
        b256 = hashlib.sha256(batch).digest()
        b512 = hashlib.sha512(batch).digest()
        for label in labels(x):
            for message in (batch, batch + label, label + batch, b256 + label,
                            label + b256, b512 + label):
                for algorithm in algorithms:
                    digest = getattr(hashlib, algorithm)(message).digest()
                    yield digest[:16]
                    if len(digest) != 16:
                        yield digest[-16:]
                for key in keys.values():
                    for algorithm in ("sha256", "sha512"):
                        digest = hmac.new(key, message, getattr(hashlib, algorithm)).digest()
                        yield digest[:16]
                        yield digest[-16:]

def xor(a, b):
    return bytes(v ^ w for v, w in zip(a, b))

checked, matches = {}, {}
for name, row in (("spare-0420", spare), ("south-0448", south), ("K04", selected)):
    count = 0
    hits = []
    for packet in emit(row):
        count += 1
        if name == "K04":
            if hashlib.sha256(xor(packet, mask)).hexdigest() == targets["slot_sha256"]["K04"]:
                hits.append(packet.hex().upper())
        elif packet == row["payload"]:
            hits.append(packet.hex().upper())
    assert count == 39600
    checked[name], matches[name] = count, hits
    assert not hits

planted = hmac.new(keys["mask"], batches["all"] + selected["job"].encode(), hashlib.sha256).digest()[:16]
synthetic_target = hashlib.sha256(xor(planted, mask)).digest()
assert any(hashlib.sha256(xor(p, mask)).digest() == synthetic_target for p in emit(selected))
print(json.dumps({
    "regular_jobs": len(regular), "late_rows": len(late), "batch_forms": len(batches),
    "public_keys": len(keys), "complete_candidate_assignments": checked,
    "original_commitment_matches": matches, "planted_full_coupon_positive": "PASS",
}, indent=2))
