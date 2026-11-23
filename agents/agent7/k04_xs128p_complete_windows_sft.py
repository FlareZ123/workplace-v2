#!/usr/bin/env python3
"""K04 complete-source xorshift128+ recovery: both native 128-bit variants.

The incident's 18:01 and 18:03 REQUESTED packets are independently fitted
as two consecutive 64-bit modulo-sum outputs of a 128-bit xorshift+ state.
Do not fit, seed, or copy bytes from the disputed 18:02 ACK2 record.

For each complete exact 2-output state under 48 serialized source views
(24 fourword orderings x global BE/LE 32bit words), scan 65,533 adjacent
16-byte coupon windows forwards or 65,535 backwards. Test every resulting
full masked component against the untouched original K04 SHA256 commitment.

Variants: V8 23/17/26, Vigna 23/18/5. The C inverses are 2^26 and 2^18
complete low-bit enumerators respectively, with no solver timeout/cap.
Requires GCC/Clang and OpenSSL/libcrypto, with no original-source writes.

Run from repository root, or set --bundle to the original ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from k04_xs128p_source_sft import find_selected_job, invert, read_original

MASK64 = (1 << 64) - 1
VARIANTS = {"v8": (17, 26), "vigna": (18, 5)}


def step(a: int, b: int, variant: str) -> tuple[int, int]:
    first_shift, second_shift = VARIANTS[variant]
    t = a
    t ^= t << 23 & MASK64
    t ^= t >> first_shift
    t ^= b
    t ^= b >> second_shift
    return b, t & MASK64


def reverse(l: int, r: int, variant: str) -> tuple[int, int]:
    first_shift, second_shift = VARIANTS[variant]
    u = r ^ l ^ (l >> second_shift)
    v = u
    shift = first_shift
    while shift < 64:
        v ^= v >> shift
        shift *= 2
    a = v ^ (v << 23 & MASK64) ^ (v << 46 & MASK64)
    return a & MASK64, l


def unpack(data: bytes, perm: tuple[int, ...], endian: str) -> tuple[int, int]:
    physical = [int.from_bytes(data[i:i + 4], endian) for i in (0, 4, 8, 12)]
    logical = [physical[perm[i]] for i in range(4)]
    return ((logical[0] << 32) | logical[1],
            (logical[2] << 32) | logical[3])


def pack(y0: int, y1: int, perm: tuple[int, ...], endian: str) -> bytes:
    logical = [y0 >> 32, y0 & 0xFFFFFFFF, y1 >> 32, y1 & 0xFFFFFFFF]
    physical = [0, 0, 0, 0]
    for index, position in enumerate(perm):
        physical[position] = logical[index]
    return b"".join(value.to_bytes(4, endian) for value in physical)


def compile_native(compiler: str, root: Path, directory: Path) -> dict[str, Path]:
    sources = {
        "v8": root / "k04_xs128p_inverse.c",
        "vigna": root / "k04_xs128p_vigna235_inverse.c",
        "scan": root / "k04_xs128p_dual_gap_scan.c",
    }
    outputs = {}
    for label, source in sources.items():
        binary = directory / (label + (".exe" if os.name == "nt" else ""))
        command = [compiler, "-O3", "-std=c11", "-Wall", "-Wextra",
                   "-o", str(binary), str(source)]
        if label == "scan":
            command.append("-lcrypto")
        subprocess.run(command, check=True)
        outputs[label] = binary
    return outputs


def synthetic_tests(binaries: dict[str, Path], route_mask: bytes) -> None:
    rng = random.Random(20261123)
    for variant in VARIANTS:
        for trial in range(4):
            a, b = rng.getrandbits(64), rng.getrandbits(64)
            values = [(a + b) & MASK64]
            for _ in range(5):
                a, b = step(a, b, variant)
                values.append((a + b) & MASK64)
            source_state = (a, b)
            # Reconstruct the initial state after the first output from six
            # generated values, including the held-out x2 selector.
            state = (rng.getrandbits(64), rng.getrandbits(64))
            output = [(state[0] + state[1]) & MASK64]
            cursor = state
            for _ in range(5):
                cursor = step(*cursor, variant)
                output.append(sum(cursor) & MASK64)
            models = invert(binaries[variant], *output[:3])
            hits = [m for m in models if m["control_match"]]
            assert len(hits) == 1, (variant, trial, len(models))
            m = hits[0]
            assert (m["state_a"], m["state_b"]) == state
            assert [m[k] for k in ("x2", "x3", "x4", "x5")] == output[2:]
            print(f"PLANTED {variant} {trial}: exact state and four future outputs PASS", flush=True)

        # Independent planted 65k-gap checks in both temporal directions.
        seed = (0x0123456789ABCDEF, 0xFA12345600123456)
        states = {0: seed}
        for index in range(1, 1240):
            states[index] = step(*states[index - 1], variant)
        for index in range(-1, -1240, -1):
            states[index] = reverse(*states[index + 1], variant)
        perm = (2, 0, 3, 1)
        endian = "little"
        for direction in ("f", "b"):
            state = states[0] if direction == "f" else states[4]
            for window in (2, 42, 1234):
                position = window if direction == "f" else 6 - window
                coupon = pack(sum(states[position]) & MASK64,
                              sum(states[position + 1]) & MASK64, perm, endian)
                component = bytes(a ^ b for a, b in zip(coupon, route_mask))
                target = hashlib.sha256(component).hexdigest()
                result = subprocess.run([
                    str(binaries["scan"]), variant, direction,
                    f"{state[0]:016X}", f"{state[1]:016X}",
                    "".join(map(str, perm)), endian,
                    route_mask.hex(), target
                ], text=True, capture_output=True, check=True, timeout=30).stdout
                assert f"index={window}" in result, (variant, direction, window, result)
                assert "hits=1" in result, (variant, direction, window, result)
                print(f"PLANTED {variant} {direction} window {window}: exact component PASS", flush=True)


def original_windows(binaries: dict[str, Path], root: Path,
                     bundle: Path | None) -> None:
    raw = read_original(bundle, root)
    printer = find_selected_job(raw["evidence/print/spool-reconstruction.log"])
    route = json.loads(raw["evidence/recovery-routing.json"])
    accepted = json.loads(raw["acceptance.json"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = accepted["slot_sha256"]["K04"]
    synthetic_tests(binaries, mask)

    for variant in VARIANTS:
        states = 0
        forwards = 0
        backwards = 0
        candidate_checks = 0
        hits = []
        for index, (perm, endian) in enumerate(itertools.product(
            itertools.permutations(range(4)), ("big", "little")
        )):
            for direction in ("f", "b"):
                source = printer[0] if direction == "f" else printer[2]
                y0, y1 = unpack(source, perm, endian)
                models = invert(binaries[variant], y0, y1)
                states += len(models)
                if direction == "f":
                    forwards += len(models)
                else:
                    backwards += len(models)
                for model in models:
                    result = subprocess.run([
                        str(binaries["scan"]), variant, direction,
                        f"{model['state_a']:016X}", f"{model['state_b']:016X}",
                        "".join(map(str, perm)), endian, mask.hex(), target
                    ], capture_output=True, text=True, check=True, timeout=30).stdout
                    summary = None
                    for line in result.splitlines():
                        if line.startswith("HIT "):
                            hits.append(line)
                        elif line.startswith("SUMMARY "):
                            summary = dict(part.split("=", 1)
                                           for part in line.split()[1:])
                    assert summary is not None
                    candidate_checks += int(summary["checked"])
                    assert int(summary["hits"]) == sum(
                        f"variant={variant} direction={direction}" in h
                        for h in result.splitlines() if h.startswith("HIT ")
                    )
            if (index + 1) % 8 == 0:
                print(json.dumps({
                    "variant": variant, "views": index + 1, "source_states": states,
                    "whole_component_SHA256_checks": candidate_checks,
                    "matches": hits
                }), flush=True)

        expected = (89, 47, 42, 5832521) if variant == "v8" else (98, 41, 57, 6422348)
        observed = (states, forwards, backwards, candidate_checks)
        assert observed == expected, (variant, observed, expected)
        print(json.dumps({
            "variant": variant, "total_source_views": 48,
            "source_states": states, "forward_states": forwards,
            "backward_states": backwards, "full_SHA256_checks": candidate_checks,
            "authentic_K04_matches": hits
        }, indent=2), flush=True)
        assert not hits, f"Original K04 candidate recovered: {hits}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    compiler = next((path for name in ("gcc", "clang", "cc")
                     if (path := shutil.which(name))), None)
    assert compiler is not None, "Requires a C compiler and OpenSSL/libcrypto"
    with tempfile.TemporaryDirectory(prefix="h17-xs128p-dual-") as directory:
        binaries = compile_native(compiler, Path(__file__).parent, Path(directory))
        original_windows(binaries, args.root, args.bundle)


if __name__ == "__main__":
    main()
