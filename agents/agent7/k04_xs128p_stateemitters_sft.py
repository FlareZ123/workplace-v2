#!/usr/bin/env python3
"""Exact raw-state, odd-multiplier and XOR xorshift128 producer family for K04.

Seven source-output functions are inverted from two complete 64-bit outputs,
under two xorshift128 transitions, both original REQUESTED anchors and all
48 32-bit chunk serializers. Enumerate complete 16-byte future/past coupon
windows through 65k output positions, verify unchanged original K04 SHA256.
No selected ACK2 payload is used as a model input. Requires OpenSSL and C.
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

from k04_xs128p_source_sft import read_original, find_selected_job

MASK64 = (1 << 64) - 1
MULTIPLIERS = {"M1": 0x9E3779B97F4A7C13, "M2": 0x2545F4914F6CDD1D}
MODES = ("L", "R", "LmulM1", "RmulM1", "LmulM2", "RmulM2", "X")
VARIANTS = {"v8": (17, 26), "vigna": (18, 5)}


def step(a: int, b: int, ra: int, rb: int) -> tuple[int, int]:
    t = a
    t ^= t << 23 & MASK64
    t ^= t >> ra
    t ^= b
    t ^= b >> rb
    return b, t & MASK64


def reverse(l: int, r: int, ra: int, rb: int) -> tuple[int, int]:
    u = r ^ l ^ (l >> rb)
    v = u
    shift = ra
    while shift < 64:
        v ^= v >> shift
        shift *= 2
    return (v ^ (v << 23 & MASK64) ^ (v << 46 & MASK64)) & MASK64, l


def emit(state: tuple[int, int], mode: str) -> int:
    a, b = state
    if mode == "X":
        return a ^ b
    word = a if mode.startswith("L") else b
    for label, multiplier in MULTIPLIERS.items():
        if label in mode:
            return (word * multiplier) & MASK64
    return word


def linear_map(a: int, ra: int, rb: int) -> int:
    # If the first two observed values are X = L XOR R, then
    # x1 XOR (x0 >> rb) = F(L), where F(L) is linear over GF(2).
    return step(a, 0, ra, rb)[1] ^ (a >> rb)


def make_basis(ra: int, rb: int) -> dict[int, tuple[int, int]]:
    basis = {}
    for index in range(64):
        mapped = linear_map(1 << index, ra, rb)
        preimage = 1 << index
        while mapped and (mapped.bit_length() - 1) in basis:
            known, origin = basis[mapped.bit_length() - 1]
            mapped ^= known
            preimage ^= origin
        assert mapped != 0, (ra, rb, index)
        basis[mapped.bit_length() - 1] = mapped, preimage
    assert len(basis) == 64
    return basis


def solve_basis(target: int, basis: dict[int, tuple[int, int]]) -> int:
    preimage = 0
    while target:
        known, origin = basis[target.bit_length() - 1]
        target ^= known
        preimage ^= origin
    return preimage


def fit(x0: int, x1: int, mode: str, ra: int, rb: int,
        basis: dict[int, tuple[int, int]]) -> tuple[int, int]:
    if mode == "X":
        a = solve_basis(x1 ^ (x0 >> rb), basis)
        b = a ^ x0
    else:
        multiplier = next((m for label, m in MULTIPLIERS.items()
                           if label in mode), None)
        inv = pow(multiplier, -1, 1 << 64) if multiplier is not None else 1
        first = (x0 * inv) & MASK64
        second = (x1 * inv) & MASK64
        if mode.startswith("L"):
            a, b = first, second
        else:
            b = first
            a, _ = reverse(b, second, ra, rb)
    state = a, b
    assert emit(state, mode) == x0
    assert emit(step(*state, ra, rb), mode) == x1
    return state


def unpack(data: bytes, perm: tuple[int, ...], endian: str) -> tuple[int, int]:
    physical = [int.from_bytes(data[i:i + 4], endian) for i in (0, 4, 8, 12)]
    logical = [physical[perm[i]] for i in range(4)]
    return ((logical[0] << 32) | logical[1],
            (logical[2] << 32) | logical[3])


def pack(outputs: tuple[int, int], perm: tuple[int, ...], endian: str) -> bytes:
    left, right = outputs
    logical = [left >> 32, left & 0xFFFFFFFF, right >> 32, right & 0xFFFFFFFF]
    physical = [0, 0, 0, 0]
    for index, position in enumerate(perm):
        physical[position] = logical[index]
    return b"".join(w.to_bytes(4, endian) for w in physical)


def predict(state: tuple[int, int], mode: str, ra: int, rb: int,
            direction: str) -> tuple[tuple[int, int], tuple[int, int]]:
    if direction == "f":
        states = {0: state}
        for index in range(1, 6):
            states[index] = step(*states[index - 1], ra, rb)
        return ((emit(states[2], mode), emit(states[3], mode)),
                (emit(states[4], mode), emit(states[5], mode)))
    states = {4: state}
    for index in (3, 2, 1, 0):
        states[index] = reverse(*states[index + 1], ra, rb)
    return ((emit(states[2], mode), emit(states[3], mode)),
            (emit(states[0], mode), emit(states[1], mode)))


def synthetic_control(binary: Path, original_mask: bytes) -> None:
    rng = random.Random(20261123)
    perm = (2, 0, 3, 1)
    endian = "little"
    for variant, (ra, rb) in VARIANTS.items():
        basis = make_basis(ra, rb)
        state = (0x0123456789ABCDEF, 0xFA12345600123456)
        states = {0: state}
        for index in range(1, 51):
            states[index] = step(*states[index - 1], ra, rb)
        for index in range(-1, -51, -1):
            states[index] = reverse(*states[index + 1], ra, rb)
        for mode in MODES:
            a, b = rng.getrandbits(64), rng.getrandbits(64)
            planted = (a, b)
            source = (emit(planted, mode),
                      emit(step(*planted, ra, rb), mode))
            assert fit(*source, mode, ra, rb, basis) == planted
            for direction in ("f", "b"):
                scan_state = states[0] if direction == "f" else states[4]
                for window in (2, 42):
                    index = window if direction == "f" else 4 - window
                    coupon = pack((emit(states[index], mode),
                                   emit(states[index + 1], mode)), perm, endian)
                    target = hashlib.sha256(bytes(a ^ b for a, b
                                                  in zip(coupon, original_mask))).hexdigest()
                    result = subprocess.run([
                        str(binary), variant, direction,
                        f"{scan_state[0]:016X}", f"{scan_state[1]:016X}",
                        "2031", endian, original_mask.hex(), target, mode
                    ], capture_output=True, text=True, check=True, timeout=30).stdout
                    assert f"index={window}" in result and "hits=1" in result, (
                        variant, mode, direction, window
                    )
            print(f"PLANTED {variant} {mode}: state inversion and four full coupons PASS", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    compiler = next((path for name in ("gcc", "clang", "cc")
                     if (path := shutil.which(name))), None)
    assert compiler is not None, "Requires a C compiler and OpenSSL/libcrypto"

    raw = read_original(args.bundle, args.root)
    route = json.loads(raw["evidence/recovery-routing.json"])
    acceptance = json.loads(raw["acceptance.json"])
    packet = find_selected_job(raw["evidence/print/spool-reconstruction.log"])
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]

    with tempfile.TemporaryDirectory(prefix="h17-emitter-") as directory:
        source = Path(__file__).with_name("k04_xs128p_emitter_gap_scan.c")
        binary = Path(directory, "scan" + (".exe" if os.name == "nt" else ""))
        subprocess.run([compiler, "-O3", "-std=c11", "-Wall", "-Wextra",
                        "-o", str(binary), str(source), "-lcrypto"], check=True)
        synthetic_control(binary, mask)
        assignments = 0
        full_checks = 0
        immediate_components: set[str] = set()
        original_hits = []
        holdouts = []
        for variant, (ra, rb) in VARIANTS.items():
            basis = make_basis(ra, rb)
            for mode in MODES:
                for perm, endian in itertools.product(
                    itertools.permutations(range(4)), ("big", "little")
                ):
                    first_request = unpack(packet[0], perm, endian)
                    last_request = unpack(packet[2], perm, endian)
                    for direction in ("f", "b"):
                        source_pair = first_request if direction == "f" else last_request
                        state = fit(*source_pair, mode, ra, rb, basis)
                        coupon_outputs, opposite = predict(state, mode, ra, rb, direction)
                        coupon = pack(coupon_outputs, perm, endian)
                        component = bytes(a ^ b for a, b in zip(coupon, mask))
                        immediate_components.add(component.hex())
                        if hashlib.sha256(component).hexdigest() == target:
                            original_hits.append(("immediate", variant, mode, perm, endian, direction,
                                                  component.hex()))
                        if opposite == (last_request if direction == "f" else first_request):
                            holdouts.append((variant, mode, perm, endian, direction))
                        result = subprocess.run([
                            str(binary), variant, direction,
                            f"{state[0]:016X}", f"{state[1]:016X}",
                            "".join(map(str, perm)), endian, mask.hex(), target, mode
                        ], capture_output=True, text=True, check=True, timeout=30).stdout
                        summary = None
                        for line in result.splitlines():
                            if line.startswith("HIT "):
                                original_hits.append((variant, mode, perm, endian,
                                                      direction, line))
                            elif line.startswith("SUMMARY "):
                                summary = dict(field.split("=", 1)
                                               for field in line.split()[1:])
                        assert summary is not None
                        full_checks += int(summary["checked"])
                        assignments += 1
                print(json.dumps({
                    "variant": variant, "mode": mode,
                    "exact_source_states": assignments,
                    "whole_component_checks": full_checks,
                    "original_hits": original_hits
                }), flush=True)
        assert assignments == 1344
        assert len(immediate_components) == 576
        assert full_checks == 88077696
        assert not original_hits
        assert not holdouts
        print(json.dumps({
            "original_source_state_assignments": assignments,
            "unique_immediate_components": len(immediate_components),
            "full_original_K04_SHA256_checks": full_checks,
            "original_K04_matches": original_hits,
            "opposite_full_request_matches": holdouts
        }, indent=2), flush=True)


if __name__ == "__main__":
    main()
