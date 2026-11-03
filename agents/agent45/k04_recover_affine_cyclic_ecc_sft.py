"""H17 K04: source-only class-specific affine cyclic integrity/ECC discriminator.

Run: python agents/agent45/k04_recover_affine_cyclic_ecc_sft.py resources
     python agents/agent45/k04_recover_affine_cyclic_ecc_sft.py h17-archive-dump.zip

Does the 16-byte RECOVER ACK coupon have an internal fixed CRC/cyclic code that
could repair the corrupted selected ACK? All 37 other original RECOVER ACK
payloads are original-source controls. Selected row129 is EXCLUDED before all
decoding. K04 acceptance, mask, K08, candidate and verifier are never read.
"""
import binascii
import hashlib
import random
import re
import sys
import zlib
from functools import reduce
from pathlib import Path
from zipfile import ZipFile

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REV = bytes(int(f"{i:08b}"[::-1], 2) for i in range(256))


def polynomial_mod(x, g):
    width = g.bit_length()
    while x.bit_length() >= width:
        x ^= g << (x.bit_length() - width)
    return x


def polynomial_gcd(a, b):
    while b:
        a, b = b, polynomial_mod(a, b)
    return a


def affine_gcd(packets):
    values = [int.from_bytes(p, "big") for p in packets]
    return reduce(polynomial_gcd, (v ^ values[0] for v in values[1:]))


def transform(packet, backward=False, reverse_bits=False, field=None):
    p = bytearray(packet)
    if field is not None:
        size, side = field
        if side == "first":
            p[:size] = reversed(p[:size])
        else:
            p[-size:] = reversed(p[-size:])
    if backward:
        p.reverse()
    if reverse_bits:
        p = bytearray(REV[x] for x in p)
    return bytes(p)


def gf_mul(a, b, primitive):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 256:
            a ^= primitive
    return result


def gf_pow(base, exp, primitive):
    result = 1
    for _ in range(exp):
        result = gf_mul(result, base, primitive)
    return result


def root_syndrome(packet, primitive, alpha, fcr):
    point = gf_pow(alpha, fcr, primitive)
    result = 0
    for c in packet:
        result = gf_mul(result, point, primitive) ^ c
    return result


def source(root):
    if root.is_file():
        with ZipFile(root) as archive:
            spool = archive.read("evidence/print/spool-reconstruction.log")
    else:
        spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    rows = []
    for line in spool.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        row = dict(token.split("=", 1) for token in line.split()[1:])
        rows.append(row)
    assert len(rows) == 133
    assert (rows[129]["JOB"], rows[129]["ATTEMPT"], rows[129]["STATE"],
            rows[129]["CLASS"]) == ("PS-261003-0417", "2", "ACK", "RECOVER")
    assert rows[129]["PAYLOAD"] == "A9A9DC5731A5E2AE879C47215C2559D5"

    # Entirely hold out the selected disputed ACK2 before deriving any code.
    ordinary = [r for i, r in enumerate(rows) if i != 129]
    assert len(ordinary) == 132
    ack = [r for r in ordinary if r["STATE"] == "ACK"]
    recover = [bytes.fromhex(r["PAYLOAD"]) for r in ack
               if r["CLASS"] == "RECOVER"]
    assert len(ack) == 130 and len(recover) == 37
    assert len([r for r in ordinary if r["STATE"] == "REQUESTED"]) == 2
    return recover


def positive_control():
    # Deterministic GF2 systematic CRC16 codewords with a *shared unknown*
    # 128-bit copy mask. Pairwise-XOR removes this fixed affine offset.
    rng = random.Random(202611032011)
    polynomial = (1 << 16) | 0x1021
    shared_mask = rng.getrandbits(128)
    packets = []
    for _ in range(37):
        message = rng.getrandbits(112)
        bits = message << 16
        codeword = bits ^ polynomial_mod(bits, polynomial)
        assert polynomial_mod(codeword, polynomial) == 0
        packets.append((codeword ^ shared_mask).to_bytes(16, "big"))
    gcd = affine_gcd(packets)
    assert gcd.bit_length() - 1 == 16, hex(gcd)
    assert polynomial_mod(gcd, polynomial) == 0
    altered = packets.copy()
    tampered = int.from_bytes(altered[10], "big") ^ (1 << 83)
    altered[10] = tampered.to_bytes(16, "big")
    assert affine_gcd(altered) == 1
    print("SYNTHETIC_AFFINE_CRC16 recovered degree 16; one-bit wrong-copy control gcd1 PASS")


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    positive_control()
    packets = source(root)

    # All direct-packet and conventional CRC-byte-order variants are
    # predeclared here. A nonconstant per-record scrambler is not covered.
    fields = (None, (2, "first"), (2, "last"),
              (4, "first"), (4, "last"))
    gcds = {}
    for backward in (False, True):
        for reverse_bits in (False, True):
            for field in fields:
                ident = (backward, reverse_bits, str(field))
                gcds[ident] = affine_gcd([
                    transform(p, backward, reverse_bits, field) for p in packets
                ])
    assert len(gcds) == 20
    assert set(gcds.values()) == {1}, gcds
    print("ORIGINAL_RECOVER_ACK_COUNT", len(packets),
          "AFFINE_CYCLIC_BYTE_BIT_LAYOUTS", len(gcds),
          "ALL_GF2_POLYNOMIAL_GCD_1", flush=True)

    # A conventional shortened systematic RS codeword, even with a fixed
    # XOR scrambler, has the same root syndrome in every encoded packet.
    # One varying root suffices to exclude each listed fixed-format model.
    rs_counts = []
    for primitive in (0x11d, 0x11b):
        for alpha in (2, 3):
            for fcr in (0, 1, 2):
                for backward in (False, True):
                    syndromes = {root_syndrome(p[::-1] if backward else p,
                                               primitive, alpha, fcr)
                                 for p in packets}
                    rs_counts.append(len(syndromes))
    assert len(rs_counts) == 24
    assert min(rs_counts) > 1
    print("ORIGINAL_RS_FIRST_ROOT_MODELS", len(rs_counts),
          "distinct_syndrome_min", min(rs_counts),
          "distinct_syndrome_max", max(rs_counts), flush=True)

    # Literal standard checksum placement controls, robust to a common
    # fixed initialization and/or output-XOR constant across equal-length
    # records: test whether the per-record checksum residual stays fixed.
    crc_counts = {}
    for side in ("last", "first"):
        for endian in ("little", "big"):
            for label, size, checksum in (
                ("CRC32", 4, zlib.crc32),
                ("CCITT16", 2, lambda b: binascii.crc_hqx(b, 0)),
                ("Adler32", 4, zlib.adler32),
            ):
                residues = []
                for packet in packets:
                    data, check = ((packet[:-size], packet[-size:])
                                   if side == "last" else
                                   (packet[size:], packet[:size]))
                    residues.append(checksum(data) ^
                                    int.from_bytes(check, endian))
                crc_counts[(label, side, endian)] = len(set(residues))
    assert len(crc_counts) == 12
    assert all(v > 1 for v in crc_counts.values())
    print("ORIGINAL_FIXED_CHECKSUM_RESIDUE_MODELS", len(crc_counts),
          "distinct_residue_min", min(crc_counts.values()),
          "distinct_residue_max", max(crc_counts.values()), flush=True)
    print("NO_SUPPORTED_RECOVER_COUPON_CRC_OR_CYCLIC_ECC_REPAIR_MODEL",
          "selected r129 untouched, original K04/K08 still missing")


if __name__ == "__main__":
    main()
