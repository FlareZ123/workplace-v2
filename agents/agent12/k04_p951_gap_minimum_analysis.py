"""Reproduce the minimum p951 gap-word set that makes K04 observable.

Run from any directory. Uses Agent49's source-only printer basis; performs no
writes. The search treats each candidate stage as one complete 32-bit native state word.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.agent49.k04_p951_symbolic_basis import ORIGIN, STARTS, source


GAP43_STAGES = tuple(range(328, 335))
GAP96_STAGES = tuple(range(721, 729))
TARGET_STAGES = tuple(range(STARTS[129], STARTS[129] + 4))
CANDIDATE_STAGES = GAP43_STAGES + GAP96_STAGES


class CoefficientSpan:
    def __init__(self) -> None:
        self.rows: dict[int, int] = {}

    def insert(self, vector: int) -> None:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = vector
                return
            vector ^= self.rows[pivot]

    def contains(self, vector: int) -> bool:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in self.rows:
                return False
            vector ^= self.rows[pivot]
        return True


def reduce_by_base(vector: int, base_rows: dict[int, int]) -> int:
    residual = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot in base_rows:
            vector ^= base_rows[pivot]
        else:
            residual |= 1 << pivot
            vector ^= 1 << pivot
    return residual


def main() -> None:
    basis, state = source(REPO_ROOT)
    base_rows = {pivot: row[0] for pivot, row in basis.rows.items()}

    target = [
        reduce_by_base(form, base_rows)
        for stage in TARGET_STAGES
        for form in state[stage - ORIGIN]
    ]
    gap_forms = {
        stage: [
            reduce_by_base(form, base_rows)
            for form in state[stage - ORIGIN]
        ]
        for stage in CANDIDATE_STAGES
    }

    print(f"base_rank={basis.rank}")
    print(f"target_bits={len(target)}")
    print(f"candidate_stages={CANDIDATE_STAGES}")

    for size in range(1, len(CANDIDATE_STAGES) + 1):
        solutions = []
        for subset in combinations(CANDIDATE_STAGES, size):
            span = CoefficientSpan()
            for stage in subset:
                for form in gap_forms[stage]:
                    span.insert(form)
            if all(span.contains(form) for form in target):
                solutions.append(subset)
        if solutions:
            print(f"minimum_fullword_count={size}")
            print(f"solutions={solutions}")
            return

    raise AssertionError("No candidate subset made the selected 128-bit payload observable")


if __name__ == "__main__":
    main()
