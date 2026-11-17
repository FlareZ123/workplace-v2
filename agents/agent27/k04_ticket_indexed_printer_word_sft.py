"""Source-indexed K04 trial: L-29/N ticket numbers as ordinary-job offsets.

Hypothesis only. The source calls ST-xxx repair-ticket IDs, and does not
assert any ticket-to-printer-word or print-media relation. This code must
not be used to promote candidate bytes without original commitment PASS.
"""
import hashlib
import itertools
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
spool = root / "evidence/print/spool-reconstruction.log"
fleet = root / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt"
assert hashlib.sha256(spool.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(fleet.read_bytes()).hexdigest() == "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf"
lines = spool.read_text().splitlines()
ordinary = [
    line for line in lines
    if "ATTEMPT=1 STATE=ACK " in line
    and (m := re.search(r"JOB=PS-261003-(\d+)", line))
    and 300 <= int(m.group(1)) <= 427
]
assert len(ordinary) == 128
assert [int(re.search(r"JOB=PS-261003-(\d+)", line).group(1)) for line in ordinary] == list(range(300, 428))
packets = [bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", line).group(1)) for line in ordinary]
tickets = [int(s) for s in re.findall(r"L-29/N\s+0[1-5]\s+ST-(\d{3})\s+", fleet.read_text())]
assert tickets == [94, 81, 106, 99, 112]
assert any(
    "JOB=PS-261003-0417" in line
    and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line
    and "PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5" in line
    for line in lines
)
mask = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
target = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
words = [[packets[t][4*j:4*j+4] for j in range(4)] for t in tickets]
def compose(picks, lanes, flips):
    return b"".join(
        words[p][j][::-1] if reverse else words[p][j]
        for p, j, reverse in zip(picks, lanes, flips)
    )
def xor_mask(coupon):
    return bytes(a ^ b for a, b in zip(coupon, mask))
planted_coupon = compose((0, 2, 3, 4), (3, 0, 1, 2), (0, 1, 0, 1))
planted_digest = hashlib.sha256(xor_mask(planted_coupon)).digest()
seen = set()
hits = []
planted_count = 0
for picks in itertools.product(range(5), repeat=4):
    for lanes in itertools.product(range(4), repeat=4):
        for flips in itertools.product(range(2), repeat=4):
            coupon = compose(picks, lanes, flips)
            if coupon in seen:
                continue
            seen.add(coupon)
            component = xor_mask(coupon)
            planted_count += hashlib.sha256(component).digest() == planted_digest
            for candidate in (coupon, component):
                if hashlib.sha256(candidate).digest() == target:
                    hits.append((candidate.hex().upper(), picks, lanes, flips))
                    print("RECOVERED_K04", hits[-1])
assert len(seen) == 5**4 * 4**4 * 2**4 == 2_560_000
assert planted_count == 1
print("ticket-to-spool-index pilot", "tickets", tickets, "distinct_coupons", len(seen),
      "original_full_sha256_checks", 2*len(seen), "planted_positive", planted_count,
      "original_matches", len(hits))
