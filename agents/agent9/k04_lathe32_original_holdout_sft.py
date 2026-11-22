"""H-17 K04: source-pinned whole-packet Lathe32RNG original holdout SFT.

Requires separately compiled k04_lathe32_64bit_complete_inverse.cpp executable.
Reads original archive evidence only; selected ACK2 row is not consulted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STATES = 1 << 32
PLANTED = ("2A0CC406", "8D47BBA1", "F9DEA1FD", "BC1D55D2")


def invert(executable: Path, words: tuple[int, int, int, int], threads: int) -> dict:
    result = subprocess.run(
        [str(executable), *(f"{w:08X}" for w in words), str(threads), "0"],
        capture_output=True,
        text=True,
        check=True,
    )
    counts = dict(
        (name, int(value))
        for name, value in re.findall(
            r"(tested|prefix2_states|heldout_word2|heldout_word3)=(\d+)",
            result.stdout,
        )
    )
    if counts["tested"] != STATES:
        raise RuntimeError(f"Incomplete state enumeration: {counts}")
    return counts | {"matched_states": re.findall(
        r"FULL_PACKET_MATCH_STATE a=([0-9A-F]{8}) b=([0-9A-F]{8})", result.stdout
    )}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    options = parser.parse_args()
    original = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_SHA:
        raise ValueError("Original spool SHA256 pin mismatch")
    source = original.decode("utf-8")
    lines = [
        row for row in source.splitlines()
        if "ATTEMPT=1 STATE=ACK " in row
        and re.search(r"\bJOB=PS-261003-03\d\d\b", row)
    ]
    if len(lines) < 5:
        raise ValueError("Insufficient original intact records")

    positive = invert(options.executable, tuple(int(x, 16) for x in PLANTED), options.threads)
    assert positive["heldout_word2"] == positive["heldout_word3"] == 1
    assert ("C0FFEE17", "BADA551E") in positive["matched_states"]
    print(json.dumps({"stage": "synthetic", "state_recovery": "PASS", "data": positive}), flush=True)

    matched = 0
    prefix = 0
    for row in lines[:5]:
        packet = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", row).group(1))
        job = re.search(r"JOB=(PS-261003-\d+)", row).group(1)
        for endian in ("big", "little"):
            native = [int.from_bytes(packet[k:k+4], endian) for k in range(0, 16, 4)]
            for reversed_order in (False, True):
                words = tuple(native[::-1] if reversed_order else native)
                counts = invert(options.executable, words, options.threads)
                matched += counts["heldout_word3"]
                prefix += counts["prefix2_states"]
                print(json.dumps({"job": job, "endian": endian,
                    "reverse": reversed_order, "state_candidates": counts}), flush=True)

    total = 20 * STATES
    print(json.dumps({
        "COMPLETE": True, "tested_packets": 5, "tested_views": 20,
        "total_exact_64bit_state_assignments": total,
        "recovered_two_word_state_candidates": prefix,
        "complete_original_packet_matches": matched,
    }), flush=True)
    # Separate same-class exceptional ACK2 control: WATCH-SPARE, not ESC-N.
    watch = next(
        row for row in source.splitlines()
        if "JOB=PS-261003-0420 " in row
        and "ATTEMPT=2 STATE=ACK CLASS=RECOVER" in row
    )
    watch_packet = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", watch).group(1))
    watch_prefix = 0
    watch_matches = 0
    for endian in ("big", "little"):
        native = [int.from_bytes(watch_packet[k:k+4], endian) for k in range(0, 16, 4)]
        for reversed_order in (False, True):
            words = tuple(native[::-1] if reversed_order else native)
            counts = invert(options.executable, words, options.threads)
            watch_prefix += counts["prefix2_states"]
            watch_matches += counts["heldout_word3"]
            print(json.dumps({"job": "PS-261003-0420", "attempt": 2,
                "endian": endian, "reverse": reversed_order,
                "state_candidates": counts}), flush=True)
    print(json.dumps({"watch_spare_original": True, "views": 4,
        "exact_state_assignments": 4 * STATES,
        "two_word_states": watch_prefix, "full_fourword_matches": watch_matches,
        "grand_total_assignments": 24 * STATES}), flush=True)
    assert matched == 0 and watch_matches == 0


if __name__ == "__main__":
    main()
