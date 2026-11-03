"""Read-only H-17 K04 complete-candidate same-job digest family.
Run: python agents/agent22/k04_samejob_digest_sft.py [resources_dir]
The historical records do not attest a hash-chain producer.
"""
import hashlib
import hmac
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOLVED = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}

def main(root):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    rows = []
    for line in raw.decode("ascii").splitlines():
        if " JOB=PS-261003-0417 " in line:
            timestamp, *tokens = line.split()
            row = dict(token.split("=", 1) for token in tokens)
            row["timestamp"] = timestamp
            rows.append(row)
    assert len(rows) == 4
    assert [(r["ATTEMPT"], r["CLASS"], r["STATE"]) for r in rows] == [
        ("1", "LABEL", "ACK"), ("1", "RECOVER", "REQUESTED"),
        ("2", "RECOVER", "ACK"), ("3", "RECOVER", "REQUESTED")]
    assert rows[2]["PAYLOAD"] == "A9A9DC5731A5E2AE879C47215C2559D5"
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    acc = json.loads((root / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = bytes.fromhex(acc["slot_sha256"]["K04"])
    keys = {name: bytes.fromhex(value) for name, value in SOLVED.items()}
    assert all(hashlib.sha256(value).hexdigest() == acc["slot_sha256"][name]
               for name, value in keys.items())
    keys["route_mask"] = mask
    keys["desk_nonce"] = bytes.fromhex(route["K08"]["desk_nonce"])
    payloads = [bytes.fromhex(row["PAYLOAD"]) for row in rows]
    keys.update({f"job_{i}": value for i, value in enumerate(payloads)})

    counts = Counter()
    found = []
    planted_digest = None
    planted_positive = 0
    first_example = None
    for cohort, indices in (("causal", (0, 1)),
                            ("retrospective", (0, 1, 2, 3))):
        for length in range(1, len(indices) + 1):
            for order in itertools.permutations(indices, length):
                for view in ("raw", "upperhex", "lowerhex"):
                    parts = [payloads[i] if view == "raw" else
                             payloads[i].hex().encode("ascii") if view == "lowerhex" else
                             payloads[i].hex().upper().encode("ascii") for i in order]
                    for sep in (b"", b"|", b":", b" "):
                        body = sep.join(parts)
                        for prefix in (b"", b"ESC-N|", b"REC8/1|", b"H17|",
                                       b"PS-261003-0417|"):
                            for suffix in (b"", b"|RECOVER", b"|2",
                                           b"|2026-10-03T18:02:00Z"):
                                msg = prefix + body + suffix
                                digests = [
                                    ("MD5", hashlib.md5(msg).digest()),
                                    ("SHA1", hashlib.sha1(msg).digest()),
                                    ("SHA256", hashlib.sha256(msg).digest()),
                                    ("BLAKE2S16", hashlib.blake2s(msg, digest_size=16).digest())]
                                digests += [("HMAC256:" + k, hmac.digest(v, msg, "sha256"))
                                            for k, v in keys.items()]
                                for algorithm, digest in digests:
                                    views = [("first", digest[:16])]
                                    if len(digest) > 16:
                                        views.append(("last", digest[-16:]))
                                    for truncation, coupon in views:
                                        component = bytes(x ^ y for x, y in zip(coupon, mask))
                                        hashed = hashlib.sha256(component).digest()
                                        if planted_digest is None:
                                            planted_digest = hashed
                                            first_example = (cohort, order, view, algorithm,
                                                             truncation, coupon.hex().upper())
                                        planted_positive += hashed == planted_digest
                                        counts[cohort] += 1
                                        counts["direct_component"] += 1
                                        label = (cohort, order, view, sep.decode(), prefix.decode(),
                                                 suffix.decode(), algorithm, truncation)
                                        if hashed == target:
                                            found.append(("route_xor", label, component.hex().upper()))
                                        if hashlib.sha256(coupon).digest() == target:
                                            found.append(("direct_component", label, coupon.hex().upper()))
    assert counts["causal"] == 28800
    assert counts["retrospective"] == 460800
    assert counts["direct_component"] == 489600
    assert planted_positive >= 1
    print(json.dumps({
        "result": "MATCH" if found else "NO_MATCH",
        "source_spool_sha256": SPOOL_SHA,
        "tested_complete_derivations": counts["direct_component"],
        "tested_route_xor_commitments": counts["direct_component"],
        "tested_direct_component_commitments": counts["direct_component"],
        "cohorts": {"causal": counts["causal"], "retrospective": counts["retrospective"]},
        "planted_positive_checks": planted_positive,
        "planted_example": first_example,
        "original_matches": found,
    }, indent=2))

if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) == 2
         else Path(__file__).resolve().parents[2] / "resources")
