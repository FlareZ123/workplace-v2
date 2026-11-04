"""Source-pinned SFT: historical cassette-ticket AES-128 derivations and K04."""
import hashlib
import itertools
import json
import os
import re
from pathlib import Path

from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
DOC = ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
LOG = ROOT / "evidence/print/spool-reconstruction.log"
assert hashlib.sha256(DOC.read_bytes()).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
assert hashlib.sha256(LOG.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

headers = {
    "N": ("PS-261003-0417", "ESC-N", "L-29/N", "FA-17", "H17-POL-17/A3", "2026-10-03T18:02:00Z", "2"),
    "S": ("PS-261003-0448", "ESC-S", "L-29/S", "LV-42", "CS-18/5", "2026-10-03T18:24:00Z", "1"),
}
source = DOC.read_text()
tickets = {}
for lane in headers:
    rows = sorted((int(t), int(n)) for t, n in re.findall(rf"^L-29/{lane}\s+(\d\d)\s+ST-(\d\d\d)\s", source, re.M))
    assert [tab for tab, _ in rows] == [1, 2, 3, 4, 5]
    tickets[lane] = [number for _, number in rows]
assert tickets == {"N": [94, 81, 106, 99, 112], "S": [130, 151, 121, 135, 142]}

spool = LOG.read_text()
assert "JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER PAYLOAD=234BE186E97EE05830909790E336109E" in spool
assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5" in spool
south = bytes.fromhex("234BE186E97EE05830909790E336109E")
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
target = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

# Independent RFC4493 / NIST native primitive known-answer checks.
c = cmac.CMAC(algorithms.AES(bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")))
c.update(b"")
assert c.finalize().hex() == "bb1d6929e95937287fa37d129b756746"
e = Cipher(algorithms.AES(bytes.fromhex("000102030405060708090a0b0c0d0e0f")), modes.ECB()).encryptor()
assert (e.update(bytes.fromhex("00112233445566778899aabbccddeeff")) + e.finalize()).hex() == "69c4e0d86a7b0430d8cdb78070b4c55a"

def material(nums, shape):
    if shape == "digits": return "".join(f"{x:03d}" for x in nums).encode()
    if shape == "hyphen": return "-".join(f"ST-{x:03d}" for x in nums).encode()
    if shape == "pipes": return "|".join(f"ST-{x:03d}" for x in nums).encode()
    if shape == "commas": return ",".join(str(x) for x in nums).encode()
    if shape == "bytes": return bytes(nums)
    if shape == "short-be": return b"".join(x.to_bytes(2, "big") for x in nums)
    if shape == "short-le": return b"".join(x.to_bytes(2, "little") for x in nums)
    raise AssertionError(shape)

def derive(b, how):
    if how == "md5": return hashlib.md5(b).digest()
    if how == "sha256-front": return hashlib.sha256(b).digest()[:16]
    if how == "sha256-back": return hashlib.sha256(b).digest()[16:]
    raise AssertionError(how)

def coupon(key, message, method):
    if method == "cmac":
        c = cmac.CMAC(algorithms.AES(key))
        c.update(message)
        return c.finalize()
    if method == "ecb-md5":
        block = hashlib.md5(message).digest()
    elif method == "ecb-sha256-front":
        block = hashlib.sha256(message).digest()[:16]
    else:
        assert method == "ecb-sha256-back"
        block = hashlib.sha256(message).digest()[16:]
    c = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return c.update(block) + c.finalize()

def message(lane, index, layout):
    job, route, rset, account, fileref, timestamp, attempt = headers[lane]
    pieces = (job, route, rset, account, fileref, timestamp, attempt, "RECOVER", "ACK")
    val = pieces[index]
    if layout == 0: return val.encode()
    if layout == 1: return f"H17/{val}".encode()
    if layout == 2: return f"REC8/1|{val}".encode()
    if layout == 3: return f"{val}|RECOVER".encode()
    if layout == 4: return f"{val}|ACK".encode()
    if layout == 5: return f"{val}|{job}".encode()
    if layout == 6: return f"{job}|{val}".encode()
    raise AssertionError(layout)

shapes = ("digits", "hyphen", "pipes", "commas", "bytes", "short-be", "short-le")
derivations = ("md5", "sha256-front", "sha256-back")
methods = ("cmac", "ecb-md5", "ecb-sha256-front", "ecb-sha256-back")
hits = []
count = 0
planted_case = ("hyphen", "md5", 0, 3, "cmac")
planted_value = None
planted_hits = 0
for shape, dk, field, layout, mode in itertools.product(shapes, derivations, range(9), range(7), methods):
    idx = (shape, dk, field, layout, mode)
    north_key = derive(material(tickets["N"], shape), dk)
    south_key = derive(material(tickets["S"], shape), dk)
    n = coupon(north_key, message("N", field, layout), mode)
    s = coupon(south_key, message("S", field, layout), mode)
    count += 1
    if s == south: hits.append(("south", idx))
    result = bytes(x ^ y for x, y in zip(n, mask))
    if hashlib.sha256(result).hexdigest() == target:
        hits.append(("K04", idx, result.hex().upper()))
    if idx == planted_case: planted_value = s
    if planted_value is not None and s == planted_value: planted_hits += 1

assert count == 5292 and planted_hits >= 1
print(json.dumps({
    "hypothesis": "historically paired cassette ticket AES-128-CMAC/ECB",
    "complete_sibling_formulas": count,
    "original_south_exact_hits": [x for x in hits if x[0] == "south"],
    "original_K04_commitment_hits": [x for x in hits if x[0] == "K04"],
    "synthetic_planted_south_hits": planted_hits,
}, indent=2))
