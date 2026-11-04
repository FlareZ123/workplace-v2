"""Read-only H17 K04 three-cassette GF(256)/GF(65536) erasure SFT.

Run from repository root using the original `resources/` source directory.
Tests hypothetical degree-one field-code relations among ESC-N, ESC-S,
WATCH-SPARE payloads; the printed source does not attest this architecture.
"""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", str(Path(__file__).resolve().parents[2] / "resources")))
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
FLEET = ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
ACCEPT = ROOT / "acceptance.json"
PINS = {
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    FLEET: "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    ACCEPT: "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
for path, digest in PINS.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
assert json.loads(ACCEPT.read_text())["slot_sha256"]["K04"] == TARGET

pattern = re.compile(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)")
rows = []
for line in SPOOL.read_text().splitlines():
    if not line or line.startswith("#"):
        continue
    match = pattern.search(line)
    assert match, line
    job, attempt, state, role, payload, dest = match.groups()
    rows.append((line.split()[0], int(job), int(attempt), state, role, bytes.fromhex(payload), dest))
assert len(rows) == 133
def late(job, minute):
    matches = [r for r in rows if r[1] == job and r[0].startswith("2026-10-03T18:" + minute)]
    assert len(matches) == 1
    return matches[0]
north, south, watch = late(417,"02"), late(448,"24"), late(420,"25")
assert north[5].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
assert south[5].hex().upper() == "234BE186E97EE05830909790E336109E"
assert watch[5].hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"

def mul(a, b, poly, bits):
    value = 0
    while b:
        if b & 1: value ^= a
        b >>= 1
        a <<= 1
        if a & (1 << bits): a ^= poly
    return value

def power(a, n, poly, bits):
    result = 1
    while n:
        if n & 1: result = mul(result, a, poly, bits)
        a = mul(a, a, poly, bits)
        n >>= 1
    return result

def interpolate(x, y, z, source_y, source_z, poly, bits, endian):
    assert y != z
    inverse = power(y ^ z, (1 << bits) - 2, poly, bits)
    assert mul(y ^ z, inverse, poly, bits) == 1
    a = mul(x ^ z, inverse, poly, bits)
    b = mul(x ^ y, inverse, poly, bits)
    n = bits // 8
    return b"".join(
        (mul(a, int.from_bytes(source_y[i:i+n], endian), poly, bits)
         ^ mul(b, int.from_bytes(source_z[i:i+n], endian), poly, bits)).to_bytes(n, endian)
        for i in range(0, len(source_y), n)
    )

# Synthetic full-coupon withheld-output recovery.
for bits, poly in [(8, 0x11B), (8, 0x11D), (16, 0x1100B)]:
    for endian in ("big", "little"):
        n = bits // 8
        offset = bytes((i * 83 + 59) & 255 for i in range(16))
        slope = bytes((i * 17 + 12) & 255 for i in range(16))
        def emitted(x):
            return b"".join(
                (int.from_bytes(offset[i:i+n], endian)
                 ^ mul(x, int.from_bytes(slope[i:i+n], endian), poly, bits)).to_bytes(n, endian)
                for i in range(0, 16, n)
            )
        assert interpolate(7, 11, 23, emitted(11), emitted(23), poly, bits, endian) == emitted(7)
print("planted_complete_positive=6 PASS")

# Every coordinate is fixed from the original L-29 fleet record or printer line.
coordinates = {
    "cabinet_ordinal": (1,2,3),
    "cabinet_ascii": (78,83,87),
    "job_suffix_mod256": (417%256,448%256,420%256),
    "minute_after_18utc": (2,24,25),
    "ticket_tab1": (94,130,164),
    "ticket_sum_mod256": (492%256,679%256,321%256),
    "cabinet_alpha_index": (14,19,23),
}
assignments, hits, similarities = 0, [], []
for label, (x,y,z) in coordinates.items():
    for bits,poly in ((8,0x11B),(8,0x11D),(16,0x1100B)):
        for endian in (("big",) if bits == 8 else ("big","little")):
            packet = interpolate(x,y,z,south[5],watch[5],poly,bits,endian)
            component = bytes(a ^ b for a,b in zip(packet, MASK))
            ok = hashlib.sha256(component).hexdigest() == TARGET
            assignments += 1
            similarities.append(sum(a==b for a,b in zip(packet,north[5])))
            if ok: hits.append((label,bits,hex(poly),endian,component.hex().upper()))
assert assignments == 28
print("original_complete_k04_candidates=", assignments, "original_hits=", hits)
print("max_match_with_disputed_spool_copy=",max(similarities),"/16")

# Cross-check the hypothesis on genuine withheld intact same-role ACK packets.
ordinary = [r for r in rows[:128] if r[3]=="ACK" and r[4]=="RECOVER" and r[6]=="bench"]
assert len(ordinary)==11
heldout,exact,max_matching = 0,0,0
for i in range(len(ordinary)-2):
    a,b,c = ordinary[i:i+3]
    x,y,z = a[1]%256,b[1]%256,c[1]%256
    for bits,poly in ((8,0x11B),(8,0x11D),(16,0x1100B)):
        for endian in (("big",) if bits==8 else ("big","little")):
            guess=interpolate(x,y,z,b[5],c[5],poly,bits,endian)
            heldout += 1
            exact += guess==a[5]
            max_matching = max(max_matching,sum(p==q for p,q in zip(guess,a[5])))
assert heldout == 36
print("normal_recover_bench_source_packets=",len(ordinary))
print("source_heldout_complete_predictions=",heldout,"exact_matches=",exact,"max_matching_bytes=",max_matching)
assert not hits and not exact
