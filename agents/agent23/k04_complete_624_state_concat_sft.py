"""K04 source-corpus 624-word state-concatenation hypothesis and backward invariant.

Read-only original evidence; synthetic MT controls; direct original commitment at the end.
"""
import hashlib
import itertools
import json
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[2] / "resources"
MASK32 = 0xFFFFFFFF


def temper(x):
    y = x ^ (x >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & MASK32


def untemper(y):
    z = y
    for _ in range(5):
        z = y ^ (z >> 18)
    y2 = z
    for _ in range(5):
        z = y2 ^ ((z << 15) & 0xEFC60000)
    y3 = z
    for _ in range(8):
        z = y3 ^ ((z << 7) & 0x9D2C5680)
    y4 = z
    for _ in range(5):
        z = y4 ^ (z >> 11)
    return z & MASK32


def inverse_twist(z):
    odd = (z >> 31) & 1
    return (((z ^ (0x9908B0DF if odd else 0)) << 1) & MASK32) | odd


def predict_next_four(out624):
    assert len(out624) == 624
    state = {i: untemper(out624[i]) for i in list(range(5)) + list(range(397, 401))}
    predictions = []
    for i in range(4):
        merged = (state[i] & 0x80000000) | (state[i + 1] & 0x7FFFFFFF)
        new = state[i + 397] ^ (merged >> 1) ^ (0x9908B0DF if merged & 1 else 0)
        predictions.append(temper(new))
    return tuple(predictions)


def predict_previous_four(out624):
    assert len(out624) == 624
    state = {
        i: untemper(out624[i])
        for i in [0] + list(range(392, 397)) + list(range(619, 624))
    }
    mixed = {t: inverse_twist(state[t + 624] ^ state[t + 397]) for t in range(-5, 0)}
    # MT19937 valid 19937-bit state has a 31-bit cross-block consistency relation.
    valid = (mixed[-1] & 0x7FFFFFFF) == (state[0] & 0x7FFFFFFF)
    previous = tuple(
        temper((mixed[t] & 0x80000000) | (mixed[t - 1] & 0x7FFFFFFF))
        for t in range(-4, 0)
    )
    return valid, previous


# Verify both temporal directions against actual independent seeded MT streams.
for seed in (0, 20261003, 314159):
    gen = Random(seed)
    original = [gen.getrandbits(32) for _ in range(628)]
    assert predict_next_four(original[:624]) == tuple(original[624:])
    assert predict_previous_four(original[4:]) == (True, tuple(original[:4]))

SPOOL = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(SPOOL).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
printer = []
for rawline in SPOOL.decode().splitlines():
    if not rawline or rawline.startswith("#"):
        continue
    if rawline.startswith("2026-10-03T18:02:00Z JOB=PS-261003-0417 "):
        continue
    fields = dict(token.split("=", 1) for token in rawline.split()[1:])
    printer.append(bytes.fromhex(fields["PAYLOAD"]))
assert len(printer) == 132
recording = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
assert recording[:8] == b"TRP2DUMP"
assert len(recording) == 16 + 88 * 24
recorder = [recording[16 + 24 * i + 12:16 + 24 * i + 16] for i in range(88)]
watch = [bytes.fromhex(x) for x in ("049AAB2E", "1CDE7A82", "CD7C6023", "4303C91A")]
procedure = [bytes.fromhex(x) for x in ("5DBF40EE", "52FAAED9", "A536D332", "6CF0D95A")]
groups = {"printer": printer, "recorder": recorder, "watch": watch, "procedure": procedure}
assert 132 * 4 + 88 + 4 + 4 == 624
routes = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(routes["K04"]["masked_component"])
target = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]["K04"]


def word_view(packets, endian, reverse, reverse_printer_words):
    output = []
    for p in (reversed(packets) if reverse else packets):
        words = [p[i:i + 4] for i in range(0, len(p), 4)]
        if reverse_printer_words:
            words.reverse()
        output.extend(int.from_bytes(w, endian) for w in words)
    return tuple(output)


views = {}
for name, packets in groups.items():
    for endian in ("little", "big"):
        for reverse in (False, True):
            for reverse_printer in ((False, True) if name == "printer" else (False,)):
                views[name, endian, reverse, reverse_printer] = word_view(
                    packets, endian, reverse, reverse_printer
                )

matches = []
total = 0
unique = set()
backward_valid = 0
for order in itertools.permutations(groups):
    options = [tuple(v for key, v in views.items() if key[0] == name) for name in order]
    for chosen in itertools.product(*options):
        state = chosen[0] + chosen[1] + chosen[2] + chosen[3]
        after = predict_next_four(state)
        valid, before = predict_previous_four(state)
        backward_valid += bool(valid)
        for output_endian in ("little", "big"):
            payload = b"".join(w.to_bytes(4, output_endian) for w in after)
            candidate = bytes(a ^ b for a, b in zip(mask, payload))
            unique.add(candidate)
            total += 1
            if hashlib.sha256(candidate).hexdigest() == target:
                matches.append(("after", order, output_endian, candidate.hex().upper()))
            if valid:
                prior_payload = b"".join(w.to_bytes(4, output_endian) for w in before)
                previous_candidate = bytes(a ^ b for a, b in zip(mask, prior_payload))
                if hashlib.sha256(previous_candidate).hexdigest() == target:
                    matches.append(("before", order, output_endian, previous_candidate.hex().upper()))
assert total == 24576
print(json.dumps({
    "synthetic_bidirectional_controls": 3,
    "hypothetical_state_layouts": total // 2,
    "forward_candidate_assignments": total,
    "distinct_forward_components": len(unique),
    "backward_31bit_valid_layouts": backward_valid,
    "authentic_K04_commitment_matches": matches,
}, indent=2))
