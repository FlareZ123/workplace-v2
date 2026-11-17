"""K04 exploratory SFT: one hidden native MT output after CLASS on every ordinary job.

This is distinct from:
- the two visible CLASS/DEST randbelow(3) calls with arbitrary outside filler;
- Agent20's one hidden output conditional on exactly one CLASS category;
- Agent47's two hidden outputs conditional on RECOVER.

Hypothesis: each job consumes one additional, unexported 32-bit output immediately
after the CLASS sampler, regardless of CLASS value. The output may represent a
hidden queue/driver token. Test all 170 source-compatible MT chronologies, all
static CLASS/DEST codebooks, both sampler orders, both row bindings, and both
leading-gap policies. Selected PS-0417 ACK2 payload and K04 commitment are not
loaded. A positive result is only a producer candidate, not historical proof.

Run from repository root:
    python agents/agent6/k04_oneword_perrow_interleave_sft.py
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
                   class_first: bool) -> set[tuple[int, int]]:
    """Optimistic CLASS/DEST accepted-code pairs with one hidden word after CLASS.

    Each visible sampler accepts codes 0..2 and rejects 3. If CLASS is first,
    one unconstrained native output is required between its accepted word and
    DEST's first attempt. If DEST is first, CLASS is second and one unconstrained
    output is required after its accepted word. Other between-sampler words
    must be possible code-3 rejections. Post-pair filler is otherwise free.
    """
    pairs: set[tuple[int, int]] = set()
    for first in range(len(gap)):
        if at_first and any(3 not in gap[k] for k in range(first)):
            break
        for first_code in gap[first] - {3}:
            if class_first:
                following = first + 2  # accepted CLASS, then one hidden output
                for second in range(following, len(gap)):
                    if any(3 not in gap[k] for k in range(following, second)):
                        break
                    for second_code in gap[second] - {3}:
                        pairs.add((first_code, second_code))
            else:
                # first sampler is DEST; second is CLASS. One hidden output
                # after CLASS must still fit before the next payload.
                for second in range(first + 1, len(gap)):
                    if any(3 not in gap[k] for k in range(first + 1, second)):
                        break
                    if second + 1 >= len(gap):
                        continue
                    for second_code in gap[second] - {3}:
                        pairs.add((second_code, first_code))
    return pairs


def score(starts: list[int], domains: list[set[int]],
          labels: list[tuple[str, str]], limit: int = LIMIT):
    gaps = [domains[starts[row] + 4:starts[row + 1]] for row in range(127)]
    assert all(len(g) >= 2 for g in gaps)
    allowed_cache: dict[tuple[bool, bool], list[set[tuple[int, int]]]] = {}
    classes = sorted({name for name, _ in labels[:128]})
    destinations = sorted({name for _, name in labels[:128]})
    minimum = limit + 1
    survivors = []
    per_order = {"classdest": limit + 1, "destclass": limit + 1}

    for at_first, class_first in itertools.product((True, False), repeat=2):
        allowed_cache[(at_first, class_first)] = [
            possible_pairs(gap, at_first, class_first) for gap in gaps
        ]

    for class_codes in itertools.permutations(range(3)):
        class_lookup = dict(zip(classes, class_codes))
        for dest_codes in itertools.permutations(range(3)):
            dest_lookup = dict(zip(destinations, dest_codes))
            for at_first, class_first, bind_next in itertools.product(
                    (True, False), repeat=3):
                allowed = allowed_cache[(at_first, class_first)]
                actual = [
                    (class_lookup[labels[row + bind_next][0]],
                     dest_lookup[labels[row + bind_next][1]])
                    for row in range(127)
                ]
                errors = sum(actual[row] not in allowed[row]
                             for row in range(limit))
                order = "classdest" if class_first else "destclass"
                minimum = min(minimum, errors)
                per_order[order] = min(per_order[order], errors)
                if errors == 0:
                    holdout = tuple(row for row in range(limit, 127)
                                    if actual[row] not in allowed[row])
                    survivors.append((class_codes, dest_codes, at_first,
                                      class_first, bind_next, len(holdout)))
    return minimum, per_order, survivors


def sample_below3(rng: random.Random):
    attempts = 0
    while True:
        value = rng.getrandbits(2)
        attempts += 1
        if value < 3:
            return value, attempts


def planted_positive(order: str):
    rng = random.Random(39117)
    stages = []
    rows = []
    labels = [(CLASS_NAMES[0], DEST_NAMES[0])]
    stage = 0
    for _row in range(128):
        if _row:
            if order == "classdest":
                class_code, count = sample_below3(rng)
                stage += count
                rng.getrandbits(32)  # the hidden per-job word after CLASS
                stage += 1
                dest_code, count = sample_below3(rng)
                stage += count
            else:
                dest_code, count = sample_below3(rng)
                stage += count
                class_code, count = sample_below3(rng)
                stage += count
                rng.getrandbits(32)  # after CLASS, now after DEST too
                stage += 1
            labels.append((CLASS_NAMES[class_code], DEST_NAMES[dest_code]))
        stages.append(stage)
        rows.append([mt.untemper(rng.getrandbits(32)) for _ in range(4)])
        stage += 4

    expressions = mt.state_expressions(stages[-1] + 3)
    basis = six.build_source_basis(expressions, rows, stages)
    domains = joint.top_two_domains(expressions, basis)
    minimum, per_order, survivors = score(stages, domains, labels)
    assert minimum == 0, (order, per_order)
    assert any(model[0] == (0, 1, 2) and model[1] == (0, 1, 2)
               and model[2] and model[3] == (order == "classdest")
               and model[4] and model[5] == 0 for model in survivors), (
                   order, survivors[:5])
    print("PLANTED_POSITIVE", order, "PASS", "draws", stage,
          "zero-holdout models", len(survivors), flush=True)


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

    planted_positive("classdest")
    planted_positive("destclass")

    expressions = mt.state_expressions(
        max(starts[-1] for starts in six.GEOMETRIES.values()) + 3)
    expected = {950: 35, 951: 28, 952: 25, 953: 21, 954: 31, 955: 30}
    counts = {}
    best = LIMIT + 1
    best_order = {"classdest": LIMIT + 1, "destclass": LIMIT + 1}
    survivors = []
    models = 0

    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        accepted = 0
        for group, shift in [(-1, 0)] + [
                (g, delta) for g in range(81) for delta in (-2, -1, 1, 2)]:
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
            minimum, per_order, complete = score(starts, domains, labels)
            best = min(best, minimum)
            for order, value in per_order.items():
                best_order[order] = min(best_order[order], value)
            survivors.extend((selected_stage, group, shift, model)
                             for model in complete)
            models += 36 * 8

        counts[selected_stage] = accepted
        print("GEOMETRY", selected_stage, "SOURCE_COMPATIBLE", accepted,
              "BEST95", best, "SURVIVORS", len(survivors), flush=True)

    assert counts == expected, counts
    assert sum(counts.values()) == 170
    assert models == 170 * 36 * 8
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("SOURCE_COMPATIBLE_CHRONOLOGIES", sum(counts.values()))
    print("MODEL_COUNT", models)
    print("ONE_HIDDEN_WORD_AFTER_CLASS_EVERY_ROW")
    print("BEST_FIRST95_MISMATCH", best)
    print("BEST_BY_CALL_ORDER", best_order)
    print("ZERO_MISMATCH_SURVIVORS", len(survivors))
    print("HOLDOUT32_SURVIVORS",
          sum(model[-1] == 0 for _, _, _, model in survivors))
    print("AUTHENTIC_K04_BITS", 0)


if __name__ == "__main__":
    main()
