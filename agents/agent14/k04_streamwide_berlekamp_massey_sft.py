"""Source-only Berlekamp-Massey holdout for the original 128 ordinary spool packets.
Run: python agents/agent14/k04_streamwide_berlekamp_massey_sft.py
Excludes the anomalous 0417/RECOVER/ACK2 target and all exceptional tail records.
"""
from pathlib import Path
from hashlib import sha256
import re

ROOT = Path(__file__).resolve().parents[2] / "resources"
source = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert sha256(source).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = []
for line in source.decode("utf-8").splitlines():
    m = re.search(r"JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32})", line)
    if m and 300 <= int(m[1]) <= 427 and m[2] == "1" and m[3] == "ACK":
        rows.append((int(m[1]), bytes.fromhex(m[5])))
assert len(rows) == 128 and [a for a, _ in rows] == list(range(300, 428))

def bits_from_bytes(block: bytes, reverse_bytes: bool, msb: bool):
    if reverse_bytes:
        block = block[::-1]
    for x in block:
        for i in (range(7, -1, -1) if msb else range(8)):
            yield (x >> i) & 1

def berlekamp_massey(data):
    C = B = 1
    L = 0
    m = -1
    hist = 0
    for n, bit in enumerate(data):
        discrepancy = bit ^ (((C >> 1) & hist).bit_count() & 1)
        if discrepancy:
            previous = C
            C ^= B << (n - m)
            if 2 * L <= n:
                L = n + 1 - L
                B = previous
                m = n
        hist = (hist << 1) | bit
    return L, C, hist

def evaluate(training, withheld):
    complexity, polynomial, history = berlekamp_massey(training)
    wrong = 0
    for expected in withheld:
        predicted = (((polynomial >> 1) & history).bit_count() & 1)
        wrong += predicted != expected
        history = (history << 1) | predicted
    return complexity, wrong

for reverse_bytes in (False, True):
    for msb in (False, True):
        bits = list(bits_from_bytes(b"".join(payload for _, payload in rows), reverse_bytes, msb))
        complexity, wrong = evaluate(bits[:112 * 128], bits[112 * 128:])
        print(f"reverse_bytes={reverse_bytes} msb_first={msb} complexity={complexity} wrong={wrong}/2048")
        assert 7000 <= complexity <= 7300 and 900 <= wrong <= 1150

# Planted degree-127 recurrence: should reproduce every withheld bit.
seed = int("cabbadcabac011abbeadbadfacedcafe", 16) & ((1 << 127) - 1)
synthetic = [(seed >> i) & 1 for i in range(127)]
for _ in range(16384 - 127):
    synthetic.append(synthetic[-127] ^ synthetic[-9] ^ synthetic[-5] ^ synthetic[-1])
degree, wrong = evaluate(synthetic[:112 * 128], synthetic[112 * 128:])
assert (degree, wrong) == (127, 0)
print("planted_degree127_control=PASS")
