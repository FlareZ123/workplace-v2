"""Original source-pinned K04: five cassette ticket numbers as 15 ASCII digits
plus one arbitrary octet inserted anywhere. Execute from repository root:
python agents/agent4/k04_five_ticket_ascii_coupon_sft.py

Exploratory physical coupon encoding, not attested historical serialization.
Never uses the disputed selected ACK2 as fitting input.
"""
from pathlib import Path
from itertools import permutations
import hashlib
import json
import re

R = Path(__file__).resolve().parents[2] / "resources"
fleet = (R / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_bytes()
spool = (R / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(fleet).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
route = json.loads((R / "evidence/recovery-routing.json").read_text())
target = json.loads((R / "acceptance.json").read_text())["slot_sha256"]["K04"]
mask = bytes.fromhex(route["K04"]["masked_component"])
assert mask.hex() == "8556c8cb6140a7f9a5123ac7571bee1c"
assert target == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
tickets = {"N": [], "S": []}
for line in fleet.decode().splitlines():
    m = re.search(r"L-29/([NS])\s+(\d{2})\s+ST-(\d{3})\b", line)
    if m:
        tickets[m.group(1)].append((int(m.group(2)), int(m.group(3))))
assert tickets == {"N": [(1,94),(2,81),(3,106),(4,99),(5,112)],
                   "S": [(1,130),(2,151),(3,121),(4,135),(5,142)]}
rows = [s for s in spool.decode().splitlines()
        if "2026-10-03T18:24:00Z JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER" in s]
assert len(rows) == 1
south = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", rows[0]).group(1))
assert south.hex() == "234be186e97ee05830909790e336109e"

def coupons(lane):
    for order in permutations(n for _, n in tickets[lane]):
        base = "".join(f"{v:03d}" for v in order).encode("ascii")
        for index in range(16):
            for b in range(256):
                yield base[:index] + bytes((b,)) + base[index:]

def reduced(raw):
    return bytes(a ^ b for a, b in zip(raw, mask))

if __name__ == "__main__":
    matches = [v.hex().upper() for v in coupons("N")
               if hashlib.sha256(reduced(v)).hexdigest() == target]
    print("NORTH", "tested=491520", "full_original_K04_matches", matches)
    closest = 129
    exact = 0
    for v in coupons("S"):
        closest = min(closest, sum((a ^ b).bit_count() for a, b in zip(v, south)))
        exact += (v == south)
    print("SOUTH", "tested=491520", "exact_source_coupons", exact,
          "min_hamming_bits", closest)
    synthetic = b"094081106099112X"
    assert len(synthetic) == 16
    planted_digest = hashlib.sha256(reduced(synthetic)).hexdigest()
    assert any(v == synthetic for v in coupons("N"))
    assert hashlib.sha256(reduced(synthetic)).hexdigest() == planted_digest
    print("SYNTHETIC", "source_generated_complete_coupon", "PASS")
    assert not matches and exact == 0 and closest == 50
    print("PASS: 15+1 direct-ticket coupon encoding rejected under tested model")
