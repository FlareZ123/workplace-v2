"""Independent Boolector QF_BV engine for conditional CPython k2496.

Uses the exact same source-derived initialized-state mask projection as the
Z3 SFT, with selected spool row129 omitted. Exit 0 on complete checked run,
including a clearly reported UNKNOWN when a compute timeout is reached.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile

from k04_cpython_k2496_shortseed_sft import (
    ROOT, SHA, OFFSET, source_states, mt, smt, as_seed, seeded_packets,
)


def boolector_check(formula: str, seconds: int) -> str:
    # The distro CLI auto-detects SMT-LIB2 from the .smt2 extension.
    formula = "\n".join(
        re.sub(r"^\\(declare-const ([^ ]+) (\\(_ BitVec [0-9]+\\))\\)$",
               r"(declare-fun \\1 () \\2)", line)
        for line in formula.splitlines()
        if not line.startswith("(set-option")
    ) + "\n(check-sat)\n"
    with tempfile.TemporaryDirectory(prefix="h17_boolector_") as directory:
        path = Path(directory) / "query.smt2"
        staged = path.with_suffix(".partial")
        staged.write_text(formula, encoding="ascii")
        os.replace(staged, path)
        try:
            run = subprocess.run(
                ["boolector", str(path)],
                capture_output=True, text=True, timeout=seconds, check=False)
        except subprocess.TimeoutExpired:
            return "UNKNOWN_TIMEOUT"
        stdout = run.stdout.strip()
        stderr = run.stderr.strip()
        if run.returncode != 0:
            raise RuntimeError(f"Boolector parse/runtime failure: code={run.returncode} stdout={stdout[:1000]} stderr={stderr[:1000]}")
        if stdout in ("sat", "unsat", "unknown"):
            return stdout.upper()
        raise RuntimeError(f"Boolector unexpected response: {stdout[:2000]} stderr={stderr[:400]}")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("1", "2", "3", "4"):
        raise SystemExit("Supply seed word count 1..4")
    n = int(sys.argv[1])
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    observed = [bytes.fromhex(x.decode("ascii")) for x in
                re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(observed) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    masks = source_states(OFFSET, observed)
    assert sum(mask.bit_count() for mask, _ in masks) == 711

    planted = [(0x12345678 + j * 0x11111111) & 0xffffffff for j in range(n)]
    full = seeded_packets(planted)
    planted_masks = source_states(OFFSET, full)
    assert all(v == (random.Random(as_seed(planted)).getstate()[1][j] & mask)
               for j, (mask, v) in enumerate(planted_masks))
    positive = boolector_check(smt(planted_masks, n, planted), 90)
    assert positive == "SAT", ("synthetic producer", n, positive)
    print("PLANTED_GENUINE_PYTHON_SOURCE_SAT", n, flush=True)

    verdict = boolector_check(smt(masks, n), 900 if n > 1 else 180)
    print("ORIGINAL_SOURCE_BOOLECTOR", "seed_words", n,
          "verdict", verdict, "selected_row_WITHHELD", flush=True)
    if verdict == "SAT":
        print("SAT only for 711 necessary initialized-state bits; no complete source fit or K04 candidate authenticated", flush=True)


if __name__ == "__main__":
    main()
