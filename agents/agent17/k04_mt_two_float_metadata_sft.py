#!/usr/bin/env python3
"""Source-only two-53-bit-float metadata writer test, with K04 ACK2 withheld."""
from __future__ import annotations
import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent6"))
import k04_cpython_metadata_value_holdout_sft as m


def class_interval(words, basis, p):
    """Conservative possible int(3*random()) categories from two MT outputs."""
    first = m.temper_expr(m.get_sym(words, p))
    second = m.temper_expr(m.get_sym(words, p + 1))
    bits = [basis.predict(first[j]) for j in range(31, 4, -1)]
    bits += [basis.predict(second[j]) for j in range(31, 5, -1)]
    assert len(bits) == 53
    low = high = 0
    for bit in bits:
        low = 2 * low + (bit if bit is not None else 0)
        high = 2 * high + (bit if bit is not None else 1)
    return int((low / (1 << 53)) * 3), int((high / (1 << 53)) * 3)


def positive_controls(words):
    rng = random.Random(0x13E17)
    for _ in range(100):
        state = rng.getstate()
        a, b = rng.getrandbits(32), rng.getrandbits(32)
        rng.setstate(state)
        assert int(3 * rng.random()) == 3 * (((a >> 5) << 26) + (b >> 6)) // (1 << 53)
    for category in (1, 2):
        around = category * (1 << 53) // 3
        for value in range(around - 4, around + 5):
            assert int((value / (1 << 53)) * 3) in (category - 1, category)
    for p in (0, 328, 724, 981):
        state = rng.getrandbits(624 * 32)
        basis = m.Basis()
        actual = []
        for ix in (p, p + 1):
            exprs = m.temper_expr(m.get_sym(words, ix))
            value = sum((((expr & state).bit_count() & 1) << j)
                        for j, expr in enumerate(exprs))
            actual.append(value)
            for j in range(5 if ix == p else 6, 32):
                assert basis.add(exprs[j], (value >> j) & 1)
        expected = 3 * (((actual[0] >> 5) << 26) + (actual[1] >> 6)) // (1 << 53)
        assert class_interval(words, basis, p) == (expected, expected)


def main():
    root = Path(__file__).resolve().parents[2]
    path = root / "resources/evidence/print/spool-reconstruction.log"
    raw, rows, payloads = m.parse_source(path)
    assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
    words = m.symbolic_words()
    positive_controls(words)
    basis = m.Basis()
    for i, payload in enumerate(payloads):
        if i == 129:
            assert payload is None
            continue
        for lane in range(4):
            value = m.untemper(int.from_bytes(payload[lane * 4:lane * 4 + 4], "little"))
            for bit, expr in enumerate(m.get_sym(words, m.STARTS[i] + lane)):
                assert basis.add(expr, (value >> bit) & 1)
    assert basis.rank == 15365

    schedules = {
        "first_DESTi_last_CLASSnext": lambda i, s, g: [(s, "DEST", i), (s + g - 2, "CLASS", i + 1)],
        "first_CLASSnext_last_DESTi": lambda i, s, g: [(s, "CLASS", i + 1), (s + g - 2, "DEST", i)],
        "last4_CLASSnext_DESTnext": lambda i, s, g: [(s + g - 4, "CLASS", i + 1), (s + g - 2, "DEST", i + 1)],
        "last4_DESTnext_CLASSnext": lambda i, s, g: [(s + g - 4, "DEST", i + 1), (s + g - 2, "CLASS", i + 1)],
        "first4_CLASSi_DESTi": lambda i, s, g: [(s, "CLASS", i), (s + 2, "DEST", i)],
        "first4_DESTi_CLASSi": lambda i, s, g: [(s, "DEST", i), (s + 2, "CLASS", i)],
    }
    perms = list(itertools.permutations(range(3)))
    output = {}
    for name, placement in schedules.items():
        records = []
        unresolved = 0
        for i in range(127):
            start = m.STARTS[i] + 4
            gap = m.STARTS[i + 1] - start
            if gap < 4:
                continue
            for pos, kind, index in placement(i, start, gap):
                lo, hi = class_interval(words, basis, pos)
                if lo != hi:
                    unresolved += 1
                    continue
                expected = (m.CLASS_CODE if kind == "CLASS" else m.DEST_CODE)[rows[index][kind]]
                records.append((kind, lo, expected))
        minimum = min(
            sum((cm if kind == "CLASS" else dm)[value] != expected
                for kind, value, expected in records)
            for cm in perms for dm in perms
        )
        lexical = sum(value != expected for kind, value, expected in records)
        output[name] = {"fully_source_fixed": len(records),
                        "lexical_conflicts": lexical,
                        "least_conflicts_over_all_36_category_maps": minimum,
                        "source_underdetermined": unresolved}
    assert [item["least_conflicts_over_all_36_category_maps"] for item in output.values()] == [13, 14, 13, 17, 17, 16]
    print(json.dumps({"source_rank": basis.rank,
                      "schedules": output,
                      "status": "NO_SOURCE_COMPATIBLE_MODEL"}, indent=2))


if __name__ == "__main__":
    main()
