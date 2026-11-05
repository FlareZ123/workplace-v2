"""H-17 K04: five cassette ticket indices modulo 16, source-derived byte repairs.
Run: python agents/agent45/k04_ticket_mod16_fivebyte_sft.py
Original evidence and acceptance remain read-only. Python standard library.
"""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import re
import zlib

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
FLEET = ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
CSV = ROOT / "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(FLEET.read_bytes()).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
lines = [s for s in SPOOL.read_text().splitlines()
         if "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in s]
assert len(lines) == 1
copied = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", lines[0]).group(1))
assert copied.hex() == "a9a9dc5731a5e2ae879c47215c2559d5"
mask = bytes.fromhex(json.loads((ROOT / "evidence/recovery-routing.json").read_text())["K04"]["masked_component"])
target = bytes.fromhex(json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"])
assert mask.hex() == "8556c8cb6140a7f9a5123ac7571bee1c"
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
tickets = []
for line in FLEET.read_text().splitlines():
    m = re.search(r"L-29/N\s+(\d+)\s+ST-(\d{3})\s+(.*)$", line)
    if m:
        tickets.append((int(m.group(1)), int(m.group(2)), m.group(3)))
assert [n for _, n, _ in tickets] == [94, 81, 106, 99, 112]
positions = [n % 16 for _, n, _ in tickets]
assert positions == [14, 1, 10, 3, 0] and len(set(positions)) == 5
docket = {}
with CSV.open(newline="") as f:
    for row in csv.DictReader(line for line in f if not line.startswith("#")):
        if (row["posting"], row["run"], row["account"], row["source"], row["folio_or_jacket"]) == (
            "POSTED", "R3", "FA-17", "L29", "H17-POL-17/A3"
        ):
            docket[int(row["line_ref"][3:])] = row
assert set(docket) == {n for _, n, _ in tickets}

def ticket_bytes(tab, number, part):
    row = docket[number]
    cents = round(float(row["amount_eur"]) * 100)
    values = [number, 255-number, tab, number//10, number%10, number%16,
              sum(map(int, str(number))), cents&255, (cents>>8)&255,
              int(row["amount_eur"].split(".")[0]), number^tab, number+tab, number-tab]
    for phrase in (f"ST-{number:03d}", row["description"], part):
        data = phrase.encode("ascii")
        values.extend((hashlib.sha256(data).digest()[0],
                       hashlib.md5(data).digest()[0], zlib.crc32(data)&255))
    return sorted({v&255 for v in values})

families = [ticket_bytes(*t) for t in tickets]
assert [len(x) for x in families] == [20, 18, 21, 17, 18]
planted = bytearray(copied)
for p, x in zip(positions, (v[0] for v in families)):
    planted[p] = x
plant_digest = hashlib.sha256(bytes(x^y for x,y in zip(planted,mask))).digest()
plant_count = 0
total = 0
matches = []
for op in ("replace", "xor", "add", "sub"):
    for values in itertools.product(*families):
        coupon = bytearray(copied)
        for position, value in zip(positions, values):
            if op == "replace": coupon[position] = value
            elif op == "xor": coupon[position] ^= value
            elif op == "add": coupon[position] = (coupon[position]+value)&255
            else: coupon[position] = (coupon[position]-value)&255
        digest = hashlib.sha256(bytes(x^y for x,y in zip(coupon,mask))).digest()
        if digest == target:
            matches.append((op, values, coupon.hex()))
        if op == "replace" and digest == plant_digest:
            plant_count += 1
        total += 1
    print("DONE",op,"assignments",total,"matches",len(matches),flush=True)
assert total == 9253440 and plant_count == 1
print("PASS 9253440 source-derived assignments, 0 original K04 matches, planted positive 1")
assert matches == []
