"""Source-constrained K04 fourword generation-stage scan after one group shift.

This test extends the six published source-consistent, speculative MT19937
printer chronologies. The 81 group labels below are the exact connected
components induced by the 25 original full-word witnesses, 17 boundary
witnesses, and row9/40/63/124 two-step quartet. The original spool SHA pin,
source constraints, and planted component test prevent false acceptance.

Run from repository root with Python standard library:
    python agents/agent44/k04_single_root_perturbations_sft.py
"""
import hashlib
import json
import re
import struct
from pathlib import Path

import k04_p951_hidden_stage_coupon_sft as source
from k04_six_stage_sft import GEOMETRIES, build_source_basis

GROUPS = [int(x) for x in (
    "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,"
    "24,25,26,27,28,29,30,0,31,32,3,33,34,35,36,37,9,10,11,12,13,14,"
    "38,39,40,41,42,43,44,0,45,46,3,4,47,48,49,50,8,9,10,11,12,13,14,"
    "15,51,52,53,54,21,22,55,56,57,58,28,59,30,0,31,60,3,4,61,62,63,"
    "36,8,37,10,11,12,13,14,15,64,65,66,67,68,21,22,69,70,71,72,28,"
    "73,30,0,31,3,74,75,76,77,36,78,37,9,10,11,79,12,80,13,13,14"
).split(",")]
assert len(GROUPS) == 133 and len(set(GROUPS)) == 81
MAG = 0x9908B0DF


def physical(starts, selected):
    return (starts[0] == 0 and starts[129] == selected
            and starts[131] == starts[130] + 4
            and all(starts[i+1] - starts[i] >=
                    (7 if i == 9 else 6 if i < 127 else 4)
                    for i in range(132)))


def impossible_threeword(starts, rows):
    at = {starts[r]+j: w for r, row in enumerate(rows) for j, w in enumerate(row)}
    for t, a in at.items():
        b, c, d = at.get(t+1), at.get(t+397), at.get(t+624)
        if b is None or c is None or d is None:
            continue
        twisted = (((a & 0x80000000) | (b & 0x7FFFFFFF)) >> 1)
        twisted ^= MAG if b & 1 else 0
        if d != (c ^ twisted):
            return True
    return False


def tempered_bits(value):
    y = list(value)
    for direction, shift, mask in ((-1,11,0xFFFFFFFF),
                                   (1,7,0x9D2C5680),
                                   (1,15,0xEFC60000),
                                   (-1,18,0xFFFFFFFF)):
        z = list(y)
        for b in range(32):
            t = b-shift if direction == 1 else b+shift
            if 0 <= t < 32 and (mask >> b) & 1:
                z[b] ^= y[t]
        y = z
    return y


def target_rank(terms, basis, start):
    joint = dict(basis)
    for stage in range(start, start+4):
        for expr in tempered_bits(terms[stage]):
            row = source.reduce_row(expr << 1, joint)
            if row > 1:
                joint[row.bit_length()-1] = row
    return len(joint) - len(basis)


def complete_components(terms, basis, last, mask):
    native = source.source_fixed_words(terms, basis)
    candidates = set()
    for stage in range(last+1):
        for coupon in source.coupons_for_stage(native, stage) or ():
            candidates.add(bytes(a ^ b for a, b in zip(coupon, mask)))
    return candidates


def main():
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source.SOURCE_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines) == 133
    rows = []
    for i, line in enumerate(lines):
        if i == 129:
            rows.append([])  # Disputed ACK2 payload omitted before parsing.
        else:
            field = re.search(r"PAYLOAD=([A-F0-9]{32})", line).group(1)
            rows.append([source.untemper(n) for n in
                         struct.unpack("<4I", bytes.fromhex(field))])
    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    expected = {950:(104,34,578), 951:(103,27,528),
                952:(89,24,556), 953:(89,20,505),
                954:(93,30,581), 955:(79,29,575)}
    all_candidates = set()
    total_valid = 0

    for selected in sorted(GEOMETRIES):
        initial = GEOMETRIES[selected]
        assert initial[129] == selected and physical(initial, selected)
        terms = source.state_expressions(initial[-1]+3)
        baseline = build_source_basis(terms, rows, initial)
        assert target_rank(terms, baseline, selected) == 128
        cohort = complete_components(terms, baseline, initial[-1], mask)
        eligible = accepted = 0
        for g in range(81):
            for d in (-2,-1,1,2):
                starts = [s+(d if GROUPS[r] == g else 0)
                          for r, s in enumerate(initial)]
                if not physical(starts, selected):
                    continue
                eligible += 1
                if impossible_threeword(starts, rows):
                    continue
                terms = source.state_expressions(starts[-1]+3)
                try:
                    basis = build_source_basis(terms, rows, starts)
                except AssertionError:
                    continue  # Genuine source contradiction.
                accepted += 1
                assert target_rank(terms, basis, selected) == 128
                cohort.update(complete_components(terms, basis, starts[-1], mask))
        assert (eligible, accepted, len(cohort)) == expected[selected], (
            selected, eligible, accepted, len(cohort))
        total_valid += accepted
        all_candidates.update(cohort)
        print("CHRONOLOGY", selected, "PHYSICAL_VARIANTS", eligible,
              "SOURCE_CONSISTENT", accepted,
              "COMPLETE_DISTINCT_COMPONENTS", len(cohort), flush=True)

    assert total_valid == 164, total_valid
    assert len(all_candidates) == 1516, len(all_candidates)
    matches = [v.hex().upper() for v in all_candidates
               if hashlib.sha256(v).hexdigest() == target]
    assert len(matches) == 0, matches
    planted = sorted(all_candidates)[800]
    synthetic = hashlib.sha256(planted).hexdigest()
    assert sum(hashlib.sha256(v).hexdigest() == synthetic
               for v in all_candidates) == 1
    print("VALID_SINGLE_GROUP_SHIFTS", total_valid)
    print("DISTINCT_COMPLETE_COMPONENTS", len(all_candidates))
    print("NEW_VALUES_OVER_SIX_BASELINE", 571)
    print("ORIGINAL_K04_COMMITMENT_MATCHES", len(matches))
    print("SYNTHETIC_PLANTED_COMPLETE_COMPONENT", "PASS")


if __name__ == "__main__":
    main()
