"""SFT: jointly test one-root printer MT chronologies and two categorical calls.

Original PS-0417 ACK2 bytes and all K04 commitments are excluded. Uses the
source-pinned MT expressions and 81-component chronology from Agent44.
Run from the workplace-v2 repository root:
    python agents/agent6/k04_one_root_joint_metadata_sft.py
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent44"))
import k04_single_root_perturbations_sft as chronology
import k04_six_stage_sft as six
import k04_p951_hidden_stage_coupon_sft as mt


def top_two_domains(expressions, basis):
    """Optimistic allowed randbelow(3) getrandbits(2) outputs at each stage."""
    domains = []
    for bits in expressions:
        tempered = chronology.tempered_bits(bits)
        lo = mt.reduce_row(tempered[30] << 1, basis)
        hi = mt.reduce_row(tempered[31] << 1, basis)
        lows = (lo,) if lo <= 1 else (0, 1)
        highs = (hi,) if hi <= 1 else (0, 1)
        domains.append({int(low) + 2 * int(high) for low in lows for high in highs})
    return domains


def consecutive_sampler_pairs(domains, at_first):
    """Consecutive randbelow(3) calls, each with zero or more rejected code 3.

    at_first=True requires the first call to begin at the first hidden word.
    False allows arbitrary unrelated draws before/after the pair, but no such
    filler between these two consecutive sampler calls. The domains deliberately
    ignore correlations among unresolved generator bits, yielding a safe superset.
    """
    pairs = set()
    for first in range(len(domains)):
        if at_first and any(3 not in domains[k] for k in range(first)):
            break
        for first_code in domains[first] - {3}:
            for second in range(first + 1, len(domains)):
                if any(3 not in domains[k] for k in range(first + 1, second)):
                    break
                for second_code in domains[second] - {3}:
                    pairs.add((first_code, second_code))
    return pairs


def source_metadata_models(starts, domains, labels, at_first, record_binding, order, limit=95):
    """Return static class/dest codebooks fitting the first limit gap labels."""
    classes = sorted({name for name, _ in labels[:128]})
    destinations = sorted({name for _, name in labels[:128]})
    assert len(classes) == len(destinations) == 3
    allowed = []
    for row in range(127):
        gap = domains[starts[row] + 4:starts[row + 1]]
        pairs = consecutive_sampler_pairs(gap, at_first)
        if order == "destclass":
            pairs = {(b, a) for a, b in pairs}
        allowed.append(pairs)

    survivors = []
    minimum_training_mismatches = limit + 1
    for class_codes in itertools.permutations(range(3)):
        class_lookup = dict(zip(classes, class_codes))
        for dest_codes in itertools.permutations(range(3)):
            dest_lookup = dict(zip(destinations, dest_codes))
            actual = [
                (class_lookup[labels[row + (record_binding == "next")][0]],
                 dest_lookup[labels[row + (record_binding == "next")][1]])
                for row in range(127)
            ]
            mismatches = sum(actual[row] not in allowed[row] for row in range(limit))
            minimum_training_mismatches = min(minimum_training_mismatches, mismatches)
            if mismatches == 0:
                holdout_errors = tuple(row for row in range(limit, 127)
                                       if actual[row] not in allowed[row])
                survivors.append((class_codes, dest_codes, holdout_errors))
    return survivors, minimum_training_mismatches


def planted_positive():
    """Real CPython randbelow(3) output with actual variable rejection count."""
    rng = random.Random(39117)
    classes = ("LABEL", "RECOVER", "STORES")
    destinations = ("bench", "desk", "store")
    starts, rows, labels = [], [], []
    stage = 0
    for row in range(128):
        if row:
            choices = []
            for _ in range(2):
                while True:
                    code = rng.getrandbits(2)
                    stage += 1
                    if code < 3:
                        choices.append(code)
                        break
            labels.append((classes[choices[0]], destinations[choices[1]]))
        else:
            labels.append((classes[0], destinations[0]))
        starts.append(stage)
        rows.append([mt.untemper(rng.getrandbits(32)) for _ in range(4)])
        stage += 4
    expressions = mt.state_expressions(stage + 3)
    basis = six.build_source_basis(expressions, rows, starts)
    projected = top_two_domains(expressions, basis)
    survivors, minimum = source_metadata_models(starts, projected, labels, True, "next", "classdest")
    assert minimum == 0
    assert any(class_codes == (0, 1, 2) and dest_codes == (0, 1, 2) and not errors
               for class_codes, dest_codes, errors in survivors)
    print("SYNTHETIC_GENUINE_CPYTHON_128_ROWS", "PASS",
          "native_draws", stage, "writer_models", len(survivors))


def main():
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == mt.SOURCE_SHA
    lines, rows, selected, _ = mt.source_rows(raw, root)
    assert selected == 129 and len(lines) == len(rows) == 133
    labels = []
    for line in lines:
        labels.append((re.search(r"CLASS=(\S+)", line).group(1),
                       re.search(r"DEST=(\S+)", line).group(1)))
    # No candidate, copied selected payload, K04 mask, or commitment is loaded.
    expressions = mt.state_expressions(max(starts[-1] for starts in six.GEOMETRIES.values()) + 3)

    counts = {}
    complete_original_models = 0
    minimum_original_mismatches = 96
    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        source_compatible = 0
        for component, delta in [(-1, 0)] + [
            (group, shift) for group in range(81) for shift in (-2, -1, 1, 2)
        ]:
            starts = [start + (delta if chronology.GROUPS[row] == component else 0)
                      for row, start in enumerate(baseline)]
            if not chronology.physical(starts, selected_stage):
                continue
            if chronology.impossible_threeword(starts, rows):
                continue
            try:
                basis = six.build_source_basis(expressions, rows, starts)
            except AssertionError:
                continue
            source_compatible += 1
            domains = top_two_domains(expressions, basis)
            for at_first, binding, call_order in itertools.product(
                (True, False), ("current", "next"), ("classdest", "destclass")
            ):
                models, minimum = source_metadata_models(starts, domains, labels,
                                                         at_first, binding, call_order)
                complete_original_models += len(models)
                minimum_original_mismatches = min(minimum_original_mismatches, minimum)
        counts[selected_stage] = source_compatible
        print("GEOMETRY", selected_stage, "SOURCE_COMPATIBLE", source_compatible)

    assert counts == {950:35, 951:28, 952:25, 953:21, 954:31, 955:30}, counts
    assert complete_original_models == 0, complete_original_models
    assert minimum_original_mismatches == 13, minimum_original_mismatches
    planted_positive()
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("SOURCE_COMPATIBLE_CHRONOLOGIES", sum(counts.values()))
    print("STATIC_THREEWAY_CODEBOOKS_PER_MODEL", 36)
    print("METADATA_ARCHITECTURES_PER_CHRONOLOGY", 8)
    print("FULL_95_GAP_TRAINING_MODEL_SURVIVORS", complete_original_models)
    print("MIN_95_GAP_TRAINING_MISMATCHES", minimum_original_mismatches)
    print("HOLDOUT_32_GAPS", "no model reached holdout")
    print("AUTHENTIC_K04_BITS", 0)


if __name__ == "__main__":
    main()
