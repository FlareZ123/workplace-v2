"""Source-only SFT: a RECOVER-conditioned two-word call between printer metadata samplers.

This is a bounded interleaved-call hypothesis, not an asserted historical API:
after the CLASS sampler accepts RECOVER, the same MT stream consumes two
unobserved native words before the DEST sampler. The two words are left
unconstrained, covering (among other possibilities) random() or getrandbits(64).

The selected PS-0417 ACK2 payload, K04 mask, acceptance commitment and candidate
are not loaded. The source basis uses only the 132 intact spool payloads.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent44"))
sys.path.insert(0, str(ROOT / "agents" / "agent6"))

import k04_single_root_perturbations_sft as chronology
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt
import k04_one_root_joint_metadata_sft as joint

LIMIT = 95
FILLER_WORDS = 2


def pairset_with_recover_filler(
    gap: list[set[int]],
    at_first: bool,
    class_first: bool,
    recover_code: int,
) -> set[tuple[int, int]]:
    """Possible (class_code, dest_code) pairs in one hidden gap.

    A randbelow(3) attempt consumes one MT word; code 3 is rejection.
    The first sampler may start at the first hidden word or after arbitrary
    unrelated prefix draws. If CLASS is first and accepts RECOVER, exactly two
    unconstrained MT words intervene before DEST. If CLASS is second, those
    two words must fit after its accepted code and before the next payload.
    Other positions between samplers must be possible rejection draws.
    Arbitrary unrelated draws after the pair are allowed.
    """
    pairs: set[tuple[int, int]] = set()
    for first in range(len(gap)):
        if at_first and any(3 not in gap[k] for k in range(first)):
            break
        for first_code in gap[first] - {3}:
            if class_first:
                second_start = first + 1 + (
                    FILLER_WORDS if first_code == recover_code else 0
                )
                for second in range(second_start, len(gap)):
                    if any(3 not in gap[k] for k in range(second_start, second)):
                        break
                    for second_code in gap[second] - {3}:
                        pairs.add((first_code, second_code))
            else:
                for second in range(first + 1, len(gap)):
                    if any(3 not in gap[k] for k in range(first + 1, second)):
                        break
                    for second_code in gap[second] - {3}:
                        if (second_code != recover_code
                                or second + FILLER_WORDS < len(gap)):
                            pairs.add((second_code, first_code))
    return pairs


def metadata_models(
    starts: list[int],
    domains: list[set[int]],
    labels: list[tuple[str, str]],
    limit: int = LIMIT,
):
    """Test all static three-way codebooks and both record/call orderings."""
    classes = sorted({name for name, _ in labels[:128]})
    destinations = sorted({name for _, name in labels[:128]})
    assert len(classes) == len(destinations) == 3

    gaps = [domains[starts[row] + 4:starts[row + 1]] for row in range(127)]
    cache: dict[tuple[bool, bool, int], list[set[tuple[int, int]]]] = {}
    survivors = []
    minimum_mismatches = limit + 1

    for class_codes in itertools.permutations(range(3)):
        class_lookup = dict(zip(classes, class_codes))
        recover_code = class_lookup["RECOVER"]
        for dest_codes in itertools.permutations(range(3)):
            dest_lookup = dict(zip(destinations, dest_codes))
            for at_first in (True, False):
                for class_first in (True, False):
                    cache_key = (at_first, class_first, recover_code)
                    if cache_key not in cache:
                        cache[cache_key] = [
                            pairset_with_recover_filler(
                                gap, at_first, class_first, recover_code
                            )
                            for gap in gaps
                        ]
                    allowed = cache[cache_key]
                    for binding in ("current", "next"):
                        actual = [
                            (
                                class_lookup[labels[row + (binding == "next")][0]],
                                dest_lookup[labels[row + (binding == "next")][1]],
                            )
                            for row in range(127)
                        ]
                        mismatches = sum(
                            actual[row] not in allowed[row] for row in range(limit)
                        )
                        minimum_mismatches = min(minimum_mismatches, mismatches)
                        if mismatches == 0:
                            holdout_errors = tuple(
                                row for row in range(limit, 127)
                                if actual[row] not in allowed[row]
                            )
                            survivors.append((
                                class_codes, dest_codes, at_first,
                                class_first, binding, holdout_errors,
                            ))
    return survivors, minimum_mismatches


def draw_below_three(rng: random.Random) -> int:
    while True:
        code = rng.getrandbits(2)
        if code < 3:
            return code


def planted_positive(order: str) -> int:
    """Verify both interleavings against a genuine seeded CPython MT stream."""
    assert order in ("classdest", "destclass")
    rng = random.Random(39117)
    class_names = ("LABEL", "RECOVER", "STORES")
    dest_names = ("bench", "desk", "store")
    starts: list[int] = []
    rows: list[list[int]] = [[] for _ in range(128)]
    labels: list[tuple[str, str]] = [("LABEL", "bench")]
    stage = 0

    for row in range(128):
        if row:
            if order == "classdest":
                class_code = draw_below_three(rng)
                stage += 1
                if class_code == 1:  # RECOVER in the planted codebook.
                    rng.getrandbits(64)
                    stage += 2
                dest_code = draw_below_three(rng)
                stage += 1
            else:
                dest_code = draw_below_three(rng)
                stage += 1
                class_code = draw_below_three(rng)
                stage += 1
                if class_code == 1:
                    rng.getrandbits(64)
                    stage += 2
            labels.append((class_names[class_code], dest_names[dest_code]))

        starts.append(stage)
        rows[row] = [
            mt.untemper(rng.getrandbits(32)) for _ in range(4)
        ]
        stage += 4

    expressions = mt.state_expressions(stage + 3)
    basis = six.build_source_basis(expressions, rows, starts)
    domains = joint.top_two_domains(expressions, basis)
    survivors, minimum = metadata_models(starts, domains, labels)
    planted_class_first = order == "classdest"
    assert minimum == 0
    assert any(
        class_codes == (0, 1, 2)
        and dest_codes == (0, 1, 2)
        and at_first
        and class_first == planted_class_first
        and binding == "next"
        and not holdout
        for class_codes, dest_codes, at_first, class_first, binding, holdout
        in survivors
    )
    return stage


def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == mt.SOURCE_SHA

    lines, rows, selected, _ = mt.source_rows(raw, ROOT)
    assert selected == 129 and len(lines) == len(rows) == 133
    labels = [
        (
            re.search(r"CLASS=(\S+)", line).group(1),
            re.search(r"DEST=(\S+)", line).group(1),
        )
        for line in lines
    ]
    assert labels[:128].count(("RECOVER", "bench")) >= 0
    assert sum(job_class == "RECOVER" for job_class, _ in labels[:128]) == 35

    max_position = max(starts[-1] for starts in six.GEOMETRIES.values()) + 3
    expressions = mt.state_expressions(max_position)
    expected = {950: 35, 951: 28, 952: 25, 953: 21, 954: 31, 955: 30}
    counts = {}
    total_models = 0
    minimum_original_mismatches = LIMIT + 1

    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        source_compatible = 0
        variants = [(-1, 0)] + [
            (group, shift)
            for group in range(81)
            for shift in (-2, -1, 1, 2)
        ]
        for component, delta in variants:
            starts = [
                start + (delta if chronology.GROUPS[row] == component else 0)
                for row, start in enumerate(baseline)
            ]
            if not chronology.physical(starts, selected_stage):
                continue
            if chronology.impossible_threeword(starts, rows):
                continue
            try:
                basis = six.build_source_basis(expressions, rows, starts)
            except AssertionError:
                continue

            source_compatible += 1
            domains = joint.top_two_domains(expressions, basis)
            survivors, minimum = metadata_models(starts, domains, labels)
            total_models += len(survivors)
            minimum_original_mismatches = min(
                minimum_original_mismatches, minimum
            )

        counts[selected_stage] = source_compatible
        print(
            "GEOMETRY", selected_stage,
            "SOURCE_COMPATIBLE", source_compatible,
            flush=True,
        )

    assert counts == expected, counts
    assert sum(counts.values()) == 170
    assert total_models == 0, total_models
    assert minimum_original_mismatches == 24, minimum_original_mismatches

    positive_class_first = planted_positive("classdest")
    positive_dest_first = planted_positive("destclass")
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("SOURCE_COMPATIBLE_CHRONOLOGIES", sum(counts.values()))
    print("CODEBOOKS_PER_CHRONOLOGY", 36)
    print("CALL_ORDERINGS", 2, "RECORD_BINDINGS", 2, "START_PLACEMENTS", 2)
    print("TOTAL_MODEL_CONFIGURATIONS", 170 * 36 * 2 * 2 * 2)
    print("RECOVER_CONDITIONAL_TWO_WORD_SURVIVORS", total_models)
    print("MINIMUM_95_GAP_TRAINING_MISMATCHES", minimum_original_mismatches)
    print("PLANTED_CLASS_THEN_DEST_POSITIVE", "PASS", "native_draws", positive_class_first)
    print("PLANTED_DEST_THEN_CLASS_POSITIVE", "PASS", "native_draws", positive_dest_first)
    print("AUTHENTIC_K04_BITS_RECOVERED", 0)


if __name__ == "__main__":
    main()
