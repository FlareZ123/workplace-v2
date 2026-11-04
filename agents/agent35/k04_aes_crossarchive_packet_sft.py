"""H17 AES-128/256 archive-keyed label emitter source holdout; original source read-only."""
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
SOURCE = {
    "K01_signed": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02_digest": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K02_raw": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K03_digest": "1384AF96E25D6ADA666209CB55E062FA",
    "K05_raw": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06_revC": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07_digest": "93495F5E425AB8E592123DABAEB68545",
    "K07_raw": "8947CEDCB9CC73BAB7E87BE63302C5C9",
    "K04_route_mask": MASK.hex(),
    "K08_desk_nonce": "5F933DA6A1BD03C32DA5CBC25344F497",
}
PDF_AES = bytes.fromhex("d1b7c63b804f0703487318ba517f296489d6c4cab523ea8a19bacc47c01c2300")

def records(path):
    src = Path(path).read_bytes()
    assert hashlib.sha256(src).hexdigest() == SPOOL_SHA
    rows = []
    rex = re.compile(
        r"^(?P<iso>\S+) JOB=PS-261003-(?P<job>\d+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\w+) CLASS=(?P<cls>\w+) PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\w+)$"
    )
    for line in src.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        m = rex.fullmatch(line)
        assert m, line
        row = m.groupdict()
        row["bytes"] = bytes.fromhex(row["payload"])
        row["job"] = int(row["job"])
        row["attempt"] = int(row["attempt"])
        rows.append(row)
    assert len(rows) == 133
    assert [(r["state"], r["cls"], r["attempt"]) for r in rows[128:131]] == [
        ("REQUESTED", "RECOVER", 1), ("ACK", "RECOVER", 2),
        ("REQUESTED", "RECOVER", 3)]
    return rows

def derive_keys():
    seeds = {k: bytes.fromhex(v) for k, v in SOURCE.items()}
    seeds.update({"PDF_AES256": PDF_AES, "PDF_AES_first16": PDF_AES[:16],
                  "PDF_AES_last16": PDF_AES[16:]})
    seeds.update({k + "_SHA256": hashlib.sha256(v).digest()
                  for k, v in tuple(seeds.items()) if len(v) == 16})
    assert len(seeds) == 25
    return seeds

def inputs(row):
    job = "PS-261003-" + str(row["job"]).zfill(4)
    cls, state, dest, attempt = row["cls"], row["state"], row["dest"], str(row["attempt"])
    moment = row["iso"].replace("+00:00", "Z")
    full = [
        job, job + "|" + cls, job + "|" + state + "|" + cls, job + "|" + attempt,
        job + "|" + attempt + "|" + state + "|" + cls + "|" + dest,
        job + "|" + attempt + "|" + state + "|" + cls + "|" + dest + "|" + moment,
        moment, moment + "|" + job, cls + "|" + dest + "|" + attempt,
        f"H17/{job}/{state}/{cls}/{attempt}/{dest}",
        json.dumps({"JOB": job, "ATTEMPT": row["attempt"], "CLASS": cls,
                    "DEST": dest, "STATE": state}, sort_keys=True, separators=(",", ":")),
    ]
    hashed = []
    for value in full:
        b = value.encode("ascii")
        hashed.extend((
            hashlib.sha256(b).digest()[:16], hashlib.md5(b).digest(),
            hashlib.blake2b(b, digest_size=16).digest(),
            b[:16].ljust(16, b"\0"), b[-16:].rjust(16, b"\0")))
    timestamp = datetime.fromisoformat(moment.replace("Z", "+00:00")).timestamp()
    for number in (row["job"], row["job"] - 300, row["attempt"], int(timestamp),
                   int(timestamp // 300)):
        hashed.extend((int(number).to_bytes(16, "big"),
                       int(number).to_bytes(16, "little")))
    assert len(hashed) == 65
    return hashed

def run(path):
    rows = records(path)
    keys = derive_keys()
    blocks = [inputs(row) for row in rows]
    count = Counter()
    original_checks = 0
    target_hits = 0
    for _, key in keys.items():
        encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
        for mode in range(65):
            matches = 0
            for rid, row in enumerate(rows):
                if rid == 129:
                    continue
                prediction = encryptor.update(blocks[rid][mode])
                original_checks += 1
                matches += prediction == row["bytes"]
            count[matches] += 1
            coupon = encryptor.update(blocks[129][mode])
            component = bytes(a ^ b for a, b in zip(coupon, MASK))
            target_hits += hashlib.sha256(component).digest() == TARGET
        assert not encryptor.finalize()
    assert original_checks == 214500
    assert count == Counter({0: 1625}) and target_hits == 0
    print("ORIGINAL_AES_KEY_COUNT", len(keys), "INPUT_LAYOUTS", 65,
          "INDEPENDENT_PRINTER_CHECKS", original_checks)
    print("MATCHING_UNDISPUTED_PACKET_COUNTS", dict(count),
          "ORIGINAL_K04_COMMITMENT_HITS", target_hits)
    testblock = blocks[0][5]
    planted = Cipher(algorithms.AES(keys["K01_signed"]), modes.ECB()).encryptor().update(testblock)
    planted_target = hashlib.sha256(bytes(a ^ b for a, b in zip(planted, MASK))).digest()
    assert planted_target != TARGET
    assert planted == Cipher(algorithms.AES(keys["K01_signed"]), modes.ECB()).encryptor().update(testblock)
    print("SYNTHETIC_AES_WHOLE_PACKET_AND_K04_ROUTE_POSITIVE PASS")

if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    run(p)
