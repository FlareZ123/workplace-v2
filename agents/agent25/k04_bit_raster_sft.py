"""Source-only H-17 K04 128-bit printer raster readback permutation test.

Run: python agents/agent25/k04_bit_raster_sft.py
Requires original resources/ at repo root. No source writes.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = [bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([A-F0-9]{32})", spool)]
assert len(rows) == 133
source = rows[129]
assert source.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
mask = bytes.fromhex(routing["K04"]["masked_component"])
target = bytes.fromhex(accept["slot_sha256"]["K04"])

def raster(data, height, width, input_mode, output_mode, mirror, flip, transposed, bitorder):
    bits = [(value >> bit) & 1 for value in data
            for bit in (range(8) if bitorder else range(7,-1,-1))]
    assert len(bits) == height*width
    def coords(mode):
        axis,serpentine = divmod(mode,2)
        if axis == 0:
            return [(i,j if not (serpentine and i%2) else width-1-j)
                    for i in range(height) for j in range(width)]
        return [(i if not (serpentine and j%2) else height-1-i,j)
                for j in range(width) for i in range(height)]
    grid = dict(zip(coords(input_mode), bits))
    grid = {(height-1-i if flip else i, width-1-j if mirror else j): v
            for (i,j),v in grid.items()}
    if transposed:
        grid = {(j,i):v for (i,j),v in grid.items()}
        height,width = width,height
    values = [grid[p] for p in coords(output_mode)]
    return bytes(sum(values[k*8+b] << (b if bitorder else (7-b))
                     for b in range(8)) for k in range(16))

def rollbits(block,height,dr,dc):
    bits = [(value >> (7-j)) & 1 for value in block for j in range(8)]
    width = 128 // height
    values = [bits[((i-dr)%height)*width+(j-dc)%width]
              for i in range(height) for j in range(width)]
    return bytes(sum(values[k*8+b] << (7-b) for b in range(8))
                 for k in range(16))

base = set()
for height in (1,2,4,8,16,32,64,128):
    for input_mode,output_mode in itertools.product(range(4),repeat=2):
        for mirror,flip,transposed,bitorder in itertools.product((False,True),repeat=4):
            base.add(raster(source,height,128//height,input_mode,output_mode,
                            mirror,flip,transposed,bitorder))
assert len(base) == 230 and source in base
extended = set(base)
for height in (2,4,8,16,32,64):
    for block in base:
        for dr in range(height):
            for dc in range(128//height):
                extended.add(rollbits(block,height,dr,dc))
assert len(extended) == 123028, len(extended)
def digest(payload):
    return hashlib.sha256(bytes(x ^ y for x,y in zip(payload,mask))).digest()
planted = next(block for block in base if block != source)
assert sum(digest(block) == digest(planted) for block in base) == 1
assert sum(digest(block) == digest(planted) for block in extended) == 1
hits = [block.hex().upper() for block in extended if digest(block) == target]
assert hits == [], hits
print("Synthetic planted candidate PASS, unique base transforms 230")
print("Distinct 128-bit raster, mirror, serpentine, scan-order and origin shifts:",len(extended))
print("Original K04 commitment matches:",len(hits))
print("Original selected physical coupon remains unauthenticated; K04 unresolved")
