"""Read-only K04 source gate: invert MurmurHash3_x64_128 and x86_128 metadata writers.

Run from repository root with Python 3:
    python agents/agent22/k04_murmur128_inverse_source_sft.py
An alternative extraction root can be supplied as H17_SOURCE_ROOT.
"""
from __future__ import annotations

import hashlib
import itertools
import os
import re
import struct
from pathlib import Path

ROOT = Path(os.environ.get("H17_SOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
C64 = (0x87C37B91114253D5, 0x4CF5AD432745937F)
C32 = (0x239B961B, 0xAB0E9789, 0x38B34AE5, 0xA1E38B93)
ADD32 = (0x561CCD1B, 0x0BCAA747, 0x96CD1C35, 0x32AC3B17)
ROT32 = (19, 17, 15, 13)
TAILROT32 = (15, 16, 17, 18)


def rol(x: int, n: int, bits: int) -> int:
    return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)


def ror(x: int, n: int, bits: int) -> int:
    return ((x >> n) | (x << (bits - n))) & ((1 << bits) - 1)


def undo_shift_xor(x: int, shift: int, bits: int) -> int:
    while shift < bits:
        x ^= x >> shift
        shift *= 2
    return x


def fmix(x: int, bits: int) -> int:
    if bits == 64:
        a, b, shift1, shift2 = 0xFF51AFD7ED558CCD, 0xC4CEB9FE1A85EC53, 33, 33
    else:
        a, b, shift1, shift2 = 0x85EBCA6B, 0xC2B2AE35, 16, 13
    mask = (1 << bits) - 1
    x ^= x >> shift1
    x = x * a & mask
    x ^= x >> shift2
    x = x * b & mask
    x ^= x >> shift1
    return x


def undo_fmix(x: int, bits: int) -> int:
    if bits == 64:
        a, b, shift1, shift2 = 0xFF51AFD7ED558CCD, 0xC4CEB9FE1A85EC53, 33, 33
    else:
        a, b, shift1, shift2 = 0x85EBCA6B, 0xC2B2AE35, 16, 13
    mod = 1 << bits
    x = undo_shift_xor(x, shift1, bits)
    x = x * pow(b, -1, mod) % mod
    x = undo_shift_xor(x, shift2, bits)
    x = x * pow(a, -1, mod) % mod
    return undo_shift_xor(x, shift1, bits)


def mixes64(part: bytes) -> tuple[int, int]:
    k1 = int.from_bytes(part[:8], "little")
    k2 = int.from_bytes(part[8:], "little")
    mask = (1 << 64) - 1
    m1 = rol(k1 * C64[0] & mask, 31, 64) * C64[1] & mask if len(part) > 0 else 0
    m2 = rol(k2 * C64[1] & mask, 33, 64) * C64[0] & mask if len(part) > 8 else 0
    return m1, m2


def mixes32(part: bytes) -> list[int]:
    mask = (1 << 32) - 1
    out = []
    for i in range(4):
        start = i * 4
        if start >= len(part):
            out.append(0)
        else:
            word = int.from_bytes(part[start:start + 4], "little")
            out.append(rol(word * C32[i] & mask, TAILROT32[i], 32) * C32[(i + 1) % 4] & mask)
    return out


def invert64(message: bytes, output: bytes) -> tuple[int, int]:
    mask = (1 << 64) - 1
    inv5 = pow(5, -1, 1 << 64)
    a, b = struct.unpack("<QQ", output)
    b = (b - a) & mask
    a = (a - b) & mask
    a, b = undo_fmix(a, 64), undo_fmix(b, 64)
    b = (b - a) & mask
    a = (a - b) & mask
    a ^= len(message)
    b ^= len(message)
    count = len(message) // 16
    tail = message[count * 16:]
    if tail:
        x, y = mixes64(tail)
        a ^= x
        b ^= y
    for i in range(count - 1, -1, -1):
        x, y = mixes64(message[16 * i:16 * (i + 1)])
        old_b = ror((((b - 0x38495AB5) & mask) * inv5 - a) & mask, 31, 64) ^ y
        old_a = ror((((a - 0x52DCE729) & mask) * inv5 - old_b) & mask, 27, 64) ^ x
        a, b = old_a, old_b
    return a, b


def invert32(message: bytes, output: bytes) -> tuple[int, int, int, int]:
    mask = (1 << 32) - 1
    inv5 = pow(5, -1, 1 << 32)
    h = list(struct.unpack("<IIII", output))
    for i in range(1, 4):
        h[i] = (h[i] - h[0]) & mask
    h[0] = (h[0] - h[1] - h[2] - h[3]) & mask
    h = [undo_fmix(x, 32) for x in h]
    for i in range(1, 4):
        h[i] = (h[i] - h[0]) & mask
    h[0] = (h[0] - h[1] - h[2] - h[3]) & mask
    h = [x ^ len(message) for x in h]
    count = len(message) // 16
    tail = message[count * 16:]
    if tail:
        mixed = mixes32(tail)
        h = [h[i] ^ mixed[i] for i in range(4)]
    for k in range(count - 1, -1, -1):
        mixed = mixes32(message[k * 16:(k + 1) * 16])
        for i in range(3, -1, -1):
            h[i] = ror(((((h[i] - ADD32[i]) & mask) * inv5) - h[(i + 1) % 4]) & mask, ROT32[i], 32) ^ mixed[i]
    return tuple(h)


def hash64(message: bytes, seed: int) -> bytes:
    mask = (1 << 64) - 1
    h1 = h2 = seed
    blocks = len(message) // 16
    for i in range(blocks):
        a, b = mixes64(message[i * 16:(i + 1) * 16])
        h1 = ((rol(h1 ^ a, 27, 64) + h2) * 5 + 0x52DCE729) & mask
        h2 = ((rol(h2 ^ b, 31, 64) + h1) * 5 + 0x38495AB5) & mask
    tail = message[blocks * 16:]
    if tail:
        a, b = mixes64(tail)
        h1 ^= a
        h2 ^= b
    h1 ^= len(message)
    h2 ^= len(message)
    h1 = (h1 + h2) & mask
    h2 = (h2 + h1) & mask
    h1, h2 = fmix(h1, 64), fmix(h2, 64)
    h1 = (h1 + h2) & mask
    h2 = (h2 + h1) & mask
    return struct.pack("<QQ", h1, h2)


def hash32(message: bytes, seed: int) -> bytes:
    mask = (1 << 32) - 1
    h = [seed] * 4
    blocks = len(message) // 16
    for k in range(blocks):
        mixed = mixes32(message[k * 16:(k + 1) * 16])
        for i in range(4):
            h[i] = ((rol(h[i] ^ mixed[i], ROT32[i], 32) + h[(i + 1) % 4]) * 5 + ADD32[i]) & mask
    tail = message[blocks * 16:]
    if tail:
        mixed = mixes32(tail)
        h = [h[i] ^ mixed[i] for i in range(4)]
    h = [v ^ len(message) for v in h]
    h[0] = (h[0] + h[1] + h[2] + h[3]) & mask
    for i in range(1, 4):
        h[i] = (h[i] + h[0]) & mask
    h = [fmix(v, 32) for v in h]
    h[0] = (h[0] + h[1] + h[2] + h[3]) & mask
    for i in range(1, 4):
        h[i] = (h[i] + h[0]) & mask
    return struct.pack("<IIII", *h)


def records() -> list[dict[str, str]]:
    path = ROOT / "evidence/print/spool-reconstruction.log"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    pattern = re.compile(
        r"(?P<time>\S+) JOB=(?P<job>\S+) ATTEMPT=(?P<attempt>\d+) "
        r"STATE=(?P<state>\S+) CLASS=(?P<class>\S+) PAYLOAD=(?P<payload>[0-9A-F]{32}) DEST=(?P<dest>\S+)"
    )
    out = [pattern.fullmatch(line).groupdict() for line in raw.decode("utf-8").splitlines() if line and not line.startswith("#")]
    assert len(out) == 133
    assert (out[129]["job"], out[129]["attempt"], out[129]["state"]) == ("PS-261003-0417", "2", "ACK")
    return out


def serializers(r: dict[str, str]) -> dict[str, str]:
    j, a, state, c, d, t = (r[k] for k in ("job", "attempt", "state", "class", "dest", "time"))
    return {
        "job": j,
        "job_attempt": j + a,
        "job:attempt": f"{j}:{a}",
        "job-attempt": f"{j}-{a}",
        "job/attempt": f"{j}/{a}",
        "job_pipe_attempt": f"{j}|{a}",
        "job|state": f"{j}|{state}",
        "job_class_dest": f"{j}|{c}|{d}",
        "job_attempt_class_dest": f"{j}|{a}|{c}|{d}",
        "job_attempt_state_class_dest": f"{j}|{a}|{state}|{c}|{d}",
        "job-attempt-clas-dest": f"{j}-{a}-{c}-{d}",
        "JOB=job": f"JOB={j}",
        "JOB...ATTEMPT": f"JOB={j} ATTEMPT={a}",
        "JOB...CLASS": f"JOB={j} CLASS={c}",
        "JOB...DEST": f"JOB={j} DEST={d}",
        "JOB...ATTEMPT...CLASS...DEST": f"JOB={j} ATTEMPT={a} CLASS={c} DEST={d}",
        "JOB...ATTEMPT...STATE...CLASS...DEST": f"JOB={j} ATTEMPT={a} STATE={state} CLASS={c} DEST={d}",
        "time|job": f"{t}|{j}",
        "time_job_attempt": f"{t}|{j}|{a}",
        "time job attempt": f"{t} JOB={j} ATTEMPT={a}",
        "time full header": f"{t} JOB={j} ATTEMPT={a} STATE={state} CLASS={c}",
        "time suffix": f"{t} JOB={j} ATTEMPT={a} STATE={state} CLASS={c} DEST={d}",
        "full log except payload": f"{t} JOB={j} ATTEMPT={a} STATE={state} CLASS={c} PAYLOAD= DEST={d}",
        "full log except payload field": f"{t} JOB={j} ATTEMPT={a} STATE={state} CLASS={c} DEST={d}",
        "suffix": j.split("-")[-1],
        "suffix_attempt": j.split("-")[-1] + a,
        "class|dest": f"{c}|{d}",
        "class_dest_job": f"{c}|{d}|{j}",
        "class_dest_job_attempt": f"{c}|{d}|{j}|{a}",
        "state|class|dest": f"{state}|{c}|{d}",
    }


def byte_views(payload: bytes, word_size: int):
    words = [payload[i:i + word_size] for i in range(0, 16, word_size)]
    for order in itertools.permutations(range(len(words))):
        for flips in itertools.product((False, True), repeat=len(words)):
            yield (order, flips), b"".join(words[order[i]][::-1] if flips[i] else words[order[i]] for i in range(len(words)))


def controls():
    samples = (
        (b"Hello", 0, "1cc4d455ff74b93544551229cfea00a0", "46ae6023c636635ef4b345adf4b345ad"),
        (b"PS-261003-0300", 0xDEADBEEF, "394b0c8a3a1c837759189ea158835457", "f4fb784c9a2d25e924ea31154ff3a6e8"),
        (b"PS-261003-0300|1", 0xDEADBEEF, "3b9d214972520191aa7fc4cffe50f7a0", "f79fc8eba9c28ed43a06c84a253f85ec"),
        (b"PS-261003-0417|2", 0xDEADBEEF, "28eeaea347e6327e069a5907a9b3e36a", "17dbfe760dd3016edce0a8bc0b6fcb32"),
    )
    for message, seed, expected64, expected32 in samples:
        for forward, reverse, expected, lanes in (
            (hash64, invert64, expected64, 2), (hash32, invert32, expected32, 4)
        ):
            actual = forward(message, seed)
            assert actual.hex() == expected
            assert reverse(message, actual) == (seed,) * lanes
    r = records()
    for forward, reverse, lanes in ((hash64, invert64, 2), (hash32, invert32, 4)):
        seed = 0xDEADBEEF
        donor = r[:2]
        text = lambda item: serializers(item)["job_attempt_class_dest"].encode("utf-8")
        recovered = [reverse(text(row), forward(text(row), seed)) for row in donor]
        assert recovered == [(seed,) * lanes] * 2
        expected = forward(text(r[129]), seed)
        actual = forward(text(r[129]), recovered[0][0])
        assert hashlib.sha256(bytes(x ^ y for x, y in zip(actual, MASK))).digest() == hashlib.sha256(
            bytes(x ^ y for x, y in zip(expected, MASK))
        ).digest()
    print("INDEPENDENT_REFERENCE_FIXTURES=PASS TWO_DONORS_TO_SELECTED_PLANTED=PASS")


def main():
    controls()
    source = records()
    for label, inverse, width, expected in (
        ("x64_128", invert64, 8, 31680),
        ("x86_128", invert32, 4, 1520640),
    ):
        matches = []
        checked = 0
        for i, row in enumerate(source):
            if i == 129:
                continue
            inputs = serializers(row)
            for view, output in byte_views(bytes.fromhex(row["payload"]), width):
                for model, message in inputs.items():
                    state = inverse(message.encode("utf-8"), output)
                    checked += 1
                    if len(set(state)) == 1 and state[0] <= 0xFFFFFFFF:
                        matches.append((i, view, model, state[0]))
        assert checked == expected
        print("ORIGINAL_SOURCE_GATE", label, "checks", checked, "initializer_matches", len(matches))
        for match in matches:
            print("SOURCE_SEED_MATCH", label, match)
    print("SOURCE_GATE_COMPLETE")


if __name__ == "__main__":
    main()
