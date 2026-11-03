"""H17 K04: two-request Boolean truth-table candidate construction.

Speculative retrospective copy-repair algebra: a four-lane bitwise map
of 18:01 REQUESTED1 and 18:03 REQUESTED3, or the earlier LABEL ACK
and REQUESTED3, could reproduce the missing authentic 18:02 ACK2.
The selected copied 18:02 bytes are withheld from candidate construction.
This source relation is not historically certified.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK32 = (1 << 32) - 1

def read(path):
    if len(sys.argv) > 1:
        with ZipFile(sys.argv[1]) as archive:
            return archive.read(path)
    return (Path(__file__).resolve().parents[2] / "resources" / path).read_bytes()

def truth(a, b, code):
    buckets = ((~a & ~b) & MASK32, (~a & b) & MASK32,
               (a & ~b) & MASK32, (a & b) & MASK32)
    return sum((v if code & (1 << i) else 0) for i, v in enumerate(buckets))

def construct(a, b, ops):
    out = bytearray()
    for lane in range(4):
        x = int.from_bytes(a[4*lane:4*lane+4], "little")
        y = int.from_bytes(b[4*lane:4*lane+4], "little")
        out.extend(truth(x, y, ops[lane]).to_bytes(4, "little"))
    return bytes(out)

raw = read("evidence/print/spool-reconstruction.log")
assert hashlib.sha256(raw).hexdigest() == PIN
lines = [line for line in raw.decode("ascii").splitlines()
         if "JOB=PS-261003-0417 " in line]
assert len(lines) == 4
assert ["CLASS=LABEL " in x for x in lines] == [True,False,False,False]
assert ["STATE=ACK " in x for x in lines] == [True,False,True,False]
assert lines[2].startswith("2026-10-03T18:02:00Z ")
assert "ATTEMPT=2 STATE=ACK CLASS=RECOVER " in lines[2]
coupons = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", x).group(1))
           for x in lines]
assert coupons[2].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
route = json.loads(read("evidence/recovery-routing.json"))
accept = json.loads(read("acceptance.json"))
mask = bytes.fromhex(route["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])
assert hashlib.sha256(bytes(x ^ y for x,y in zip(coupons[2],mask))).digest() != target

# A source-to-source discriminator: could any of the 16 possible Boolean
# functions even reproduce each copied ACK2 32-bit word? The copied 18:02
# fragment is untrusted, so a NO_MATCH does not rule out a different true
# physical coupon; it does challenge this rule's observable original footprint.
copied_source_word_matches = {}
for label, earlier in (("request1",coupons[1]),("earlier_label",coupons[0])):
    per_lane = []
    for lane in range(4):
        x = int.from_bytes(earlier[4*lane:4*lane+4],"little")
        y = int.from_bytes(coupons[3][4*lane:4*lane+4],"little")
        observed = int.from_bytes(coupons[2][4*lane:4*lane+4],"little")
        per_lane.append([f for f in range(16) if truth(x,y,f)==observed])
    copied_source_word_matches[label] = per_lane
assert all(all(not lane for lane in lanes)
           for lanes in copied_source_word_matches.values())


# Verify all 16 truth tables on all four binary input patterns.
for code in range(16):
    for aa, bb in itertools.product((0,MASK32),repeat=2):
        expected = MASK32 if (code >> (2*bool(aa)+bool(bb))) & 1 else 0
        assert truth(aa, bb, code) == expected

planted_ops = (3,5,10,12)
planted_coupon = construct(coupons[1], coupons[3], planted_ops)
planted_digest = hashlib.sha256(bytes(x ^ y for x,y in zip(planted_coupon,mask))).digest()
assert planted_digest != target
checks, plant_hits, original_hits = 0, [], []
for name, earlier in (("request1",coupons[1]),("earlier_label",coupons[0])):
    for ops in itertools.product(range(16),repeat=4):
        coupon = construct(earlier,coupons[3],ops)
        for stage, candidate in (
            ("coupon_xor_mask",bytes(x ^ y for x,y in zip(coupon,mask))),
            ("direct_component",coupon),
        ):
            digest = hashlib.sha256(candidate).digest()
            checks += 1
            if digest == planted_digest:
                plant_hits.append((name,ops,stage))
            if digest == target:
                original_hits.append((name,ops,stage,candidate.hex().upper()))
assert checks == 262144
assert plant_hits == [("request1",planted_ops,"coupon_xor_mask")]
print(json.dumps({"spool_sha256":PIN,"source_lines":4,"selected_copy_withheld":True,
                  "complete_K04_assignments":checks,
                  "copied_source_word_matches":copied_source_word_matches,
                  "planted_positive":plant_hits,
                  "original_K04_matches":original_hits},indent=2))
