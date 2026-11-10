"""Exact original K04 conditional p951 MT stage -1082 rank-28 search.

Reads 132 intact original printer coupons, withholding selected row129 BEFORE
decoding. Constructs the full affine set of possible fourword coupons at the
single new rank-28 native stage, then checks every complete historical
SHA256(XOR-mask coupon). Pure stdlib; no source or candidate writes.

Run from repository root: python agents/agent26/k04_rank28_stage_fullscan_sft.py
This full test performs exactly 268,435,456 SHA256 comparisons.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import time

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
    "agent49_p951_source",ROOT/"agents/agent49/k04_p951_symbolic_basis.py"
)
mt=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
source,words=mt.source(ROOT)
assert source.rank==15365
assert mt.ORIGIN==-1100
assert mt.STARTS[129]==951
stage=-1082

def reduce_original(bitform):
    observed=0
    free=0
    while bitform:
        p=bitform.bit_length()-1
        row=source.rows.get(p)
        if row is None:
            free ^= 1<<p
            bitform ^= 1<<p
        else:
            bitform ^= row[0]
            observed ^= row[1]
    return observed,free

native_base=0
residuals=[]
for lane in range(4):
    for bit,form in enumerate(mt.get(words,stage+lane)):
        obs,free=reduce_original(form)
        native_base |= obs<<(32*lane+bit)
        residuals.append(free)

free_positions=0
for item in residuals:
    free_positions |= item
columns={}
native_deltas=[]
for p in range(free_positions.bit_length()-1,-1,-1):
    if not ((free_positions>>p)&1):
        continue
    column=sum(((r>>p)&1)<<i for i,r in enumerate(residuals))
    x=column
    while x:
        pivot=x.bit_length()-1
        if pivot not in columns:
            columns[pivot]=x
            native_deltas.append(column)
            break
        x ^= columns[pivot]
assert len(native_deltas)==28

def serialize_native(native):
    # The exact same little-endian 32bit-word printer serializer as intact rows.
    out=bytearray()
    for lane in range(4):
        value=(native>>(32*lane))&0xffffffff
        value ^= value>>11
        value ^= (value<<7)&0x9d2c5680
        value ^= (value<<15)&0xefc60000
        value ^= value>>18
        out.extend((value&0xffffffff).to_bytes(4,"little"))
    return bytes(out)

printer_base=serialize_native(native_base)
printer_deltas=[serialize_native(d) for d in native_deltas]
assert printer_base.hex().upper()=="020000000296C31CC1ABD694A9C9EAE2"
assert printer_deltas[0].hex().upper()=="02110844000000000000000000000000"

routing=json.loads((ROOT/"resources/evidence/recovery-routing.json").read_text())
accept=json.loads((ROOT/"resources/acceptance.json").read_text())
mask=bytes.fromhex(routing["K04"]["masked_component"])
target=bytes.fromhex(accept["slot_sha256"]["K04"])
assert target.hex()=="930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

base=bytes(a^b for a,b in zip(printer_base,mask))
value_deltas=printer_deltas
TOTAL=1<<28

def scan(digest,limit):
    current=bytearray(base)
    count=0
    for i in range(limit):
        if i:
            delta=value_deltas[(i&-i).bit_length()-1]
            for j in range(16):
                current[j]^=delta[j]
        if hashlib.sha256(current).digest()==digest:
            count+=1
            print("MATCH",i,bytes(current).hex().upper(),flush=True)
    return count

# Planted complete component positive on the identical affine coupon space.
index=1337
g=index^(index>>1)
planted=bytearray(base)
for j,d in enumerate(value_deltas):
    if (g>>j)&1:
        for k in range(16):
            planted[k]^=d[k]
planted_digest=hashlib.sha256(planted).digest()
assert scan(planted_digest,65536)==1
print("PLANTED_COMPLETE_POSITIVE_PASS",flush=True)

start=time.monotonic()
hits=scan(target,TOTAL)
print("ORIGINAL_COMPLETE",TOTAL,"rank28",len(value_deltas),
      "authentic_hits",hits,"elapsed_sec",round(time.monotonic()-start,3),
      flush=True)
assert hits==0
