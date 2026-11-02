"""SFT: source-only conditional p951 TRP2 event/latch PRNG selector witnesses.

Runs alongside sibling 20261102_k04_multicarrier_p951_sft.py.
Selected K04 ACK row129, route XOR mask and commitments are never read.
Usage: python agents/agent2/20261102_k04_recorder_selector_sft.py resources
"""
import hashlib
import runpy
import struct
import sys
import zlib
from pathlib import Path

sibling = Path(__file__).with_name("20261102_k04_multicarrier_p951_sft.py")
model = runpy.run_path(str(sibling))
root = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/"resources"
word, mask, offset = model["source_closure"](root)
temper = model["temper"]
untemper = model["untemper"]
M = model["MASK"]
raw = (root/"evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest() == model["REC_SHA"]

# Original recorder index, source-inferred source index, source-only prediction
# of the corresponding event and latch selector outputs when both are known.
for record_index, control_at, predicted, rejected_latch in (
    (3,-683,True,False),
    (39,-540,True,False),
    (26,-339,False,True),
):
    start = 16 + record_index * 24
    ts,node,event,latch,seq,control,aux,crc = struct.unpack_from(
        "<IHBBI4sII",raw,start)
    assert node == 50 and zlib.crc32(raw[start:start+20]) == crc
    control_state = untemper(int.from_bytes(control,"little"))
    assert ((word[offset+control_at]^control_state)&mask[offset+control_at]) == 0
    print("REC",record_index,"seq",seq,"event",event,"latch",latch,
          "hidden control position",control_at)
    a,b = control_at-2,control_at-1
    assert mask[offset+a] == M and mask[offset+b] == M
    first = temper(word[offset+a])
    second = temper(word[offset+b])
    if predicted:
        # Source-derived 6-bit accepted index maps 0..38 -> event 1..39.
        # Source-derived 3-bit accepted index maps 0..3 -> latch 0..3.
        assert (first >> 26) + 1 == event
        assert (second >> 29) == latch
        print("PASS event-from-top6",first>>26,"+1 =",event,
              "latch-from-top3",second>>29,"=",latch)
    if rejected_latch:
        # The penultimate source output cannot be a selected latch: its
        # three high bits are 7, an invalid return for _randbelow(4).
        assert first >> 29 == 7
        assert second >> 29 == latch
        print("PASS rejected three-bit latch index",first>>29,
              "followed by accepted index",second>>29)
print("All independently retained metadata checks PASS.")
print("Model hypothesis: getrandbits(6) event selection and getrandbits(3) latch selection;")
print("rejection loops remain conditional. K04 p951 target masks stay empty.")
