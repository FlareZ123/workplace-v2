"""H-17: source-predicted recorder control timestamps reverse native MT order.

This is a historical producer-causality falsifier conditional on Agent49's
unverified p951 shared MT writer. Original selected printer ACK2 is withheld.
No acceptance, K04 mask, candidate or K08 key is read.
"""
import hashlib
import importlib.util
import os
import struct
import zlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
DEP = Path(__file__).resolve().parents[1] / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("h17_source_model", DEP)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
basis, forms = mt.source(ROOT)
assert basis.rank == 15365

raw = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
assert raw[:8] == b"TRP2DUMP"
version, record_size, count = struct.unpack_from("<HHI", raw, 8)
assert (version, record_size, count) == (2, 24, 88)
assert len(raw) == 16 + record_size * count

# These four independently archived recorder controls were found as exact
# source-predictable native output words, using an independent original-source
# crossarchive search. The selected copied 18:02 payload is absent from fit.
stages = {201: -321, 203: -315, 990: -322, 992: -316}
found = {}
for index in range(count):
    packet = raw[16 + 24*index:16 + 24*(index+1)]
    utc, node, event, latch, seq, control, aux, crc = struct.unpack("<IHBBI4sII", packet)
    if node != 49 or event != 82 or seq not in stages:
        continue
    assert seq not in found
    assert zlib.crc32(packet[:20]) == crc
    stage = stages[seq]
    observed_native = mt.untemper(int.from_bytes(control, "little"))
    fixed = 0
    for bit, equation in enumerate(mt.get(forms, stage)):
        expected_bit = basis.predict(equation)
        if expected_bit is not None:
            assert expected_bit == ((observed_native >> bit) & 1)
            fixed += 1
    assert fixed == 32, (seq, fixed)
    found[seq] = (utc, stage, latch, index, control.hex().upper())

assert set(found) == set(stages)
# Two independent authentic, CRC-valid old/new event pairs at the SAME
# recorder node/event advance by eight seconds but retreat one MT state index.
for old, new in ((201, 990), (203, 992)):
    oldtime, oldstage, _, _, _ = found[old]
    newtime, newstage, _, _, _ = found[new]
    assert newtime - oldtime == 8
    assert newstage - oldstage == -1

print("ORIGINAL_RECORDER_SHA256_PASS SOURCE_SPOOL_RANK", basis.rank)
for seq in sorted(found):
    utc, stage, latch, index, control = found[seq]
    print("INDEPENDENT_SOURCE_PREDICTED_CONTROL", seq,
          datetime.fromtimestamp(utc, timezone.utc).isoformat(),
          "node49 event82 latch", latch, "native_stage", stage,
          "fixed_source_bits", 32, "CRC_PASS", control)
print("TWO_EIGHT_SECOND_FUTURE_TIME_PAIRS_BOTH_STEP_BACK_ONE_NATIVE_INDEX")
print("CONDITIONAL_SINGLE_LIVE_TIME_MONOTONE_GENERATOR_CONTRADICTED")
print("PREGENERATED_OR_REPLAYED_OUTPUTS_AND_ALTERNATIVE_PRODUCERS_NOT_EXCLUDED")
print("K04_PHYSICAL_BITS=0 K08_FINAL_WORDS=0 REC8_INCOMPLETE")
