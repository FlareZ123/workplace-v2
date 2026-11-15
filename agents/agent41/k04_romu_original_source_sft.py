"""Source-only H-17 printer Romu-family predictor SFT.

Use official RomuDuo, RomuDuoJr and RomuTrio 64-bit recurrences, inverted
from two / three consecutive outputs. Test the original 128 chronological
routine spool packets as one stream and grouped by CLASS and/or DEST.
The disputed 18:02 PS-0417 ACK2 is excluded from all inference.
"""
from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from pathlib import Path

MASK = (1 << 64) - 1
C = 15241094284759029579
INV_C = pow(C, -1, 1 << 64)
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SOURCE = Path(__file__).resolve().parents[2] / "resources" / "evidence" / "print" / "spool-reconstruction.log"


def rol(value: int, n: int) -> int:
    return ((value << n) | (value >> (64 - n))) & MASK


def ror(value: int, n: int) -> int:
    return ((value >> n) | (value << (64 - n))) & MASK


def step(name: str, state: tuple[int, ...]) -> tuple[int, tuple[int, ...]]:
    if name == "RomuDuoJr":
        x, y = state
        return x, ((C * y) & MASK, rol((y - x) & MASK, 27))
    if name == "RomuDuo":
        x, y = state
        return x, ((C * y) & MASK, (rol(y, 36) + rol(y, 15) - x) & MASK)
    if name == "RomuTrio":
        x, y, z = state
        return x, ((C * z) & MASK, rol((y - x) & MASK, 12), rol((z - y) & MASK, 44))
    raise ValueError(name)


def predict_next(name: str, known: tuple[int, ...]) -> int:
    if name in {"RomuDuo", "RomuDuoJr"}:
        x0, x1 = known
        y0 = (INV_C * x1) & MASK
        _, state = step(name, (x0, y0))
        _, state = step(name, state)
        predicted, _ = step(name, state)
        return predicted
    x0, x1, x2 = known
    z0, z1 = (INV_C * x1) & MASK, (INV_C * x2) & MASK
    y0 = (z0 - ror(z1, 44)) & MASK
    state = (x0, y0, z0)
    for _ in range(3):
        _, state = step(name, state)
    predicted, _ = step(name, state)
    return predicted


def test_synthetic() -> None:
    states = {
        "RomuDuo": (0xD3ABBB18331286AA, 0xCAFE0C0612A1440E),
        "RomuDuoJr": (0xD3ABBB18331286AA, 0xCAFE0C0612A1440E),
        "RomuTrio": (0xD3ABBB18331286AA, 0xCAFE0C0612A1440E, 0xF17468A98B340CC1),
    }
    for name, state in states.items():
        xs = []
        for _ in range(12):
            x, state = step(name, state)
            xs.append(x)
        k = 3 if name == "RomuTrio" else 2
        assert all(predict_next(name, tuple(xs[i:i+k])) == xs[i+k] for i in range(12-k))
        mutated = xs.copy()
        mutated[-1] ^= 1
        assert predict_next(name, tuple(mutated[-k-1:-1])) != mutated[-1]
    print("Planted Romu predictors and mutation controls: PASS")


def parse_rows(data: bytes) -> list[dict[str, str]]:
    assert hashlib.sha256(data).hexdigest() == PIN
    lines = [line for line in data.decode("ascii").splitlines() if "JOB=" in line]
    assert len(lines) == 133
    rows = [dict(re.findall(r"(\w+)=([^\s]+)", line)) for line in lines]
    routine = rows[:128]
    for i, row in enumerate(routine):
        assert row["JOB"] == f"PS-261003-{i+300:04d}"
        assert row["STATE"] == "ACK" and row["ATTEMPT"] == "1"
        assert len(bytes.fromhex(row["PAYLOAD"])) == 16
    assert rows[129]["JOB"] == "PS-261003-0417" and rows[129]["ATTEMPT"] == "2"
    return routine


def words(rows: list[dict[str, str]], endian: str, reverse_pair: bool) -> list[int]:
    output = []
    for row in rows:
        blob = bytes.fromhex(row["PAYLOAD"])
        pair = [int.from_bytes(blob[:8], endian), int.from_bytes(blob[8:], endian)]
        if reverse_pair:
            pair.reverse()
        output.extend(pair)
    return output


def run(source: bytes) -> dict[str, tuple[int, int]]:
    test_synthetic()
    rows = parse_rows(source)
    models = ("RomuDuoJr", "RomuDuo", "RomuTrio")
    groups: dict[str, list[dict[str, str]]] = {"whole spool": rows}
    for key, chooser in (
        ("CLASS", lambda r: r["CLASS"]),
        ("DEST", lambda r: r["DEST"]),
        ("CLASS/DEST", lambda r: r["CLASS"] + "/" + r["DEST"]),
    ):
        by = defaultdict(list)
        for row in rows:
            by[chooser(row)].append(row)
        for label, subset in by.items():
            groups[key + ":" + label] = subset
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    matching_windows = []
    for group_name, subset in groups.items():
        for endian in ("big", "little"):
            for reverse in (False, True):
                xs = words(subset, endian, reverse)
                for model in models:
                    k = 3 if model == "RomuTrio" else 2
                    windows = len(xs) - k
                    hits = [i for i in range(windows) if predict_next(model, tuple(xs[i:i+k])) == xs[i+k]]
                    counts[model][0] += windows
                    counts[model][1] += len(hits)
                    if hits:
                        matching_windows.append((group_name, endian, reverse, model, hits))
    for model in models:
        checked, hits = counts[model]
        print(f"{model}: {checked} source-only next-64-bit predictions, {hits} exact matches")
    print("Matching original windows:", matching_windows)
    return {model: tuple(counts[model]) for model in models}


if __name__ == "__main__":
    chosen = Path(os.environ.get("H17_PRINTER_SOURCE", SOURCE))
    print("Source:", chosen)
    counts = run(chosen.read_bytes())
    assert all(hits == 0 for checked, hits in counts.values()), "Investigate original source match"
