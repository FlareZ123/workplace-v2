"""SFT: north/south cassette ticket-whitening with an unknown shared pad.

Pass a source root (default: resources); original evidence is never changed.
"""
import collections
import hashlib
import hmac
import json
from pathlib import Path
import random
import re
import struct
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
note = (root / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
route_bytes = (root / "evidence/recovery-routing.json").read_bytes()
accept_bytes = (root / "acceptance.json").read_bytes()
assert hashlib.sha256(note).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route_bytes).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert hashlib.sha256(accept_bytes).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
route, acceptance = json.loads(route_bytes), json.loads(accept_bytes)
mask, nonce = bytes.fromhex(route["K04"]["masked_component"]), bytes.fromhex(route["K08"]["desk_nonce"])
target = acceptance["slot_sha256"]["K04"]
assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
k01 = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
assert hashlib.sha256(k01).hexdigest() == acceptance["slot_sha256"]["K01"]
rows = [line for line in spool.decode().splitlines() if "JOB=PS-261003-0448 " in line and "ATTEMPT=1 STATE=ACK CLASS=RECOVER " in line]
assert len(rows) == 1 and rows[0].startswith("2026-10-03T18:24:00Z ")
south = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rows[0]).group(1))
assert south.hex().upper() == "234BE186E97EE05830909790E336109E"
meta = {
    "N": ("PS-261003-0417", "ESC-N", "L-29/N", "FA-17", "H17-POL-17/A3", "2026-10-03T18:02:00Z", "2", "bench"),
    "S": ("PS-261003-0448", "ESC-S", "L-29/S", "LV-42", "CS-18/5", "2026-10-03T18:24:00Z", "1", "desk"),
}
tickets = {k: re.findall(rf"L-29/{k}\s+0\d\s+ST-(\d{{3}})", note.decode()) for k in meta}
assert [len(tickets[k]) for k in ("N", "S")] == [5, 5]


def all_forms(lane):
    raw = tickets[lane]
    ints = list(map(int, raw))
    bases = []
    for delimiter in ("", " ", "|", ",", ":", "-", "\n"):
        for spelling in (raw, list(map(str, ints)), ["ST-" + x for x in raw]):
            bases.append(delimiter.join(spelling).encode())
    for fmt in ("B", "<H", ">H", "<I", ">I"):
        bases.append(b"".join(struct.pack(fmt, n) for n in ints))
    yield from bases
    for delim in ("", "|", ":", " ", "\n"):
        for field in meta[lane]:
            for base in bases:
                separator = delim.encode()
                value = field.encode()
                yield base + separator + value
                yield value + separator + base


def digests(value):
    for name in ("md5", "sha1", "sha256", "sha512", "sha3_256", "blake2s", "blake2b"):
        out = hashlib.new(name, value).digest()
        yield out[:16]
        yield out[(len(out)-16)//2:(len(out)+16)//2]
        yield out[-16:]
    for name in ("sha256", "sha512"):
        for key in (nonce, k01):
            yield hmac.digest(key, value, name)[:16]


def xor_all(*values):
    out = bytearray(16)
    for value in values:
        for i, byte in enumerate(value):
            out[i] ^= byte
    return bytes(out)


def as_seed(value, mode):
    if mode == "bytes":
        return value
    if mode == "text":
        return value.decode("latin1")
    return int.from_bytes(value, "big" if mode == "intbe" else "little")


pair_source = list(dict.fromkeys(zip(all_forms("S"), all_forms("N"))))
assert len(pair_source) == 2106
planted_master = bytes.fromhex("D92A1447CE31D1674A3B4EF00D7E9451")
planted = collections.Counter()
counts = collections.Counter()
hits = []
for idx, (raw_s, raw_n) in enumerate(pair_source):
    for number, (pad_s, pad_n) in enumerate(zip(digests(raw_s), digests(raw_n))):
        counts["digest"] += 1
        component = xor_all(south, pad_s, pad_n, mask)
        if hashlib.sha256(component).hexdigest() == target:
            hits.append((idx, "digest", number, component.hex().upper()))
        if idx == 137 and number == 6:
            planted_s = xor_all(planted_master, pad_s)
            assert xor_all(planted_s, pad_s, pad_n) == xor_all(planted_master, pad_n)
            planted["digest"] += 1
    for mode in ("bytes", "text", "intbe", "intle"):
        generator_s = random.Random(as_seed(raw_s, mode))
        generator_n = random.Random(as_seed(raw_n, mode))
        for phase in range(256):
            pad_s = generator_s.randbytes(16)
            pad_n = generator_n.randbytes(16)
            counts["python"] += 1
            component = xor_all(south, pad_s, pad_n, mask)
            if hashlib.sha256(component).hexdigest() == target:
                hits.append((idx, mode, phase, component.hex().upper()))
            if idx == 137 and mode == "bytes" and phase == 73:
                planted_s = xor_all(planted_master, pad_s)
                assert xor_all(planted_s, pad_s, pad_n) == xor_all(planted_master, pad_n)
                planted["python"] += 1
assert counts == {"digest": 52650, "python": 2156544}
assert planted == {"digest": 1, "python": 1}
print("PAIRED_SOURCE_FORMS", len(pair_source))
print("COMPLETE_K04_COMPARISONS", sum(counts.values()), dict(counts))
print("SYNTHETIC_FULL_COUPON_POSITIVES", dict(planted))
print("ORIGINAL_K04_HITS", len(hits), hits)
