"""Source-pinned K04 printer internal checksum-lane search."""
from hashlib import sha256
from pathlib import Path
import re
import struct
import zlib
import binascii

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
REC_HASH = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SELECTED = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")


def crc_reflected(data, init, poly, width, xorout=0):
    value = init
    mask = (1 << width) - 1
    for b in data:
        value ^= b
        for _ in range(8):
            value = (value >> 1) ^ (poly if value & 1 else 0)
    return (value ^ xorout) & mask


def algorithms():
    return [
        (2, "ccitt_0", lambda d: binascii.crc_hqx(d, 0)),
        (2, "ccitt_ffff", lambda d: binascii.crc_hqx(d, 0xFFFF)),
        (2, "arc", lambda d: crc_reflected(d, 0, 0xA001, 16)),
        (2, "modbus", lambda d: crc_reflected(d, 0xFFFF, 0xA001, 16)),
        (2, "kermit", lambda d: crc_reflected(d, 0, 0x8408, 16)),
        (2, "x25", lambda d: crc_reflected(d, 0xFFFF, 0x8408, 16, 0xFFFF)),
        (4, "crc32", zlib.crc32),
        (4, "crc32c", lambda d: crc_reflected(d, 0xFFFFFFFF, 0x82F63B78, 32, 0xFFFFFFFF)),
        (4, "adler32", zlib.adler32),
    ]


def run():
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    recorder = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert sha256(spool).hexdigest() == SPOOL_HASH
    assert sha256(recorder).hexdigest() == REC_HASH
    packets = [bytes.fromhex(s.decode()) for s in re.findall(
        rb"^\d{4}-\d\d-\d\dT[^\n]+PAYLOAD=([0-9A-F]{32})", spool, re.M)]
    assert len(packets) == 133
    assert [i for i, p in enumerate(packets) if p == SELECTED] == [129]
    intact = packets[:129] + packets[130:]
    assert recorder[:8] == b"TRP2DUMP"
    assert struct.unpack_from("<HHI", recorder, 8) == (2, 24, 88)
    records = [recorder[16 + 24*i:40 + 24*i] for i in range(88)]
    good = sum(zlib.crc32(r[:20]) == struct.unpack_from("<I", r, 20)[0]
               for r in records)
    assert good == 84
    assert zlib.crc32(b"123456789") == 0xCBF43926
    assert crc_reflected(b"123456789", 0xFFFFFFFF, 0x82F63B78, 32, 0xFFFFFFFF) == 0xE3069283
    assert crc_reflected(b"123456789", 0, 0xA001, 16) == 0xBB3D
    assert crc_reflected(b"123456789", 0xFFFF, 0xA001, 16) == 0x4B37
    assert crc_reflected(b"123456789", 0, 0x8408, 16) == 0x2189
    assert crc_reflected(b"123456789", 0xFFFF, 0x8408, 16, 0xFFFF) == 0x906E
    assert binascii.crc_hqx(b"123456789", 0xFFFF) == 0x29B1
    hypothesis_count = 0
    total_matches = 0
    for width, label, calculate in algorithms():
        matches = 0
        for offset in range(17 - width):
            for order in ("little", "big"):
                hypothesis_count += 1
                for packet in intact:
                    actual = int.from_bytes(packet[offset:offset+width], order)
                    expected = calculate(packet[:offset] + packet[offset+width:])
                    matches += actual == expected
                assert calculate(SELECTED[:offset] + SELECTED[offset+width:]) != int.from_bytes(
                    SELECTED[offset:offset+width], order)
        print(label, "models", 2*(17-width), "intact_matches", matches)
        total_matches += matches
    assert hypothesis_count == 258
    assert total_matches == 0
    parity = sum(not (lambda p: __import__("functools").reduce(int.__xor__, p))(p)
                 for p in packets)
    assert parity == 2
    print("source_recorder_crc_positive", good, "of", 88)
    print("printer_crc_geometries", hypothesis_count)
    print("printer_crc_matches", total_matches)
    print("printer_fullbyte_xor_parity_zero", parity)


if __name__ == "__main__":
    run()
