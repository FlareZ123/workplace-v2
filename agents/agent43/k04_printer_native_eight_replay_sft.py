"""Whole K04 coupon from two intact printer packets as native MT replay donors.

Hypothetical p951 source law: stages 328..331 and 724..727 are the
target-causal native MT donor quartets. Each quartet is assigned from
one original, independently intact printer packet under a fixed 32-bit
word view. Selected row129 is excluded from donor acquisition.
Requires only the Python standard library. Run from repository checkout:
python agents/agent43/k04_printer_native_eight_replay_sft.py
"""
from pathlib import Path
import hashlib
import itertools
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

basis, symbolic = mt.source(ROOT / "resources")
assert basis.rank == 15365
donor_stages = (328, 329, 330, 331, 724, 725, 726, 727)
for i, stage in enumerate(donor_stages):
    for bit, equation in enumerate(mt.get(symbolic, stage)):
        basis.insert(equation, 1 << (1 + 32 * i + bit))
assert basis.rank == 15621

# Build a 128bit affine output map: every selected tempered bit is
# a parity of the 256 formal donor bits plus an observed source constant.
projected = []
for stage in range(951, 955):
    native_bit_formulas = [basis.predict(x) for x in mt.get(symbolic, stage)]
    assert all(x is not None for x in native_bit_formulas)
    projected.extend(mt.temper(native_bit_formulas))
assert len(projected) == 128
base = sum((expr & 1) << j for j, expr in enumerate(projected))
columns = [
    sum(((projected[j] >> (i + 1)) & 1) << j for j in range(128))
    for i in range(256)
]

spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(spool).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
packets = [bytes.fromhex(x.decode()) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
assert len(packets) == 133
# Independently intact packets only: exclude disputed ACK2 at source row129.
controls = [(i, x) for i, x in enumerate(packets) if i != 129]


def contribution(words, quartet):
    """The complete selected coupon's linear dependence on one quartet."""
    total = 0
    for i, word in enumerate(words):
        for bit in range(32):
            if (word >> bit) & 1:
                total ^= columns[(quartet * 4 + i) * 32 + bit]
    return total


options = [[], []]
for row, packet in controls:
    for endian, reverse, untemper in itertools.product(
        ("little", "big"), (False, True), (False, True)
    ):
        words = [int.from_bytes(packet[k:k + 4], endian) for k in range(0, 16, 4)]
        if reverse:
            words.reverse()
        if untemper:
            words = [mt.untemper(value) for value in words]
        for quartet in range(2):
            options[quartet].append((row, contribution(words, quartet)))
assert len(options[0]) == len(options[1]) == 1056

mask = int.from_bytes(bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C"), "little")
original_digest = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
count = 0
original_matches = []
synthetic_digest = None
synthetic_hits = 0
for first_row, first in options[0]:
    left = first ^ base ^ mask
    for second_row, second in options[1]:
        if first_row == second_row:
            continue
        coupon_component = (left ^ second).to_bytes(16, "little")
        digest = hashlib.sha256(coupon_component).digest()
        if synthetic_digest is None:
            synthetic_digest = digest
        synthetic_hits += digest == synthetic_digest
        if digest == original_digest:
            original_matches.append((first_row, second_row, coupon_component.hex()))
        count += 1

assert count == 132 * 131 * 64 == 1106688
assert synthetic_hits == 1
assert not original_matches
print(f"printer original source rank=15365, native donor rank=256")
print(f"distinct ordered-pair whole-coupon original checks={count}")
print(f"original K04 matches={len(original_matches)}, planted full commitment hits={synthetic_hits}")
print("NO_MATCH: original K04 unrecovered under hypothetical two-printer-quartet replay.")
