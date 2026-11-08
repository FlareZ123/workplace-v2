"""Read-only SFT for a shared fourth-order GF(256) recurrence across REC8 slots.

Run from the repository root:
    python agents/agent34/rec8_order4_gf256_crossslot_sft.py

The hypothesis is exploratory. It does not alter candidate.json, acceptance.json,
or the official verifier.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIELDS = (0x11B, 0x11D)
KNOWN = {
    "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03": "1384AF96E25D6ADA666209CB55E062FA",
    "K05": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K07": "93495F5E425AB8E592123DABAEB68545",
}
TARGETS = {
    "K04": "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0",
    "K08": "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747",
}


def field_tables(polynomial: int) -> tuple[list[list[int]], list[int | None]]:
    """Build multiplication and inverse tables for GF(256)."""
    reduction = polynomial & 0xFF
    multiply = [[0] * 256 for _ in range(256)]
    for left in range(256):
        for right in range(256):
            a, b, value = left, right, 0
            for _ in range(8):
                if b & 1:
                    value ^= a
                high = a & 0x80
                a = ((a << 1) & 0xFF) ^ (reduction if high else 0)
                b >>= 1
            multiply[left][right] = value

    inverse: list[int | None] = [None] * 256
    for value in range(1, 256):
        inverse[value] = next(other for other in range(1, 256)
                              if multiply[value][other] == 1)
    return multiply, inverse


def solve_linear(
    matrix: list[list[int]],
    right: list[int],
    multiply: list[list[int]],
    inverse: list[int | None],
) -> list[tuple[int, ...]]:
    """Return every solution to a small GF(256) linear system."""
    rows = [list(row) + [right[index]] for index, row in enumerate(matrix)]
    variable_count = len(matrix[0])
    pivots: list[int] = []
    pivot_row = 0

    for column in range(variable_count):
        selected = next((index for index in range(pivot_row, len(rows))
                         if rows[index][column]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        scale = inverse[rows[pivot_row][column]]
        assert scale is not None
        rows[pivot_row] = [multiply[scale][value] for value in rows[pivot_row]]
        for index in range(len(rows)):
            if index == pivot_row or not rows[index][column]:
                continue
            factor = rows[index][column]
            rows[index] = [
                left ^ multiply[factor][right_value]
                for left, right_value in zip(rows[index], rows[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1

    for row in rows[pivot_row:]:
        if not any(row[:variable_count]) and row[variable_count]:
            return []

    free = [column for column in range(variable_count) if column not in pivots]
    solutions: list[tuple[int, ...]] = []
    for free_values in itertools.product(range(256), repeat=len(free)):
        values = [0] * variable_count
        for column, value in zip(free, free_values):
            values[column] = value
        for row_index, column in enumerate(pivots):
            value = rows[row_index][variable_count]
            for free_column in free:
                value ^= multiply[rows[row_index][free_column]][values[free_column]]
            values[column] = value
        solutions.append(tuple(values))
    return solutions


def solve_forward(
    k1: bytes,
    k2: bytes,
    k3: bytes,
    k5: bytes,
    k6: bytes,
    k7: bytes,
    multiply: list[list[int]],
    inverse: list[int | None],
) -> list[tuple[int, int, int, int, bytes, bytes]]:
    """Solve K5..K7 recurrence constraints and derive K4 and K8."""
    candidates: set[tuple[int, int, int, int, bytes, bytes]] = set()

    # For a != 0, E5 determines each K4 byte. E6 gives a linear
    # consistency constraint on c and d across all sixteen byte lanes.
    for a in range(1, 256):
        a_squared = multiply[a][a]
        for b in range(256):
            b_squared = multiply[b][b]
            denominator = [
                multiply[b][k1[j]] ^ multiply[a][k2[j]]
                for j in range(16)
            ]
            base = [
                multiply[a][k6[j]]
                ^ multiply[a_squared][k5[j]]
                ^ multiply[b][k5[j]]
                ^ multiply[b_squared][k3[j]]
                for j in range(16)
            ]
            slope = [
                multiply[b][k2[j]] ^ multiply[a][k3[j]]
                for j in range(16)
            ]
            reference = next((j for j in range(16) if denominator[j]), None)

            if reference is None:
                # E6 leaves d free when every denominator is zero.
                c_value = None
                inconsistent = False
                for j in range(16):
                    coefficient, constant = slope[j], base[j]
                    if coefficient:
                        value = multiply[constant][inverse[coefficient]]
                    elif constant:
                        inconsistent = True
                        break
                    else:
                        continue
                    if c_value is None:
                        c_value = value
                    elif c_value != value:
                        inconsistent = True
                        break
                if inconsistent:
                    continue
                c_values = range(256) if c_value is None else (c_value,)
                for c in c_values:
                    if any(base[j] ^ multiply[c][slope[j]] for j in range(16)):
                        continue
                    for d in range(256):
                        k4 = bytes(
                            multiply[inverse[a]][
                                k5[j] ^ multiply[b][k3[j]]
                                ^ multiply[c][k2[j]] ^ multiply[d][k1[j]]
                            ]
                            for j in range(16)
                        )
                        if any(
                            (multiply[a][k6[j]] ^ multiply[b][k5[j]]
                             ^ multiply[c][k4[j]] ^ multiply[d][k3[j]]) != k7[j]
                            for j in range(16)
                        ):
                            continue
                        k8 = bytes(
                            multiply[a][k7[j]] ^ multiply[b][k6[j]]
                            ^ multiply[c][k5[j]] ^ multiply[d][k4[j]]
                            for j in range(16)
                        )
                        candidates.add((a, b, c, d, k4, k8))
                continue

            c_value = None
            inconsistent = False
            ref_den = denominator[reference]
            ref_base = base[reference]
            ref_slope = slope[reference]
            for j in range(16):
                if j == reference:
                    continue
                if not denominator[j]:
                    coefficient, constant = slope[j], base[j]
                    if coefficient:
                        value = multiply[constant][inverse[coefficient]]
                    elif constant:
                        inconsistent = True
                        break
                    else:
                        continue
                else:
                    coefficient = (
                        multiply[ref_slope][denominator[j]]
                        ^ multiply[slope[j]][ref_den]
                    )
                    constant = (
                        multiply[ref_base][denominator[j]]
                        ^ multiply[base[j]][ref_den]
                    )
                    if coefficient:
                        value = multiply[constant][inverse[coefficient]]
                    elif constant:
                        inconsistent = True
                        break
                    else:
                        continue
                if c_value is None:
                    c_value = value
                elif c_value != value:
                    inconsistent = True
                    break
            if inconsistent:
                continue

            c_values = range(256) if c_value is None else (c_value,)
            for c in c_values:
                d = multiply[base[reference] ^ multiply[c][slope[reference]]][
                    inverse[ref_den]
                ]
                if any(
                    (base[j] ^ multiply[c][slope[j]])
                    != multiply[d][denominator[j]]
                    for j in range(16)
                ):
                    continue
                k4 = bytes(
                    multiply[inverse[a]][
                        k5[j] ^ multiply[b][k3[j]]
                        ^ multiply[c][k2[j]] ^ multiply[d][k1[j]]
                    ]
                    for j in range(16)
                )
                if any(
                    (multiply[a][k6[j]] ^ multiply[b][k5[j]]
                     ^ multiply[c][k4[j]] ^ multiply[d][k3[j]]) != k7[j]
                    for j in range(16)
                ):
                    continue
                k8 = bytes(
                    multiply[a][k7[j]] ^ multiply[b][k6[j]]
                    ^ multiply[c][k5[j]] ^ multiply[d][k4[j]]
                    for j in range(16)
                )
                candidates.add((a, b, c, d, k4, k8))

    # For a == 0, E5 is a 16-row linear system for b, c and d.
    matrix = [[k3[j], k2[j], k1[j]] for j in range(16)]
    right = [k5[j] for j in range(16)]
    for b, c, d in solve_linear(matrix, right, multiply, inverse):
        if b:
            k4 = bytes(
                multiply[inverse[b]][
                    k6[j] ^ multiply[c][k3[j]] ^ multiply[d][k2[j]]
                ]
                for j in range(16)
            )
        elif c:
            k4 = bytes(
                multiply[inverse[c]][
                    k7[j] ^ multiply[b][k5[j]] ^ multiply[d][k3[j]]
                ]
                for j in range(16)
            )
        else:
            # If b=c=0, the observed slots do not determine K4.
            continue

        if any(
            (multiply[b][k4[j]] ^ multiply[c][k3[j]]
             ^ multiply[d][k2[j]]) != k6[j]
            for j in range(16)
        ):
            continue
        if any(
            (multiply[b][k5[j]] ^ multiply[c][k4[j]]
             ^ multiply[d][k3[j]]) != k7[j]
            for j in range(16)
        ):
            continue
        k8 = bytes(
            multiply[b][k6[j]] ^ multiply[c][k5[j]] ^ multiply[d][k4[j]]
            for j in range(16)
        )
        candidates.add((0, b, c, d, k4, k8))

    return sorted(candidates)


def solve_reverse(
    k1: bytes,
    k2: bytes,
    k3: bytes,
    k5: bytes,
    k6: bytes,
    k7: bytes,
    multiply: list[list[int]],
    inverse: list[int | None],
) -> list[tuple[int, int, int, int, bytes, bytes]]:
    """Solve in reverse chronology and invert the final recurrence step."""
    reverse_models = solve_forward(k7, k6, k5, k3, k2, k1, multiply, inverse)
    candidates = []
    for a, b, c, d, k4, _ in reverse_models:
        if not d:
            continue
        k8 = bytes(
            multiply[inverse[d]][
                k4[j] ^ multiply[a][k5[j]]
                ^ multiply[b][k6[j]] ^ multiply[c][k7[j]]
            ]
            for j in range(16)
        )
        candidates.append((a, b, c, d, k4, k8))
    return candidates


def make_sequence(
    coefficients: tuple[int, int, int, int],
    multiply: list[list[int]],
    seed: int,
) -> list[bytes]:
    """Generate eight complete 16-byte symbols from a real order-4 recurrence."""
    a, b, c, d = coefficients
    rng = random.Random(seed)
    sequence = [bytes(rng.randrange(256) for _ in range(16)) for _ in range(4)]
    for index in range(4, 8):
        sequence.append(bytes(
            multiply[a][sequence[index - 1][lane]]
            ^ multiply[b][sequence[index - 2][lane]]
            ^ multiply[c][sequence[index - 3][lane]]
            ^ multiply[d][sequence[index - 4][lane]]
            for lane in range(16)
        ))
    return sequence


def synthetic_controls() -> tuple[int, int]:
    patterns = (
        (0x3C, 0xC9, 0x52, 0x11),
        (0x01, 0x00, 0x00, 0x9F),
        (0xFF, 0x42, 0x99, 0x00),
        (0x00, 0x33, 0x91, 0x4A),
        (0x00, 0x00, 0x77, 0x29),
    )
    forward_count = 0
    reverse_count = 0

    for polynomial in FIELDS:
        multiply, inverse = field_tables(polynomial)
        for index, coefficients in enumerate(patterns):
            sequence = make_sequence(
                coefficients, multiply, 1000 + index + polynomial
            )
            recovered = solve_forward(
                sequence[0], sequence[1], sequence[2],
                sequence[4], sequence[5], sequence[6],
                multiply, inverse,
            )
            assert any(
                model[:4] == coefficients
                and model[4] == sequence[3]
                and model[5] == sequence[7]
                for model in recovered
            )
            forward_count += 1

        for index in (0, 1, 3):
            coefficients = patterns[index]
            reverse_sequence = make_sequence(
                coefficients, multiply, 3000 + index + polynomial
            )
            k8, k7, k6, k5, k4, k3, k2, k1 = reverse_sequence
            recovered = solve_reverse(
                k1, k2, k3, k5, k6, k7, multiply, inverse
            )
            assert any(
                model[:4] == coefficients
                and model[4] == k4
                and model[5] == k8
                for model in recovered
            )
            reverse_count += 1

    print(f"SYNTHETIC forward controls: {forward_count} PASS")
    print(f"SYNTHETIC reverse controls: {reverse_count} PASS")
    return forward_count, reverse_count


def original_data() -> None:
    candidate = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    acceptance = json.loads(
        (ROOT / "resources" / "acceptance.json").read_text(encoding="utf-8")
    )
    assert {slot: candidate[slot] for slot in KNOWN} == KNOWN
    assert candidate["K04"] is None and candidate["K08"] is None
    assert acceptance["slot_sha256"]["K04"] == TARGETS["K04"]
    assert acceptance["slot_sha256"]["K08"] == TARGETS["K08"]

    for slot, value in KNOWN.items():
        assert hashlib.sha256(bytes.fromhex(value)).hexdigest() == (
            acceptance["slot_sha256"][slot]
        )

    values = [bytes.fromhex(KNOWN[slot]) for slot in
              ("K01", "K02", "K03", "K05", "K06", "K07")]
    k1, k2, k3, k5, k6, k7 = values
    for polynomial in FIELDS:
        multiply, inverse = field_tables(polynomial)
        forward = solve_forward(k1, k2, k3, k5, k6, k7, multiply, inverse)
        reverse = solve_reverse(k1, k2, k3, k5, k6, k7, multiply, inverse)
        candidates = [("forward", model) for model in forward]
        candidates.extend(("reverse", model) for model in reverse)
        k4_hits = sum(
            hashlib.sha256(model[4]).hexdigest() == TARGETS["K04"]
            for _, model in candidates
        )
        k8_hits = sum(
            hashlib.sha256(model[5]).hexdigest() == TARGETS["K08"]
            for _, model in candidates
        )
        joint_hits = sum(
            hashlib.sha256(model[4]).hexdigest() == TARGETS["K04"]
            and hashlib.sha256(model[5]).hexdigest() == TARGETS["K08"]
            for _, model in candidates
        )
        print(
            f"GF(256) 0x{polynomial:X}: "
            f"forward_models={len(forward)}, reverse_models={len(reverse)}, "
            f"K04_hits={k4_hits}, K08_hits={k8_hits}, joint_hits={joint_hits}"
        )
        assert not forward and not reverse
        assert not k4_hits and not k8_hits and not joint_hits

    print("RESULT: no tested shared-coefficient GF(256) order-4 recurrence")


if __name__ == "__main__":
    synthetic_controls()
    original_data()
