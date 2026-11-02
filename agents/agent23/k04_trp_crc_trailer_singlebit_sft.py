"""TRP2 four damaged CRCs: exact one-bit error-location diagnostic.

Original read-only H-17 24byte recorder entries. No K05 invalid records
are promoted as accepted; the source-pinned CRC consistency test is distinct
from REC8 slot verification.
"""
from pathlib import Path
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2] / "resources"
recording = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(recording).hexdigest() == (
    "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
)
assert recording[:8] == b"TRP2DUMP"
assert len(recording) == 16 + 88 * 24

bad = []
valid_control = None
for record_id in range(88):
    packet = recording[16 + 24 * record_id:16 + 24 * (record_id + 1)]
    expected = zlib.crc32(packet[:20])
    stored = struct.unpack_from("<I", packet, 20)[0]
    delta = stored ^ expected
    if delta:
        bad.append((record_id, delta, packet[12:16].hex().upper()))
    if record_id == 28:
        assert delta == 0
        valid_control = packet
assert [(n, d) for n, d, _ in bad] == [(14, 0x100), (41, 0x100), (72, 0x100), (77, 0x100)]

# CRC32 is affine over a fixed 20-byte length: one-bit syndrome is input-independent.
source = bytes(20)
start = zlib.crc32(source)
syndromes = {}
for bit in range(160):
    damaged = bytearray(source)
    damaged[bit // 8] ^= 1 << (bit % 8)
    syndrome = start ^ zlib.crc32(damaged)
    syndromes[syndrome] = bit
assert 0x100 not in syndromes

# Positive control: flip bit8 of the CRC trailer of a genuinely valid packet.
changed = bytearray(valid_control)
changed[21] ^= 1
assert (
    zlib.crc32(changed[:20]) ^ struct.unpack_from("<I", changed, 20)[0]
) == 0x100

print(json.dumps({
    "source_record_count": 88,
    "bad_crc_records": bad,
    "all_four_syndrome": "0x00000100",
    "data_single_bit_positions_with_that_syndrome": 0,
    "single_crc_trailer_bit8_positive": True,
    "implication": "CRC trailer bit8 is the sole single-bit explanation; multiple data bit errors remain possible",
}, indent=2))
