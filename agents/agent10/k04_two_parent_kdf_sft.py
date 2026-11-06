"""H-17 K04: original-source paired same-job complete-coupon KDF test.

Run from the workplace-v2 repository. Uses the unchanged official evidence,
original mask and original complete slot commitment.
"""
from pathlib import Path
import hashlib
import hmac
import re

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "resources"
spool = (P / "evidence/print/spool-reconstruction.log").read_bytes()
route = (P / "evidence/recovery-routing.json").read_bytes()
acceptance = (P / "acceptance.json").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(route).hexdigest() == "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
assert hashlib.sha256(acceptance).hexdigest() == "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"

rows = []
for line in spool.decode().splitlines():
    m = re.search(r"JOB=([^ ]+) ATTEMPT=(\d+) STATE=([^ ]+) CLASS=([^ ]+) PAYLOAD=([0-9A-F]{32}) DEST=(\S+)", line)
    if m:
        rows.append((m.group(1), int(m.group(2)), m.group(3), m.group(4), bytes.fromhex(m.group(5)), m.group(6)))
sel = [r for r in rows if r[0] == "PS-261003-0417"]
assert [(r[1], r[2], r[3]) for r in sel] == [
    (1, "ACK", "LABEL"), (1, "REQUESTED", "RECOVER"),
    (2, "ACK", "RECOVER"), (3, "REQUESTED", "RECOVER"),
]
label1, request1, _withheld_ack2, request3 = (r[4] for r in sel)
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
target = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def views(value):
    words = [value[i:i + 4] for i in range(0, 16, 4)]
    return sorted({
        b"".join(w[::-1] if endian else w for w in (words[::-1] if swap else words))
        for swap in (0, 1) for endian in (0, 1)
    })

groups = [
    ("label_requested", label1, request1),
    ("requested1_requested3", request1, request3),
    ("label_requested3", label1, request3),
]
context = [
    b"", b"K04", b"H17", b"ESC-N", b"PS-261003-0417",
    b"RECOVER", b"ACK", b"2", b"2026-10-03T18:02:00Z", b"H17-IR-261003",
]
patterns = [
    lambda a, b, s: a + b + s,
    lambda a, b, s: s + a + b,
    lambda a, b, s: a + s + b,
    lambda a, b, s: b + a + s,
    lambda a, b, s: s + b + a,
    lambda a, b, s: b + s + a,
]
hash_names = ("md5", "sha1", "sha256", "sha384", "sha512", "sha3_256", "blake2b", "blake2s")

checked = 0
unique = set()
hits = []
planted = None
planted_count = 0
for group, left, right in groups:
    group_count = 0
    group_unique = set()
    for av in views(left):
        for bv in views(right):
            for salt in context:
                for encode in patterns:
                    material = encode(av, bv, salt)
                    digests = []
                    for name in hash_names:
                        plain = hashlib.new(name, material).digest()
                        digests += [(name + "_first", plain[:16]), (name + "_last", plain[-16:])]
                        keyed_ab = hmac.new(av, bv + salt, name).digest()
                        keyed_ba = hmac.new(bv, av + salt, name).digest()
                        digests += [
                            (name + "_hmac_ab_first", keyed_ab[:16]),
                            (name + "_hmac_ab_last", keyed_ab[-16:]),
                            (name + "_hmac_ba_first", keyed_ba[:16]),
                            (name + "_hmac_ba_last", keyed_ba[-16:]),
                        ]
                    digests += [
                        ("shake128", hashlib.shake_128(material).digest(16)),
                        ("shake256", hashlib.shake_256(material).digest(16)),
                    ]
                    for descriptor, packet in digests:
                        for oriented in (packet, packet[::-1]):
                            component = bytes(x ^ y for x, y in zip(oriented, mask))
                            checked += 1
                            group_count += 1
                            unique.add(component)
                            group_unique.add(component)
                            if planted is None:
                                planted = component
                            if component == planted:
                                planted_count += 1
                            if hashlib.sha256(component).hexdigest() == target:
                                hits.append((group, descriptor, oriented.hex()))
    print(f"GROUP {group} checked={group_count} unique={len(group_unique)}")
print(f"TOTAL checked={checked} unique={len(unique)} planted_count={planted_count} original_hits={hits}")
assert checked == 288000
assert len(unique) == 120192
assert planted_count == 6
assert not hits
