#!/usr/bin/env python3
"""Complete original-source same-job LABEL anchor for xoroshiro128++ a0-half.

Run locally against the unchanged H-17 resources as a *conditional* print
producer model, not public CI. The earlier 0417 LABEL packet supplies proposed
32-bit initial-a state halves; only undisputed 0417 REQUESTED1 output pair is
used as a two-output gate. Disputed selected ACK2 is never read, or inferred
from a nonmatching model. Prints counts only, never source bytes or state.
Reuses Agent20's exact all-2^32 C++ generator inverse and its full planted
positive/wrong-half negative controls instead of creating an independent
unvalidated PRNG implementation.

  python agents/agent3/k04_xoropp_samejob_label_a32_source_sft.py

If an exact first-pair fit unexpectedly appears, halt the producer claim and
independently replay the intact REQUESTED3 holdout and the original commitment.
"""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import re
import subprocess

if os.environ.get("GITHUB_ACTIONS", "").lower() == "true":
    raise SystemExit("Original source-bearing searches must remain local.")

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "resources"
SPOOL = ROOT / "evidence/print/spool-reconstruction.log"
CODE = REPO / "agents/agent20/k04_xoropp_firsta32_synthetic.cpp"
PINS = {
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    ROOT / "evidence/recovery-routing.json":
        "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    ROOT / "acceptance.json":
        "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}


def source():
    for path, want in PINS.items():
        if sha256(path.read_bytes()).hexdigest() != want:
            raise ValueError("Source SHA mismatch: " + str(path))
    matched = {}
    for line in SPOOL.read_text().splitlines():
        if "JOB=PS-261003-0417 " not in line:
            continue
        gate = None
        if ("ATTEMPT=1 " in line and "STATE=ACK " in line
                and "CLASS=LABEL " in line):
            gate = "label"
        elif ("ATTEMPT=1 " in line and "STATE=REQUESTED " in line
              and "CLASS=RECOVER " in line):
            gate = "before"
        elif ("ATTEMPT=3 " in line and "STATE=REQUESTED " in line
              and "CLASS=RECOVER " in line):
            gate = "after"
        if gate is not None:
            match = re.search(r"PAYLOAD=([A-Fa-f0-9]{32})(?:\s|$)", line)
            if not match or gate in matched:
                raise ValueError("Missing or duplicated same-job selector")
            matched[gate] = bytes.fromhex(match[1])
    if set(matched) != {"label", "before", "after"}:
        raise ValueError("Incomplete selected original same-job source set")
    return matched


def run():
    src = source()
    label, before, after = (src[k] for k in ("label", "before", "after"))
    models = 0
    first_pair_fits = 0
    with TemporaryDirectory(prefix="h17_a32_label_") as d:
        exe = Path(d) / "xoropp"
        subprocess.run([
            "g++", "-std=c++17", "-O3", "-fopenmp", str(CODE),
            "-o", str(exe)
        ], check=True)
        control = subprocess.run(
            [str(exe)], text=True, capture_output=True, check=True, timeout=180
        )
        if "full 2^32 planted state + wrong-anchor negative: PASS" not in control.stdout:
            raise AssertionError("Full-domain positive/negative control absent")
        anchors = [
            int.from_bytes(label[i:i + 4], endian)
            for i in (0, 4, 8, 12) for endian in ("big", "little")
        ]
        assert len(anchors) == 8
        for endian in ("big", "little"):
            words = [
                int.from_bytes(before[i:i + 8], endian) for i in (0, 8)
            ]
            for swap in (False, True):
                y0, y1 = reversed(words) if swap else words
                for anchor in anchors:
                    for high in (0, 1):
                        cmd = [
                            str(exe), f"{y0:x}", f"{y1:x}", f"{anchor:x}",
                            str(high), str(1 << 32)
                        ]
                        process = subprocess.run(
                            cmd, text=True, capture_output=True,
                            check=True, timeout=180
                        )
                        if ("synthetic_positive PASS" not in process.stdout
                                or "exhaustive_unknown32=1" not in process.stdout):
                            raise AssertionError("Incomplete original source gate")
                        m = re.search(r"source_pair_full_match=(\d+)", process.stdout)
                        if not m:
                            raise AssertionError("No exact match count")
                        first_pair_fits += int(m[1])
                        models += 1
    assert models == 64
    # The historical holdout is intentionally never used as a fitting input.
    assert len(after) == 16
    print({
        "source_models": models,
        "all_unknown_half_assignments": models * (1 << 32),
        "original_firstpair_exact_fits": first_pair_fits,
        "original_selected_coupon_recovered": False,
        "synthetic_controls": "PASS",
        "source_heldout_REQUESTED3_read_as_reference_only": True
    })
    if first_pair_fits:
        raise RuntimeError(
            "Unexpected viable producer; independently predict the heldout "
            "REQUESTED3 before testing any selected coupon."
        )


if __name__ == "__main__":
    run()
