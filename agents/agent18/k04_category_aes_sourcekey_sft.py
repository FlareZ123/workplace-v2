"""K04: selected 16-byte source-cue AES versus 128 categorical spool records.

Read-only local SFT. Does not output source-derived keys or candidate bytes.
Run at repo root: python agents/agent18/k04_category_aes_sourcekey_sft.py
Requires numpy and cryptography. Never run with original inputs on public CI.
"""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(__file__).resolve().parents[2] / "resources"
notes = (ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
route = (ROOT / "evidence/recovery-routing.json").read_bytes()
assert hashlib.sha256(notes).hexdigest() == "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"

note_lines = {
    int(n): line for n, name, line in
    re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", notes.decode())
}
def tokens(text):
    return re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text)
def body(note_id):
    return note_lines[note_id].split(": ", 1)[-1]

# The upstream N09->N13->N23->N20 selector is previously reported;
# derive (never print) the 16-character four-word key from its fixed positions.
words = [tokens(body(n))[0] for n in (9, 13, 23)] + [tokens(body(20))[18]]
source_key = "".join(words)
assert len(source_key) == 16
keys = [source_key.lower().encode(), source_key.upper().encode(), source_key.encode()]

rows = re.findall(
    rb"(?m)^20[^\n]+?CLASS=(LABEL|STORES|RECOVER) PAYLOAD=[A-F0-9]{32} DEST=(store|bench|desk)",
    spool
)
assert len(rows) == 133
classes = {b"LABEL": 0, b"STORES": 1, b"RECOVER": 2}
destinations = {b"store": 0, b"bench": 1, b"desk": 2}
categories = np.array(
    [3 * classes[c] + destinations[d] for c, d in rows[:128]],
    dtype=np.uint8
)
# All 512 complete Boolean functions of nine CLASS/DEST outcomes, 128 cyclic
# alignments, and four exact bit/byte packing layouts: 262,144 candidates.
packed = []
for assignment in range(512):
    bits = np.array(
        [(assignment >> int(category)) & 1 for category in categories],
        dtype=np.uint8
    )
    for shift in range(128):
        ordered = np.roll(bits, -shift)
        for bit_order in ("little", "big"):
            p = np.packbits(ordered, bitorder=bit_order).tobytes()
            packed.extend((p, p[::-1]))
assert len(packed) == 262144
raw = b"".join(packed)

mask = bytes.fromhex(json.loads(route)["K04"]["masked_component"])
target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]

# Independently planted full 16-byte coupon (nonhistorical) and
# plaintext/ciphertext round-trip through the same AES+pack+mask reducer.
planted = bytes.fromhex("a16393079258c1746d5e2b105f4cf098")
synthetic_payload = bytes(a ^ b for a, b in zip(planted, mask))
enc = Cipher(algorithms.AES(keys[0]), modes.ECB()).encryptor()
synthetic_ct = enc.update(synthetic_payload) + enc.finalize()
bits = np.unpackbits(
    np.frombuffer(synthetic_ct, dtype=np.uint8), bitorder="little"
)
assert len(bits) == 128
repacked = np.packbits(bits, bitorder="little").tobytes()
dec = Cipher(algorithms.AES(keys[0]), modes.ECB()).decryptor()
recovered = dec.update(repacked) + dec.finalize()
assert bytes(a ^ b for a, b in zip(recovered, mask)) == planted

checks = hits = 0
printable = 0
for key in keys:
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    for direction in ("encrypt", "decrypt"):
        transform = cipher.encryptor() if direction == "encrypt" else cipher.decryptor()
        result = transform.update(raw) + transform.finalize()
        for i in range(0, len(result), 16):
            out = result[i:i+16]
            printable += all(32 <= c < 127 for c in out)
            for component in (
                out, bytes(a ^ b for a, b in zip(out, mask))
            ):
                checks += 1
                hits += hashlib.sha256(component).hexdigest() == target

assert checks == 3145728
print(json.dumps({
    "ordinary_records": 128,
    "boolean_functions": 512,
    "cyclic_alignments": 128,
    "packing_views": 4,
    "cipher_keys": 3,
    "aes_ecb_directions": 2,
    "full_original_k04_checks": checks,
    "original_hits": hits,
    "printable_blocks": printable,
    "independent_planted_full_coupon_control": "PASS",
}, sort_keys=True))
