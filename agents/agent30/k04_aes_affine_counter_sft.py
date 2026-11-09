"""AES-128 affine-counter printer issuer, complete held-out packet source gate.
Usage: python agents/agent30/k04_aes_affine_counter_sft.py [resource-root]
Uses historical printer rows 0300..0427; never fits selected 0417 ACK2.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
for line in spool.decode().splitlines():
    match = re.search(r"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK .*?PAYLOAD=([0-9A-F]{32})", line)
    if match and 300 <= int(match[1]) <= 427:
        rows.append((int(match[1]), bytes.fromhex(match[2])))
assert [i for i, _ in rows] == list(range(300, 428))
packets = [p for _, p in rows]

known = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
    "K02_PREHASH": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K07_PREHASH": "8947CEDCB9CC73BAB7E87BE63302C5C9",
}
route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
known["MASK"] = route["K04"]["masked_component"]
known["NONCE"] = route["K08"]["desk_nonce"]
keys = {name: bytes.fromhex(h) for name, h in known.items()}

def view(value, reverse_bytes, reverse_words, swap_halves):
    words = [value[i:i+4] for i in range(0, 16, 4)]
    if reverse_bytes:
        words = [w[::-1] for w in words]
    if reverse_words:
        words.reverse()
    if swap_halves:
        words = words[2:] + words[:2]
    return b"".join(words)

def crypt(key, plaintext, encrypt):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    ctx = cipher.encryptor() if encrypt else cipher.decryptor()
    return ctx.update(plaintext) + ctx.finalize()

def extrapolate(source, key, encrypt, endian, order):
    # The counter's base and arbitrary stride are inferred from two complete real packets.
    first, second = [crypt(key, view(p, *order), not encrypt) for p in source[:2]]
    base = int.from_bytes(first, endian)
    stride = (int.from_bytes(second, endian) - base) % (1 << 128)
    result = []
    for index in range(len(source)):
        counter = ((base + stride * index) % (1 << 128)).to_bytes(16, endian)
        result.append(view(crypt(key, counter, encrypt), *order))
    return result

orders = list(itertools.product((False, True), repeat=3))
count = 0
third = []
whole = []
for name, key in keys.items():
    for encrypt, endian, order in itertools.product((False, True), ("big", "little"), orders):
        count += 1
        predicted = extrapolate(packets, key, encrypt, endian, order)
        if predicted[2] == packets[2]:
            third.append((name, encrypt, endian, order))
        if predicted == packets:
            whole.append((name, encrypt, endian, order))
assert count == 320
print("historical models:", count, "full third-packet matches:", len(third), "whole 128-packet matches:", len(whole))
assert not third and not whole

# Independently planted 128-packet issuer: 126 complete original-shaped holdouts.
key = keys["K06"]
order = (True, True, False)
base = 0x73492A1500000000000000000012AC70
stride = 5
planted = [view(crypt(key, ((base + stride * index) % (1<<128)).to_bytes(16, "little"), True), *order)
           for index in range(128)]
assert extrapolate(planted, key, True, "little", order) == planted
print("synthetic withheld whole-packet positives: 126 / 126 PASS")
