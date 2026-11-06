"""Original-source-only MT19937 hidden-output bitplane information test.

Tests whether *hypothetical* exact middle16 bits of unprinted tempered
MT outputs intersect the omitted ESC-N K04 coupon quotient. No original
coupon, copied selected payload, K04 commitment or route mask is read.
The p951 chronology/PRNG is speculative and not historical attestation.

Run from repository root: python agents/agent23/k04_middle_tempered_oracle_sft.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import ORIGIN, STARTS, source, temper


class Rank:
    def __init__(self, pivot_rows=None):
        self.rows = {} if pivot_rows is None else dict(pivot_rows)
        self.rank = len(self.rows)

    def add(self, v):
        while v:
            index = v.bit_length() - 1
            old = self.rows.get(index)
            if old is None:
                self.rows[index] = v
                self.rank += 1
                return
            v ^= old

    def extend(self, vectors):
        for vector in vectors:
            self.add(vector)


def rank_with_oracle(base, source_bits, target_bits):
    b = Rank(base)
    b.extend(source_bits)
    observed_rank = b.rank
    b.extend(target_bits)
    return observed_rank, b.rank - observed_rank


def main():
    basis, symbols = source(ROOT / "resources")
    assert basis.rank == 15365
    source_basis = {index: row[0] for index, row in basis.rows.items()}
    observed = {start + lane for row, start in enumerate(STARTS)
                if row != 129 for lane in range(4)}
    selected = set(range(951, 955))
    assert STARTS[129] == 951 and selected.isdisjoint(observed)
    target = [bit for stage in sorted(selected)
              for bit in temper(symbols[stage - ORIGIN])]
    native_target_rank, native_target_residual = rank_with_oracle(
        source_basis, (), target)
    assert native_target_rank == 15365 and native_target_residual == 128

    hidden = [stage for stage in range(STARTS[0], STARTS[-1] + 4)
              if stage not in observed and stage not in selected]
    assert len(hidden) == 435
    assert all(stage in hidden for stage in
               (328, 329, 330, 331, 724, 725, 726, 727))
    tempered = {stage: temper(symbols[stage - ORIGIN]) for stage in hidden}
    critical = (328, 329, 330, 331, 724, 725, 726, 727)

    def run(stages, low, high):
        equations = (tempered[stage][bit]
                     for stage in stages for bit in range(low, high))
        return rank_with_oracle(source_basis, equations, target)

    checks = {
        "all_tempered_low12": run(hidden, 0, 12),
        "all_tempered_high12": run(hidden, 20, 32),
        "all_tempered_mid16": run(hidden, 8, 24),
        "critical8_tempered_mid16": run(critical, 8, 24),
        "critical_early4_tempered_mid16": run(critical[:4], 8, 24),
        "critical_late4_tempered_mid16": run(critical[4:], 8, 24),
        "critical8_tempered_low16": run(critical, 0, 16),
        "critical8_tempered_high16": run(critical, 16, 32),
    }
    assert checks == {
        "all_tempered_low12": (18203, 128),
        "all_tempered_high12": (18203, 128),
        "all_tempered_mid16": (18820, 115),
        "critical8_tempered_mid16": (15493, 116),
        "critical_early4_tempered_mid16": (15429, 128),
        "critical_late4_tempered_mid16": (15429, 128),
        "critical8_tempered_low16": (15493, 127),
        "critical8_tempered_high16": (15493, 127),
    }, checks

    # Distinguish the bare MT recurrence from additional original-source
    # constraints: these observations alone transmit 11 target equations.
    no_source_critical = rank_with_oracle(
        {}, (tempered[stage][bit] for stage in critical
             for bit in range(8, 24)), target)
    no_source_full = rank_with_oracle(
        {}, (tempered[stage][bit] for stage in hidden
             for bit in range(8, 24)), target)
    assert no_source_critical == (128, 117), no_source_critical
    assert no_source_full == (6889, 117), no_source_full

    # A planted 8-bit observation of each genuinely selected output word
    # must remove exactly 32 of its 128 independent dimensions.
    planted = []
    for stage in sorted(selected):
        planted.extend(temper(symbols[stage - ORIGIN])[:8])
    assert rank_with_oracle(source_basis, planted, target) == (15397, 96)

    print(json.dumps({
        "source_rank": basis.rank,
        "intact_source_packets": 132,
        "source_hidden_unprinted_stages": len(hidden),
        "selected_without_oracle": native_target_residual,
        "oracle_rank_and_target_residual": checks,
        "unassisted_MT_critical8_rank_residual": no_source_critical,
        "unassisted_MT_full435_rank_residual": no_source_full,
        "planted_target_byte_control": "PASS",
        "original_coupon_or_K04_commitment_loaded": False,
        "historical_selected_coupon_bits_authenticated": 0
    }, indent=2))


if __name__ == "__main__":
    main()
