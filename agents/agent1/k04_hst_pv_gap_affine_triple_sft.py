"""H-17: exact historian PV -> matched-job printer MT gap falsifier.
Read-only standard-library SFT, Windows 11 compatible.
Based on Agent49's independently source-pinned symbolic printer basis.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

HST_PIN = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"


def u_first_word_bounds(basis: mt.Basis, symbolic_words: list, pos: int) -> tuple[float, float, int]:
    """Safe bounds for ((MT32[pos]>>5)*2^26+MT32[pos+1]>>6)/2^53.

    Unknown source bits are assigned both extremes; second MT output is
    conservatively left completely unknown. These are over-approximations.
    """
    word = mt.temper(mt.get(symbolic_words, pos))
    bits = [basis.predict(v) for v in word[5:]]
    low = sum((int(bit) if bit is not None else 0) << i for i, bit in enumerate(bits))
    high = sum((int(bit) if bit is not None else 1) << i for i, bit in enumerate(bits))
    return low / (1 << 27), (high + 1) / (1 << 27), sum(bit is not None for bit in bits)


def pv_highword_mask(m: int) -> tuple[int, int]:
    """Fixed high bits of MT32[pos] required by round(12+76*U53,3)."""
    lo_n, hi_n = 2 * m - 24001, 2 * m - 23999
    lo = max(0, (lo_n * (1 << 53) + 151999) // 152000)
    hi = min(1 << 53, (hi_n * (1 << 53) + 151999) // 152000)
    assert 0 <= lo < hi <= 1 << 53
    common = ((1 << 53) - 1) ^ ((1 << (lo ^ (hi - 1)).bit_length()) - 1)
    return (common >> 26) << 5, (lo >> 26) << 5


def main() -> None:
    blob = (ROOT / "resources" / "evidence" / "telemetry" / "freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == HST_PIN
    pv = {row["seq"]: row for row in (json.loads(line) for line in blob.splitlines())
          if row["field"] == "PV"}
    assert set(pv) == set(range(100, 212))
    basis, symbolic = mt.source(ROOT)  # withholds selected copied row129
    assert basis.rank == 15365
    assert len(mt.STARTS) == 133
    assert all((mt.STARTS[i + 1] - mt.STARTS[i]) >= 6 for i in range(112))

    # First 112 printer job numbers 0300..0411 map arithmetically
    # onto HST sequence numbers 100..211 via job_suffix=seq+200.
    records = []
    for seq, pos in ((133, 248), (180, 606), (211, 835)):
        row = pv[seq]
        assert row["quality"] == "GOOD" and row["tag"] == "FT-13" and row["unit"] == "degC"
        assert mt.STARTS[seq - 100] + 4 == pos
        assert mt.STARTS[seq - 100 + 1] - pos == 2, seq  # single possible two-word float start
        low, high, n = u_first_word_bounds(basis, symbolic, pos)
        assert n == 27 and high - low <= 1 / (1 << 27) + 1e-14
        records.append((seq, pos, row["value"], low, high, n))

    ordered = sorted(records, key=lambda r: r[3])
    assert [r[0] for r in ordered] == [211, 133, 180]
    assert all(ordered[i][4] < ordered[i + 1][3] for i in (0, 1))
    assert [r[2] for r in ordered] == [67.218, 25.557, 65.433]

    # Any real affine y=A+B*U is monotone (either slope sign).
    # Rounding to .001 cannot reverse 40+ or 1+ degree differences.
    assert ordered[0][2] > ordered[1][2] + 0.001
    assert ordered[2][2] > ordered[1][2] + 0.001
    planted = [round(12 + 76 * row[3], 3) for row in ordered]
    assert planted == sorted(planted) and len(set(planted)) == 3
    print("GLOBAL_AFFINE_REJECTED three_original_GOOD_FT13_degC=", ordered)
    print("PLANTED_SOURCE_AFFINE_ORDER_POSITIVE", planted)

    original_valid = 0
    zero_rows = []
    good_zeros = []
    all_stages = 0
    synthetic_positives = 0
    for i in range(112):
        seq = 100 + i
        row = pv[seq]
        m = int(round(1000 * row["value"]))
        mask, value = pv_highword_mask(m)
        survivors = 0
        for pos in range(mt.STARTS[i] + 4, mt.STARTS[i + 1] - 1):
            all_stages += 1
            predicted = mt.temper(mt.get(symbolic, pos))
            known = [basis.predict(bit) for bit in predicted]
            if all((known[j] is None or known[j] == (value >> j) & 1)
                   for j in range(32) if mask >> j & 1):
                survivors += 1
        if survivors == 0:
            zero_rows.append(seq)
            if row["quality"] == "GOOD":
                good_zeros.append(seq)
        else:
            original_valid += 1
    assert all_stages == 277
    assert len(zero_rows) == 29
    assert original_valid == 83
    print("FIXED_12_76_ROUNDED source_positions", all_stages,
          "rows_with_some_consistent_gap", original_valid,
          "rows_with_zero", len(zero_rows),
          "GOOD_rows_with_zero", len(good_zeros),
          "zero_good_seq", good_zeros)
    print("ORIGINAL_K04_COMPONENT_NOT_RECOVERED")


if __name__ == "__main__":
    main()
