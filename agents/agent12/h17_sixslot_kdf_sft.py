"""Read-only H-17 K04/K08 complete component HKDF and joint-six-slot hypothesis.

Run from repository root under Python 3, standard library only.
All original records/commitments remain untouched. A planted synthetic HKDF
target checks that the actual enumerator reaches a fully derived candidate.
"""
import hashlib
import hmac
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
A = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02": bytes.fromhex("0D7E3AB56FB75DA3EB0E2E06786D239E"),
    "K03": bytes.fromhex("1384AF96E25D6ADA666209CB55E062FA"),
    "K05": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07": bytes.fromhex("93495F5E425AB8E592123DABAEB68545"),
}
acceptance = json.loads((ROOT / "resources/acceptance.json").read_text())
route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
for key, value in A.items():
    assert hashlib.sha256(value).hexdigest() == acceptance["slot_sha256"][key]
M = bytes.fromhex(route["K04"]["masked_component"])
N = bytes.fromhex(route["K08"]["desk_nonce"])
T = {key: bytes.fromhex(acceptance["slot_sha256"][key]) for key in ("K04", "K08")}
salts = {
    "zeros": bytes(32),
    "mask": M,
    "nonce": N,
    "mask_nonce": M + N,
    "nonce_mask": N + M,
}
infos = {
    "K04": b"K04",
    "K04/LF": b"K04\n",
    "REC8/K04": b"REC8/1|K04",
    "H17/K04": b"H17-IR-261003|K04",
    "ESC-N": b"ESC-N",
    "job": b"PS-261003-0417",
    "job_attempt": b"PS-261003-0417|2",
    "mask": M,
    "nonce": N,
    "rec8": b"CEG-ARCHIVE-RECOVERY/v1\n",
    "K08": b"K08",
    "K08/LF": b"K08\n",
    "REC8/K08": b"REC8/1|K08",
    "H17/K08": b"H17-IR-261003|K08",
    "keeper": b"keeper",
    "desk": b"desk",
    "caption": b"keeper caption",
    "empty": b"",
}
names = sorted(A)
planted_prk = hmac.digest(M, b"".join(A[key] for key in names), "sha256")
planted = hmac.digest(planted_prk, b"K04\x01", "sha256")[:16]
counts = {"K04_direct": 0, "K04_coupon": 0, "K08_direct": 0}
hits = []
planted_hits = []


def test(component: bytes, description: str) -> None:
    assert len(component) == 16
    if component == planted:
        planted_hits.append(description)
    digest = hashlib.sha256(component).digest()
    if digest == T["K04"]:
        hits.append(("K04_direct", description, component.hex().upper()))
    counts["K04_direct"] += 1
    coupon_component = bytes(a ^ b for a, b in zip(component, M))
    if hashlib.sha256(coupon_component).digest() == T["K04"]:
        hits.append(("K04_coupon", description, coupon_component.hex().upper()))
    counts["K04_coupon"] += 1
    if digest == T["K08"]:
        hits.append(("K08_direct", description, component.hex().upper()))
    counts["K08_direct"] += 1


for order in itertools.permutations(names):
    concatenated = b"".join(A[k] for k in order)
    raw_sources = {
        "raw": concatenated,
        "hex": concatenated.hex().upper().encode("ascii"),
        "lf": b"\n".join(A[k].hex().upper().encode("ascii") for k in order) + b"\n",
    }
    for source_label, source in raw_sources.items():
        for info_label, info in infos.items():
            for payload in (source, source + info, info + source):
                digest = hashlib.sha256(payload).digest()
                test(digest[:16], f"sha256h:{order}:{source_label}:{info_label}")
                test(digest[16:], f"sha256t:{order}:{source_label}:{info_label}")
                digest = hashlib.sha512(payload).digest()
                for start in range(0, 64, 16):
                    test(digest[start : start + 16], f"sha512-{start}:{order}:{source_label}:{info_label}")
    for salt_label, salt in salts.items():
        prk = hmac.digest(salt, concatenated, "sha256")
        for info_label, info in infos.items():
            digest = hmac.digest(prk, info + b"\x01", "sha256")
            test(digest[:16], f"hkdfh:{order}:{salt_label}:{info_label}")
            test(digest[16:], f"hkdft:{order}:{salt_label}:{info_label}")
            for key in names:
                digest = hmac.digest(A[key], concatenated + info, "sha256")
                test(digest[:16], f"hmach:{order}:{key}:{info_label}")
                test(digest[16:], f"hmact:{order}:{key}:{info_label}")
assert len(planted_hits) == 1, f"Planted HKDF output count was {len(planted_hits)}"
assert counts == {"K04_direct": 1607040, "K04_coupon": 1607040, "K08_direct": 1607040}
print("SYNTHETIC_FULL_CANDIDATE_PASS", planted.hex().upper())
print("ORIGINAL_COMMITMENT_MATCHES", hits)
print("COMPLETE_ASSIGNMENT_CHECKS", counts)
