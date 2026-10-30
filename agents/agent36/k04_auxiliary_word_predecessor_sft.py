"""Replication of Agent41 20-Oct TRP2 aux direct-LE MT donor test; not novel.

Original broader test: agents/agent41/k04_aux_mt_donor_sft.py (both endians).
Selected ACK and acceptance commitments remain withheld.
"""
import hashlib
import re
import struct
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'resources/evidence'
SPOOL = ROOT / 'print/spool-reconstruction.log'
REC = ROOT / 'recorder/trip-recorder.raw'
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == '7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083'
assert hashlib.sha256(REC.read_bytes()).hexdigest() == '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'


def ur(y, shift):
    x = y
    for _ in range(6):
        x = y ^ (x >> shift)
    return x & 0xFFFFFFFF


def ul(y, shift, mask):
    x = y
    for _ in range(6):
        x = y ^ ((x << shift) & mask)
    return x & 0xFFFFFFFF


def untemper(y):
    return ur(ul(ul(ur(y, 18), 15, 0xEFC60000), 7, 0x9D2C5680), 11)


def inverse_twist(y):
    bit = y >> 31
    mixed = (((y ^ (0x9908B0DF if bit else 0)) << 1) | bit) & 0xFFFFFFFF
    assert ((mixed >> 1) ^ (0x9908B0DF if mixed & 1 else 0)) == y
    return mixed


lines = [l for l in SPOOL.read_text().splitlines() if l.startswith('2026-')]
assert len(lines) == 133
words = []
for row, line in enumerate(lines):
    if row == 129:
        continue
    payload = bytes.fromhex(re.search(r'PAYLOAD=([0-9A-F]{32})', line).group(1))
    for j, val in enumerate(struct.unpack('<4I', payload)):
        words.append((row, j, untemper(val)))

raw = REC.read_bytes()
assert raw[:8] == b'TRP2DUMP'
count = struct.unpack_from('<I', raw, 12)[0]
assert count == 88 and len(raw) == 16 + count*24
aux = defaultdict(list)
controls = defaultdict(list)
for i in range(count):
    d = raw[16+i*24:16+(i+1)*24]
    stamp,node,event,latch,seq,ctl,reading,crc = struct.unpack('<IHBBI4sII', d)
    valid = zlib.crc32(d[:20]) & 0xFFFFFFFF == crc
    aux[untemper(reading) & 0x7FFFFFFF].append((i, reading, valid))
    controls[untemper(int.from_bytes(ctl,'little')) & 0x7FFFFFFF].append((i,seq,valid))

pair_count = 0
aux_hits = []
control_hits = []
for a,(row,j,x) in enumerate(words):
    for nextrow,k,y in words[a+1:]:
        if row == nextrow:
            continue
        pair_count += 1
        candidate = inverse_twist(x ^ y) & 0x7FFFFFFF
        for i,reading,valid in aux.get(candidate,()):
            aux_hits.append((i,reading,row,j,nextrow,k,valid))
        for i,seq,valid in controls.get(candidate,()):
            control_hits.append((i,seq,row,j,nextrow,k,valid))

assert pair_count == 138336, pair_count
assert len(control_hits) == 7, control_hits
assert (28,992,10,0,41,0,True) in control_hits
# Inject a known, original positive control into the auxiliary field's lookup.
# This is purely synthetic; it does not change any recorded source byte.
known = untemper(int.from_bytes(raw[16+28*24+12:16+28*24+16], 'little')) & 0x7FFFFFFF
synthetic_aux = dict(aux)
synthetic_aux[known] = [(28, int.from_bytes(raw[16+28*24+12:16+28*24+16], 'little'), True)]
assert (28, 992, 10, 0, 41, 0, True) in control_hits
assert any(row == 10 and j == 0 and nextrow == 41 and k == 0 and
           synthetic_aux.get(inverse_twist(x ^ y) & 0x7FFFFFFF)
           for a, (row, j, x) in enumerate(words)
           for nextrow, k, y in words[a+1:])
assert len(aux_hits) == 0
print('SCHEMA_RECORDS',count,'NONSELECTED_PRINTER_PAIRS',pair_count)
print('ORIGINAL_OFFSET12_CONTROL_POSITIVE_MATCHES',len(control_hits),'including_record28',True)
print('SYNTHETIC_INJECT_OFFSET16_COPY_OF_RECORD28_CONTROL', 'PASS')
print('ORIGINAL_OFFSET16_RAW_PROCESS_READING_MATCHES',len(aux_hits))
for hit in aux_hits: print('  ',hit)
print('K04_SELECTED_ROW129_USED',False,'K04_ACCEPTANCE_USED',False)
