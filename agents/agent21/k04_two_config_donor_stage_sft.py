"""Two original config fields as jointly staged p951 MT coupon donors.

Runs the single-donor SFT as an importable source-quotient initializer, then
adds joint source-consistency and full-coupon reconstruction checks.
"""
import hashlib
import importlib.util
import itertools
import re
from pathlib import Path

THIS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("one_donor", THIS / "k04_mask_nonce_shared_mt_donor_sft.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

def convert(data, endian, representation):
    x = [int.from_bytes(data[j*4:j*4+4], endian) for j in range(4)]
    return [b.model.untemper(v) for v in x] if representation == "tempered" else x

def reconstruct_two(first, start1, second, start2):
    equations = {}
    for observed, start in ((first, start1), (second, start2)):
        for lane in range(4):
            for bit, (v0, source_bit) in enumerate(b.quotient[start + lane - b.model.ORIGIN]):
                v = v0
                rhs = ((observed[lane] >> bit) & 1) ^ source_bit
                while v:
                    pivot = v.bit_length() - 1
                    if pivot not in equations:
                        equations[pivot] = (v, rhs)
                        break
                    other, value = equations[pivot]
                    v ^= other
                    rhs ^= value
                if not v and rhs:
                    return "CONTRADICTION", None, 0

    native = []
    count = 0
    for lane in range(4):
        val = 0
        for bit, (v0, source_bit) in enumerate(b.target[lane]):
            v = v0
            rhs = source_bit
            while v:
                pivot = v.bit_length() - 1
                if pivot not in equations:
                    break
                other, value = equations[pivot]
                v ^= other
                rhs ^= value
            if not v:
                count += 1
                val |= rhs << bit
        native.append(val)
    if count < 128:
        return "PARTIAL", None, count
    return "FULL", b"".join(b.temper(x).to_bytes(4, "little") for x in native), 128

# Source-accurate stage950/954 synthetic positive: stage950 carries intact
# printer row128 final word, then copied row129 first 3; stage954 carries
# copied row129 final word, then intact row130 first 3.
log = (b.source / "evidence/print/spool-reconstruction.log").read_bytes()
rows = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", log)]
assert len(rows) == 133
left = rows[128][12:] + rows[129][:12]
right = rows[129][12:] + rows[130][:12]
status, payload, count = reconstruct_two(convert(left, "little", "tempered"), 950,
                                         convert(right, "little", "tempered"), 954)
assert (status, count, payload) == ("FULL", 128, rows[129])
print("joint two-source coupon reconstruction planted positive PASS")

fields = {"mask": b.mask, "nonce": b.nonce}
orientations = list(itertools.product(("little", "big"), ("tempered", "native")))
counts = {"CONTRADICTION": 0, "PARTIAL": 0, "FULL": 0}
original_hits = []
for order in itertools.permutations(fields, 2):
    for p, q in itertools.product(range(948, 955), repeat=2):
        for op, oq in itertools.product(orientations, repeat=2):
            x = convert(fields[order[0]], *op)
            y = convert(fields[order[1]], *oq)
            status, candidate, count = reconstruct_two(x, p, y, q)
            counts[status] += 1
            if status == "FULL":
                component = bytes(a ^ c for a, c in zip(candidate, b.mask))
                if hashlib.sha256(component).hexdigest() == b.targets["slot_sha256"]["K04"]:
                    original_hits.append((order, p, q, op, oq, component.hex().upper()))
assert counts == {"CONTRADICTION": 1568, "PARTIAL": 0, "FULL": 0}
assert not original_hits
print("PASS: 1568 paired mask/nonce placements incompatible with original adjacent printer source")
