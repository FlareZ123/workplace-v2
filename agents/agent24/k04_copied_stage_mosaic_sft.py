"""H-17 K04: copied ACK2 as a displaced printer packet, 384 serializers.

Read-only original-source SFT. The suspicious selected copied packet enters
only the tested relocation hypothesis; it is excluded from the original MT
state inference. Neither K04 hash, mask, candidate nor verifier is read.
"""
from collections import Counter
from itertools import permutations
from pathlib import Path
import hashlib
import importlib.util
import os
import re

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
DEPENDENCY = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("h17_native_source", DEPENDENCY)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
basis, words = mt.source(ROOT)
assert basis.rank == 15365

raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
lines = [line for line in raw.decode().splitlines() if "PAYLOAD=" in line]
assert len(lines) == 133
assert "JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
packets = [bytes.fromhex(re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1)) for line in lines]

def reduce_source(v):
    known = 0
    remainder = 0
    while v:
        pivot = v.bit_length() - 1
        if pivot in basis.rows:
            w, bit = basis.rows[pivot]
            v ^= w
            known ^= bit
        else:
            remainder |= 1 << pivot
            v ^= 1 << pivot
    return remainder, known

reduced = [
    tuple(reduce_source(v) for v in mt.get(words, pos))
    for pos in range(mt.ORIGIN, mt.LAST + 1)
]

def source_parity_checks(stage):
    """Eliminate all 128 source-relative quartet bits and keep exact syndromes."""
    free = {}
    checks = []
    for lane in range(4):
        for bit, (residual, known) in enumerate(reduced[stage + lane - mt.ORIGIN]):
            trace = 1 << (lane * 32 + bit)
            while residual:
                pivot = residual.bit_length() - 1
                if pivot not in free:
                    free[pivot] = (residual, known, trace)
                    break
                word, rhs, mask = free[pivot]
                residual ^= word
                known ^= rhs
                trace ^= mask
            if not residual:
                checks.append((trace, known))
    assert len(free) + len(checks) == 128
    return checks

stages = [
    (stage, source_parity_checks(stage))
    for stage in range(mt.ORIGIN, mt.LAST - 2)
]
assert len(stages) == 2138
histogram = Counter(len(checks) for stage, checks in stages)
assert tuple(histogram[n] for n in (128, 127, 126, 125, 124)) == (284, 118, 43, 9, 4)
assert len(next(checks for stage, checks in stages if stage == 951)) == 0

def untemper_packet(packet):
    value = 0
    for lane in range(4):
        x = int.from_bytes(packet[4*lane:4*(lane+1)], "little")
        value |= mt.untemper(x) << (32*lane)
    return value

def compatible(value, checks):
    return all(((value & mask).bit_count() & 1) == rhs for mask, rhs in checks)

# Real source-blind holdout: additionally exclude entire intact row83 from
# the original source system. The OTHER 131 intact rows must predict 95 bits
# (including two complete native words) of row83 without inspecting its value.
holdout_row = 83
holdout_basis = mt.Basis()
for row, packet in enumerate(packets):
    if row in (129, holdout_row):
        continue
    for lane in range(4):
        value = mt.untemper(int.from_bytes(packet[4*lane:4*(lane+1)], "little"))
        for bit, equation in enumerate(mt.get(words, mt.STARTS[row] + lane)):
            holdout_basis.insert(equation, (value >> bit) & 1)
assert holdout_basis.rank == 15332
fixed_by_lane = []
for lane in range(4):
    value = mt.untemper(int.from_bytes(packets[holdout_row][4*lane:4*(lane+1)], "little"))
    fixed = 0
    for bit, equation in enumerate(mt.get(words, mt.STARTS[holdout_row] + lane)):
        inferred = holdout_basis.predict(equation)
        if inferred is not None:
            assert inferred == ((value >> bit) & 1)
            fixed += 1
    fixed_by_lane.append(fixed)
assert fixed_by_lane == [32, 0, 31, 32]

# A complete untouched, known original packet must fit its true source stage.
control = next(checks for stage, checks in stages if stage == mt.STARTS[3])
assert len(control) == 128 and compatible(untemper_packet(packets[3]), control)
mutated = bytearray(packets[3])
mutated[0] ^= 1
assert not compatible(untemper_packet(mutated), control)

copied = [packets[129][4*lane:4*(lane+1)] for lane in range(4)]
pass_counts = Counter()
views = 0
for order in permutations(range(4)):
    for endian_mask in range(16):
        serialized = b"".join(
            copied[src][::-1] if (endian_mask >> lane) & 1 else copied[src]
            for lane, src in enumerate(order)
        )
        copied_native = untemper_packet(serialized)
        views += 1
        for stage, checks in stages:
            if compatible(copied_native, checks):
                pass_counts[len(checks)] += 1

assert views == 384
assert sum(pass_counts.values()) == 52176
assert dict(sorted(pass_counts.items())) == {0: 42624, 1: 5184, 2: 3432, 3: 704, 4: 200, 5: 32}
null_expected = 384 * sum(2.0 ** (-len(checks)) for stage, checks in stages)
print("ORIGINAL_SHA256_PASS SOURCE_RANK", basis.rank)
print("BLINDED_SOURCE_STAGE_WINDOWS", len(stages))
print("SOURCE_STAGES_FREE_0_TO_4", [histogram[128-free] for free in range(5)])
print("COPIED_ACK_REPLAY_VIEWS", views, "ASSIGNMENTS", views * len(stages))
print("SOURCE_COMPATIBLE_BY_INDEPENDENT_PARITY_BITS", dict(sorted(pass_counts.items())))
print("EXPECTED_SOURCE_COMPATIBLE_UNIFORM_COPY", null_expected)
print("MAX_INDEPENDENT_SOURCE_BITS_PER_SURVIVING_REPLAY", max(pass_counts))
print("INDEPENDENT_ROW83_SOURCE_HOLDOUT_PREDICTED_BITS", fixed_by_lane, "PASS")\nprint("GENUINE_INTACT_PACKET_TRUE_AND_SINGLEBIT_FALSE_CONTROLS_PASS")
print("SELECTED_STAGE_951_HAS_128_UNOBSERVED_BITS")
print("NO_ORIGINAL_K04_MEDIA_BITS_OR_K08_AUTHOR_FINAL_WORDS_RECOVERED")
