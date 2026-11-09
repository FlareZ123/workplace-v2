"""Check a historically plausible Delphi RTL RandSeed LCG against intact spool packets.

Run from repository root: python agents/agent18/k04_delphi_legacy_randseed_sft.py
Requires numpy. Reads original evidence, writes nothing.

Delphi Random(range) uses RandSeed <- 0x08088405 * RandSeed + 1 modulo 2^32;
Random(256) gives the top eight bits, Random(65536) the top sixteen bits.
Source: https://docwiki.embarcadero.com/Libraries/Athens/en/System.Random
Detailed historical recurrence: https://groups.google.com/g/borland.public.delphi.language.delphi.general/c/TedBrYcVMYQ
This is a conditional exploratory model, not an authenticated printer issuer.
"""
from pathlib import Path
import hashlib
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPOOL = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
raw = SPOOL.read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
rows = [bytes.fromhex(s.decode("ascii")) for s in
        re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
assert len(rows) == 133
assert rows[129].hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
MULTIPLIER = np.uint32(0x08088405)
ONE = np.uint32(1)


def whole_packet_state_count(packet: bytes, unit_bytes: int) -> int:
    """All complete 32-bit states at first output, with each later output exact."""
    shift = 32 - 8 * unit_bytes
    first = int.from_bytes(packet[:unit_bytes], "big")
    states = (np.arange(1 << shift, dtype=np.uint32)
              | np.uint32(first << shift))
    for start in range(unit_bytes, len(packet), unit_bytes):
        states = states * MULTIPLIER + ONE
        expected = int.from_bytes(packet[start:start + unit_bytes], "big")
        states = states[(states >> shift) == expected]
        if not len(states):
            break
    return int(len(states))


def orientations(packet: bytes):
    yield "native", packet
    yield "reverse-each-4", b"".join(packet[i:i + 4][::-1]
                                     for i in range(0, 16, 4))
    yield "reverse-four-blocks", b"".join(
        [packet[i:i + 4] for i in range(0, 16, 4)][::-1])
    yield "reverse-entire-packet", packet[::-1]


for unit in (1, 2):
    seed = 0x12345678
    packet = bytearray()
    for _ in range(16 // unit):
        seed = (seed * 0x08088405 + 1) & 0xFFFFFFFF
        packet.extend((seed >> (32 - unit * 8)).to_bytes(unit, "big"))
    assert whole_packet_state_count(bytes(packet), unit) >= 1
    if unit == 1:
        # Include ordinary early jobs and all late nonselected roles.
        indices = [0, 1, 3, 6, 8, 12, 129, 130, 131, 132]
    else:
        # Smaller inverse (2^16 states): all genuine nonselected packets.
        indices = list(range(133))
    positive = []
    tested = 0
    for i in indices:
        if i == 129:
            continue
        for name, transformed in orientations(rows[i]):
            tested += 1
            count = whole_packet_state_count(transformed, unit)
            if count:
                positive.append((i, name, count))
    print(f"Delphi Random({1 << (8 * unit)}) packet: "
          f"planted PASS, genuine complete checks={tested}, "
          f"genuine exact matches={positive}")
    assert not positive
