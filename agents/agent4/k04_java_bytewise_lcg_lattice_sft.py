"""Exact Java Random nextInt(256) source-only K04 printer generator sieve.

Requires SymPy (Matrix.lll). Python standard-library arithmetic for the
complete rational Gram-Schmidt / finite closest-point enumeration.

Run at repository root:
    python agents/agent4/k04_java_bytewise_lcg_lattice_sft.py

H17_RESOURCE_ROOT may point at an unmodified extraction of the original ZIP.
Does not read the selected ACK2, K04 acceptance or K08.
"""
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import os
import re

from sympy import Matrix

A = 0x5DEECE66D
C = 11
M = 1 << 48
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
ROOT = Path(os.environ.get("H17_RESOURCE_ROOT",
    str(Path(__file__).resolve().parents[2] / "resources")))
SOURCE = ROOT / "evidence/print/spool-reconstruction.log"


def emit(initial, count, stride=1):
    state = initial
    output = bytearray()
    for _ in range(count):
        for _ in range(stride):
            state = (state * A + C) % M
        output.append(state >> 40)
    return bytes(output)


def exact_states(observed, stride):
    """Exhaust *all* 48-bit starting states, via an exact lattice CVP bound.

    Every compatible initial state has one point in the modular lattice
    within the closed radius sqrt((n+1)*M*M/4) of the centered byte region.
    All basis reductions, Gram-Schmidt projections and pruning comparisons
    are exact; isqrt only makes integer enumeration bounds wider.
    """
    count = len(observed)
    coefficient, bias = 1, 0
    coefficients, biases = [], []
    for _ in observed:
        for _ in range(stride):
            coefficient = (coefficient * A) % M
            bias = (bias * A + C) % M
        coefficients.append(coefficient)
        biases.append(bias)

    # First lattice coordinate is the 48-bit unknown starting state.
    # Remaining coordinates are 256*(A^(stride*i)*state - k_i*M).
    basis = [[1] + [256 * v for v in coefficients]]
    for i in range(count):
        row = [0] * (count + 1)
        row[i + 1] = 256 * M
        basis.append(row)
    target = [M // 2] + [
        256 * (value * (1 << 40) + (1 << 39) - offset)
        for value, offset in zip(observed, biases)
    ]

    reduced = [list(map(int, r)) for r in Matrix(basis).lll().tolist()]
    dimension = len(reduced)

    # Exact Gram-Schmidt orthogonalization of LLL-reduced ROW basis.
    orthogonal, multipliers, lengths = [], [], []
    for i in range(dimension):
        vector = [F(value) for value in reduced[i]]
        row = [F(0)] * dimension
        for j in range(i):
            ratio = (sum(vector[k] * orthogonal[j][k]
                         for k in range(dimension)) / lengths[j])
            row[j] = ratio
            for k in range(dimension):
                vector[k] -= ratio * orthogonal[j][k]
        orthogonal.append(vector)
        multipliers.append(row)
        lengths.append(sum(v * v for v in vector))

    projections = [
        sum(F(target[k]) * orthogonal[j][k] for k in range(dimension))
        / lengths[j] for j in range(dimension)
    ]
    radius2 = F(dimension * M * M, 4)
    coefficients_reduced = [0] * dimension
    found = []
    exact_points = 0

    def visit(index, used):
        nonlocal exact_points
        if index < 0:
            exact_points += 1
            point = [
                sum(coefficients_reduced[j] * reduced[j][k]
                    for j in range(dimension))
                for k in range(dimension)
            ]
            error = [point[k] - target[k] for k in range(dimension)]
            if not all(-M // 2 <= x < M // 2 for x in error):
                return
            state = point[0]
            if 0 <= state < M and emit(state, count, stride) == observed:
                found.append(state)
            return

        center = (projections[index] -
            sum(F(coefficients_reduced[j]) * multipliers[j][index]
                for j in range(index + 1, dimension)))
        remaining = radius2 - used
        if remaining < 0:
            return
        squared_bound = remaining / lengths[index]
        # Guaranteed overestimate of all integral coefficients at this depth.
        wide = isqrt((squared_bound.numerator +
                      squared_bound.denominator - 1)
                     // squared_bound.denominator) + 2
        midpoint = center.numerator // center.denominator
        for value in range(midpoint - wide, midpoint + wide + 2):
            increment = lengths[index] * (F(value) - center) ** 2
            if increment <= remaining:
                coefficients_reduced[index] = value
                visit(index - 1, used + increment)

    visit(dimension - 1, F(0))
    return found, exact_points


def views(packet):
    return (
        ("raw", packet),
        ("reverse", packet[::-1]),
        ("reverse_words", b"".join(packet[i:i+4] for i in (12,8,4,0))),
        ("reverse_bytes_in_words", b"".join(
            packet[i:i+4][::-1] for i in (0,4,8,12))),
    )


def main():
    raw = SOURCE.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    records = [line for line in raw.decode("ascii").splitlines()
               if "PAYLOAD=" in line]
    assert len(records) == 133
    normal = []
    for j, line in enumerate(records[:128]):
        assert f"JOB=PS-261003-{j+300:04d} " in line
        assert "ATTEMPT=1 STATE=ACK " in line
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        normal.append(bytes.fromhex(match[1]))

    assert emit((42 ^ A) & (M - 1), 16).hex().upper() == (
        "BA0DAE0C4FF146B5AA17E7735E6146B0"
    )  # Exact independently checked OpenJDK 21 Random(42).nextInt(256).
    positives = 0
    for stride in range(1,17):
        for seed in (0,1,42,424242,0x123456789ABC):
            start = (seed ^ A) & (M - 1)
            actual = emit(start, 8, stride)
            solved, _ = exact_states(actual, stride)
            assert start in solved, (seed, stride)
            positives += 1
    print("actual_OpenJDK_fixture PASS, planted_exact_states", positives)

    attempts = 0
    for stride in range(1,17):
        matches, points = [], 0
        for j, packet in enumerate(normal):
            for orientation, candidate in views(packet):
                solved, examined = exact_states(candidate[:8], stride)
                attempts += 1
                points += examined
                if solved:
                    matches.append((j, orientation, solved))
        print("stride", stride, "original_packet_views", len(normal)*4,
              "finite_lattice_points", points, "complete_source_states", len(matches),
              flush=True)
        assert not matches, matches
    assert attempts == 128 * 4 * 16
    print("source_only_complete_assignments", attempts,
          "original_compatible_states", 0, "source_sha256", PIN)


if __name__ == "__main__":
    main()
