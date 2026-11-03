"""H17 REC8: test systematic P/Q dual-parity, with K04/K08 as parity slots.

This differs from a degree-five evaluation-polynomial RS(8,6) codeword:
the six accepted components are *data* and two missing slots would be
explicit XOR P and weighted Q checksum blocks. No original document
attests this speculative cross-component coding architecture.
"""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys
from zipfile import ZipFile

SLOTS = ("K01", "K02", "K03", "K05", "K06", "K07")
VALUES = (
    "049AAB2E1CDE7A82CD7C60234303C91A",
    "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "1384AF96E25D6ADA666209CB55E062FA",
    "FF8B78200A56E8586DCDA00EF01E4572",
    "5DBF40EE52FAAED9A536D3326CF0D95A",
    "93495F5E425AB8E592123DABAEB68545",
)

def field_mul(a, b, width, reduce):
    mask = (1 << width) - 1
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a = ((a << 1) & mask) ^ (reduce if a & (1 << (width-1)) else 0)
    return out

def parity(data, width, reduce, order, coefficients):
    assert len(data) == len(coefficients) == 6
    chunk = width // 8
    p, q = bytearray(16), bytearray(16)
    for offset in range(0,16,chunk):
        words = [int.from_bytes(x[offset:offset+chunk], order) for x in data]
        pw = 0
        qw = 0
        for w,c in zip(words,coefficients):
            pw ^= w
            qw ^= field_mul(w,c,width,reduce)
        p[offset:offset+chunk] = pw.to_bytes(chunk,order)
        q[offset:offset+chunk] = qw.to_bytes(chunk,order)
    return bytes(p),bytes(q)

def read_acceptance():
    if len(sys.argv) > 1:
        with ZipFile(sys.argv[1]) as archive:
            return json.loads(archive.read("acceptance.json"))
    root = Path(__file__).resolve().parents[2] / "resources"
    return json.loads((root / "acceptance.json").read_text())

accept = read_acceptance()
known = tuple(bytes.fromhex(x) for x in VALUES)
assert all(sha256(v).hexdigest() == accept["slot_sha256"][name]
           for name, v in zip(SLOTS, known))
assert field_mul(0x57,0x13,8,0x1B) == 0xFE
assert field_mul(0x80,2,8,0x1B) == 0x1B
assert field_mul(0x80,2,8,0x1D) == 0x1D
assert field_mul(1 << 127,2,128,0x87) == 0x87
target4 = bytes.fromhex(accept["slot_sha256"]["K04"])
target8 = bytes.fromhex(accept["slot_sha256"]["K08"])

records = []
for width, reduce in ((8,0x1D),(8,0x1B),(128,0x87)):
    orders = ("big","little") if width == 128 else ("little",)
    for endian, reverse, coord, swap in product(
            orders,(False,True),("compact","slot"),(False,True)):
        data = known[::-1] if reverse else known
        indices = (0,1,2,4,5,6) if coord == "slot" else tuple(range(6))
        coefficients = tuple(1 << i for i in indices)
        p,q = parity(data,width,reduce,endian,coefficients)
        predicted4, predicted8 = ((q,p) if swap else (p,q))
        # Genuine planted parity pair with its own two independently SHA256
        # committed synthetic component values, checking the same recovery path.
        synthetic = tuple(sha256(f"systematic-{width}-{reduce}-{i}".encode()).digest()[:16]
                          for i in range(6))
        planted_p, planted_q = parity(synthetic,width,reduce,endian,coefficients)
        manual_p = bytes(synthetic[0][j] ^ synthetic[1][j] ^ synthetic[2][j] ^
                         synthetic[3][j] ^ synthetic[4][j] ^ synthetic[5][j]
                         for j in range(16))
        assert planted_p == manual_p
        planted4, planted8 = ((planted_q,planted_p) if swap
                              else (planted_p,planted_q))
        controlled = parity(synthetic,width,reduce,endian,coefficients)
        controlled4, controlled8 = (controlled[::-1] if swap else controlled)
        assert sha256(controlled4).digest() == sha256(planted4).digest()
        assert sha256(controlled8).digest() == sha256(planted8).digest()
        records.append({
            "width":width,"polynomial":reduce,"endian":endian,
            "reverse":reverse,"coord":coord,"swap":swap,
            "k04":predicted4.hex().upper(),"k08":predicted8.hex().upper(),
            "k04_match":sha256(predicted4).digest()==target4,
            "k08_match":sha256(predicted8).digest()==target8,
        })
assert len(records)==32 and len({(r["k04"],r["k08"]) for r in records})==32
print(json.dumps({
    "models":len(records),"distinct_complete_pairs":32,
    "six_original_accepted_components_verified":True,
    "planted_complete_dual_parity_positive":True,
    "original_K04_matches":[r for r in records if r["k04_match"]],
    "original_K08_matches":[r for r in records if r["k08_match"]],
    "sample_first_pair":records[0],
},indent=2))
