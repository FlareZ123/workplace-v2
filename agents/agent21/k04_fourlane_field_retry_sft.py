"""Four 32-bit lane GF(2^32) affine retry issuer, source-selected complete K04 test.
Source original coupon row129 withheld from all calculations.
Run: python k04_fourlane_field_retry_sft.py [archive_root]
"""
import hashlib
import re
import sys
from itertools import permutations
from pathlib import Path

MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
POLYS = (0x10000008D, 0x1000000AF, 0x1000000C5)
U32 = (1 << 32) - 1


def multiply(a, b, polynomial):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 32):
            a ^= polynomial
    return result


def exponentiate(a, n, polynomial):
    value = 1
    while n:
        if n & 1:
            value = multiply(value, a, polynomial)
        a = multiply(a, a, polynomial)
        n >>= 1
    return value


def unpack(raw, endian, reverse_bits):
    words = [int.from_bytes(raw[j:j+4], endian) for j in range(0, 16, 4)]
    if reverse_bits:
        words = [int(f"{w:032b}"[::-1], 2) for w in words]
    return words


def pack(words, endian, reverse_bits):
    if reverse_bits:
        words = [int(f"{w:032b}"[::-1], 2) for w in words]
    return b"".join(w.to_bytes(4, endian) for w in words)


def learn(a, b, u, v, polynomial, order):
    pairs = []
    for output_lane, input_lane in enumerate(order):
        den = a[input_lane] ^ u[input_lane]
        assert den != 0
        slope = multiply(
            b[output_lane] ^ v[output_lane],
            exponentiate(den, (1 << 32) - 2, polynomial),
            polynomial,
        )
        intercept = b[output_lane] ^ multiply(slope, a[input_lane], polynomial)
        assert multiply(slope, u[input_lane], polynomial) ^ intercept == v[output_lane]
        pairs.append((slope, intercept))
    return pairs


def apply(pairs, words, polynomial, order):
    return [
        multiply(slope, words[input_lane], polynomial) ^ intercept
        for (slope, intercept), input_lane in zip(pairs, order)
    ]


def main(root):
    spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    rows = [bytes.fromhex(x.decode())
            for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(rows) == 133
    assert b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in spool
    a, b, c, u, v = [rows[i] for i in (117, 128, 130, 120, 132)]
    assert a.hex().upper() == "E1E60D5F6B6DD2225FA6D5A2A63AD932"
    assert b.hex().upper() == "CD3E4F216ADB2FB180DA2AA90B33F7A4"
    assert c.hex().upper() == "44D53DFC29D7943A95D89371DA58EC64"
    assert u.hex().upper() == "31C9714DD36DB2677BB9006670A9DFFD"
    assert v.hex().upper() == "432475F72A62DB39F3D5693E2C937FA4"
    attempts = negatives = positives = whole_holdouts = partial_holdouts = 0
    for polynomial in POLYS:
        for endian in ("little", "big"):
            for reverse_bits in (False, True):
                source = [unpack(x, endian, reverse_bits) for x in (a,b,c,u,v)]
                aw,bw,cw,uw,vw = source
                for order in permutations(range(4)):
                    coefficients = learn(aw,bw,uw,vw,polynomial,order)
                    predicted = apply(coefficients,bw,polynomial,order)
                    holdout = apply(coefficients,predicted,polynomial,order)
                    agreements = sum(x == y for x,y in zip(holdout,cw))
                    partial_holdouts += agreements
                    whole_holdouts += agreements == 4
                    coupon = pack(predicted,endian,reverse_bits)
                    component = bytes(x ^ y for x,y in zip(coupon,MASK))
                    negatives += hashlib.sha256(component).hexdigest() == TARGET
                    attempts += 1
                    # Synthetic two-pair learning, missing middle and heldout
                    # under the same full-field machine, permutation and hash.
                    planted_coeff = [((0x93A47521+17*i)&U32,
                                      (0x1ABCD234+13*i)&U32) for i in range(4)]
                    plant_a = [((0x7B33C45F+31*i)&U32) for i in range(4)]
                    plant_u = [((0xB243D569+29*i)&U32) for i in range(4)]
                    plant_b = apply(planted_coeff,plant_a,polynomial,order)
                    plant_v = apply(planted_coeff,plant_u,polynomial,order)
                    derived = learn(plant_a,plant_b,plant_u,plant_v,polynomial,order)
                    plant_x = apply(planted_coeff,plant_b,polynomial,order)
                    plant_c = apply(planted_coeff,plant_x,polynomial,order)
                    assert apply(derived,plant_x,polynomial,order) == plant_c
                    candidate = pack(apply(derived,plant_b,polynomial,order),
                                     endian,reverse_bits)
                    planted = pack(plant_x,endian,reverse_bits)
                    target = hashlib.sha256(bytes(x ^ y for x,y in zip(planted,MASK))).digest()
                    positives += hashlib.sha256(bytes(x ^ y for x,y in zip(candidate,MASK))).digest() == target
    assert attempts == 288 and negatives == 0 and positives == 288
    assert whole_holdouts == 0 and partial_holdouts == 0
    print({"models":attempts, "original_K04_hits":negatives,
           "source_holdout_word_agreements":partial_holdouts,
           "source_holdout_whole_packet_hits":whole_holdouts,
           "synthetic_full_target_hits":positives})


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("."))
