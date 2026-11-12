"""All-21 source-compatible chronology extension of the K04 gap donor screen.

Run from the repository root:
    python agents/agent43/k04_unique_gap_source_blocks_all_21_sft.py

The selected printer row is withheld by the p951 packet helper. The K04 mask
and acceptance hash are accessed only after all candidate payloads are fixed.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent23"))
sys.path.insert(0, str(ROOT / "agents" / "agent43"))
sys.path.insert(0, str(ROOT / "agents" / "agent49"))

from k04_mt_stagefree_gap_bounds_sft import relations
from k04_p951_symbolic_basis import Basis, STARTS, get, packets, untemper, words, temper
from k04_late_component_target_quotient_sft import components, source_rank_and_target_quotient
from k04_unique_gap_source_block_pair_sft import read_blocks, reduce_source, insert_small, reduce_small


def reduce_no_rhs(rows, value):
    remainder = 0
    while value:
        pivot = value.bit_length() - 1
        if pivot in rows:
            value ^= rows[pivot][0]
        else:
            remainder |= 1 << pivot
            value ^= 1 << pivot
    return remainder


def rank_after_pair(bank_a, bank_b, target):
    rows = {}
    for value in bank_a + bank_b:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = value
                break
            value ^= rows[pivot]
    residual = {}
    for value in target:
        while value:
            pivot = value.bit_length() - 1
            if pivot in rows:
                value ^= rows[pivot]
            elif pivot in residual:
                value ^= residual[pivot]
            else:
                residual[pivot] = value
                break
    return len(residual)


def build_basis(starts, original, symbolic):
    basis = Basis()
    for row, packet in enumerate(original):
        if row == 129:
            continue
        for lane in range(4):
            native = untemper(int.from_bytes(packet[4*lane:4*lane+4], "little"))
            for bit, expression in enumerate(get(symbolic, starts[row] + lane)):
                basis.insert(expression, (native >> bit) & 1)
    assert basis.rank == 15365
    return basis


def block_interpretations(blocks):
    result = {}
    for name, block in blocks.items():
        result[name] = {}
        for endian in ("little", "big"):
            for representation in ("tempered", "native"):
                words = []
                for lane in range(4):
                    value = int.from_bytes(block[4*lane:4*lane+4], endian)
                    words.append(untemper(value) if representation == "tempered" else value)
                result[name][(endian, representation)] = words
    return result


def main():
    route, blocks = read_blocks()
    original, selected = packets(ROOT)
    assert selected == 129 and len(original) == 133 and original[129] == b""
    source_path = ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log"
    edges = relations(source_path.read_bytes())
    assert len(edges) == 49

    groups, find = components(edges)
    focus = [groups[find(row)] for row in (127, 128, 129, 130, 132)]
    assert len({tuple(group) for group in focus}) == 5
    baseline = STARTS[:]
    symbolic = words()
    assert source_rank_and_target_quotient(baseline, original, symbolic) == (15365, 128, 0)

    admissible = []
    compatible = []
    for shifts in product(range(-3, 4), repeat=5):
        starts = baseline[:]
        for group, step in zip(focus, shifts):
            for row in group:
                starts[row] += step
        if starts[0] != 0 or any(b-a < 4 for a, b in zip(starts, starts[1:])):
            continue
        assert all(starts[b] - starts[a] == delta for a, b, delta in edges)
        admissible.append((shifts, starts))
        quotient = source_rank_and_target_quotient(starts, original, symbolic)
        if quotient is not None:
            compatible.append((shifts, starts, quotient))

    assert len(admissible) == 196
    assert len(compatible) == 21
    stage_counts = Counter(starts[129] for shifts, starts, quotient in compatible)
    assert stage_counts == {950: 6, 951: 9, 952: 6}
    assert all(q == (15365, 128, 0) for shifts, starts, q in compatible)

    interpretations = block_interpretations(blocks)
    candidate_payloads = []
    schedule_summary = []
    complete_pairs_total = 0
    no_pair_schedules = 0
    inconsistent = 0
    underdetermined = 0

    for shifts, starts, quotient in compatible:
        basis = build_basis(starts, original, symbolic)
        gap_starts = []
        for row in range(132):
            if row in (128, 129):
                continue
            gap_starts.extend(range(starts[row] + 4, starts[row+1] - 3))

        bank = {
            gap: [
                reduce_no_rhs(basis.rows, expression)
                for stage in range(gap, gap+4)
                for expression in get(symbolic, stage)
            ]
            for gap in gap_starts
        }
        target_native = [
            reduce_no_rhs(basis.rows, expression)
            for stage in range(starts[129], starts[129]+4)
            for expression in get(symbolic, stage)
        ]
        complete_pairs = [
            (a, b) for a, b in combinations(gap_starts, 2)
            if rank_after_pair(bank[a], bank[b], target_native) == 0
        ]
        assert len(complete_pairs) <= 1
        if not complete_pairs:
            no_pair_schedules += 1
            schedule_summary.append({
                "shifts": shifts, "target_stage": starts[129],
                "gap_windows": len(gap_starts), "complete_pair": None,
                "candidate_models": 0,
            })
            continue

        complete_pairs_total += 1
        pair = complete_pairs[0]
        donor_stages = (
            list(range(pair[0], pair[0]+4))
            + list(range(pair[1], pair[1]+4))
        )
        donor_forms = {
            stage: [
                reduce_source(basis.rows, expression)
                for expression in get(symbolic, stage)
            ]
            for stage in donor_stages
        }
        target_forms = [
            reduce_source(basis.rows, expression)
            for stage in range(starts[129], starts[129]+4)
            for expression in temper(get(symbolic, stage))
        ]

        model_count = 0
        names = list(blocks)
        for name_a, name_b in combinations(names, 2):
            for endian_a, rep_a, endian_b, rep_b in product(
                ("little", "big"), ("tempered", "native"),
                ("little", "big"), ("tempered", "native"),
            ):
                for swapped in (False, True):
                    assigned = (
                        ((name_b, endian_b, rep_b), (name_a, endian_a, rep_a))
                        if swapped else
                        ((name_a, endian_a, rep_a), (name_b, endian_b, rep_b))
                    )
                    small = {}
                    valid = True
                    for block_index, (name, endian, representation) in enumerate(assigned):
                        words_for_block = interpretations[name][(endian, representation)]
                        for lane, native_word in enumerate(words_for_block):
                            stage = donor_stages[block_index*4 + lane]
                            for bit, (residual, offset) in enumerate(donor_forms[stage]):
                                if not insert_small(small, residual, ((native_word >> bit) & 1) ^ offset):
                                    valid = False
                                    break
                            if not valid:
                                break
                        if not valid:
                            break
                    if not valid:
                        inconsistent += 1
                        continue

                    payload = bytearray()
                    fixed = True
                    for lane in range(4):
                        word = 0
                        for bit in range(32):
                            residual, offset = target_forms[lane*32 + bit]
                            residual, value = reduce_small(small, residual, offset)
                            if residual:
                                fixed = False
                                break
                            word |= value << bit
                        if not fixed:
                            break
                        payload.extend(word.to_bytes(4, "little"))
                    if not fixed:
                        underdetermined += 1
                        continue

                    model_count += 1
                    candidate_payloads.append((
                        shifts, starts[129], pair, name_a, endian_a, rep_a,
                        name_b, endian_b, rep_b, swapped, bytes(payload)
                    ))

        assert model_count == 1760, (shifts, pair, model_count)
        schedule_summary.append({
            "shifts": shifts, "target_stage": starts[129],
            "gap_windows": len(gap_starts), "complete_pair": pair,
            "candidate_models": model_count,
        })

    assert complete_pairs_total == 15
    assert no_pair_schedules == 6
    assert len(candidate_payloads) == 26400
    assert inconsistent == 0 and underdetermined == 0

    # Only after every source-block candidate payload is fixed, consult K04.
    mask = bytes.fromhex(route["K04"]["masked_component"])
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text())
    target_hash = acceptance["slot_sha256"]["K04"]
    hits = []
    for candidate in candidate_payloads:
        payload = candidate[-1]
        component = bytes(a ^ b for a, b in zip(payload, mask))
        if hashlib.sha256(component).hexdigest() == target_hash:
            hits.append(candidate[:-1] + (payload.hex().upper(), component.hex().upper()))
    assert hits == [], hits

    print(json.dumps({
        "stage_shift_assignments": len(admissible),
        "whole_source_compatible_chronologies": len(compatible),
        "selected_stage_counts": dict(sorted(stage_counts.items())),
        "source_blocks": list(blocks),
        "distinct_source_blocks": len(blocks),
        "chronologies_with_unique_complete_gap_pair": complete_pairs_total,
        "chronologies_without_complete_gap_pair": no_pair_schedules,
        "gap_pair_summaries": schedule_summary,
        "complete_candidate_models": len(candidate_payloads),
        "inconsistent_models": inconsistent,
        "underdetermined_models": underdetermined,
        "K04_commitment_hits": hits,
        "new_K04_bits_recovered": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
