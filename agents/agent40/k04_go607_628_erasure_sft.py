"""Go legacy math/rand 607/273 lagged-fibonacci source/selected-erasure test.

Optional argument: resources directory (otherwise repository resources/).
Read-only SFT; original source pins, 3 planted quotient controls,
and original complete coupon SHA256 reducer.
"""
from pathlib import Path
import hashlib
import itertools
import json
import random
import re
import struct
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
spool = (root / "evidence/print/spool-reconstruction.log").read_bytes()
rec = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
assert hashlib.sha256(rec).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
route = json.loads((root / "evidence/recovery-routing.json").read_text())
acceptance = json.loads((root / "acceptance.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
target = acceptance["slot_sha256"]["K04"]
packets = []
selected = None
for line in spool.decode().splitlines():
    match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
    if match is None:
        continue
    if all(item in line for item in ("JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK")):
        assert selected is None
        selected = len(packets)
    packets.append(bytes.fromhex(match.group(1)))
assert selected == 129 and len(packets) == 133
recorders = [rec[16 + i * 24 + 12:16 + i * 24 + 16] for i in range(88)]
trusted = bytes.fromhex(
    "049AAB2E1CDE7A82CD7C60234303C91A"
    "5DBF40EE52FAAED9A536D3326CF0D95A"
)
assert len(rec) >= 16 + 88 * 24 and len(trusted) == 32
MASK32 = (1 << 32) - 1


def source_test(words, missing):
    """Projected Go Uint32 recurrence: q[n]-q[n-607]-q[n-273] in {0,1}."""
    fixed = 0
    missing_candidates = []
    for n in range(607, len(words)):
        prediction = (words[n - 607] + words[n - 273]) & MASK32
        if n in missing:
            missing_candidates.append((prediction, (prediction + 1) & MASK32))
        else:
            if (words[n] - prediction) & MASK32 not in (0, 1):
                return False, fixed, missing_candidates
            fixed += 1
    return True, fixed, missing_candidates


# Real recurrence controls for each relevant bit-window: low32, Uint32, high32.
rng = random.Random(314159)
raw = [rng.getrandbits(64) for _ in range(607)]
for i in range(607, 628):
    raw.append((raw[i - 607] + raw[i - 273]) & ((1 << 64) - 1))
for shift in (0, 31, 32):
    observed = [(value >> shift) & MASK32 for value in raw]
    full_selected = observed[612:616]
    unknown = observed.copy()
    for index in range(612, 616):
        unknown[index] = None
    ok, fixed, values = source_test(unknown, set(range(612, 616)))
    assert ok and fixed == 17 and len(values) == 4
    assert all(value in options for value, options in zip(full_selected, values))

checked = 0
fitted = 0
tested_coupons = 0
found = []
for printer_endian, recorder_endian, trusted_endian in itertools.product(("<", ">"), repeat=3):
    for reverse_printer, reverse_recorder, reverse_trusted in itertools.product((False, True), repeat=3):
        p = []
        for index, packet in enumerate(packets):
            if index == selected:
                p.extend([None] * 4)
            else:
                words = list(struct.unpack(printer_endian + "4I", packet))
                p.extend(words[::-1] if reverse_printer else words)
        r = [struct.unpack(recorder_endian + "I", packet)[0]
             for packet in (recorders[::-1] if reverse_recorder else recorders)]
        a = list(struct.unpack(trusted_endian + "8I", trusted))
        if reverse_trusted:
            a.reverse()
        for order in itertools.permutations("pra"):
            groups = {"p": p, "r": r, "a": a}
            words = [word for group in order for word in groups[group]]
            assert len(words) == 628
            erased = {i for i, word in enumerate(words) if word is None}
            if min(erased) < 607:
                continue
            checked += 1
            ok, _, domain = source_test(words, erased)
            if not ok:
                continue
            fitted += 1
            assert len(domain) == 4
            for bits in itertools.product((0, 1), repeat=4):
                selected_words = [options[bit] for options, bit in zip(domain, bits)]
                if reverse_printer:
                    selected_words.reverse()
                coupon = struct.pack(printer_endian + "4I", *selected_words)
                component = bytes(x ^ y for x, y in zip(coupon, mask))
                tested_coupons += 1
                if hashlib.sha256(component).hexdigest() == target:
                    found.append((order, bits, coupon.hex().upper(), component.hex().upper()))
print(json.dumps({
    "conditional_layouts_with_selected_erasure_in_predictive_suffix": checked,
    "source_compatible_layouts": fitted,
    "whole_coupon_candidates": tested_coupons,
    "original_acceptance_hits": found,
    "planted_recurrence_controls": 3,
}, indent=2))
