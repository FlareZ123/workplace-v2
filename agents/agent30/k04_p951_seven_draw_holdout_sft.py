"""K04 p951: source-only heldout node50 constant-seven-draw falsifier.

Under the conditional p951 printer chronology, node50 sequence 41 and 45
match independent reconstructed MT outputs at -568 and -540. The inferred
seven-output stride yields -547 at sequence 44. Inspect that previously
unused original control as a heldout test. No selected ACK or acceptance read.

Reuses Agent2's current source-only printer closure without copying its
source timetable; does not modify original files.
"""
from hashlib import sha256
import importlib.util
from pathlib import Path
import struct
import zlib

repo = Path(__file__).resolve().parents[2]
root = repo / "resources"
source = repo / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
spec = importlib.util.spec_from_file_location("source_p951_agent2", source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
value, known, offset = mod.source_closure(root)

record_bytes = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
assert sha256(record_bytes).hexdigest() == mod.REC_SHA
node50 = {}
for i in range(88):
    start = 16 + 24 * i
    ts, node, event, latch, seq, control, aux, crc = struct.unpack_from(
        "<IHBBI4sII", record_bytes, start
    )
    if node == 50:
        assert zlib.crc32(record_bytes[start:start + 20]) == crc
        node50[seq] = (i, mod.untemper(int.from_bytes(control, "little")), control)

# Frozen source-matched anchors. Sequence 44 is NOT involved in choosing
# either the source chronology or the proposed seven-draw slope.
for seq, index in ((41, -568), (45, -540)):
    _, state, raw = node50[seq]
    mask = known[offset + index]
    assert mask.bit_count() >= 31
    assert ((value[offset + index] ^ state) & mask) == 0
    print(f"ANCHOR seq={seq} at={index} known={mask.bit_count()} raw={raw.hex().upper()}")

assert (-540 - (-568)) == 7 * (45 - 41)
proposed_index = -568 + 7 * (44 - 41)
assert proposed_index == -547
row, actual, raw = node50[44]
mask = known[offset + proposed_index]
predicted = value[offset + proposed_index] & mask
disagree = (value[offset + proposed_index] ^ actual) & mask
print(f"HELDOUT seq=44 record={row} inferred_index={proposed_index} "
      f"original_control={raw.hex().upper()} known_mask={mask:08X} "
      f"predicted_masked={predicted:08X} disagreements={disagree:08X} "
      f"mismatch_count={disagree.bit_count()}")
assert mask == 0x7FFFFFFF
assert predicted == 0x07D52D87
assert raw.hex().upper() == "D317A5F4"
assert disagree == 0x7206E905 and disagree.bit_count() == 13

# A superficially similar 7->12 interval supplies no independent middle
# evidence: all four proposed intervening control states have known mask 0.
for seq in range(8, 12):
    index = -810 + 7 * (seq - 7)
    assert known[offset + index] == 0

assert all(known[offset + mod.STARTS[129] + j] == 0 for j in range(4))
print("CONDITIONAL_FIXED_SEVEN_DRAW_SEQ41_TO45_FALSIFIED; "
      "EARLY_SEQ7_TO12_HOLDOUT_UNTESTABLE; SELECTED_K04_MASKS_ZERO")
