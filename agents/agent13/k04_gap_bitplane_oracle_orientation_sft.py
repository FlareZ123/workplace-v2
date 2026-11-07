"""Original H-17 K04 alternate perfect-gap-bitplane bounds.

This is a mathematical information-oracle experiment, not observed historical
metadata. The copied selected row129 is withheld entirely by source().
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "agents" / "agent49" / "k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("original_mt_source", FIXTURE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def insert(rows, vector):
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in rows:
            rows[pivot] = vector
            return 1
        vector ^= rows[pivot]
    return 0


def free_target(rows, target):
    test = rows.copy()
    return sum(insert(test, vector) for vector in target)


def oracle(source_rows, gapwords, target, positions):
    rows = source_rows.copy()
    records = {}
    for count, pos in enumerate(positions, 1):
        for word in gapwords:
            insert(rows, word[pos])
        records[count] = free_target(rows, target)
    return records, len(rows) - len(source_rows)


def main():
    observed, stream = model.source(ROOT / "resources")
    source = {p: vector for p, (vector, _) in observed.rows.items()}
    target = [bit for stage in range(951, 955)
              for bit in model.get(stream, stage)]
    assert len(source) == 15365 and free_target(source, target) == 128
    stages = [pos for i in range(127)
              for pos in range(model.STARTS[i] + 4, model.STARTS[i + 1])]
    assert len(stages) == 434
    gapwords = [model.temper(model.get(stream, pos)) for pos in stages]
    orders = {
        "highest_first": list(range(31, -1, -1)),
        "lowest_first": list(range(32)),
        "midpoint_first": sorted(range(32), key=lambda j: abs(j - 15.5)),
        "byte_0_only": list(range(0, 8)),
        "byte_1_only": list(range(8, 16)),
        "byte_2_only": list(range(16, 24)),
        "byte_3_only": list(range(24, 32)),
    }
    expected = {
        "highest_first": {8: 128, 12: 128, 15: 128, 16: 127, 20: 95, 24: 63, 28: 31, 32: 0},
        "lowest_first": {8: 128, 12: 128, 15: 128, 16: 127, 20: 95, 24: 63, 28: 31, 32: 0},
        "midpoint_first": {8: 128, 12: 124, 15: 115, 16: 115, 20: 95, 24: 63, 28: 31, 32: 0},
        "byte_0_only": {8: 128},
        "byte_1_only": {8: 127},
        "byte_2_only": {8: 128},
        "byte_3_only": {8: 128},
    }
    for title, positions in orders.items():
        observations, rank_gain = oracle(source, gapwords, target, positions)
        for count, dimension in expected[title].items():
            assert observations[count] == dimension, (title, count, observations[count])
        print(title, "equation_rank_gain", rank_gain,
              "remaining_at_8", observations[8],
              "remaining_at_12", observations.get(12, "-"),
              "remaining_at_15", observations.get(15, "-"),
              "remaining_at_16", observations.get(16, "-"),
              "remaining_at_32", observations.get(32, "-"))

    donors = (328, 329, 330, 331, 724, 725, 726, 727)
    for name, selected in (
        ("full_words", range(32)),
        ("lower_halfwords", range(16)),
        ("upper_halfwords", range(16, 32)),
    ):
        rows = source.copy()
        for stage in donors:
            for bit in selected:
                insert(rows, model.get(stream, stage)[bit])
        remaining = free_target(rows, target)
        assert remaining == (0 if name == "full_words" else 68)
        print(name, "source-rank-gain", len(rows) - len(source),
              "selected-free-dimensions", remaining)
    print("ALL_ORIGINAL_SOURCE_ONLY_ORACLE_BOUNDS_PASS",
          "source_rank", observed.rank, "selected_physical_bits_authenticated", 0)


if __name__ == "__main__":
    main()
