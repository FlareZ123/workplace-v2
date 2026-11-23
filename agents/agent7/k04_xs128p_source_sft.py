#!/usr/bin/env python3
"""Source-pinned H17 K04 complete xorshift128+ recovery attempt.

Compile the adjacent native inverse, check five withheld seeded controls, then
enumerate every exact first-pair state from the original 18:01 REQUESTED
packet in four conventional 64-bit serialization views. Original 18:02 ACK2
payload is excluded from both source fitting and target construction.

Run from repo root: python agents/agent7/k04_xs128p_source_sft.py
Optional original ZIP: --bundle /path/to/h17-archive-dump.zip
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

MOD = 1 << 64
SOURCE_SHA = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def step(a: int, b: int) -> tuple[int, int]:
    t = a
    t ^= t << 23 & (MOD - 1)
    t ^= t >> 17
    t ^= b
    t ^= b >> 26
    return b, t & (MOD - 1)


def emit_from_post_first(a: int, b: int) -> list[int]:
    output = [(a + b) % MOD]
    for _ in range(5):
        a, b = step(a, b)
        output.append((a + b) % MOD)
    return output


def invert(binary: Path, x0: int, x1: int, x2: int | None = None) -> list[dict[str, int]]:
    command = [str(binary), f"{x0:016X}", f"{x1:016X}"]
    if x2 is not None:
        command.append(f"{x2:016X}")
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=100)
    solutions: list[dict[str, int]] = []
    summary = None
    for line in result.stdout.splitlines():
        if line.startswith("SOLUTION "):
            fields = dict(part.split("=", 1) for part in line.split()[1:])
            a, b = (int(v, 16) for v in fields["state_after_x0"].split(":"))
            solutions.append({
                "state_a": a,
                "state_b": b,
                **{k: int(fields[k], 16) for k in ("x2", "x3", "x4", "x5")},
                "control_match": int(fields["synthetic_x2_match"]),
            })
        elif line.startswith("SUMMARY "):
            summary = dict(part.split("=", 1) for part in line.split()[1:])
    assert summary is not None
    assert len(solutions) == int(summary["first_pair_states"])
    if x2 is not None:
        assert sum(s["control_match"] for s in solutions) == int(summary["synthetic_x2_states"])
    return solutions


def read_original(bundle: Path | None, root: Path) -> dict[str, bytes]:
    if bundle is not None:
        with zipfile.ZipFile(bundle) as archive:
            raw = {key: archive.read(key) for key in SOURCE_SHA}
    else:
        raw = {key: (root / key).read_bytes() for key in SOURCE_SHA}
    for key, digest in SOURCE_SHA.items():
        assert hashlib.sha256(raw[key]).hexdigest() == digest, key
    return raw


def find_selected_job(spool: bytes) -> list[bytes]:
    found = []
    for line in spool.decode("utf-8").splitlines():
        if "JOB=PS-261003-0417" not in line or "2026-10-03T18:" not in line:
            continue
        n = int(re.search(r"ATTEMPT=(\d+)", line).group(1))
        state = re.search(r"STATE=(\w+)", line).group(1)
        role = re.search(r"CLASS=(\w+)", line).group(1)
        data = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]+)", line).group(1))
        found.append((n, state, role, data))
    assert [(n, s, role) for n, s, role, _ in found] == [
        (1, "REQUESTED", "RECOVER"),
        (2, "ACK", "RECOVER"),
        (3, "REQUESTED", "RECOVER"),
    ]
    assert all(len(payload) == 16 for *_, payload in found)
    return [payload for *_, payload in found]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    compiler = next((path for tool in ("gcc", "clang", "cc")
                     if (path := shutil.which(tool))), None)
    assert compiler is not None, "A C compiler is required for complete 2^26 state inversion"
    native = Path(__file__).with_name("k04_xs128p_inverse.c")
    with tempfile.TemporaryDirectory(prefix="h17-xs128p-") as directory:
        binary = Path(directory, "inverse" + (".exe" if os.name == "nt" else ""))
        subprocess.run([
            compiler, "-O3", "-std=c11", "-Wall", "-Wextra",
            "-o", str(binary), str(native)
        ], check=True)
        seeds = [(0x0123456789ABCDEF, 0xFA12345600123456)]
        rng = random.Random(20261123)
        seeds.extend((rng.getrandbits(64), rng.getrandbits(64)) for _ in range(4))
        for index, (a, b) in enumerate(seeds):
            observed = emit_from_post_first(a, b)
            possibilities = invert(binary, *observed[:3])
            matched = [p for p in possibilities if p["control_match"]]
            assert len(matched) == 1, (index, len(possibilities), len(matched))
            exact = matched[0]
            assert (exact["state_a"], exact["state_b"]) == (a, b)
            assert [exact[k] for k in ("x2", "x3", "x4", "x5")] == observed[2:]
            print(f"PLANTED {index}: {len(possibilities)} exact first-pair states; withheld full-state recovery PASS", flush=True)

        original = read_original(args.bundle, args.root)
        route = json.loads(original["evidence/recovery-routing.json"])
        acceptance = json.loads(original["acceptance.json"])
        mask = bytes.fromhex(route["K04"]["masked_component"])
        target = acceptance["slot_sha256"]["K04"]
        source = find_selected_job(original["evidence/print/spool-reconstruction.log"])
        counts = []
        for endian in ("big", "little"):
            for swap in (False, True):
                def unpack(payload: bytes) -> list[int]:
                    words = [int.from_bytes(payload[i:i + 8], endian) for i in (0, 8)]
                    return list(reversed(words)) if swap else words

                def pack(words: list[int]) -> bytes:
                    arrange = list(reversed(words)) if swap else words
                    return b"".join(w.to_bytes(8, endian) for w in arrange)

                x0, x1 = unpack(source[0])
                x4, x5 = unpack(source[2])
                solutions = invert(binary, x0, x1)
                observations = []
                for s in solutions:
                    coupon = pack([s["x2"], s["x3"]])
                    component = bytes(x ^ y for x, y in zip(coupon, mask))
                    observations.append({
                        "coupon_hex": coupon.hex().upper(),
                        "component_hex": component.hex().upper(),
                        "component_sha256": hashlib.sha256(component).hexdigest(),
                        "original_commitment_hit": hashlib.sha256(component).hexdigest() == target,
                        "third_REQUESTED_holdout_hit": s["x4"] == x4 and s["x5"] == x5,
                    })
                counts.append((len(solutions),
                               sum(record["original_commitment_hit"] for record in observations),
                               sum(record["third_REQUESTED_holdout_hit"] for record in observations)))
                print(json.dumps({"endian": endian, "swap64": swap,
                                  "source_models": len(solutions), "candidates": observations},
                                 indent=2), flush=True)
        assert counts == [(1, 0, 0), (1, 0, 0), (0, 0, 0), (2, 0, 0)], counts
        print("ORIGINAL: 4 complete middle coupons; 0 K04 accepted; 0 third-request full holdouts", flush=True)


if __name__ == "__main__":
    main()
