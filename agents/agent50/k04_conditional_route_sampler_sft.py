"""K04 exploratory SFT: conditional printer-route randbelow(3) call.

Source cue: archive-labels.ini and the print-fleet retirement register name
three logical printer routes (ESC-N, ESC-S, WATCH-SPARE). Test whether a third
randbelow(3) route selection is consumed only for CLASS=RECOVER jobs, after
CLASS has been selected. The selected PS-0417 ACK2 payload is withheld.

The route labels for PS-0417/0448/0420 are source-authored holdouts. This is a
bounded exploratory producer hypothesis, not an assertion about historical
firmware or an authenticated K04 reconstruction.

Run from the repository root:
    python agents/agent50/k04_conditional_route_sampler_sft.py
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
ROUTE_NAMES = ("ESC-N", "ESC-S", "WATCH-SPARE")
ORDERS = ("class_route_dest", "class_dest_route", "dest_class_route")
EXPECTED_CHRONOLOGIES = {950: 35, 951: 28, 952: 25, 953: 21, 954: 31, 955: 30}


def possible_pairs(gap: list[set[int]], at_first: bool,
                   class_first: bool) -> set[tuple[int, int]]:
    """Possible visible class/dest accepted codes when route is not sampled."""
    pairs: set[tuple[int, int]] = set()
    for first in range(len(gap)):
        if at_first and any(3 not in gap[k] for k in range(first)):
            break
        for first_code in gap[first] - {3}:
            for second in range(first + 1, len(gap)):
                if any(3 not in gap[k] for k in range(first + 1, second)):
                    break
                for second_code in gap[second] - {3}:
                    pairs.add((first_code, second_code) if class_first
                              else (second_code, first_code))
    return pairs


def possible_triples(gap: list[set[int]], at_first: bool,
                     order: str) -> set[tuple[int, int, int]]:
    """Possible accepted codes in the actual sampler call order.

    Every randbelow(3) attempt emits a two-bit code: 3 is rejected, 0..2 is
    accepted. Between calls only rejected attempts are allowed. Arbitrary
    leading filler is allowed only when at_first=False; trailing filler is
    unrestricted.
    """
    triples: set[tuple[int, int, int]] = set()
    for first in range(len(gap)):
        if at_first and any(3 not in gap[k] for k in range(first)):
            break
        for a in gap[first] - {3}:
            for second in range(first + 1, len(gap)):
                if any(3 not in gap[k] for k in range(first + 1, second)):
                    break
                for b in gap[second] - {3}:
                    for third in range(second + 1, len(gap)):
                        if any(3 not in gap[k] for k in range(second + 1, third)):
                            break
                        for c in gap[third] - {3}:
                            if order not in ORDERS:
                                raise AssertionError(order)
                            triples.add((a, b, c))
    return triples


def source_route_rows(lines: list[str]) -> dict[int, str]:
    """Read the three source-defined job-to-cassette assignments."""
    route_text = (ROOT / "resources/evidence/archive-labels.ini").read_text()
    fleet_text = (ROOT / "resources/evidence/h17-supplemental-office-files/"
                  "print-fleet-retirement-note.txt").read_text()
    section = re.search(
        r"(?ms)^\\[printer_routes_2026-09-01_to_2026-10-03\\]\\s*(.*?)(?=^\\[|\\Z)",
        route_text
    )
    assert section, "missing incident-date printer route section"
    route_to_job = dict(re.findall(
        r"^(ESC-N|ESC-S|WATCH-SPARE)=(PS-[0-9-]+)$",
        section.group(1), flags=re.MULTILINE
    ))
    expected = {
        "ESC-N": "PS-261003-0417",
        "ESC-S": "PS-261003-0448",
        "WATCH-SPARE": "PS-261003-0420",
    }
    assert route_to_job == expected, route_to_job
    for route, job in expected.items():
        assert job in fleet_text and route in fleet_text
    row_by_job = {}
    for index, line in enumerate(lines):
        job = re.search(r"JOB=(PS-[0-9-]+)", line).group(1)
        row_by_job[job] = index
    out = {row_by_job[job]: route for route, job in expected.items()}
    assert out == {129: "ESC-N", 131: "ESC-S", 132: "WATCH-SPARE"}, out
    return out


def evaluate(starts, domains, labels, route_by_row, train_limit=LIMIT,
             keep_all_examples=False):
    """Fit CLASS/DEST codebooks, then test held-out source route assignments."""
    gaps = [
        domains[starts[row] + 4:starts[row + 1]]
        for row in range(132)
    ]
    pair_cache = {
        (at_first, class_first): [
            possible_pairs(gap, at_first, class_first) for gap in gaps
        ]
        for at_first in (True, False)
        for class_first in (True, False)
    }
    triple_cache = {
        (at_first, order): [
            possible_triples(gap, at_first, order) for gap in gaps
        ]
        for at_first in (True, False)
        for order in ORDERS
    }

    survivors = []
    best_training = train_limit + 1
    models_zero_train = 0
    models_zero_holdout = 0
    route_codebook_survivors = 0
    class_list = sorted({name for name, _ in labels[:128]})
    dest_list = sorted({name for _, name in labels[:128]})
    assert tuple(class_list) == tuple(sorted(CLASS_NAMES))
    assert tuple(dest_list) == tuple(sorted(DEST_NAMES))

    for order in ORDERS:
        class_first = order != "dest_class_route"
        for at_first, binding in itertools.product((True, False), ("current", "next")):
            for class_codes in itertools.permutations(range(3)):
                class_lookup = dict(zip(class_list, class_codes))
                for dest_codes in itertools.permutations(range(3)):
                    dest_lookup = dict(zip(dest_list, dest_codes))
                    actual = []
                    allowed = []
                    for gap_index in range(127):
                        meta_row = gap_index + (binding == "next")
                        cls, dest = labels[meta_row]
                        pair = (class_lookup[cls], dest_lookup[dest])
                        actual.append(pair)
                        if cls == "RECOVER":
                            triplets = triple_cache[(at_first, order)][gap_index]
                            if order == "class_route_dest":
                                allowed.append({(a, c) for a, _, c in triplets})
                            elif order == "class_dest_route":
                                allowed.append({(a, b) for a, b, _ in triplets})
                            else:
                                allowed.append({(b, a) for a, b, _ in triplets})
                        else:
                            allowed.append(
                                pair_cache[(at_first, class_first)][gap_index]
                            )

                    errors = sum(actual[g] not in allowed[g]
                                 for g in range(train_limit))
                    best_training = min(best_training, errors)
                    if errors:
                        continue
                    models_zero_train += 1
                    holdout_errors = sum(
                        actual[g] not in allowed[g]
                        for g in range(train_limit, 127)
                    )
                    if holdout_errors:
                        continue
                    models_zero_holdout += 1

                    # The route codebook is deliberately learned only from the
                    # three source-authored late route labels, not ordinary rows.
                    for route_codes in itertools.permutations(range(3)):
                        route_lookup = dict(zip(ROUTE_NAMES, route_codes))
                        route_ok = True
                        for row, route in route_by_row.items():
                            gap_index = row - 1 if binding == "next" else row
                            if not (0 <= gap_index < 132):
                                continue
                            cls, dest = labels[row]
                            if cls != "RECOVER":
                                route_ok = False
                                break
                            triple = {
                                "class_route_dest": (
                                    class_lookup[cls], route_lookup[route],
                                    dest_lookup[dest]
                                ),
                                "class_dest_route": (
                                    class_lookup[cls], dest_lookup[dest],
                                    route_lookup[route]
                                ),
                                "dest_class_route": (
                                    dest_lookup[dest], class_lookup[cls],
                                    route_lookup[route]
                                ),
                            }[order]
                            if triple not in triple_cache[(at_first, order)][gap_index]:
                                route_ok = False
                                break
                        if route_ok:
                            route_codebook_survivors += 1
                            if keep_all_examples or len(survivors) < 30:
                                survivors.append({
                                    "order": order,
                                    "binding": binding,
                                    "at_first": at_first,
                                    "class_codes": class_codes,
                                    "dest_codes": dest_codes,
                                    "route_codes": route_codes,
                                    "late_route_rows_checked": sum(
                                        1 for row in route_by_row
                                        if (row - 1 if binding == "next" else row) < 132
                                    ),
                                })

    return {
        "best_training_mismatches": best_training,
        "zero_training_models": models_zero_train,
        "zero_holdout_models": models_zero_holdout,
        "route_codebook_survivors": route_codebook_survivors,
        "examples": survivors,
    }


def sample_below3(rng: random.Random):
    draws = 0
    while True:
        value = rng.getrandbits(2)
        draws += 1
        if value < 3:
            return value, draws


def planted_positive(order: str):
    """Full seeded CPython MT control with conditional route sampling."""
    for seed in range(1000, 11000):
        rng = random.Random(seed)
        starts, rows, labels = [], [], []
        route_codes_by_row = {}
        stage = 0
        class_to_name = {0: "LABEL", 1: "RECOVER", 2: "STORES"}
        dest_to_name = {0: "bench", 1: "desk", 2: "store"}
        for row in range(133):
            if row:
                if order == "class_route_dest":
                    cls, n = sample_below3(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3(rng); stage += n
                    dest, n = sample_below3(rng); stage += n
                elif order == "class_dest_route":
                    cls, n = sample_below3(rng); stage += n
                    dest, n = sample_below3(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3(rng); stage += n
                elif order == "dest_class_route":
                    dest, n = sample_below3(rng); stage += n
                    cls, n = sample_below3(rng); stage += n
                    route = None
                    if cls == 1:
                        route, n = sample_below3(rng); stage += n
                else:
                    raise AssertionError(order)
                labels.append((class_to_name[cls], dest_to_name[dest]))
                if route is not None:
                    route_codes_by_row[row] = route
            else:
                labels.append(("LABEL", "bench"))
            starts.append(stage)
            if row == 129:
                rows.append([])  # withhold target packet completely
            else:
                rows.append([mt.untemper(rng.getrandbits(32)) for _ in range(4)])
            stage += 4

        late_codes = [route_codes_by_row.get(r) for r in (129, 131, 132)]
        if None in late_codes or len(set(late_codes)) != 3:
            continue
        if set(name for name, _ in labels[:128]) != set(CLASS_NAMES):
            continue
        if set(name for _, name in labels[:128]) != set(DEST_NAMES):
            continue
        code_to_route = dict(zip(late_codes, ROUTE_NAMES))
        route_by_row = {r: code_to_route[c] for r, c in route_codes_by_row.items()
                        if r in (129, 131, 132)}
        expressions = mt.state_expressions(stage + 3)
        basis = six.build_source_basis(expressions, rows, starts)
        domains = joint.top_two_domains(expressions, basis)
        result = evaluate(starts, domains, labels, route_by_row,
                          keep_all_examples=True)
        assert result["best_training_mismatches"] == 0, (order, result)
        assert result["zero_training_models"] > 0, (order, result)
        assert result["zero_holdout_models"] > 0, (order, result)
        assert result["route_codebook_survivors"] > 0, (order, result)
        # The planted order and source-derived route map must be represented.
        planted_class_codes = (0, 1, 2)
        planted_dest_codes = (0, 1, 2)
        planted_route_codes = tuple(
            {v: k for k, v in code_to_route.items()}[name] for name in ROUTE_NAMES
        )
        assert any(
            x["order"] == order
            and x["binding"] == "next"
            and x["at_first"] is True
            and x["class_codes"] == planted_class_codes
            and x["dest_codes"] == planted_dest_codes
            and x["route_codes"] == planted_route_codes
            for x in result["examples"]
        ), (order, result["examples"])
        print("PLANTED_CONDITIONAL_ROUTE_POSITIVE", order, "PASS",
              "seed", seed, "native_draws", stage,
              "route_rows", route_by_row, flush=True)
        return
    raise AssertionError(f"no seeded positive with distinct late route codes for {order}")


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
    route_by_row = source_route_rows(lines)
    assert all(labels[row][0] == "RECOVER" for row in route_by_row)

    for order in ORDERS:
        planted_positive(order)

    expressions = mt.state_expressions(
        max(starts[-1] for starts in six.GEOMETRIES.values()) + 3
    )
    counts = {}
    aggregate = {
        "best_training_mismatches": LIMIT + 1,
        "zero_training_models": 0,
        "zero_holdout_models": 0,
        "route_codebook_survivors": 0,
        "examples": [],
    }
    for selected_stage, baseline in sorted(six.GEOMETRIES.items()):
        accepted = 0
        for group, shift in [(-1, 0)] + [
            (g, delta) for g in range(81) for delta in (-2, -1, 1, 2)
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
            result = evaluate(starts, domains, labels, route_by_row)
            aggregate["best_training_mismatches"] = min(
                aggregate["best_training_mismatches"],
                result["best_training_mismatches"]
            )
            for key in ("zero_training_models", "zero_holdout_models",
                        "route_codebook_survivors"):
                aggregate[key] += result[key]
            if len(aggregate["examples"]) < 30:
                aggregate["examples"].extend(result["examples"])
        counts[selected_stage] = accepted
        print("GEOMETRY", selected_stage, "SOURCE_COMPATIBLE", accepted, flush=True)

    assert counts == EXPECTED_CHRONOLOGIES, counts
    print("ORIGINAL_SPOOL_SHA256", mt.SOURCE_SHA)
    print("SOURCE_ROUTE_ROWS", route_by_row)
    print("SOURCE_COMPATIBLE_CHRONOLOGIES", sum(counts.values()))
    print("MODEL_SCOPE", "two randbelow(3) calls; conditional route randbelow(3) only on RECOVER")
    print("ROUTE_CALL_ORDERS", ORDERS)
    print("METADATA_BINDINGS", ("current", "next"))
    print("LEADING_PLACEMENTS", ("at_first", "arbitrary_prefix"))
    print("TRAINING_GAPS", LIMIT, "HOLDOUT_GAPS", 32)
    print("BEST_TRAINING_MISMATCHES", aggregate["best_training_mismatches"])
    print("ZERO_TRAINING_MODELS", aggregate["zero_training_models"])
    print("ZERO_HOLDOUT_MODELS", aggregate["zero_holdout_models"])
    print("SOURCE_ROUTE_CODEBOOK_SURVIVORS", aggregate["route_codebook_survivors"])
    print("EXAMPLES", aggregate["examples"])
    print("SELECTED_ACK2_PAYLOAD_DECODED", "NO")
    print("K04_MASK_OR_COMMITMENT_LOADED", "NO")
    print("AUTHENTIC_K04_BITS_RECOVERED", 0)


if __name__ == "__main__":
    main()
