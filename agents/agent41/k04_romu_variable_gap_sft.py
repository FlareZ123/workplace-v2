"""Read-only H-17 selected K04 Romu hidden-draw search, single runnable test.

From the intact 18:01 REQUESTED1 packet, invert all 128 RomuDuo/Jr
state bits. Enumerate contiguous two-word complete physical coupon
windows at native output offsets 2..131072 (unknown intermediate draws).
Compare 18:03 REQUESTED3 as independent complete original holdout.
The copied selected 18:02 ACK2 payload is never consulted.
"""
from __future__ import annotations
import hashlib
import os
import re
from pathlib import Path

PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
M64 = (1 << 64) - 1
C = 15241094284759029579
IC = pow(C, -1, 1 << 64)
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = bytes.fromhex("930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0")
SOURCE = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
N = 131072


def rot(x, n):
    return ((x << n) | (x >> (64 - n))) & M64


def step(model, state):
    x, y = state
    return ((C * y) & M64,
            rot((y - x) & M64, 27) if model == "Jr"
            else (rot(y, 36) + rot(y, 15) - x) & M64)


def pack(values, endian, reverse):
    if reverse:
        values = list(reversed(values))
    return b"".join(v.to_bytes(8, endian) for v in values)


def gen_cut(model, first, endian, reverse, n):
    values = [int.from_bytes(first[i:i+8], endian) for i in (0, 8)]
    if reverse:
        values.reverse()
    state = (values[0], (IC * values[1]) & M64)
    for _ in range(n):
        yield state[0]
        state = step(model, state)


def planted():
    for model in ("Jr", "Duo"):
        state = (0xD3ABBB18331286AA, 0xCAFE0C0612A1440E)
        stream = []
        for _ in range(520):
            stream.append(state[0])
            state = step(model, state)
        for endian in ("big", "little"):
            for reverse in (False, True):
                original = pack(stream[:2], endian, reverse)
                rebuilt = list(gen_cut(model, original, endian, reverse, 520))
                assert rebuilt == stream
                assert pack(rebuilt[127:129], endian, reverse) == pack(stream[127:129], endian, reverse)
    print("Planted variable-offset generator controls: PASS")


def main():
    planted()
    data = Path(os.environ.get("H17_PRINTER_SOURCE", SOURCE)).read_bytes()
    assert hashlib.sha256(data).hexdigest() == PIN
    rows = [dict(re.findall(r"(\w+)=([^\s]+)", line))
            for line in data.decode("ascii").splitlines() if "JOB=" in line]
    assert len(rows) == 133
    assert [(rows[i]["JOB"], rows[i]["ATTEMPT"]) for i in (128,129,130)] == [
        ("PS-261003-0417", "1"), ("PS-261003-0417", "2"), ("PS-261003-0417", "3")]
    early = bytes.fromhex(rows[128]["PAYLOAD"])
    late = bytes.fromhex(rows[130]["PAYLOAD"])
    tested = hits = controls = 0
    for model in ("Jr", "Duo"):
        for endian in ("big", "little"):
            for reverse in (False, True):
                stream = gen_cut(model, early, endian, reverse, N + 4)
                previous = next(stream)
                local_tested = local_hits = local_controls = 0
                for index, word in enumerate(stream, 1):
                    if 3 <= index <= N + 1:
                        packet = pack([previous, word], endian, reverse)
                        candidate = bytes(a ^ b for a, b in zip(packet, MASK))
                        if hashlib.sha256(candidate).digest() == TARGET:
                            local_hits += 1
                            print("K04 HIT", model, endian, reverse, index - 1,
                                  candidate.hex().upper())
                        if index >= 5 and packet == late:
                            local_controls += 1
                            print("18:03 ORIGINAL MATCH", model, endian, reverse, index - 1)
                        local_tested += 1
                    previous = word
                tested += local_tested
                hits += local_hits
                controls += local_controls
                print(model, endian, reverse, "complete candidates", local_tested,
                      "K04 matches", local_hits, "18:03 matches", local_controls)
    print("TOTAL", tested, "full component candidates; K04 hits", hits,
          "18:03 original source hits", controls)
    assert tested == 1048568 and hits == 0 and controls == 0


if __name__ == "__main__":
    main()
