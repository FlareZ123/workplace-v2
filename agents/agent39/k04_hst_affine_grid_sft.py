"""Source-only p951 K04: global affine HST4 PV-to-MT32 necessary-condition screen.

Run from repository root: python agents/agent39/k04_hst_affine_grid_sft.py
Printer ACK2 is omitted by the imported source model before basis fitting.
The original K04/K08 commitments and original selected ACK2 payload are not read.
"""
from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent49.k04_p951_symbolic_basis import (
    STARTS, ORIGIN, Basis, source, untemper, temper,
)

PV_HASH = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
BASES = (0, 5000, 10000, 11000, 12000, 13000, 15000, 18000, 20000)
SCALES = (50000, 60000, 65000, 70000, 72000, 75000, 76000, 78000, 80000, 85000, 90000, 100000)


def source_pv():
    data = (ROOT / "resources/evidence/telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PV_HASH
    values = {}
    for line in data.splitlines():
        row = json.loads(line)
        if row["field"] == "PV":
            values[int(row["seq"])] = row
    assert sorted(values) == list(range(100, 212))
    return values


def stage_known(basis, vectors, stage):
    bits = temper(vectors[stage - ORIGIN])
    mask = value = 0
    for j, expr in enumerate(bits):
        predicted = basis.predict(expr)
        if predicted is not None:
            mask |= 1 << j
            value |= predicted << j
    return mask, value


def possible(millivalue, base, scale, mask, known):
    # Necessary interval for round(base + scale*u32/2**32, 3).
    denominator = 2 * scale
    lo = ((2 * millivalue - 1 - 2 * base) * (1 << 32) + denominator - 1) // denominator
    hi = ((2 * millivalue + 1 - 2 * base) * (1 << 32) + denominator - 1) // denominator - 1
    lo = max(0, lo)
    hi = min((1 << 32) - 1, hi)
    if not 0 <= lo <= hi < (1 << 32):
        return False
    common = 32 - (lo ^ hi).bit_length()
    prefix_mask = ((1 << common) - 1) << (32 - common) if common else 0
    return ((lo ^ known) & mask & prefix_mask) == 0


def gap_stages(basis, vectors):
    return [
        [stage_known(basis, vectors, q) for q in range(STARTS[i] + 4, STARTS[i + 1])]
        for i in range(112)
    ]


def original():
    values = source_pv()
    basis, vectors = source(ROOT)
    assert basis.rank == 15365
    positions = gap_stages(basis, vectors)
    assert sum(map(len, positions)) == 389
    assert sum(any(mask for mask, value in row) for row in positions) == 72
    ranked = []
    for base in BASES:
        for scale in SCALES:
            failed = []
            for i in range(112):
                record = values[i + 100]
                milli = round(float(record["value"]) * 1000)
                if not any(possible(milli, base, scale, mask, value)
                           for mask, value in positions[i]):
                    failed.append(i + 100)
            ranked.append((len(failed), base, scale, failed))
    ranked.sort()
    assert len(ranked) == 108
    minimum, base, scale, failed = ranked[0]
    assert minimum == 16
    assert failed == [102, 122, 123, 125, 133, 134, 158, 177, 179, 180, 182, 183, 192, 193, 200, 208]
    assert all(item[0] >= minimum for item in ranked)
    print("ORIGINAL_SOURCE_PV", len(values), "GAP_STAGE_ASSIGNMENTS", sum(map(len, positions)))
    print("GLOBAL_AFFINE_MODELS", len(ranked), "MINIMUM_CONTRADICTED_ROWS", minimum)
    print("BEST_BASE_MILLI", base, "BEST_SCALE_MILLI", scale, "CONTRADICTED_SEQS", failed)
    return vectors


def synthetic(vectors):
    # A true source-consistent MT stream must pass all 112 gap assignments
    # under each exact chosen quantizer, using the same source basis.
    rng = random.Random(0x4A17C9)
    words = [rng.getrandbits(32) for _ in range(967)]
    basis = Basis()
    for i, start in enumerate(STARTS):
        if i == 129:
            continue
        for lane in range(4):
            state = untemper(words[start + lane])
            for j, vector in enumerate(vectors[start + lane - ORIGIN]):
                basis.insert(vector, (state >> j) & 1)
    assert basis.rank == 15365
    positions = gap_stages(basis, vectors)
    for base, scale in ((12000, 76000), (0, 100000), (5000, 85000)):
        for i in range(112):
            m = round(base + scale * words[STARTS[i] + 4] / (1 << 32))
            assert any(possible(m, base, scale, mask, value)
                       for mask, value in positions[i]), (base, scale, i)
        print("SYNTHETIC_KNOWN_EMITTER_PASS", base, scale, "112/112")


if __name__ == "__main__":
    synthetic(original())
