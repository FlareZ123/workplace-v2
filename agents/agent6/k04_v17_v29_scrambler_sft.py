#!/usr/bin/env python3
"""H-17 K04: exact ITU-T V.17/V.29 self-synchronizing scrambler test.

The N22 "label printer ... like a fax machine" remark is only a weak hypothesis
cue, not evidence of fax-modem firmware. V.17 and V.29 specify the polynomial
1 + x^-18 + x^-23. This script tests both transmitter-scramble and receiver-
descramble recurrences, MSB-first and LSB-first byte serialization, and every
possible 23-bit preceding history for each branch.

The selected ACK2 payload, route mask, source files and original commitment
are read-only. No phase offsets, byte permutations, other fax standards or
other polynomials are silently added.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTOR = (
    "2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 "
    "STATE=ACK CLASS=RECOVER"
)
STATE_COUNT = 1 << 23
SYNTHETIC_STATE = 0x5A3C12


def resource_root(root: Path) -> Path:
    if (root / "resources" / "evidence").is_dir():
        return root / "resources"
    if (root / "evidence").is_dir():
        return root
    raise FileNotFoundError(f"cannot locate resources/evidence below {root}")


def bits_from_bytes(data: bytes, msb_first: bool) -> list[int]:
    order = range(7, -1, -1) if msb_first else range(8)
    return [(byte >> bit) & 1 for byte in data for bit in order]


def bytes_from_bits(bits: list[int], msb_first: bool) -> bytes:
    assert len(bits) % 8 == 0
    out = bytearray()
    for i in range(0, len(bits), 8):
        value = 0
        for j, bit in enumerate(bits[i:i + 8]):
            value |= bit << ((7 - j) if msb_first else j)
        out.append(value)
    return bytes(out)


def transform(data: bytes, history_state: int, msb_first: bool,
              direction: str) -> bytes:
    """Apply one 23-bit-history branch of the V.17/V.29 polynomial.

    descramble: y[n] = x[n] XOR x[n-18] XOR x[n-23], with x the
    received scrambled stream.
    scramble:   y[n] = x[n] XOR y[n-18] XOR y[n-23], with x the
    message stream and y the transmitted scrambled stream.

    State bit 0 is the oldest of the 23 preceding bits.
    """
    if not 0 <= history_state < STATE_COUNT:
        raise ValueError("history state must be a 23-bit value")
    if direction not in ("scramble", "descramble"):
        raise ValueError(direction)

    inp = bits_from_bytes(data, msb_first)
    history = [(history_state >> i) & 1 for i in range(23)]
    out: list[int] = []

    for n, bit in enumerate(inp):
        if direction == "descramble":
            def delayed(delay: int) -> int:
                k = n - delay
                return inp[k] if k >= 0 else history[k + 23]
        else:
            def delayed(delay: int) -> int:
                k = n - delay
                return out[k] if k >= 0 else history[k + 23]
        out.append(bit ^ delayed(18) ^ delayed(23))

    return bytes_from_bits(out, msb_first)


def output_basis(data: bytes, msb_first: bool,
                 direction: str) -> tuple[bytes, list[bytes]]:
    base = transform(data, 0, msb_first, direction)
    basis = []
    for bit in range(23):
        one = transform(data, 1 << bit, msb_first, direction)
        basis.append(bytes(a ^ b for a, b in zip(one, base)))
    return base, basis


def search_variant(data: bytes, mask: bytes, target: bytes,
                   msb_first: bool, direction: str) -> tuple[list[tuple[int, str]], float]:
    base, basis = output_basis(data, msb_first, direction)
    current = bytearray(base)
    previous_gray = 0
    hits: list[tuple[int, str]] = []
    start = time.perf_counter()

    for index in range(STATE_COUNT):
        gray = index ^ (index >> 1)
        if index:
            changed = gray ^ previous_gray
            bit = (changed & -changed).bit_length() - 1
            delta = basis[bit]
            for j in range(16):
                current[j] ^= delta[j]
        previous_gray = gray

        candidate = bytes(current[j] ^ mask[j] for j in range(16))
        if hashlib.sha256(candidate).digest() == target:
            hits.append((gray, candidate.hex().upper()))

    return hits, time.perf_counter() - start


def load_source(root: Path) -> tuple[bytes, bytes, bytes, str]:
    res = resource_root(root)
    spool_path = res / "evidence" / "print" / "spool-reconstruction.log"
    spool_bytes = spool_path.read_bytes()
    digest = hashlib.sha256(spool_bytes).hexdigest()
    if digest != SPOOL_SHA256:
        raise ValueError(f"unexpected spool SHA256: {digest}")

    text = spool_bytes.decode("utf-8")
    rows = [line for line in text.splitlines()
            if "JOB=PS-261003-0417" in line
            and "ATTEMPT=2" in line
            and "STATE=ACK" in line
            and "CLASS=RECOVER" in line]
    if len(rows) != 1 or SELECTOR not in rows[0]:
        raise ValueError(f"selected ACK2 row count/selector mismatch: {rows!r}")
    match = re.search(r"\bPAYLOAD=([0-9A-Fa-f]{32})\b", rows[0])
    if not match:
        raise ValueError("selected ACK2 row has no 16-byte payload")
    payload = bytes.fromhex(match.group(1))

    routing = json.loads((res / "evidence" / "recovery-routing.json").read_text())
    acceptance = json.loads((res / "acceptance.json").read_text())
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    if len(payload) != 16 or len(mask) != 16 or len(target) != 32:
        raise ValueError("unexpected K04 field length")
    return payload, mask, target, rows[0]


def run_synthetic_control() -> None:
    synthetic_mask = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    message = bytes.fromhex("0123456789ABCDEF1032547698BADCFE")
    state = SYNTHETIC_STATE

    # Check both inverse directions and both byte-bit serializations.
    for msb in (True, False):
        transmitted = transform(message, state, msb, "scramble")
        recovered = transform(transmitted, state, msb, "descramble")
        assert recovered == message

        received = transform(message, state, msb, "descramble")
        recovered_other_way = transform(received, state, msb, "scramble")
        assert recovered_other_way == message

        # Confirm the 23 basis streams span the direct transform for several states.
        for direction in ("scramble", "descramble"):
            base, basis = output_basis(message, msb, direction)
            for test_state in (0, 1, 2, 3, state, STATE_COUNT - 1, 0x123456):
                predicted = bytearray(base)
                for bit in range(23):
                    if (test_state >> bit) & 1:
                        for j in range(16):
                            predicted[j] ^= basis[bit][j]
                assert bytes(predicted) == transform(message, test_state, msb, direction)

    # Full 2^23 planted positive for the exact same Gray-code search routine.
    scrambled = transform(message, state, True, "scramble")
    expected_component = bytes(a ^ b for a, b in zip(message, synthetic_mask))
    planted_target = hashlib.sha256(expected_component).digest()
    hits, _ = search_variant(scrambled, synthetic_mask, planted_target, True, "descramble")
    assert hits == [(state, expected_component.hex().upper())], hits
    print(f"SYNTHETIC_FULL_POSITIVE_PASS state=0x{state:06X} unique_hit=1")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--variant", choices=(
        "msb-descramble", "lsb-descramble", "msb-scramble", "lsb-scramble"))
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args()

    run_synthetic_control()
    if args.synthetic_only:
        return 0

    payload, mask, target, row = load_source(args.root)
    print(f"SPOOL_SHA256={SPOOL_SHA256}")
    print(f"SELECTOR={row}")
    print(f"PAYLOAD={payload.hex().upper()}")
    print(f"MASK={mask.hex().upper()}")
    print(f"K04_SHA256_TARGET={target.hex()}")
    print(f"STATES_PER_VARIANT={STATE_COUNT}")

    variants = {
        "msb-descramble": (True, "descramble"),
        "lsb-descramble": (False, "descramble"),
        "msb-scramble": (True, "scramble"),
        "lsb-scramble": (False, "scramble"),
    }
    names = [args.variant] if args.variant else list(variants)
    total_hits = 0
    total_seconds = 0.0
    for name in names:
        msb, direction = variants[name]
        hits, seconds = search_variant(payload, mask, target, msb, direction)
        total_hits += len(hits)
        total_seconds += seconds
        print(f"{name}: checks={STATE_COUNT} hits={hits} seconds={seconds:.3f}",
              flush=True)

    print(f"TOTAL_CHECKS={STATE_COUNT * len(names)} TOTAL_HITS={total_hits} "
          f"TOTAL_SECONDS={total_seconds:.3f}")
    return 0 if total_hits == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
