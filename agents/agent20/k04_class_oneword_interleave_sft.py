"""K04 source-only test: one conditional native MT word between CLASS/DEST calls.

Distinct from existing two-consecutive-call and RECOVER-two-word interleave tests:
the omitted call consumes *one* MT output and is selected by exactly one of the
three actual CLASS labels. Test all three triggers and both field call orders.
The selected PS-0417 attempt-2 payload and K04 commitment are not loaded.

The native MT chronologies are inherited from Agent44's original-source-only
170 compatible six-baseline/one-root placements, with original row129 withheld.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for name in ("agent44", "agent6"):
    sys.path.insert(0, str(ROOT / "agents" / name))
import k04_single_root_perturbations_sft as chronology
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt
import k04_one_root_joint_metadata_sft as joint

LIMIT = 95
CLASS_NAMES = ("LABEL", "RECOVER", "STORES")
DEST_NAMES = ("bench", "desk", "store")


def possible_pairs(gap: list[set[int]], at_first: bool,
                   class_first: bool, trigger_code: int) -> set[tuple[int, int]]:
    """Optimistic possible CLASS/DEST accepted codes with one class-triggered draw.

    Each sampler accepts codes 0..2, rejecting 3; at_first forces leading
    source words to be sampler rejection draws. A trigger inserts one arbitrary
    native word immediately after CLASS accepts. Between other sampler attempts,
    only rejection draws are permitted. Post-pair filler is unrestricted.
    """
    pairs: set[tuple[int, int]] = set()
    for first in range(len(gap)):
        if at_first and any(3 not in gap[k] for k in range(first)):
            break
        for first_code in gap[first] - {3}:
            if class_first:
                following = first + 1 + int(first_code == trigger_code)
                for second in range(following, len(gap)):
                    if any(3 not in gap[k] for k in range(following, second)):
                        break
                    for second_code in gap[second] - {3}:
                        pairs.add((first_code, second_code))
            else:
                for second in range(first + 1, len(gap)):
                    if any(3 not in gap[k] for k in range(first + 1, second)):
                        break
                    for second_code in gap[second] - {3}:
                        if second_code != trigger_code or second + 1 < len(gap):
                            pairs.add((second_code, first_code))
    return pairs


def score(starts: list[int], domains: list[set[int]],
          labels: list[tuple[str, str]], limit: int = LIMIT):
    gaps = [domains[starts[row]+4:starts[row+1]] for row in range(127)]
    assert all(len(g) >= 2 for g in gaps)
    cache: dict[tuple[bool, bool, int], list[set[tuple[int, int]]]] = {}
    min_mismatch = limit + 1
    complete = []
    hist: dict[str, int] = {name: limit+1 for name in CLASS_NAMES}
    for class_codes in itertools.permutations(range(3)):
        class_lookup = dict(zip(CLASS_NAMES, class_codes))
        for dest_codes in itertools.permutations(range(3)):
            dest_lookup = dict(zip(DEST_NAMES, dest_codes))
            for trigger in CLASS_NAMES:
                trigger_code = class_lookup[trigger]
                for at_first, class_first, bind_next in itertools.product(
                        (True, False), repeat=3):
                    cache_key = (at_first, class_first, trigger_code)
                    if cache_key not in cache:
                        cache[cache_key] = [
                            possible_pairs(g, at_first, class_first, trigger_code)
                            for g in gaps
                        ]
                    allowed = cache[cache_key]
                    actual = [
                        (class_lookup[labels[row + bind_next][0]],
                         dest_lookup[labels[row + bind_next][1]])
                        for row in range(127)
                    ]
                    errors = sum(actual[row] not in allowed[row]
                                 for row in range(limit))
                    min_mismatch = min(min_mismatch, errors)
                    hist[trigger] = min(hist[trigger], errors)
                    if errors == 0:
                        test_errors = [
                            row for row in range(limit, 127)
                            if actual[row] not in allowed[row]
                        ]
                        complete.append((trigger, class_codes, dest_codes,
                                         at_first, class_first, bind_next,
                                         len(test_errors)))
    return min_mismatch, hist, complete


def sample_below3(rng: random.Random):
    attempts = 0
    while True:
        value = rng.getrandbits(2)
        attempts += 1
        if value < 3:
            return value, attempts


def positive(order: str, trigger: str):
    rng = random.Random(39117)
    stages = []
    rows = []
    labels = [(CLASS_NAMES[0], DEST_NAMES[0])]
    stage = 0
    for row in range(128):
        if row:
            if order == "classdest":
                class_code, count = sample_below3(rng)
                stage += count
                if CLASS_NAMES[class_code] == trigger:
                    rng.getrandbits(32)
                    stage += 1
                dest_code, count = sample_below3(rng)
                stage += count
            else:
                dest_code, count = sample_below3(rng)
                stage += count
                class_code, count = sample_below3(rng)
                stage += count
                if CLASS_NAMES[class_code] == trigger:
                    rng.getrandbits(32)
                    stage += 1
            labels.append((CLASS_NAMES[class_code], DEST_NAMES[dest_code]))
        stages.append(stage)
        rows.append([mt.untemper(rng.getrandbits(32)) for _ in range(4)])
        stage += 4
    expressions = mt.state_expressions(stage + 3)
    basis = six.build_source_basis(expressions, rows, stages)
    domains = joint.top_two_domains(expressions, basis)
    mismatch, hist, complete = score(stages, domains, labels)
    assert mismatch == 0, (order, trigger, hist)
    assert any(row[0] == trigger and row[1] == (0,1,2)
               and row[2] == (0,1,2) and row[3] and row[4] == (order == "classdest")
               and row[5] and row[6] == 0 for row in complete), (order,trigger,complete)
    print("PLANTED", order, trigger, "PASS stage", stage,
          "survivors", len(complete), flush=True)


def main():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == mt.SOURCE_SHA
    lines, rows, selected, _ = mt.source_rows(raw, ROOT)
    assert selected == 129 and len(lines) == len(rows) == 133
    labels = [
        (re.search(r"CLASS=(\S+)", line).group(1),
         re.search(r"DEST=(\S+)", line).group(1))
        for line in lines
    ]
    assert set(labels[:128]) <= set(itertools.product(CLASS_NAMES, DEST_NAMES))
    for order in ("classdest", "destclass"):
        for trigger in CLASS_NAMES:
            positive(order, trigger)
    expressions = mt.state_expressions(
        max(starts[-1] for starts in six.GEOMETRIES.values()) + 3)
    counts = {}
    best = LIMIT + 1
    class_best = {k: LIMIT+1 for k in CLASS_NAMES}
    survivors = []
    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        accepted = 0
        for group, shift in [(-1, 0)] + [
            (g, shift) for g in range(81) for shift in (-2,-1,1,2)
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
            domains = joint.top_two_domains(expressions, basis)
            minimum, histogram, complete = score(starts, domains, labels)
            best = min(best, minimum)
            for trigger, value in histogram.items():
                class_best[trigger] = min(class_best[trigger], value)
            survivors.extend((selected_stage, group, shift, model)
                             for model in complete)
        counts[selected_stage] = accepted
        print("GEOMETRY", selected_stage, "SOURCE_COMPATIBLE", accepted,flush=True)
    assert counts == {950:35,951:28,952:25,953:21,954:31,955:30}, counts
    print("ONE_WORD_CONDITIONAL_MODELS",
          170*36*3*2*2*2)
    print("ORIGINAL_FIRST95_BEST_MISMATCH", best)
    print("ORIGINAL_FIRST95_MIN_BY_CLASS_TRIGGER", class_best)
    print("ORIGINAL_FIRST95_SURVIVORS", len(survivors))
    print("HOLDOUT32_SURVIVORS",
          sum(model[-1] == 0 for _,_,_,model in survivors))
    if survivors:
        print("SOURCE_CONDITIONED_MODELS", survivors[:20])
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("AUTHENTIC_K04_COMPONENT_BITS", 0)


if __name__ == "__main__":
    main()
