"""Original-source, low-affine-rank 53-bit telemetry/MT carrier scan.

Unlike bitwise fixed-mask screens, this enumerates every affine output state
where the full local quotient rank is <=9. This can find narrow original
float witnesses even if no individual output bit is fixed by the spool.
The selected coupon and both missing acceptance commitments are excluded.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources"
MODEL = ROOT / "agents/agent4/k04_mt_full_state_gf2.py"
HIST = SOURCE / "evidence/telemetry/freeze-export.jsonl"
HIST_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
SCALE = 1 << 53


def model_state():
    spec = importlib.util.spec_from_file_location("original_source_mt", MODEL)
    assert spec and spec.loader
    mt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mt)
    mt.START, mt.STOP = -3000, 2000
    words = mt.symbolic_words()
    basis = mt.Basis()
    for stage, actual in mt.printer_observations(SOURCE):
        basis.add_word(words[stage - mt.START], actual)
    assert len(basis.rows) == 15365
    assert mt.target_quotient(basis, words) == 128
    return mt, words, basis


def affine_values(forms, basis, max_rank=9):
    local = {}
    columns = []
    base = 0
    for bit, expression in enumerate(forms):
        coefficient = constant = 0
        while expression:
            pivot = expression.bit_length() - 1
            if pivot in basis.rows:
                expression ^= basis.rows[pivot]
                constant ^= basis.values[pivot]
            elif pivot in local:
                row, vector = local[pivot]
                expression ^= row
                coefficient ^= vector
            else:
                if len(columns) >= max_rank:
                    return None
                local[pivot] = (expression, 1 << len(columns))
                columns.append(0)
                coefficient ^= 1 << (len(columns) - 1)
                expression = 0
        if constant:
            base |= 1 << bit
        for index in range(len(columns)):
            if coefficient >> index & 1:
                columns[index] |= 1 << bit
    return base, columns


def float_milli(fraction53):
    return (12000 * SCALE + 76000 * fraction53 + SCALE // 2) // SCALE


def interval(milli):
    ceil = lambda a, b: -((-a) // b)
    lo = ceil((2 * milli - 24001) * SCALE, 152000)
    hi = ceil((2 * milli - 23999) * SCALE, 152000) - 1
    return max(0, lo), min(SCALE - 1, hi)


def main():
    raw = HIST.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HIST_SHA
    rows = [
        json.loads(line) for line in raw.splitlines()
        if json.loads(line)["field"] == "PV"
    ]
    by_value = defaultdict(list)
    for row in rows:
        by_value[round(row["value"] * 1000)].append(row["seq"])
    assert len(rows) == 112 and sorted(row["seq"] for row in rows) == list(range(100, 212))

    seed = random.Random(90314)
    for _ in range(64):
        v = seed.getrandbits(53)
        milli = float_milli(v)
        lo, hi = interval(milli)
        assert lo <= v <= hi
    print("Planted seeded exact 53-bit rounding/interval controls: PASS 64")

    mt, words, basis = model_state()
    stages = Counter()
    indexed = defaultdict(list)
    evaluated = 0
    for stage in range(mt.START, mt.STOP):
        first = mt.tempered_bits(words[stage - mt.START])
        second = mt.tempered_bits(words[stage + 1 - mt.START])
        output = affine_values(second[6:] + first[5:], basis)
        if output is None:
            continue
        baseline, columns = output
        rank = len(columns)
        stages[rank] += 1
        values = [baseline]
        for column in columns:
            values.extend(x ^ column for x in values[:])
        evaluated += len(values)
        for n in values:
            milli = float_milli(n)
            for seq in by_value.get(milli, ()):
                indexed[(seq, stage)].append(n)

    expected = {0: 857, 1: 239, 2: 131, 3: 67, 4: 67, 5: 42,
                6: 42, 7: 15, 8: 10, 9: 5}
    assert dict(stages) == expected, stages
    assert sum(stages.values()) == 1475 and evaluated == 14539
    observed = {
        (seq, stage): len(values)
        for (seq, stage), values in indexed.items()
    }
    assert observed == {(175, -1567): 1, (176, -1560): 8,
                        (177, -1553): 8, (198, 17): 1}, observed
    triples = []
    for (seq, stage) in observed:
        for stride in range(3, 15):
            if (seq + 1, stage + stride) in observed and (
                    seq + 2, stage + 2 * stride) in observed:
                triples.append((seq, stage, stride))
    assert triples == [(175, -1567, 7)], triples

    print("Original known rank<=9 native stages", sum(stages.values()))
    print("Complete hypothetical 53-bit outputs enumerated", evaluated)
    print("Source-compatible original (seq,stage):", observed)
    print("Consecutive three-PV stage witnesses", triples)
    print("Conditional order-permutation probability: 1/(112*111)")
    print("Selected K04 quotient 128/128 remains unknown; K08 not recovered")


if __name__ == "__main__":
    main()
