"""H-17 K04: CPython n=24 byte-seed test at three whole-register startup origins.

These exact prior-output phases (624, 1248, 1872) lie between the earlier
first-register k0..623 and four-register k2496..3119 source studies.
Use the conditional original p951 native MT printer geometry; original
selected ACK2 packet is withheld by the imported source reader. Run once.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent45"))

from k04_source_n24_phase_sweep_sft import (
    genuine_n24_control,
    original_native,
    phase_scan,
)
from k04_k2496_nineteen_term_source_sft import words

PHASES = (624, 1248, 1872)


def main() -> None:
    symbolic = words(max(PHASES))
    original = original_native()
    assert len(original) == 133
    # Each selected source packet is absent from phase_scan by construction.
    results = []
    for phase in PHASES:
        genuine_n24_control(symbolic, phase)
        nterms, npairs, ndisjoint, excluded, sets = phase_scan(
            original, symbolic, phase
        )
        status = "EXCLUDED" if 24 in excluded else "OPEN"
        print(
            "ORIGINAL_N24_INITIAL_REGISTER_ORIGIN",
            f"prior_outputs={phase}",
            f"terms={nterms}",
            f"pairs={npairs}",
            f"disjoint={ndisjoint}",
            f"n24={status}",
            f"open_keylengths_le68={sum(n not in excluded for n in range(1,69))}",
            flush=True,
        )
        results.append((phase, status))
    print("ORIGINAL_PHASE_SUMMARY", results, flush=True)
    assert len(results) == 3


if __name__ == "__main__":
    main()
