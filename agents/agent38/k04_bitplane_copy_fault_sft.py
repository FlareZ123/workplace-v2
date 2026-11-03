"""H-17 K04: exact one-bitplane arbitrary-per-byte copy-fault test.

Original sources and acceptance commitments remain read-only.
Supply the official archive ZIP as the optional first argument; when omitted,
read the equivalent unpacked repository resources/ directory.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile


def source(name: str) -> bytes:
    if len(sys.argv) > 1:
        with zipfile.ZipFile(sys.argv[1]) as archive:
            return archive.read(name)
    repo = Path(__file__).resolve().parents[2]
    return (repo / 'resources' / name).read_bytes()


route = json.loads(source('evidence/recovery-routing.json'))
accept = json.loads(source('acceptance.json'))
spool = source('evidence/print/spool-reconstruction.log').decode('ascii')
mask = bytes.fromhex(route['K04']['masked_component'])
assert len(mask) == 16
matches = []
for line in spool.splitlines():
    if ('JOB=PS-261003-0417' in line and 'ATTEMPT=2' in line
            and 'STATE=ACK' in line and 'CLASS=RECOVER' in line):
        matches.append(bytes.fromhex(re.search(r'\bPAYLOAD=([0-9A-F]{32})\b', line).group(1)))
assert len(matches) == 1
copied = bytes(a ^ b for a, b in zip(matches[0], mask))
target = accept['slot_sha256']['K04']
assert len(target) == 64
print('selected_ack=', matches[0].hex().upper())
print('copy_reduction=', copied.hex().upper())
print('original_sha256=', target)
print('source_lines=', len(spool.splitlines()))

# A serial/parity fault can independently toggle one shared bit lane in
# each byte. This covers 8 possible lane choices * 2^16 error masks, including
# >6 changed bytes which the earlier bounded bit-flip search did not cover.
planted_plane = 7
planted_positions = sum(1 << i for i in range(8))
planted = bytes((v ^ (0x80 if planted_positions >> i & 1 else 0)) for i, v in enumerate(copied))
planted_digest = hashlib.sha256(planted).hexdigest()
assert planted_digest != target
found = []
positive = []
for plane in range(8):
    e = 1 << plane
    current = bytearray(copied)
    # Gray code changes exactly one byte per candidate.
    prev = 0
    for index in range(1 << 16):
        gray = index ^ (index >> 1)
        change = gray ^ prev
        if change:
            byte_idx = (change & -change).bit_length() - 1
            current[byte_idx] ^= e
        prev = gray
        digest = hashlib.sha256(current).hexdigest()
        if digest == target:
            found.append((plane, gray, bytes(current).hex().upper()))
        if digest == planted_digest:
            positive.append((plane, gray, bytes(current).hex().upper()))
    print('completed_plane=', plane, 'candidates=', 65536)
assert positive == [(planted_plane, planted_positions, planted.hex().upper())], positive
print('planted_8_byte_bit7_copy_fault_positive=PASS')
print('total_tested_assignments=', 8 * (1 << 16))
print('original_matches=', len(found))
for hit in found:
    print('RECOVERED', hit)
