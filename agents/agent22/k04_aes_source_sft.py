"""Exploratory source-constrained AES coupon producer and copy-stage test.

Run: python agents/agent22/k04_aes_source_sft.py [resources]
The original archive does not attest an AES printer producer.
Requires the cryptography package. Historical source remains read-only.
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOLVED = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}

def forms(r, i):
    job = r["JOB"]
    j = int(job.rsplit("-", 1)[-1])
    t = int(datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).timestamp())
    metadata = "|".join(r[k] for k in ("JOB", "ATTEMPT", "CLASS", "DEST", "STATE", "timestamp")).encode()
    return {
        "seq_be": i.to_bytes(16, "big"),
        "seq_le": i.to_bytes(16, "little"),
        "job_be": j.to_bytes(16, "big"),
        "job_le": j.to_bytes(16, "little"),
        "time_be": t.to_bytes(16, "big"),
        "time_le": t.to_bytes(16, "little"),
        "job_ascii": job.encode()[:16].ljust(16, b"\0"),
        "suffix_ascii": job[-4:].encode().ljust(16, b"\0"),
        "meta_sha": hashlib.sha256(metadata).digest()[:16],
        "meta_md5": hashlib.md5(metadata).digest(),
        "jobtime_sha": hashlib.sha256(f'{job}|{r["timestamp"]}'.encode()).digest()[:16],
        "suffix_seq_be": (j * 256 + int(r["ATTEMPT"])).to_bytes(16, "big"),
    }

def run(root):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    rows = []
    for line in raw.decode("ascii").splitlines():
        if not line.startswith("2026"):
            continue
        timestamp, *tokens = line.split()
        r = dict(token.split("=", 1) for token in tokens)
        r["timestamp"] = timestamp
        rows.append(r)
    assert len(rows) == 133
    assert (rows[129]["JOB"], rows[129]["ATTEMPT"], rows[129]["STATE"],
            rows[129]["CLASS"]) == ("PS-261003-0417", "2", "ACK", "RECOVER")
    routing = json.loads((root / "evidence/recovery-routing.json").read_text())
    acc = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = bytes.fromhex(acc["slot_sha256"]["K04"])
    keys = {k: bytes.fromhex(v) for k, v in SOLVED.items()}
    assert all(hashlib.sha256(k).hexdigest() == acc["slot_sha256"][name]
               for name, k in keys.items())
    keys.update(mask=mask, desk_nonce=bytes.fromhex(routing["K08"]["desk_nonce"]))
    jobdata = [bytes.fromhex(r["PAYLOAD"]) for r in rows
               if r["JOB"] == "PS-261003-0417"]
    assert len(jobdata) == 4
    keys.update({f"job{i}": data for i, data in enumerate(jobdata)})
    messages = [forms(r, i) for i, r in enumerate(rows)]
    checks = dict(intact_packet=0, indexed_target=0, job_ecb_target=0,
                  job_cbc_target=0, synthetic=0)
    hits = []
    def acceptance(coupon):
        return hashlib.sha256(coupon).digest() == target
    def reduce(buf, context):
        for stage, component in (
            ("direct", buf),
            ("route_xor", bytes(a ^ b for a, b in zip(buf, mask))),
        ):
            if acceptance(component):
                hits.append((context, stage, component.hex().upper()))
    for keyname, key in keys.items():
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        enc, dec = cipher.encryptor(), cipher.decryptor()
        test = bytes(range(16))
        assert dec.update(enc.update(test)) == test
        checks["synthetic"] += 1
        for form in messages[0]:
            for direction, processor in (("encrypt", enc), ("decrypt", dec)):
                for idx, r in enumerate(rows):
                    predicted = processor.update(messages[idx][form])
                    if idx == 129:
                        reduce(predicted, (keyname, form, direction))
                        checks["indexed_target"] += 2
                    else:
                        checks["intact_packet"] += 1
                        if predicted == bytes.fromhex(r["PAYLOAD"]):
                            hits.append(("INTACT", idx, keyname, form, direction))
        for idx, buf in enumerate(jobdata):
            for direction, processor in (("encrypt", enc), ("decrypt", dec)):
                reduce(processor.update(buf), (keyname, "job", idx, "ECB", direction))
                checks["job_ecb_target"] += 2
                for ivname, iv in (("zero", bytes(16)), ("mask", mask),
                                   ("nonce", keys["desk_nonce"])):
                    cbc = Cipher(algorithms.AES(key), modes.CBC(iv))
                    ctx = cbc.encryptor() if direction == "encrypt" else cbc.decryptor()
                    reduce(ctx.update(buf) + ctx.finalize(),
                           (keyname, "job", idx, "CBC", ivname, direction))
                    checks["job_cbc_target"] += 2
        enc.finalize()
        dec.finalize()
    assert len(keys) == 12 and len(messages[0]) == 12
    assert checks == dict(intact_packet=38016, indexed_target=576,
                          job_ecb_target=192, job_cbc_target=576, synthetic=12)
    assert not hits
    print(json.dumps({"result": "NO_MATCH", "intact_packet_sha256": PIN,
                      "key_count": len(keys), "metadata_block_forms": len(messages[0]),
                      "checks": checks, "hits": hits}, indent=2))

if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1
        else Path(__file__).resolve().parents[2] / "resources")
