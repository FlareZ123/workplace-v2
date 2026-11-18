"""Source-only K04 test: 4-way weighted CLASS choice plus 3-way DEST choice.

Hypothesis: CLASS is random.choice() over a four-entry list containing one
duplicate class, while DEST is random.choice() over three destinations. CPython
Random._randbelow_with_getrandbits uses getrandbits(3) for n=4 (accept 0..3,
reject 4..7) and getrandbits(2) for n=3 (accept 0..2, reject 3).

The two calls must consume the whole ordinary inter-payload gap. We test both
call orders and all current/next label bindings across all 170 source-compatible
six-baseline/one-root MT chronologies. Selected row129 and all K04 commitments
are excluded.
"""
from __future__ import annotations

import hashlib
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for name in ("agent44", "agent6"):
    sys.path.insert(0, str(ROOT / "agents" / name))

import k04_single_root_perturbations_sft as chronology
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt

LIMIT = 95
CLASS_NAMES = ("LABEL", "RECOVER", "STORES")
DEST_NAMES = ("bench", "desk", "store")


def top_domains(expressions, basis, width):
    out = []
    first = 32 - width
    for bits in expressions:
        tempered = chronology.tempered_bits(bits)
        choices = [()]
        for bit in range(first, 32):
            residue = mt.reduce_row(tempered[bit] << 1, basis)
            vals = (residue,) if residue <= 1 else (0, 1)
            choices = [prefix + (v,) for prefix in choices for v in vals]
        values = set()
        for tuple_bits in choices:
            value = sum(int(v) << j for j, v in enumerate(tuple_bits))
            values.add(value)
        out.append(values)
    return out


def mixed_pairs(gap2, gap3, order):
    """All accepted raw codes when the two calls consume the complete gap."""
    if len(gap2) != len(gap3) or len(gap2) < 2:
        return set()
    if order == "classdest":
        first_domains, second_domains = gap3, gap2
        first_accept, first_reject = set(range(4)), set(range(4, 8))
        second_accept, second_reject = set(range(3)), {3}
    else:
        first_domains, second_domains = gap2, gap3
        first_accept, first_reject = set(range(3)), {3}
        second_accept, second_reject = set(range(4)), set(range(4, 8))

    pairs = set()
    last = len(gap2) - 1
    for split in range(last):
        if any(not (first_domains[i] & first_reject) for i in range(split)):
            continue
        first_values = first_domains[split] & first_accept
        if not first_values:
            continue
        if any(not (second_domains[i] & second_reject)
               for i in range(split + 1, last)):
            continue
        second_values = second_domains[last] & second_accept
        for a in first_values:
            for b in second_values:
                pairs.add((a, b))
    return pairs


def positive_controls():
    # Top-three values 7,5,6,2 imply top-two values 3,2,3,1.
    d3 = [{7}, {5}, {6}, {2}]
    d2 = [{v >> 1 for v in values} for values in d3]
    assert mixed_pairs(d2, d3, "destclass") == {(2, 2)}

    # 6,1,7,4: CLASS rejects 6, accepts 1; DEST rejects top2=3, accepts 2.
    d3 = [{6}, {1}, {7}, {4}]
    d2 = [{v >> 1 for v in values} for values in d3]
    assert mixed_pairs(d2, d3, "classdest") == {(1, 2)}


def score(starts, d2, d3, labels):
    gap_pairs = {}
    for order in ("classdest", "destclass"):
        gap_pairs[order] = [
            mixed_pairs(d2[starts[r] + 4:starts[r + 1]],
                        d3[starts[r] + 4:starts[r + 1]], order)
            for r in range(127)
        ]

    class_maps = [
        mapping for mapping in itertools.product(range(3), repeat=4)
        if set(mapping) == {0, 1, 2}
    ]
    assert len(class_maps) == 36
    dest_maps = list(itertools.permutations(range(3)))
    class_index = {name: i for i, name in enumerate(CLASS_NAMES)}
    dest_index = {name: i for i, name in enumerate(DEST_NAMES)}

    best = LIMIT + 1
    survivors = []
    for cls_at, dst_at in itertools.product((0, 1), repeat=2):
        actual = [
            (class_index[labels[r + cls_at][0]],
             dest_index[labels[r + dst_at][1]])
            for r in range(127)
        ]
        for order in ("classdest", "destclass"):
            raw = gap_pairs[order]
            for class_map in class_maps:
                for dest_map in dest_maps:
                    errors = 0
                    for r in range(LIMIT):
                        want_c, want_d = actual[r]
                        ok = False
                        for a, b in raw[r]:
                            if order == "classdest":
                                c, d = a, b
                            else:
                                d, c = a, b
                            if class_map[c] == want_c and dest_map[d] == want_d:
                                ok = True
                                break
                        if not ok:
                            errors += 1
                    best = min(best, errors)
                    if errors:
                        continue
                    holdout_errors = 0
                    for r in range(LIMIT, 127):
                        want_c, want_d = actual[r]
                        ok = False
                        for a, b in raw[r]:
                            if order == "classdest":
                                c, d = a, b
                            else:
                                d, c = a, b
                            if class_map[c] == want_c and dest_map[d] == want_d:
                                ok = True
                                break
                        holdout_errors += int(not ok)
                    survivors.append(
                        (cls_at, dst_at, order, class_map, dest_map, holdout_errors)
                    )
    return best, survivors


def main():
    positive_controls()
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == mt.SOURCE_SHA
    lines, rows, selected, _ = mt.source_rows(raw, ROOT)
    assert selected == 129
    labels = [
        (re.search(r"CLASS=(\S+)", line).group(1),
         re.search(r"DEST=(\S+)", line).group(1))
        for line in lines
    ]
    assert set(labels[:128]) <= set(itertools.product(CLASS_NAMES, DEST_NAMES))

    expressions = mt.state_expressions(
        max(starts[-1] for starts in six.GEOMETRIES.values()) + 3
    )
    counts = {}
    global_best = LIMIT + 1
    all_survivors = []
    hard_gap_counts = []

    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        accepted = 0
        for group, shift in [(-1, 0)] + [
            (g, shift) for g in range(81) for shift in (-2, -1, 1, 2)
        ]:
            starts = [
                pos + (shift if chronology.GROUPS[row] == group else 0)
                for row, pos in enumerate(baseline)
            ]
            if not chronology.physical(starts, selected_stage):
                continue
            if chronology.impossible_threeword(starts, rows):
                continue
            try:
                basis = six.build_source_basis(expressions, rows, starts)
            except AssertionError:
                continue
            accepted += 1
            d2 = top_domains(expressions, basis, 2)
            d3 = top_domains(expressions, basis, 3)
            best, survivors = score(starts, d2, d3, labels)
            global_best = min(global_best, best)
            hard = {
                order: sum(
                    not mixed_pairs(d2[starts[r] + 4:starts[r + 1]],
                                    d3[starts[r] + 4:starts[r + 1]], order)
                    for r in range(95)
                )
                for order in ("classdest", "destclass")
            }
            hard_gap_counts.append((selected_stage, group, shift, hard))
            all_survivors.extend(
                (selected_stage, group, shift, model) for model in survivors
            )
        counts[selected_stage] = accepted
        print("GEOMETRY", selected_stage, "SOURCE_COMPATIBLE", accepted, flush=True)

    assert counts == {950:35, 951:28, 952:25, 953:21, 954:31, 955:30}, counts
    print("SOURCE_COMPATIBLE_CHRONOLOGIES", sum(counts.values()))
    print("WEIGHTED_CLASS_MAPS", 36)
    print("DEST_CODEBOOKS", 6)
    print("BINDINGS", 4)
    print("CALL_ORDERS", 2)
    print("FIRST95_BEST_MISMATCH", global_best)
    print("FIRST95_SURVIVORS", len(all_survivors))
    print("HOLDOUT32_ZERO_ERROR_SURVIVORS",
          sum(model[-1] == 0 for _, _, _, model in all_survivors))
    if all_survivors:
        print("SURVIVORS", all_survivors[:40])
    best_hard = min(
        (item[3][order], item[0], item[1], item[2], order)
        for item in hard_gap_counts for order in ("classdest", "destclass")
    )
    print("MIN_UNCONDITIONAL_IMPOSSIBLE_TRAINING_GAPS", best_hard)
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("SELECTED_ROW_WITHHELD", selected)
    print("AUTHENTIC_K04_BITS", 0)


if __name__ == "__main__":
    main()
