"""Cross-archive selected-source label emitter probe (no missing-slot guesses).

Run: python agents/agent46/k04_crossarchive_label_emitter_sft.py
The five 16-byte blocks are original selected prehash/opaque source objects.
A cross-family deterministic emitter must reproduce originals, without being
trained on the unknown 0417 coupon or final Emily caption.
"""
import hashlib
import hmac
import json
import random
from pathlib import Path

root = Path(__file__).resolve().parents[2]
acceptance = json.loads((root / "resources/acceptance.json").read_text())
routing = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
blocks = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K02": bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507"),
    "K05": bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
    "K07": bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9"),
}
for slot, block in blocks.items():
    derived = hashlib.sha256(block).digest()[:16] if slot in ("K02", "K07") else block
    assert hashlib.sha256(derived).hexdigest() == acceptance["slot_sha256"][slot]

aliases = {
    "K01": ("WN-14", "WN14", "WATCH REGISTER", "INK", "WATCH-REGISTER"),
    "K02": ("LT-204", "LT204", "DIAG_WORD", "FREEZE TELEMETRY", "HOLD"),
    "K05": ("TRP2", "TRP-2", "NODE49", "NODE=49", "EVENT=82", "TRIP RECORDER"),
    "K06": ("RC-17", "RC17", "REV C", "REVISION C", "SERVICE_ORDER"),
    "K07": ("AX-7782", "AX7782", "TRANSFER AUDIT", "COMMIT", "GABRIEL"),
}
dates = ("", "2026-10-03", "20261003", "261003", "2026-09-24", "20260924")
roots = ("", "H17", "H-17", "IR-261003-H17", "H17-IR-261003", "REC8/1", "CEG-ARCHIVE-RECOVERY/v1")
joiners = ("", "/", "|", ":", "-", "_", " ", "\n")
keys = {
    "mask": bytes.fromhex(routing["K04"]["masked_component"]),
    "nonce": bytes.fromhex(routing["K08"]["desk_nonce"]),
    "envelope-ascii": routing["envelope_id"].encode("ascii"),
    "combined-prefix": routing["combined"]["prefix"].encode("ascii"),
}

def forms(slot):
    for alias in aliases[slot]:
        for case in (alias, alias.lower(), alias.upper()):
            for prefix in roots:
                for sep in joiners:
                    if prefix:
                        yield f"{prefix}{sep}{case}"
                        yield f"{case}{sep}{prefix}"
                    else:
                        yield case
                    if prefix:
                        yield f"{prefix}{sep}{slot}{sep}{case}"
                        yield f"{case}{sep}{slot}{sep}{prefix}"
                    else:
                        yield f"{slot}{sep}{case}"
                for date in dates:
                    if date:
                        for sep in ("/", ":", "|", " ", "-"):
                            yield f"{case}{sep}{date}"
                            yield f"{date}{sep}{case}"

def emitters(message):
    results = {
        "md5": hashlib.md5(message).digest(),
        "sha256/head": hashlib.sha256(message).digest()[:16],
        "sha256/tail": hashlib.sha256(message).digest()[-16:],
        "sha512/head": hashlib.sha512(message).digest()[:16],
        "sha512/tail": hashlib.sha512(message).digest()[-16:],
        "sha3_256/head": hashlib.sha3_256(message).digest()[:16],
        "blake2b/16": hashlib.blake2b(message, digest_size=16).digest(),
        "blake2s/16": hashlib.blake2s(message, digest_size=16).digest(),
    }
    for name, key in keys.items():
        d = hmac.digest(key, message, "sha256")
        results[f"hmac256/{name}/head"] = d[:16]
        results[f"hmac256/{name}/tail"] = d[-16:]
        results[f"blake2b/{name}/16"] = hashlib.blake2b(message, key=key, digest_size=16).digest()
        results[f"blake2s/{name}/16"] = hashlib.blake2s(message, key=key, digest_size=16).digest()
    return results

assert emitters(b"REC8/1/K05/TRP2")["blake2b/16"] == hashlib.blake2b(b"REC8/1/K05/TRP2", digest_size=16).digest()
assert "REC8/1/K05/TRP2" in set(forms("K05"))

hash_hits, prng_hits = [], []
counts = {"hash": 0, "prng": 0}
by_slot = {}
for slot, target in blocks.items():
    strings = set(forms(slot))
    by_slot[slot] = len(strings)
    for string in strings:
        message = string.encode("ascii")
        for model, block in emitters(message).items():
            counts["hash"] += 1
            if block == target:
                hash_hits.append((slot, string, model))
        seeds = (
            ("str", string), ("bytes", message),
            ("sha256-32big", int.from_bytes(hashlib.sha256(message).digest()[:4], "big")),
            ("sha256-32little", int.from_bytes(hashlib.sha256(message).digest()[:4], "little")),
        )
        for seed_name, seed in seeds:
            rng = random.Random(seed)
            words = [rng.getrandbits(32) for _ in range(48)]
            for i in range(33):
                for endian in ("big", "little"):
                    block = b"".join(x.to_bytes(4, endian) for x in words[i:i+4])
                    counts["prng"] += 1
                    if block == target:
                        prng_hits.append((slot, string, seed_name, i, endian))

assert not hash_hits, hash_hits
assert not prng_hits, prng_hits
assert counts["prng"] == 3445728
print(json.dumps({"source": "original selected five source families",
                  "forms_by_slot": by_slot,
                  "hash_emitter_count": len(emitters(b"test")),
                  "checks": counts, "matches": hash_hits + prng_hits,
                  "synthetic_hash_control": "PASS"}, indent=2))
