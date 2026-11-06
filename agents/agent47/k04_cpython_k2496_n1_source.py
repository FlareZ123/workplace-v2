"""Source-pinned CPython k2496 one-word inversion witness, read-only.

Uses Agent28's existing exact p951 MT state projector. No selected row129
and no K04 digest enters the fitted source equations. Invoke with optional
original ZIP path; otherwise use repository resources directory.
"""
from __future__ import annotations

import hashlib
import random
import re
import sys
import zipfile
from pathlib import Path

AGENTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTS / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
OFFSET = 2496
S6 = 0xE403BB7D
S7 = 0x1F7B301F
A7 = 0x2AED5290
U = 0xFFFFFFFF


def prefix7(key: int) -> int:
    g = [19650218]
    for i in range(1, 8):
        g.append((1812433253 * (g[-1] ^ (g[-1] >> 30)) + i) & U)
    a = g[0]
    for i in range(1, 8):
        a = ((g[i] ^ ((1664525 * (a ^ (a >> 30))) & U)) + key) & U
    return a


def observable_a7(s6: int, s7: int) -> int:
    return ((s7 + 7) & U) ^ ((1566083941 * (s6 ^ (s6 >> 30))) & U)


def planted_packets(seed: int) -> list[bytes]:
    rng = random.Random(seed)
    words = [rng.getrandbits(32) for _ in range(OFFSET + max(mt.STARTS) + 4)]
    return [b"".join(words[OFFSET + p + j].to_bytes(4, "little") for j in range(4))
            for p in mt.STARTS]


def main(path: str | None) -> None:
    if path:
        with zipfile.ZipFile(path) as z:
            spool = z.read("evidence/print/spool-reconstruction.log")
    else:
        spool = (Path(__file__).resolve().parents[2] /
                 "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    rows = [bytes.fromhex(b.decode()) for b in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(rows) == len(mt.STARTS) == 133
    assert mt.STARTS[129] == 951

    synthetic_seed = 0x12345678
    guessed = source_states(OFFSET, planted_packets(synthetic_seed))
    true_state = random.Random(synthetic_seed).getstate()[1][:624]
    assert all(v == (m & full) for (m, v), full in zip(guessed, true_state))
    assert guessed[6] == (U, true_state[6]) and guessed[7] == (U, true_state[7])
    assert observable_a7(true_state[6], true_state[7]) == prefix7(synthetic_seed)
    print("GENUINE_CPYTHON_K2496_SOURCE_POSITIVE=PASS")

    original = source_states(OFFSET, rows)
    assert original[6] == (U, S6) and original[7] == (U, S7)
    assert observable_a7(S6, S7) == A7
    print("ORIGINAL_SELECTED_WITHHELD_SOURCE",
          "S6", f"{S6:08X}", "S7", f"{S7:08X}", "A7", f"{A7:08X}")
    print("EXHAUSTIVE_ONEWORD_INVERSION",
          "see agents/agent47/k04_cpython_k2496_n1_fullseed_sft.cpp")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
