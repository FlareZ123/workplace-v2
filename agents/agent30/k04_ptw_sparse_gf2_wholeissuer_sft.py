#!/usr/bin/env python3
"""Source-only PTW serial -> printer packet sparse-GF2 whole-output falsifier.

The 27 signed PTW-390..416 seal serials have exact job-number-matched
PS-261003-0390..0416 historical ACK coupons. The model requires each of
128 output bits to be parity of at most 3 serial bits, optionally complemented.
Fit first 20 whole pairs, blind-test the last 7. K04 selected job 417 and its
disputed 18:02 copied payload are excluded entirely.
"""
import hashlib
import itertools
import json
import re
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[2] / "resources" / "evidence"
SEALS = EVIDENCE / "maintenance" / "seal-receipts.jsonl"
SPOOL = EVIDENCE / "print" / "spool-reconstruction.log"
assert hashlib.sha256(SEALS.read_bytes()).hexdigest() == "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
assert hashlib.sha256(SPOOL.read_bytes()).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

receipts = [json.loads(s) for s in SEALS.read_text().splitlines() if s.strip()]
printer_lines = SPOOL.read_text().splitlines()
serials, coupons = [], []
for n in range(390, 417):
    selected = [
        r for r in receipts
        if r["permit"] == f"PTW-{n}"
        and r["signed"] and r["state"] == "CLOSED"
        and r["fitment"] == "AS_LEFT"
    ]
    packet = [
        s for s in printer_lines
        if f"JOB=PS-261003-{n:04d} " in s and "STATE=ACK " in s
    ]
    assert len(selected) == len(packet) == 1, n
    serial = selected[0]["serial"]
    match = re.search(r" PAYLOAD=([0-9A-F]{32}) ", packet[0])
    assert match and serial.startswith("SG-") and len(serial) == 11
    serials.append(int(serial[3:], 16))
    coupons.append(int(match.group(1), 16))
assert len(serials) == len(coupons) == 27

masks = [0] + [
    sum(1 << bit for bit in indices)
    for size in (1, 2, 3)
    for indices in itertools.combinations(range(32), size)
]
assert len(masks) == 5489

def fit(inputs, outputs):
    train = 20
    signatures = {}
    for mask in masks:
        sig = sum((((x & mask).bit_count() & 1) << i)
                  for i, x in enumerate(inputs[:train]))
        signatures.setdefault(sig, (mask, 0))
        signatures.setdefault(sig ^ ((1 << train) - 1), (mask, 1))
    fitted = {}
    for bit in range(128):
        sig = sum((((value >> bit) & 1) << i)
                  for i, value in enumerate(outputs[:train]))
        if sig in signatures:
            fitted[bit] = signatures[sig]
    correct = sum(
        (((inputs[i] & mask).bit_count() & 1) ^ flip)
        == ((outputs[i] >> bit) & 1)
        for bit, (mask, flip) in fitted.items()
        for i in range(train, len(inputs))
    )
    return len(fitted), correct, len(fitted) == 128 and correct == 128 * 7

bits, right, complete = fit(serials, coupons)
print(f"ORIGINAL: 27 same-ID pairs, 20 train, 7 withheld; "
      f"{len(masks)} support masks; {bits}/128 fitted output bits; "
      f"holdout {right}/{bits * 7} correct; whole-output={complete}")
assert (bits, right, complete) == (2, 6, False)

# Independent genuine planted issuer: each output bit is truly generated
# from a fixed supported serial-bit mask; holdout payload bytes are unseen.
plant = [(masks[(bit * 43 + 1) % len(masks)], bit % 2)
         for bit in range(128)]
synthetic = [
    sum(((((x & mask).bit_count() & 1) ^ flip) << bit)
        for bit, (mask, flip) in enumerate(plant))
    for x in serials
]
pbits, pright, pcomplete = fit(serials, synthetic)
assert (pbits, pright, pcomplete) == (128, 896, True)
print("PLANTED: full 128-bit issuer, 7/7 completely withheld packets PASS")
print("SFT PASS: original sparse issuer falsified; no K04 selected bytes inferred")
