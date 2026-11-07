"""Post-spool acquisition-order screen for the conditional p951 MT source basis.

Run from the repository root:
    python agents/agent50/k04_pv_postspool_chronology_sft.py

Uses only the original printer spool and HST-4 historian export. It never reads
the selected ESC-N ACK payload, K04 mask/commitment, K08 nonce/commitment, or
any candidate key material. The p951 stage chronology remains a hypothesis.
"""
from __future__ import annotations

import bisect
import hashlib
import importlib.util
import json
import re
from itertools import groupby, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "agents/agent50/k04_pv_early_float_triple_sft.py"
spec = importlib.util.spec_from_file_location("agent50_pv_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

LAST_STAGE = 10_000
POST_START = base.STARTS[-1] + 4  # last four-word packet ends at stage 966
MIN_FIXED_HIGH17 = 12
FULL53 = (1 << 53) - 1
PV_BIN_COUNT = 76_001  # round(12 + 76*r, 3), inclusive 12.000..88.000

TAG_MAPS = (
    {"FT-13": 0, "LT-204": 2, "PT-118": 3, "TT-92": 1},
    {"FT-13": 3, "LT-204": 2, "PT-118": 0, "TT-92": 1},
)
UNIT_MAPS = (
    {"degC": 0, "kPa": 1, "percent": 2},
    {"degC": 2, "kPa": 0, "percent": 1},
)
QUALITY_MAP = {"GOOD": 1, "SUSPECT": 0}


def source_basis(packets: list[bytes], last_stage: int):
    """Build the same source-only 15,365-rank basis with a 624-word ring."""
    total = last_stage - base.ORIGIN + 1
    source_at: dict[int, list[tuple[int, int, bytes]]] = {}
    for row, (packet, pos) in enumerate(zip(packets, base.STARTS)):
        if row == 129:  # whole selected row withheld
            continue
        for lane in range(4):
            source_at.setdefault(pos + lane - base.ORIGIN, []).append(
                (row, lane, packet)
            )

    basis = base.Basis()
    ring = [[1 << (32 * i + j) for j in range(32)] for i in range(624)]

    def add_source_word(index: int, word: list[int]) -> None:
        for row, lane, packet in source_at.get(index, ()):
            native = base.untemper(
                int.from_bytes(packet[4 * lane:4 * lane + 4], "little")
            )
            for bit, vector in enumerate(word):
                basis.insert(vector, (native >> bit) & 1)

    for index in range(min(624, total)):
        add_source_word(index, ring[index])

    for index in range(624, total):
        w0, w1, w397 = ring[0], ring[1], ring[397]
        word = [
            w397[j]
            ^ (w0[31] if j == 30 else (w1[j + 1] if j < 30 else 0))
            ^ (w1[0] if (base.MAG >> j) & 1 else 0)
            for j in range(32)
        ]
        ring = ring[1:] + [word]
        add_source_word(index, word)

    assert basis.rank == 15_365
    return basis


def predict_words(basis, last_stage: int) -> list[tuple[int, int]]:
    """Return (known-value, known-bit-mask) for each tempered native word."""
    total = last_stage - base.ORIGIN + 1
    ring = [[1 << (32 * i + j) for j in range(32)] for i in range(624)]
    outputs: list[tuple[int, int] | None] = [None] * total

    def project(word: list[int]) -> tuple[int, int]:
        value = mask = 0
        for bit, vector in enumerate(base.temper(word)):
            known = basis.predict(vector)
            if known is not None:
                mask |= 1 << bit
                value |= known << bit
        return value, mask

    for index in range(min(624, total)):
        outputs[index] = project(ring[index])

    for index in range(624, total):
        w0, w1, w397 = ring[0], ring[1], ring[397]
        word = [
            w397[j]
            ^ (w0[31] if j == 30 else (w1[j + 1] if j < 30 else 0))
            ^ (w1[0] if (base.MAG >> j) & 1 else 0)
            for j in range(32)
        ]
        ring = ring[1:] + [word]
        outputs[index] = project(word)

    assert all(value is not None for value in outputs)
    return outputs  # type: ignore[return-value]


def pair_projection(outputs, stage: int) -> tuple[int, int]:
    a, am = outputs[stage - base.ORIGIN]
    b, bm = outputs[stage + 1 - base.ORIGIN]
    return ((a >> 5) << 26) | (b >> 6), ((am >> 5) << 26) | (bm >> 6)


def possible_codes(outputs, stage: int, width: int) -> set[int]:
    value, mask = outputs[stage - base.ORIGIN]
    shift = 32 - width
    value = (value >> shift) & ((1 << width) - 1)
    mask = (mask >> shift) & ((1 << width) - 1)
    return {
        code for code in range(1 << width)
        if (code & mask) == value
    }


def high17_known(mask: int) -> int:
    return (mask >> 36).bit_count()


def longest_time_ordered_chain(records: list[dict]) -> tuple[int, list[dict]]:
    """Maximize stage order; records sharing a second may be permuted freely."""
    ordered: list[dict] = []
    for _, group in groupby(
        sorted(records, key=lambda row: (row["ts"], row["seq"])),
        key=lambda row: row["ts"],
    ):
        ordered.extend(sorted(group, key=lambda row: row["stage"]))

    lengths = [1] * len(ordered)
    previous: list[int | None] = [None] * len(ordered)
    for i, row in enumerate(ordered):
        for j in range(i):
            if ordered[j]["stage"] < row["stage"] and lengths[j] + 1 > lengths[i]:
                lengths[i] = lengths[j] + 1
                previous[i] = j

    if not ordered:
        return 0, []
    end = max(range(len(ordered)), key=lengths.__getitem__)
    chain = []
    while end is not None:
        chain.append(ordered[end])
        end = previous[end]
    chain.reverse()
    return len(chain), chain


def call_accept_possible(
    outputs, start: int, width: int, n: int, expected: int, max_rejects: int = 3
) -> tuple[bool, int | None]:
    """Necessary local test for CPython randrange rejection followed by a code."""
    for rejects in range(max_rejects + 1):
        if any(
            not any(code >= n for code in possible_codes(outputs, start + j, width))
            for j in range(rejects)
        ):
            continue
        codes = possible_codes(outputs, start + rejects, width)
        if expected in codes and expected < n:
            return True, rejects
    return False, None


def rejection_aware_local_row(
    outputs, row: dict, stage: int, tag_map: dict, unit_map: dict, quality_map: dict
) -> bool:
    """Loose local over-approximation; tag is accepted at s-1, PV at s/s+1."""
    tag_code = tag_map[row["tag"]]
    if tag_code >= 4 or tag_code not in possible_codes(outputs, stage - 1, 3):
        return False

    quality_ok, quality_rejects = call_accept_possible(
        outputs, stage + 2, 2, 2, quality_map[row["quality"]]
    )
    if not quality_ok:
        return False

    unit_ok, _ = call_accept_possible(
        outputs,
        stage + 3 + quality_rejects,
        2,
        3,
        unit_map[row["unit"]],
    )
    return unit_ok


def fixed_schedule_holdout(
    outputs, pv_rows: list[dict], q_values: dict[int, int]
) -> tuple[int, int, int, int]:
    """Whole-row chronological split for the strict five-word/no-rejection branch.

    Training uses only the first 38 complete timestamp groups. The remaining
    groups are not evaluated unless a training start/codebook survives.
    """
    ordered = sorted(pv_rows, key=lambda row: (row["ts"], row["seq"]))
    groups = []
    index = 0
    for _, group in groupby(ordered, key=lambda row: row["ts"]):
        records = list(group)
        positions = list(range(index, index + len(records)))
        groups.append((positions, records))
        index += len(records)

    train_groups = groups[:38]
    holdout_groups = groups[38:]
    train_rows = sum(len(records) for _, records in train_groups)
    holdout_rows = sum(len(records) for _, records in holdout_groups)
    assert (len(groups), train_rows, holdout_rows) == (75, 59, 53)

    max_start = 3_000
    max_tag_stage = max_start + 5 * 111
    stage_range = range(POST_START, max_tag_stage + 1)
    models = [(tag_map, unit_map, QUALITY_MAP)
              for tag_map in TAG_MAPS for unit_map in UNIT_MAPS]

    def compatibility(records: list[dict], tag_map, unit_map, quality_map):
        by_seq = {}
        for row in records:
            q = q_values[row["seq"]]
            accepted = set()
            for stage in stage_range:
                tag_codes = possible_codes(outputs, stage, 3)
                quality_codes = possible_codes(outputs, stage + 3, 2)
                unit_codes = possible_codes(outputs, stage + 4, 2)
                pv_value, pv_mask = pair_projection(outputs, stage + 1)
                if (
                    tag_map[row["tag"]] in tag_codes
                    and tag_map[row["tag"]] < 4
                    and base.compatible(q, pv_value, pv_mask)
                    and quality_map[row["quality"]] in quality_codes
                    and quality_map[row["quality"]] < 2
                    and unit_map[row["unit"]] in unit_codes
                    and unit_map[row["unit"]] < 3
                ):
                    accepted.add(stage)
            by_seq[row["seq"]] = accepted
        return by_seq

    def group_passes(group, start_stage: int, by_seq) -> bool:
        positions, records = group
        slots = [start_stage + 5 * position for position in positions]
        return any(
            all(slot in by_seq[row["seq"]] for slot, row in zip(slots, order))
            for order in permutations(records)
        )

    candidates = []
    for model_index, (tag_map, unit_map, quality_map) in enumerate(models):
        train_compat = compatibility(
            [row for _, records in train_groups for row in records],
            tag_map, unit_map, quality_map
        )
        for start_stage in range(POST_START, max_start + 1):
            if all(
                group_passes(group, start_stage, train_compat)
                for group in train_groups
            ):
                candidates.append((model_index, start_stage))

    holdout_survivors = 0
    if candidates:
        for model_index, start_stage in candidates:
            tag_map, unit_map, quality_map = models[model_index]
            holdout_compat = compatibility(
                [row for _, records in holdout_groups for row in records],
                tag_map, unit_map, quality_map
            )
            if all(
                group_passes(group, start_stage, holdout_compat)
                for group in holdout_groups
            ):
                holdout_survivors += 1

    return train_rows, holdout_rows, len(candidates), holdout_survivors


def main() -> None:
    spool = base.SPOOL.read_bytes()
    historian = base.HIST.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == base.SPOOL_PIN
    assert hashlib.sha256(historian).hexdigest() == base.HIST_PIN

    packets = [
        bytes.fromhex(value.decode())
        for value in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)
    ]
    assert len(packets) == len(base.STARTS) == 133

    pv = [
        row for row in map(json.loads, historian.splitlines())
        if row["field"] == "PV"
    ]
    assert len(pv) == 112
    assert {row["seq"] for row in pv} == set(range(100, 212))
    assert all(row["state"] == "RUN" and row["revision"] == 1 for row in pv)

    basis = source_basis(packets, LAST_STAGE)
    outputs = predict_words(basis, LAST_STAGE)
    q_values = {row["seq"]: round(row["value"] * 1000) for row in pv}

    # Whole-record chronological training/holdout test for the strict five-word
    # no-rejection branch. The final 53 rows are not used unless training fits.
    train_rows, holdout_rows, train_candidates, holdout_survivors = fixed_schedule_holdout(
        outputs, pv, q_values
    )
    assert (train_rows, holdout_rows, train_candidates, holdout_survivors) == (59, 53, 0, 0)

    # Regression control: reproduce the five high-information matches in the
    # original -2000..1038 window before extending beyond the final packet.
    pre_matches = []
    for stage in range(base.ORIGIN, 1039):
        value, mask = pair_projection(outputs, stage)
        if high17_known(mask) < MIN_FIXED_HIGH17:
            continue
        for row in pv:
            if base.compatible(q_values[row["seq"]], value, mask):
                pre_matches.append((row["seq"], stage))
    assert sorted(pre_matches) == [
        (175, -1567), (176, -1560), (177, -1553), (198, 17), (103, 202)
    ]

    eligible = 0
    post_matches: list[dict] = []
    fully_predicted: list[tuple[int, float, int, int]] = []
    for stage in range(POST_START, LAST_STAGE):
        value, mask = pair_projection(outputs, stage)
        fixed = high17_known(mask)
        if fixed < MIN_FIXED_HIGH17:
            continue
        eligible += 1

        # A rounded value is fully determined if every completion of the
        # masked 53-bit output falls inside the same 0.001 PV bin.
        low = value & mask
        high = value | (FULL53 ^ mask)
        q_low = round(12 + 76 * (low / (1 << 53)), 3)
        q_high = round(12 + 76 * (high / (1 << 53)), 3)
        if q_low == q_high:
            fully_predicted.append((stage, q_low, mask.bit_count(), fixed))

        for row in pv:
            if base.compatible(q_values[row["seq"]], value, mask):
                post_matches.append({
                    "seq": row["seq"],
                    "ts": row["ts"],
                    "tag": row["tag"],
                    "pv": row["value"],
                    "unit": row["unit"],
                    "quality": row["quality"],
                    "stage": stage,
                    "fixed53": mask.bit_count(),
                    "fixed_high17": fixed,
                })

    post_matches.sort(key=lambda row: (row["ts"], row["seq"]))
    observed = [(row["seq"], row["stage"]) for row in post_matches]
    expected = [
        (154, 1823), (193, 2833), (158, 1848), (175, 1440),
        (180, 2099), (190, 2855), (140, 2101), (127, 5193),
        (112, 2130), (151, 1291), (196, 2094), (106, 1757),
        (115, 6410), (120, 1099),
    ]
    assert observed == expected
    assert len({row["seq"] for row in post_matches}) == 14
    assert eligible == 712

    unique_bins = {q for _, q, _, _ in fully_predicted}
    observed_bins = {round(row["value"], 3) for row in pv}
    matched_unique_bins = unique_bins & observed_bins
    assert len(fully_predicted) == 387
    assert len(unique_bins) == 386
    assert matched_unique_bins == {19.319}
    assert [(stage, q) for stage, q, _, _ in fully_predicted if q in matched_unique_bins] == [
        (1823, 19.319)
    ]
    crude_uniform_bin_expectation = len(unique_bins) * len(pv) / PV_BIN_COUNT

    chain_length, chain = longest_time_ordered_chain(post_matches)
    assert chain_length == 6

    # Strict adjacent-field screen for the four previously selected metadata
    # codebooks: tag at s-1, PV double at s/s+1, quality at s+2, unit at s+3.
    field_counts = []
    for tag_map in TAG_MAPS:
        for unit_map in UNIT_MAPS:
            passed = []
            for row in post_matches:
                stage = row["stage"]
                tag_codes = possible_codes(outputs, stage - 1, 3)
                quality_codes = possible_codes(outputs, stage + 2, 2)
                unit_codes = possible_codes(outputs, stage + 3, 2)
                if (
                    tag_map[row["tag"]] in tag_codes
                    and tag_map[row["tag"]] < 4
                    and QUALITY_MAP[row["quality"]] in quality_codes
                    and QUALITY_MAP[row["quality"]] < 2
                    and unit_map[row["unit"]] in unit_codes
                    and unit_map[row["unit"]] < 3
                ):
                    passed.append(row["seq"])
            field_counts.append(len(passed))
    assert field_counts == [7, 6, 7, 6]

    # More permissive rejection-aware local screen across all 288 global
    # category codebooks. It remains an over-approximation, not a joint fit.
    tag_names = sorted({row["tag"] for row in pv})
    unit_names = sorted({row["unit"] for row in pv})
    quality_names = sorted({row["quality"] for row in pv})
    assert (len(tag_names), len(unit_names), len(quality_names)) == (4, 3, 2)
    rejection_counts = []
    for tag_codes in permutations(range(4)):
        tag_map = dict(zip(tag_names, tag_codes))
        for unit_codes in permutations(range(3)):
            unit_map = dict(zip(unit_names, unit_codes))
            for quality_codes in permutations(range(2)):
                quality_map = dict(zip(quality_names, quality_codes))
                passed = sum(
                    any(
                        rejection_aware_local_row(
                            outputs, row, candidate["stage"],
                            tag_map, unit_map, quality_map
                        )
                        for candidate in post_matches
                        if candidate["seq"] == row["seq"]
                    )
                    for row in pv
                    if row["seq"] in {candidate["seq"] for candidate in post_matches}
                )
                rejection_counts.append(passed)
    assert len(rejection_counts) == 288
    assert max(rejection_counts) == 12
    assert rejection_counts.count(12) == 30

    print("source pins: PASS")
    print(f"original packets: {len(packets)}; selected row129 withheld")
    print(f"p951 source-basis rank: {basis.rank}")
    print(f"post-spool stage starts: {POST_START}..{LAST_STAGE - 1}")
    print(f"eligible stages with >=12 fixed high17 bits: {eligible}")
    print(f"post-spool PV matches: {len(post_matches)} / 112")
    print(f"fixed five-word whole-record split: train={train_rows}, holdout={holdout_rows}, "
          f"training candidates={train_candidates}, holdout survivors={holdout_survivors}")
    print(f"fully determined PV bins: {len(fully_predicted)} stage projections, "
          f"{len(unique_bins)} distinct bins, observed intersection={sorted(matched_unique_bins)}")
    print(f"crude uniform-bin expectation for full-bin hits: {crude_uniform_bin_expectation:.3f}")
    print(f"maximum acquisition-time-ordered stage chain: {chain_length} / 14")
    print("four prior adjacent-field codebook screens:", field_counts)
    print(f"rejection-aware local codebooks: max={max(rejection_counts)}/14, "
          f"maps attaining max={rejection_counts.count(12)}/288")
    print("post-spool matches (seq, UTC, stage, fixed53, fixed_high17):")
    for row in post_matches:
        print(
            row["seq"], row["ts"], row["stage"],
            row["fixed53"], row["fixed_high17"]
        )
    print("maximal chronological chain:")
    for row in chain:
        print(row["seq"], row["ts"], row["stage"])


if __name__ == "__main__":
    main()
