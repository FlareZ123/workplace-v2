"""Exact three-attempt H-17 K04 Romu producer test; read-only, standard-library SFT.

Infer 64-bit state from the first intact PS-0417 REQUESTED payload.
Predict the selected ACK2 coupon and separately the later REQUESTED3
payload. The selected copied ACK2 buffer is deliberately withheld.
"""
from __future__ import annotations
import hashlib
import os
import re
from pathlib import Path

C = 15241094284759029579
M64 = (1 << 64) - 1
M32 = (1 << 32) - 1
IC64 = pow(C, -1, 1 << 64)
IC32 = pow(C, -1, 1 << 32)
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROOT = Path(__file__).resolve().parents[2] / "resources"
MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def rol(v: int, n: int) -> int:
    return ((v << n) | (v >> (64 - n))) & M64


def step(model: str, state: tuple[int, int]) -> tuple[int, int]:
    x, y = state
    if model == "RomuDuo":
        return (C * y) & M64, (rol(y, 36) + rol(y, 15) - x) & M64
    if model == "RomuDuoJr":
        return (C * y) & M64, rol((y - x) & M64, 27)
    raise ValueError(model)


def predict_duo(model: str, packet: bytes, endian: str, rev: bool):
    v = [int.from_bytes(packet[i:i+8], endian) for i in (0, 8)]
    if rev:
        v.reverse()
    state = (v[0], (v[1] * IC64) & M64)
    emitted = []
    for _ in range(6):
        emitted.append(state[0])
        state = step(model, state)
    assert emitted[:2] == v
    def pack(words):
        if rev:
            words = list(reversed(words))
        return b"".join(w.to_bytes(8, endian) for w in words)
    return pack(emitted[2:4]), pack(emitted[4:6])


def predict_mono(packet: bytes, endian: str, rev: bool):
    words = [int.from_bytes(packet[i:i+4], endian) for i in (0, 4, 8, 12)]
    if rev:
        words.reverse()
    state = ((words[1] * IC32 & M32) << 32) | words[0]
    emitted = []
    for _ in range(12):
        emitted.append(state & M32)
        state = ((((state & M32) << 32) | (state >> 32)) * C) & M64
    if emitted[:4] != words:
        return None
    def pack(values):
        if rev:
            values = list(reversed(values))
        return b"".join(w.to_bytes(4, endian) for w in values)
    return pack(emitted[4:8]), pack(emitted[8:12])


def planted() -> None:
    for model in ("RomuDuo", "RomuDuoJr"):
        state = (0xD3ABBB18331286AA, 0xCAFE0C0612A1440E)
        outputs = []
        for _ in range(6):
            outputs.append(state[0])
            state = step(model, state)
        for endian in ("big", "little"):
            for rev in (False, True):
                def pack(values):
                    if rev:
                        values = list(reversed(values))
                    return b"".join(w.to_bytes(8, endian) for w in values)
                src, middle, late = [pack(outputs[i:i+2]) for i in (0, 2, 4)]
                assert predict_duo(model, src, endian, rev) == (middle, late)
    state = 0xD3ABBB18331286AA
    outputs = []
    for _ in range(12):
        outputs.append(state & M32)
        state = ((((state & M32) << 32) | (state >> 32)) * C) & M64
    for endian in ("big", "little"):
        for rev in (False, True):
            def pack(values):
                if rev:
                    values = list(reversed(values))
                return b"".join(w.to_bytes(4, endian) for w in values)
            src, middle, late = [pack(outputs[i:i+4]) for i in (0, 4, 8)]
            assert predict_mono(src, endian, rev) == (middle, late)
    print("Three-attempt planted whole-object producer controls: PASS")


def main():
    planted()
    source = Path(os.environ.get(
        "H17_PRINTER_SOURCE", ROOT / "evidence/print/spool-reconstruction.log")).read_bytes()
    assert hashlib.sha256(source).hexdigest() == PIN
    rows = [dict(re.findall(r"(\w+)=([^\s]+)", line))
            for line in source.decode("ascii").splitlines() if "JOB=" in line]
    assert len(rows) == 133
    assert [(rows[i]["JOB"], rows[i]["ATTEMPT"], rows[i]["STATE"]) for i in (128,129,130)] == [
        ("PS-261003-0417", "1", "REQUESTED"),
        ("PS-261003-0417", "2", "ACK"),
        ("PS-261003-0417", "3", "REQUESTED")]
    early = bytes.fromhex(rows[128]["PAYLOAD"])
    late = bytes.fromhex(rows[130]["PAYLOAD"])
    counts = {"models": 12, "source_fit": 0, "heldout_matches": 0, "k04_matches": 0}
    for model in ("RomuDuoJr", "RomuDuo", "RomuMono"):
        for endian in ("big", "little"):
            for rev in (False, True):
                output = (predict_mono(early, endian, rev) if model == "RomuMono"
                          else predict_duo(model, early, endian, rev))
                if output is None:
                    print(model, endian, rev, "first-request source fit: FAIL")
                    continue
                counts["source_fit"] += 1
                selected, later = output
                candidate = bytes(x ^ y for x, y in zip(selected, MASK))
                held = later == late
                hit = hashlib.sha256(candidate).hexdigest() == TARGET
                counts["heldout_matches"] += int(held)
                counts["k04_matches"] += int(hit)
                print(model, endian, rev, "candidate", candidate.hex().upper(),
                      "later_original_control", held, "K04_commitment", hit)
    print(counts)
    assert counts == {"models": 12, "source_fit": 8, "heldout_matches": 0, "k04_matches": 0}


if __name__ == "__main__":
    main()
