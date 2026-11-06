"""Read-only H-17 K04 UUIDv3/v5 archival-name issuer experiment.

Usage: python agent16_k04_uuid_archival_name_sft.py /path/to/h17-archive-dump.zip
No original evidence, route, commitment or canonical candidate is modified.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
import uuid
from zipfile import ZipFile

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROUTE_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
TARGET_SHA256 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
K_ACCEPTED = (
    "049AAB2E1CDE7A82CD7C60234303C91A",  # Original validated K01
    "0D7E3AB56FB75DA3EB0E2E06786D239E",  # K02
    "1384AF96E25D6ADA666209CB55E062FA",  # K03
    "FF8B78200A56E8586DCDA00EF01E4572",  # K05
    "5DBF40EE52FAAED9A536D3326CF0D95A",  # K06
    "93495F5E425AB8E592123DABAEB68545",  # K07
)


def layouts(value: bytes):
    return (
        value,
        uuid.UUID(bytes=value).bytes_le,
        value[::-1],
        b"".join(value[i:i+4] for i in (12, 8, 4, 0)),
        b"".join(value[i:i+4][::-1] for i in (0, 4, 8, 12)),
    )


def main(path: str):
    with ZipFile(path) as z:
        spool = z.read("evidence/print/spool-reconstruction.log")
        routing = z.read("evidence/recovery-routing.json")
        labels = z.read("evidence/archive-labels.ini")
        assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA256
        assert hashlib.sha256(routing).hexdigest() == ROUTE_SHA256
        route = json.loads(routing)
        assert b"ESC-N=PS-261003-0417" in labels

    rows = []
    for line in spool.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        obj = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|PAYLOAD|DEST)=([^ ]+)", line))
        obj["timestamp"] = line.split(" ", 1)[0]
        rows.append(obj)
    assert len(rows) == 133
    selected = [r for r in rows if r["JOB"] == "PS-261003-0417" and r["ATTEMPT"] == "2" and r["STATE"] == "ACK" and r["CLASS"] == "RECOVER"]
    assert len(selected) == 1 and selected[0]["PAYLOAD"] == "A9A9DC5731A5E2AE879C47215C2559D5"
    chosen = selected[0]
    bad_copy = bytes.fromhex(chosen["PAYLOAD"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert len(mask) == 16
    assert hashlib.sha256(bytes(a ^ b for a, b in zip(bad_copy, mask))).hexdigest() != TARGET_SHA256

    def uuid_version_variant(v: bytes) -> bool:
        return v[6] >> 4 in (3, 5) and v[8] >> 6 == 2

    ordinary = [r for r in rows if r is not chosen]
    ordinary_uuid = sum(uuid_version_variant(bytes.fromhex(r["PAYLOAD"])) for r in ordinary)
    ordinary_anylayout = sum(any(uuid_version_variant(v) for v in layouts(bytes.fromhex(r["PAYLOAD"]))) for r in ordinary)

    baseline_names = [
        chosen["JOB"], chosen["JOB"].split("-")[-1], "ESC-N", "ESCN",
        "H-17", "H17", route["envelope_id"], "IR-261003-H17",
        chosen["timestamp"], "2026-10-03", "20261003", "18:02", "1802",
        chosen["ATTEMPT"], "ACK", "RECOVER", "bench", "PS-261003-0417-2",
        "REC8/1", "K04", "coupon", "escrow coupon",
    ]
    atom = [chosen["JOB"], "ESC-N", "2", "ACK", "RECOVER", "bench", chosen["timestamp"]]
    names = set(baseline_names)
    for s in ("", "|", ":", "/", "-", "_", " ", ";", "#"):
        for size in (2, 3):
            for tup in itertools.permutations(atom, size):
                names.add(s.join(tup))
    for name in list(names):
        names.add(name.lower())
        names.add(name.upper())

    namespace_fields = {
        "RFC_DNS": uuid.NAMESPACE_DNS.bytes,
        "RFC_URL": uuid.NAMESPACE_URL.bytes,
        "RFC_OID": uuid.NAMESPACE_OID.bytes,
        "RFC_X500": uuid.NAMESPACE_X500.bytes,
        "route_K04_mask": mask,
        "route_K08_nonce": bytes.fromhex(route["K08"]["desk_nonce"]),
        "copied_ACK2": bad_copy,
    }
    for i, k in enumerate(K_ACCEPTED):
        namespace_fields[f"accepted_component_{i}"] = bytes.fromhex(k)
    for name, index in (("pre_REQUESTED1", 128), ("post_REQUESTED3", 130),
                        ("ESC_S_ACK", 131), ("WATCH_SPARE_ACK", 132)):
        namespace_fields[name] = bytes.fromhex(rows[index]["PAYLOAD"])

    coupons = set()
    hmask = bytes(mask)
    original_hits = []
    produced = 0
    for ns_label, ns in namespace_fields.items():
        for name in names:
            raw = name.encode("utf-8")
            for version, hash_fn in ((3, hashlib.md5), (5, hashlib.sha1)):
                digest = bytearray(hash_fn(ns + raw).digest()[:16])
                digest[6] = (digest[6] & 15) | version << 4
                digest[8] = (digest[8] & 63) | 128
                for layout_index, coupon in enumerate(layouts(bytes(digest))):
                    produced += 1
                    coupons.add(coupon)
                    reduced = bytes(a ^ b for a, b in zip(coupon, hmask))
                    if hashlib.sha256(reduced).hexdigest() == TARGET_SHA256:
                        original_hits.append((ns_label, name, version, layout_index, reduced.hex().upper()))

    plant_ns = namespace_fields["RFC_URL"]
    plant_name = chosen["JOB"] + ":2:ACK"
    assert plant_name in names
    planted_uuid = uuid.uuid5(uuid.UUID(bytes=plant_ns), plant_name).bytes
    planted_coupon = layouts(planted_uuid)[1]
    synthetic_digest = hashlib.sha256(bytes(a ^ b for a,b in zip(planted_coupon, hmask))).digest()
    planted_hits = sum(hashlib.sha256(bytes(a ^ b for a,b in zip(coupon, hmask))).digest() == synthetic_digest for coupon in coupons)
    assert planted_hits == 1
    assert not original_hits
    digest = hashlib.sha256(b"".join(sorted(coupons))).hexdigest()
    print(json.dumps({
        "source_control": "PASS",
        "selected": "PS-261003-0417/RECOVER/ACK2",
        "ordinary_packets": len(ordinary),
        "ordinary_uuid_v3_v5_canonical": ordinary_uuid,
        "ordinary_uuid_any_five_layouts": ordinary_anylayout,
        "copied_selected_uuid_v3_v5": uuid_version_variant(bad_copy),
        "namespace_count": len(namespace_fields),
        "distinct_names": len(names),
        "candidate_assignments": produced,
        "distinct_coupons": len(coupons),
        "sorted_coupon_sha256": digest,
        "original_k04_matches": original_hits,
        "planted_complete_candidate_hits": planted_hits,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
