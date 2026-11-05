"""K04: invert a shared cassette printer pad on 15-digit service-ticket encodings.
Original 46-file evidence only, no source modifications. Python stdlib SFT:
python agents/agent45/k04_ticket_literal_sharedpad_sft.py
"""
from pathlib import Path
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
FLEET = (ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
assert hashlib.sha256(SPOOL).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(FLEET).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
tickets = {}
for line in FLEET.decode().splitlines():
    match = re.search(r"L-29/([NS])\s+(\d+)\s+ST-(\d{3})\s+(.*)$",line)
    if match:
        tickets.setdefault(match.group(1), []).append((int(match.group(2)),int(match.group(3))))
assert tickets == {"N":[(1,94),(2,81),(3,106),(4,99),(5,112)],
                   "S":[(1,130),(2,151),(3,121),(4,135),(5,142)]}
rows = [line for line in SPOOL.decode().splitlines()
        if ("2026-10-03T18:24:00Z" in line and
            "JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER" in line)]
assert len(rows) == 1
south = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})",rows[0]).group(1))
assert south.hex() == "234be186e97ee05830909790e336109e"
mask = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
target = bytes.fromhex(json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"])
assert mask.hex() == "8556c8cb6140a7f9a5123ac7571bee1c"
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"

def forms(lane,sentinel):
    numbers = [number for _,number in tickets[lane]]
    results=[]
    for permutation in itertools.permutations(numbers):
        digits = "".join(f"{n:03}" for n in permutation).encode()
        assert len(digits) == 15
        for insert in range(16):
            results.append(digits[:insert] + sentinel + digits[insert:])
    assert len(results) == 1920
    return results

def north_from_south(observed,fs,fn,law):
    if law == "xor":
        return bytes(v^a^b for v,a,b in zip(observed,fs,fn))
    if law in ("ring_le","ring_be"):
        byteorder = "little" if law=="ring_le" else "big"
        return ((int.from_bytes(observed,byteorder)-int.from_bytes(fs,byteorder)
                 +int.from_bytes(fn,byteorder))%(1<<128)).to_bytes(16,byteorder)
    return bytes((v-a+b)&255 for v,a,b in zip(observed,fs,fn))

matched=[];total=0
for pad_s,pad_n in ((b"0",b"0"),(b"S",b"N")):
    sf=forms("S",pad_s)
    nf=forms("N",pad_n)
    for insert in range(16):
        for fs in sf[insert::16]:
            for fn in nf[insert::16]:
                for law in ("xor","ring_le","ring_be","byte_add"):
                    physical = north_from_south(south,fs,fn,law)
                    component = bytes(x^y for x,y in zip(physical,mask))
                    if hashlib.sha256(component).digest()==target:
                        matched.append((pad_s,pad_n,insert,fs,fn,law,physical.hex()))
                    total+=1
    print("SOURCE_FAMILY",pad_s,pad_n,"checks",total,"matches",len(matched),flush=True)

planted=0
fs=forms("S",b"0")[0];fn=forms("N",b"0")[0]
u=bytes.fromhex("45a78c210fe32bd8e17ab046c02f915d")
for law in ("xor","ring_le","ring_be","byte_add"):
    if law=="xor":
        generated_s=bytes(a^b for a,b in zip(u,fs))
        expected_n=bytes(a^b for a,b in zip(u,fn))
    elif law in ("ring_le","ring_be"):
        byteorder="little" if law=="ring_le" else "big"
        generated_s=((int.from_bytes(u,byteorder)+int.from_bytes(fs,byteorder))%(1<<128)).to_bytes(16,byteorder)
        expected_n=((int.from_bytes(u,byteorder)+int.from_bytes(fn,byteorder))%(1<<128)).to_bytes(16,byteorder)
    else:
        generated_s=bytes((a+b)&255 for a,b in zip(u,fs))
        expected_n=bytes((a+b)&255 for a,b in zip(u,fn))
    assert north_from_south(generated_s,fs,fn,law)==expected_n
    planted+=1
assert total==1843200 and matched==[] and planted==4
print("PASS: 1843200 authentic K04 NO_MATCH, four independent full-coupon synthetic controls")
