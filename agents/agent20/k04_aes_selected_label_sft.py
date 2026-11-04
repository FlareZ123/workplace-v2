"""Source-pinned SFT: AES-128 CMAC/ECB selected-source label emitter and K04."""
import hashlib
import itertools
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
CHECKS = {
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}
for rel, digest in CHECKS.items():
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((ROOT / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]
assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"
assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

SOURCES = {
    "K01": ("WN-14", "WN14", "INK"),
    "K02": ("LT-204", "LT204", "DIAG_WORD"),
    "K05": ("TRP2", "NODE49", "EVENT82"),
    "K06": ("RC-17", "RC17", "REV-C"),
    "K07": ("AX-7782", "AX7782", "COMMIT"),
    "K04": ("ESC-N", "PS-261003-0417", "RECOVER"),
}
BLOCKS = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "8947CEDCB9CC73BAB7E87BE63302C5C9",
}
KEYS = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "K02-source": BLOCKS["K02"],
    "K07-source": BLOCKS["K07"],
    "K04-mask": route["K04"]["masked_component"],
    "K08-nonce": route["K08"]["desk_nonce"],
}
METHODS = ("cmac", "md5", "sha256-front", "sha256-back", "raw-zero-pad")
SEPS = ("", "-", "/", ":", "|", " ", "\n")
PREFIXES = ("", "H17", "IR-261003-H17", "CEG-ARCHIVE-RECOVERY/v1", "REC8/1")
SUFFIXES = ("", "2026-10-03", "20261003", "ACK", "2")

def emit(key, msg, method):
    if method == "cmac":
        c = cmac.CMAC(algorithms.AES(key))
        c.update(msg)
        return c.finalize()
    if method == "md5":
        block = hashlib.md5(msg).digest()
    elif method == "sha256-front":
        block = hashlib.sha256(msg).digest()[:16]
    elif method == "sha256-back":
        block = hashlib.sha256(msg).digest()[16:]
    elif method == "raw-zero-pad":
        if len(msg) > 16:
            return None
        block = msg.ljust(16, b"\x00")
    else:
        raise AssertionError(method)
    c = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return c.update(block) + c.finalize()

def labels(slot):
    seen = set()
    for alias, sep, prefix, suffix in itertools.product(SOURCES[slot], SEPS, PREFIXES, SUFFIXES):
        msg = sep.join(p for p in (prefix, alias, suffix) if p).encode("ascii")
        if msg not in seen:
            seen.add(msg)
            yield msg

# Independent primitive known-answer controls, not tautological cipher roundtrips.
known = cmac.CMAC(algorithms.AES(bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")))
known.update(b"")
assert known.finalize().hex() == "bb1d6929e95937287fa37d129b756746"
known_cipher = Cipher(algorithms.AES(bytes.fromhex("000102030405060708090a0b0c0d0e0f")), modes.ECB()).encryptor()
assert (known_cipher.update(bytes.fromhex("00112233445566778899aabbccddeeff")) + known_cipher.finalize()).hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"

observed = {k: bytes.fromhex(v) for k, v in BLOCKS.items()}
counts = {k: 0 for k in SOURCES}
matches = []
planted_value = emit(bytes.fromhex(KEYS["K08-nonce"]), b"H17/ESC-N/ACK", "cmac")
planted_hits = 0
for key_label, key_text in KEYS.items():
    key = bytes.fromhex(key_text)
    for slot in SOURCES:
        for msg in labels(slot):
            for method in METHODS:
                v = emit(key, msg, method)
                if v is None: continue
                counts[slot] += 1
                if slot == "K04":
                    c = bytes(x ^ y for x, y in zip(v, mask))
                    if hashlib.sha256(c).hexdigest() == target:
                        matches.append((slot, key_label, method, msg.decode(), c.hex().upper()))
                elif v == observed[slot]:
                    matches.append((slot, key_label, method, msg.decode()))
                if slot == "K04" and key_label == "K08-nonce" and method == "cmac" and msg == b"H17/ESC-N/ACK":
                    planted_hits += int(v == planted_value)

assert sum(counts.values()) == 132800 and planted_hits == 1
print(json.dumps({
    "complete_candidates_by_slot": counts,
    "total_produced_blocks": sum(counts.values()),
    "authentic_selected_source_hits": [m for m in matches if m[0] != "K04"],
    "original_K04_hits": [m for m in matches if m[0] == "K04"],
    "planted_positive_hits": planted_hits,
}, indent=2))
