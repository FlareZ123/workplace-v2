"""Source-only heldout seq44 EVENT/LATCH test under pinned p951 states.

The state values and masks are derived by the separate reproducible Agent2
printer closure at agents/agent2/20261102_k04_multicarrier_p951_sft.py.
This check uses the original, CRC-valid independent recorder fields.
"""
from pathlib import Path
import hashlib
import struct
import sys
import zlib

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "resources"
raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
record = struct.unpack_from("<IHBBI4sII", raw, 16 + 24 * 38)
ts, node, event, latch, seq, control, aux, crc = record
assert zlib.crc32(raw[16 + 24 * 38:16 + 24 * 38 + 20]) == crc
assert (node, event, latch, seq) == (50, 28, 2, 44)

def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9d2c5680
    value ^= (value << 15) & 0xefc60000
    return (value ^ (value >> 18)) & 0xffffffff

# Printer-only closure, without disputed ACK2: exact p951 source states.
state_event = 0x53D0FF55       # index -548, all 32 bits fixed
state_latch_low31 = 0x07D52D87 # index -547, low 31 bits fixed
event_code = temper(state_event) >> 26
latch_codes = [temper(state_latch_low31 | bit) >> 29
               for bit in (0, 0x80000000)]
assert event_code == 39
assert latch_codes == [3, 7]
assert event_code != event - 1
assert latch not in latch_codes
print("seq44 strict accepted-event/latch precontrol stage: FALSIFIED")
print("EVENT code:", event_code, "recorded:", event)
print("LATCH code options:", latch_codes, "recorded:", latch)
print("Conditional model only; no K04 key bits or REC8 pass")
