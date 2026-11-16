"""H-17 K04: ITU V.27ter x^-6+x^-7 seven-bit scrambler-core SFT.

Read-only: verifies official source digests, tests the complete bounded
core polynomial family against the untouched K04 commitment, and checks
a planted full-coupon positive.  Does not implement V.27ter guard circuitry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

EXPECTED_SHA256 = {
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
    "evidence/crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
}
TARGET_LINE = re.compile(
    r"^2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 "
    r"STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=bench$",
)


def bits_from_bytes(raw: bytes, msb_first: bool) -> list[int]:
    positions = range(7, -1, -1) if msb_first else range(8)
    return [(byte >> bit) & 1 for byte in raw for bit in positions]


def bytes_from_bits(bits: list[int], msb_first: bool) -> bytes:
    assert len(bits) == 128
    return bytes(
        sum(bits[8 * i + j] << (7 - j if msb_first else j) for j in range(8))
        for i in range(16)
    )


def v27_core(bits: list[int], history: int, descramble: bool) -> list[int]:
    """Polynomial 1+x^-6+x^-7 with an arbitrary seven-bit prior history."""
    prior = [(history >> j) & 1 for j in range(7)]
    if descramble:
        received = prior + bits
        return [
            b ^ received[i + 1] ^ received[i] for i, b in enumerate(bits)
        ]
    transmitted = prior.copy()
    out: list[int] = []
    for b in bits:
        emitted = b ^ transmitted[-6] ^ transmitted[-7]
        out.append(emitted)
        transmitted.append(emitted)
    return out


def has_45_bit_periodic_guard_sequence(bits: list[int]) -> bool:
    """Necessary detectable 45-bit periodicity used by V.27 guard checks."""
    for stop in range(45, len(bits) + 1):
        for period in (9, 12):
            if all(bits[j] == bits[j + period]
                   for j in range(stop - 45, stop - period)):
                return True
    return False


def run(source: dict[str, bytes]) -> dict[str, object]:
    for name, expected in EXPECTED_SHA256.items():
        actual = hashlib.sha256(source[name]).hexdigest()
        assert actual == expected, f"{name}: source mismatch"
    assert "N22 / Simon" in source["evidence/crew/noticeboard-and-desk-notes.txt"].decode()
    assert "thinking it is a fax machine" in source[
        "evidence/crew/noticeboard-and-desk-notes.txt"
    ].decode()
    matches = [
        TARGET_LINE.fullmatch(line)
        for line in source["evidence/print/spool-reconstruction.log"].decode().splitlines()
    ]
    selected = [match for match in matches if match is not None]
    assert len(selected) == 1
    copied = bytes.fromhex(selected[0].group(1))
    routing = json.loads(source["evidence/recovery-routing.json"])
    acceptance = json.loads(source["acceptance.json"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]

    for order in (True, False):
        original = bits_from_bytes(copied, order)
        assert bytes_from_bits(original, order) == copied
        for history in (0, 42, 127):
            transmitted = v27_core(original, history, False)
            assert v27_core(transmitted, history, True) == original

    planted = bytes(
        x ^ y for x, y in zip(
            bytes_from_bits(v27_core(bits_from_bytes(copied, True), 93, True), True),
            mask,
        )
    )
    planted_digest = hashlib.sha256(planted).hexdigest()
    original_hits: list[dict[str, object]] = []
    planted_hits: list[dict[str, object]] = []
    guard_window_count = 0
    attempts = 0
    for order in (True, False):
        input_bits = bits_from_bytes(copied, order)
        for descramble in (True, False):
            for history in range(128):
                result_bits = v27_core(input_bits, history, descramble)
                result = bytes_from_bits(result_bits, order)
                component = bytes(a ^ b for a, b in zip(result, mask))
                digest = hashlib.sha256(component).hexdigest()
                descriptor: dict[str, object] = {
                    "msb_first": order, "descramble": descramble,
                    "history": history,
                }
                if digest == target:
                    original_hits.append({**descriptor, "component_hex": component.hex().upper()})
                if digest == planted_digest:
                    planted_hits.append(descriptor)
                prior = [(history >> j) & 1 for j in range(7)]
                bit_stream = prior + (input_bits if descramble else result_bits)
                if has_45_bit_periodic_guard_sequence(bit_stream):
                    guard_window_count += 1
                attempts += 1

    assert attempts == 512
    assert planted_hits == [{"msb_first": True, "descramble": True, "history": 93}]
    assert original_hits == []
    assert guard_window_count == 0
    return {
        "model": "ITU V.27ter seven-bit unguarded self-synchronizing polynomial core",
        "source_checks_passed": len(EXPECTED_SHA256),
        "complete_original_commitment_checks": attempts,
        "original_matches": original_hits,
        "synthetic_planted_complete_coupon_matches": len(planted_hits),
        "synthetic_inverse_controls": 6,
        "detectable_45bit_guard_periodic_windows": guard_window_count,
        "scope": "no pre-window guard effects or independent native physical coupon",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, help="Path to original h17-archive-dump.zip")
    args = parser.parse_args()
    if args.archive is None:
        root = Path(__file__).resolve().parents[2] / "resources"
        files = {name: (root / name).read_bytes() for name in EXPECTED_SHA256}
    else:
        with zipfile.ZipFile(args.archive) as archive:
            files = {name: archive.read(name) for name in EXPECTED_SHA256}
    print(json.dumps(run(files), indent=2))


if __name__ == "__main__":
    main()
