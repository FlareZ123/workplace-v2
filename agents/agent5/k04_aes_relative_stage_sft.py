"""SFT: source-relative AES/XOR coupon issuer; one complete historical heldout.
Run from a workplace-v2 checkout using Python and cryptography. Read-only originals.
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2]
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def view(a, order):
    if order == 0: return a
    if order == 1: return a[::-1]
    if order == 2: return b"".join(a[i:i+4][::-1] for i in range(0,16,4))
    return b"".join(a[i:i+4] for i in range(12,-1,-4))

def read_original():
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
    candidate = json.loads((ROOT / "candidate.json").read_text())
    assert route["K04"]["masked_component"] == MASK.hex().upper()
    assert route["K08"]["desk_nonce"] == NONCE.hex().upper()
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    assert candidate["K04"] is None and candidate["K08"] is None
    keys = {}
    for name, value in candidate.items():
        if value is not None:
            key = bytes.fromhex(value)
            assert hashlib.sha256(key).hexdigest() == acceptance["slot_sha256"][name]
            keys[name] = key
    assert set(keys) == {"K01", "K02", "K03", "K05", "K06", "K07"}
    keys["mask"] = MASK
    keys["nonce"] = NONCE
    regex = re.compile(
        r"^(?P<time>\S+) JOB=PS-261003-(?P<job>\d+) "
        r"ATTEMPT=(?P<attempt>\d+) STATE=(?P<state>\S+) "
        r"CLASS=(?P<class>\S+) PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)$"
    )
    rows = []
    for line in spool.decode("ascii").splitlines()[1:]:
        match = regex.fullmatch(line)
        assert match, line
        row = match.groupdict()
        row["job"] = int(row["job"])
        row["attempt"] = int(row["attempt"])
        row["bytes"] = bytes.fromhex(row["payload"])
        rows.append(row)
    assert len(rows) == 133
    north, south, watch = rows[129], rows[131], rows[132]
    assert (north["job"], north["attempt"], north["state"], north["class"]) == (417, 2, "ACK", "RECOVER")
    assert (south["job"], south["attempt"], south["state"], south["class"]) == (448, 1, "ACK", "RECOVER")
    assert (watch["job"], watch["attempt"], watch["state"], watch["class"]) == (420, 2, "ACK", "RECOVER")
    assert south["bytes"].hex().upper() == "234BE186E97EE05830909790E336109E"
    assert watch["bytes"].hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
    return keys, north, south, watch

def blocks(row):
    job = f"PS-261003-{row['job']:04d}"
    moment = row["time"].replace("+00:00", "Z")
    attempt = str(row["attempt"])
    cls, dest, state = row["class"], row["dest"], row["state"]
    labels = [
        job, job + "|" + attempt, job + "|" + cls + "|" + dest,
        job + "|" + attempt + "|" + state + "|" + cls + "|" + dest,
        job + "/" + cls + "/" + dest,
        f"H17/{job}/{attempt}/{state}/{cls}/{dest}",
        moment, moment + "|" + job, job + "|" + moment,
        f"{row['job']}|{cls}|{dest}|{attempt}",
        f"{row['job']}/{attempt}", f"{row['job']}:{cls}:{dest}",
        json.dumps({"job": job, "attempt": row["attempt"], "class": cls,
                    "dest": dest, "state": state}, sort_keys=True, separators=(",", ":")),
    ]
    out = []
    for label in labels:
        b = label.encode("ascii")
        digest = hashlib.sha256(b).digest()
        out.extend((hashlib.md5(b).digest(), digest[:16], digest[-16:],
                    hashlib.blake2s(b, digest_size=16).digest(),
                    b[:16].ljust(16,b"\x00"), b[-16:].rjust(16,b"\x00")))
    epoch = int(datetime.fromisoformat(moment.replace("Z","+00:00")).timestamp())
    for n in (row["job"], row["job"]-300, epoch, epoch//300, row["attempt"]):
        out.extend((n.to_bytes(16,"big"), n.to_bytes(16,"little"),
                    n.to_bytes(4,"big")*4, n.to_bytes(4,"little")*4))
    assert len(out) == 98
    return out

def run():
    keys, north, south, watch = read_original()
    source_blocks = blocks(south), blocks(watch), blocks(north)
    planted_pad = hashlib.sha256(b"independent planted H17 AES pad").digest()[:16]
    unique_components = set()
    models = source_hits = target_hits = planted = 0
    for name, key in keys.items():
        for layout in range(98):
            for presentation in range(4):
                triplet = [view(b[layout], presentation) for b in source_blocks]
                cipher = Cipher(algorithms.AES(key), modes.ECB())
                for direction in ("encrypt", "decrypt"):
                    op = cipher.encryptor() if direction == "encrypt" else cipher.decryptor()
                    e_south, e_watch, e_north = [op.update(b) for b in triplet]
                    assert op.finalize() == b""
                    pad = xor(south["bytes"], e_south)
                    predicted_watch = xor(e_watch, pad)
                    component = xor(xor(e_north, pad), MASK)
                    source_hits += predicted_watch == watch["bytes"]
                    target_hits += hashlib.sha256(component).hexdigest() == K04_SHA
                    unique_components.add(component)
                    # Whole-object positive: one source south, one withheld watch, one target north.
                    synthetic_south = xor(e_south, planted_pad)
                    synthetic_watch = xor(e_watch, planted_pad)
                    synthetic_north = xor(e_north, planted_pad)
                    recovered = xor(synthetic_south, e_south)
                    assert xor(e_watch, recovered) == synthetic_watch
                    assert xor(e_north, recovered) == synthetic_north
                    planted += 1
                    models += 1
                    if hashlib.sha256(component).hexdigest() == K04_SHA:
                        print("ORIGINAL_K04_MATCH", name, layout, presentation,
                              direction, component.hex().upper())
    assert models == 8*98*4*2 == 6272 and planted == models
    result = {"source_models": models, "distinct_complete_K04": len(unique_components),
              "withheld_WATCH_SPARE_exact": source_hits,
              "original_K04_commitment_hits": target_hits,
              "planted_three_route_controls": planted}
    assert result == {"source_models":6272, "distinct_complete_K04":5089,
                      "withheld_WATCH_SPARE_exact":0, "original_K04_commitment_hits":0,
                      "planted_three_route_controls":6272}
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run()
