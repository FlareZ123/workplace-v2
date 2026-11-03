"""H17 original-source V8 state0 byte emitter / 64-cache geometry falsifier.

Old V8 implementation: https://chromium.googlesource.com/v8/v8/+/4ff869ed3cab620e6cebb4af853ae0376f01e49f/src/math-random.cc
Current implementation differs: https://github.com/v8/v8/blob/main/src/numbers/math-random.cc
Model is hypothetical, and source-only; selected 18:02 attempt-2 payload is withheld.
"""
from pathlib import Path
import hashlib
import re

SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)

packets = []
for line in SOURCE.read_text().splitlines():
    found = re.search(
        r"JOB=PS-261003-(\d+).*?ATTEMPT=(\d+) STATE=(\w+) "
        r"CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)",
        line,
    )
    if found is None:
        continue
    job, attempt, state, kind, payload, destination = found.groups()
    if (job, attempt, state, kind) == ("0417", "2", "ACK", "RECOVER"):
        continue
    packets.append(bytes.fromhex(payload))
assert len(packets) == 132

# Each state bit is an exactly tracked GF(2) linear form in 128 unknown bits.
s0 = [1 << bit for bit in range(64)]
s1 = [1 << (bit + 64) for bit in range(64)]
state_outputs = []
for _ in range(512):
    t = s0.copy()
    t = [v ^ (t[i - 23] if i >= 23 else 0) for i, v in enumerate(t)]
    t = [v ^ (t[i + 17] if i + 17 < 64 else 0) for i, v in enumerate(t)]
    t = [v ^ s1[i] ^ (s1[i + 26] if i + 26 < 64 else 0)
         for i, v in enumerate(t)]
    s0, s1 = s1, t
    state_outputs.append(s0)


def compatible(values, width, phase, gap, byteorder, order):
    """Eliminate all 128 initial state bits from the observed source bits."""
    draws = 128 // width
    basis = {}
    for packet_index, payload in enumerate(values):
        for local in range(draws):
            b = payload[local * (width // 8):(local + 1) * (width // 8)]
            observed = int.from_bytes(b, byteorder)
            logical = packet_index * (draws + gap) + local + phase
            physical = (64 * (logical // 64) + 63 - logical % 64
                        if order == "reverse" else logical)
            for bit, coeff in enumerate(state_outputs[physical][64 - width:]):
                augmented = (coeff << 1) | ((observed >> bit) & 1)
                while augmented >> 1:
                    leading = (augmented >> 1).bit_length()
                    if leading not in basis:
                        basis[leading] = augmented
                        break
                    augmented ^= basis[leading]
                else:
                    if augmented & 1:
                        return False
    return True


def xorshift_step(a, b):
    """V8 xorshift128 update; older state0 result, before output conversion."""
    mask = (1 << 64) - 1
    t = a ^ ((a << 23) & mask)
    t ^= t >> 17
    t ^= b ^ (b >> 26)
    return b, t & mask


def seeded_fixture(width, phase, gap, byteorder, order):
    a, b = 0x1234567890ABCDEF, 0x9876543210012345
    outputs = []
    for _ in range(512):
        a, b = xorshift_step(a, b)
        outputs.append(a)
    draws = 128 // width
    items = []
    for row in range(3):
        packet = bytearray()
        for local in range(draws):
            logical = row * (draws + gap) + local + phase
            physical = (64 * (logical // 64) + 63 - logical % 64
                        if order == "reverse" else logical)
            raw = outputs[physical] >> (64 - width)
            packet.extend(raw.to_bytes(width // 8, byteorder))
        items.append(bytes(packet))
    return items


if __name__ == "__main__":
    models = 0
    positives = 0
    for order in ("reverse", "forward"):
        for width in (8, 16, 32):
            endian_options = ("big",) if width == 8 else ("big", "little")
            seeded = seeded_fixture(width, 29, 2, endian_options[-1], order)
            assert compatible(seeded, width, 29, 2, endian_options[-1], order)
            positives += 1
            matches = 0
            for endian in endian_options:
                for phase in range(64):
                    for gap in range(4):
                        models += 1
                        if compatible(packets[:2], width, phase, gap, endian, order):
                            matches += 1
            print(f"original order={order} bits={width}: source-consistent={matches}")
            assert matches == 0
    assert models == 2560 and positives == 6
    print(f"PASS: {positives} planted controls; {models} original 2-packet model candidates, zero compatible")
