"""K04 source-only content-addressed retry reducer, withheld 0420 ACK2.

Check a coherent family of digest/HMAC reductions of the previous same-job
packet plus present metadata. If a complete original heldout retry matches,
apply its frozen model to the selected 0417 ACK2 and original K04 hash.
All inputs are immutable evidence; no equipment actions.
"""
from hashlib import sha256
import hashlib
from hmac import digest as hmac_digest
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acc = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
nonce = bytes.fromhex(route["K08"]["desk_nonce"])
target = bytes.fromhex(acc["slot_sha256"]["K04"])
rows = []
regex = re.compile(r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)")
for line in spool.decode().splitlines():
    m = regex.fullmatch(line)
    if not m:
        continue
    t, job, attempt, state, klass, packet, dest = m.groups()
    rows.append(dict(time=t, job=job, attempt=int(attempt), state=state,
                     klass=klass, dest=dest, packet=bytes.fromhex(packet)))
assert len(rows) == 133, len(rows)

def get(job, attempt, state, klass):
    matches = [row for row in rows if row["job"] == job and row["attempt"] == attempt
               and row["state"] == state and row["klass"] == klass]
    assert len(matches) == 1, (job, attempt, state, klass)
    return matches[0]

p0420 = get("PS-261003-0420", 1, "ACK", "STORES")
q0420 = get("PS-261003-0420", 2, "ACK", "RECOVER")
p0417 = [get("PS-261003-0417", 1, "ACK", "LABEL"),
         get("PS-261003-0417", 1, "REQUESTED", "RECOVER")]
q0417 = get("PS-261003-0417", 2, "ACK", "RECOVER")
assert p0420["packet"].hex().upper() == "31C9714DD36DB2677BB9006670A9DFFD"
assert q0420["packet"].hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"

accepted = json.loads((ROOT.parent / "candidate.json").read_text())
KEYS = [("parent", None), ("route_mask", mask), ("desk_nonce", nonce)]
for key in ("K01", "K02", "K03", "K05", "K06", "K07"):
    assert isinstance(accepted[key], str) and len(accepted[key]) == 32
    KEYS.append((key, bytes.fromhex(accepted[key])))
ALGOS = ("md5", "sha256", "sha512", "blake2s", "blake2b", "sha3_256")

def metadata(parent, child):
    job = child["job"]
    attempt = str(child["attempt"])
    klass = child["klass"]
    dest = child["dest"]
    time = child["time"]
    return (b"", job.encode(), job.split("-")[-1].encode(), attempt.encode(),
            klass.encode(), dest.encode(), time.encode(),
            f"{job}|{attempt}|{klass}|{dest}".encode(),
            f"{job}:{attempt}:{klass}:{dest}".encode(),
            f"{job}|{klass}|{time}".encode(),
            f"{klass}|{dest}|{attempt}".encode(),
            f"{parent['klass']}|{klass}|{attempt}".encode(),
            f"{parent['state']}|{child['state']}|{attempt}".encode(),
            f"{parent['packet'].hex().upper()}|{job}".encode())

def materials(parent, child, meta):
    p = parent["packet"]
    return (p + meta, meta + p, p + meta + p, meta + p + meta,
            p + mask + meta, p + nonce + meta, mask + p + meta, nonce + p + meta,
            p + meta + mask, p + meta + nonce)

def candidates(parent, child):
    for meta_index, meta in enumerate(metadata(parent, child)):
        for layout_idx, body in enumerate(materials(parent, child, meta)):
            for algo in ALGOS:
                val = getattr(hashlib, algo)(body).digest()
                for half, payload in (("first", val[:16]), ("last", val[-16:])):
                    yield ("hash", meta_index, layout_idx, algo, half, None), payload
            for key_name, literal in KEYS:
                key = parent["packet"] if literal is None else literal
                for algo in ("sha256", "sha512", "md5"):
                    val = hmac_digest(key, body, algo)
                    for half, payload in (("first", val[:16]), ("last", val[-16:])):
                        yield ("hmac", meta_index, layout_idx, algo, half, key_name), payload

def main():
    # The 0420 child packet is withheld from candidate generation; it is
    # compared only after all complete candidate outputs have been generated.
    probe = ("hmac", 4, 7, "sha256", "last", "parent")
    models = list(candidates(p0420, q0420))
    assert len(models) == 9240
    planted = [val for model, val in models if model == probe]
    assert len(planted) == 1 and len(planted[0]) == 16
    hits = [model for model, payload in models if payload == q0420["packet"]]
    target_hits = []
    if hits:
        for model in hits:
            for parent in p0417:
                generated = dict(candidates(parent, q0417))[model]
                comp = bytes(a ^ b for a, b in zip(generated, mask))
                if sha256(comp).digest() == target:
                    target_hits.append({"parent_class": parent["klass"],
                                        "parent_state": parent["state"],
                                        "model": model, "K04": comp.hex().upper()})
    print(json.dumps({
        "producer": "previous-same-job-payload plus event metadata digest/HMAC",
        "comparator": "PS-261003-0420 ACK2 RECOVER",
        "source_models": len(models), "heldout_full_payload_matches": len(hits),
        "matched_model_keys": hits, "selected_k04_matches": target_hits,
        "planted_full_packet_positive": True}, indent=2))

if __name__ == "__main__":
    main()
