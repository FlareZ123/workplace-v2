"""Source-pinned single-file K04 selected-only symmetric transport hypothesis.

Requires cryptography. This is a finite speculative test, not an attested
printer cipher. Run from repository root. Neither source nor candidate written.
"""
import hashlib
import json
from itertools import permutations
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
raw = SPOOL.read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
selected = b"2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5"
assert selected in raw
copied = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
known = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "nonce": "5F933DA6A1BD03C32DA5CBC25344F497",
    "mask": "8556C8CB6140A7F9A5123AC7571BEE1C",
}
keys16 = {name: bytes.fromhex(value) for name, value in known.items()}
mask = keys16["mask"]
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
assert bytes.fromhex(routing["K04"]["masked_component"]) == mask
assert bytes.fromhex(routing["K08"]["desk_nonce"]) == keys16["nonce"]
accepted = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]
assert accepted == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
ivs = {
    **keys16,
    "zero": bytes(16),
    "job_ascii": b"PS-261003-0417".ljust(16, b"\0"),
    "job_lowint": (417).to_bytes(16, "little"),
    "job_bigint": (417).to_bytes(16, "big"),
}
assert all(len(iv) == 16 for iv in ivs.values())
keys = {
    **keys16,
    **{f"{a}:{b}": keys16[a] + keys16[b] for a, b in permutations(keys16, 2)},
}
blocks = {
    "copied": copied,
    "xor_reduced": bytes(x ^ y for x, y in zip(copied, mask)),
}
matches = []
trials = 0

def check(label, value):
    global trials
    for stage, item in (
        ("direct", value),
        ("xor_mask", bytes(x ^ y for x, y in zip(value, mask))),
    ):
        trials += 1
        if hashlib.sha256(item).hexdigest() == accepted:
            matches.append((label, stage, item.hex().upper()))

for key_name, key in keys.items():
    aes = algorithms.AES(key)
    for block_name, block in blocks.items():
        for kind, action in (
            ("ecb_encrypt", Cipher(aes, modes.ECB()).encryptor()),
            ("ecb_decrypt", Cipher(aes, modes.ECB()).decryptor()),
        ):
            check((key_name, block_name, kind), action.update(block) + action.finalize())
        for iv_name, iv in ivs.items():
            for mode_name, mode in (("CBC", modes.CBC(iv)), ("CTR", modes.CTR(iv))):
                cipher = Cipher(aes, mode)
                for way, action in (
                    ("encrypt", cipher.encryptor()),
                    ("decrypt", cipher.decryptor()),
                ):
                    check(
                        (key_name, block_name, iv_name, mode_name, way),
                        action.update(block) + action.finalize(),
                    )
    if len(key) == 32:
        for iv_name, iv in ivs.items():
            for block_name, block in blocks.items():
                action = Cipher(algorithms.ChaCha20(key, iv), mode=None).decryptor()
                check((key_name, block_name, iv_name, "ChaCha20"), action.update(block) + action.finalize())

# Plant a genuine one-block AES-CBC transit ciphertext and recover it exactly.
planted_key, planted_iv, planted_payload = keys16["K06"], keys16["nonce"], keys16["K03"]
action = Cipher(algorithms.AES(planted_key), modes.CBC(planted_iv)).encryptor()
planted_ciphertext = action.update(planted_payload) + action.finalize()
action = Cipher(algorithms.AES(planted_key), modes.CBC(planted_iv)).decryptor()
assert action.update(planted_ciphertext) + action.finalize() == planted_payload

assert trials == 15488 and not matches, (trials, matches)
print(json.dumps({
    "result": "NO_ORIGINAL_MATCH", "complete_candidates": trials,
    "aes_keys": len(keys), "nonces": len(ivs),
    "synthetic_AESCBC_roundtrip": "PASS",
}, indent=2))
