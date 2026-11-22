"""K04 exploratory MT metadata writer test: getrandbits(2) modulo-three labels.

This extends the existing 170-chronology source-only test. The prior test
allowed only 0..2 and modeled rejection of value 3. This test instead asks
whether a custom writer maps the four 2-bit outcomes to three labels via
value % 3, followed by any fixed permutation of the three labels.

The selected ACK2 payload and K04 commitment are excluded from training.
No candidate bytes are modified and no facility equipment is accessed.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent44"))
import k04_single_root_perturbations_sft as variants
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt

CLASSES = ("LABEL", "RECOVER", "STORES")
DESTS = ("bench", "desk", "store")
PERMS = tuple(itertools.permutations(range(3)))
TRAIN = 95
TOTAL = 127


def possible_values(expression, basis):
    low = mt.reduce_row(expression[30] << 1, basis)
    high = mt.reduce_row(expression[31] << 1, basis)
    lows = (low,) if low <= 1 else (0, 1)
    highs = (high,) if high <= 1 else (0, 1)
    return {lo + 2 * hi for lo in lows for hi in highs}


def pair_mask_modulo_three(positions, class_map, dest_map):
    """Nine-bit mask using all four values, with raw value 3 mapped to 0."""
    result = 0
    for i, left in enumerate(positions):
        class_values = {class_map[value % 3] for value in left}
        for j, right in enumerate(positions):
            if i == j:
                continue
            dest_values = {dest_map[value % 3] for value in right}
            for class_code in class_values:
                for dest_code in dest_values:
                    result |= 1 << (3 * class_code + dest_code)
    return result


def score_model(masks, class_ids, dest_ids, class_at, dest_at):
    train = held = 0
    for row, allowed in enumerate(masks):
        class_code = class_ids[row + class_at]
        dest_code = dest_ids[row + dest_at]
        ok = (allowed >> (3 * class_code + dest_code)) & 1
        if row < TRAIN:
            train += ok
        else:
            held += ok
    return train, held


def main():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == mt.SOURCE_SHA
    lines, rows, selected, _ = mt.source_rows(raw, ROOT)
    assert selected == 129 and len(rows) == len(lines) == 133 and rows[129] == []

    labels = [
        tuple(re.search(
            r"CLASS=(\w+) PAYLOAD=[0-9A-F]{32} DEST=(\w+)", line
        ).groups())
        for line in lines
    ]
    assert set(labels[:128]) == set(itertools.product(CLASSES, DESTS))
    class_ids = [CLASSES.index(c) for c, _ in labels]
    dest_ids = [DESTS.index(d) for _, d in labels]

    end = max(x[-1] for x in six.GEOMETRIES.values()) + 5
    terms = mt.state_expressions(end)
    tempered = [variants.tempered_bits(word) for word in terms]

    outcomes = defaultdict(lambda: {
        "valid": 0,
        "min_train_errors": TRAIN + 1,
        "min_total_errors": TOTAL + 1,
        "training_survivors": 0,
        "complete_survivors": 0,
        "best_train": 0,
        "best_total": 0,
    })
    p951 = None
    for target_stage, baseline in sorted(six.GEOMETRIES.items()):
        source_valid = 0
        for component, delta in [(-1, 0)] + [
            (group, shift)
            for group in range(81)
            for shift in (-2, -1, 1, 2)
        ]:
            starts = [
                start + (delta if variants.GROUPS[row] == component else 0)
                for row, start in enumerate(baseline)
            ]
            if not variants.physical(starts, target_stage):
                continue
            if variants.impossible_threeword(starts, rows):
                continue
            try:
                basis = six.build_source_basis(terms, rows, starts)
            except AssertionError:
                continue
            source_valid += 1

            position_sets = [
                [
                    possible_values(tempered[pos], basis)
                    for pos in range(starts[row] + 4, starts[row + 1])
                ]
                for row in range(127)
            ]

            best_for_bindings = [0, 0, 0, 0]
            for class_map, dest_map in itertools.product(PERMS, repeat=2):
                masks = [
                    pair_mask_modulo_three(gap, class_map, dest_map)
                    for gap in position_sets
                ]
                for binding_index, (class_at, dest_at) in enumerate(
                    itertools.product((0, 1), repeat=2)
                ):
                    train, held = score_model(
                        masks, class_ids, dest_ids, class_at, dest_at
                    )
                    total = train + held
                    best_for_bindings[binding_index] = max(
                        best_for_bindings[binding_index], total
                    )
                    item = outcomes[target_stage]
                    item["min_train_errors"] = min(
                        item["min_train_errors"], TRAIN - train
                    )
                    item["min_total_errors"] = min(
                        item["min_total_errors"], TOTAL - total
                    )
                    item["best_train"] = max(item["best_train"], train)
                    item["best_total"] = max(item["best_total"], total)
                    if train == TRAIN:
                        item["training_survivors"] += 1
                        if held == TOTAL - TRAIN:
                            item["complete_survivors"] += 1
                            print(
                                "FULL_SOURCE_WRITER",
                                target_stage,
                                component,
                                delta,
                                "binding",
                                class_at,
                                dest_at,
                                "class_map",
                                class_map,
                                "dest_map",
                                dest_map,
                                flush=True,
                            )
            if target_stage == 951 and component == -1:
                p951 = best_for_bindings

        outcomes[target_stage]["valid"] = source_valid
        print(
            "STAGE",
            target_stage,
            "SOURCE_COMPATIBLE",
            source_valid,
            "BEST_TRAIN",
            outcomes[target_stage]["best_train"],
            "BEST_TOTAL",
            outcomes[target_stage]["best_total"],
            "MIN_ERRORS_TRAIN",
            outcomes[target_stage]["min_train_errors"],
            "MIN_ERRORS_ALL",
            outcomes[target_stage]["min_total_errors"],
            "FULL_WRITERS",
            outcomes[target_stage]["complete_survivors"],
            flush=True,
        )

    expected = {950: 35, 951: 28, 952: 25, 953: 21, 954: 31, 955: 30}
    assert {stage: outcomes[stage]["valid"] for stage in expected} == expected
    print(json.dumps({
        "spool_sha256": mt.SOURCE_SHA,
        "selected_row129_payload_used": False,
        "selected_K04_bytes_authenticated": 0,
        "mapping": "raw_2bit_value_mod_3_then_fixed_permutation",
        "source_compatible_chronologies": sum(
            item["valid"] for item in outcomes.values()
        ),
        "p951_binding_best_totals": p951,
        "by_selected_stage": outcomes,
    }, indent=2), flush=True)
    if sum(item["complete_survivors"] for item in outcomes.values()):
        print("ACTION: modulo-three metadata writer survived; validate independently")
    else:
        print("NO COMPLETE MODULO-THREE METADATA WRITER in this 170-chronology family")


if __name__ == "__main__":
    main()
