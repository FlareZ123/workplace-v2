#!/usr/bin/env python3
"""Test whether historical MT lane-witness signatures can transfer to row 129.

Requires numpy and scipy>=1.11. Source row 129 is withheld from witness discovery.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "resources/evidence/print/spool-reconstruction.log"
EXPECTED_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
TARGET_ROW = 129  # zero-based selected PS-0417 ACK2
MASK = 0xFFFFFFFF


def undo_right(value: int, shift: int) -> int:
    out = value
    for _ in range(5):
        out = value ^ (out >> shift)
    return out & MASK


def undo_left(value: int, shift: int, mask: int) -> int:
    out = value
    for _ in range(5):
        out = value ^ ((out << shift) & mask)
    return out & MASK


def untemper(value: int) -> int:
    value = undo_right(value, 18)
    value = undo_left(value, 15, 0xEFC60000)
    value = undo_left(value, 7, 0x9D2C5680)
    return undo_right(value, 11)


def twist_pair(previous: int, current: int) -> int:
    joined = (previous & 0x80000000) | (current & 0x7FFFFFFF)
    return (joined >> 1) ^ (0x9908B0DF if current & 1 else 0)


def read_rows():
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == EXPECTED_SHA256, (digest, EXPECTED_SHA256)
    lines = [line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines) == 133, len(lines)
    words, states = [], []
    for index, line in enumerate(lines):
        meta = re.match(r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)", line)
        assert meta, (index, line)
        states.append(meta.group(4))
        if index == TARGET_ROW:
            words.append(None)  # never use disputed target payload as a witness
            continue
        payload = re.search(r"\bPAYLOAD=([0-9A-F]{32})\b", line)
        if not payload:
            words.append(None)
            continue
        packet = bytes.fromhex(payload.group(1))
        words.append(tuple(untemper(int.from_bytes(packet[offset:offset + 4], "little"))
                           for offset in (0, 4, 8, 12)))
    return words, states


def discover_witnesses(words):
    by_word = {}
    for row, packet in enumerate(words):
        if packet is None:
            continue
        for lane, word in enumerate(packet):
            by_word.setdefault(word, []).append((row, lane))
    witnesses = []
    for row, packet in enumerate(words):
        if packet is None:
            continue
        for source_lane in (1, 2, 3):
            patch = twist_pair(packet[source_lane - 1], packet[source_lane])
            for middle_row in range(row + 1, len(words)):
                middle = words[middle_row]
                if middle is None:
                    continue
                for middle_lane, middle_word in enumerate(middle):
                    for target_row, target_lane in by_word.get(patch ^ middle_word, []):
                        if target_row > middle_row:
                            witnesses.append((row, source_lane, middle_row, middle_lane,
                                              target_row, target_lane))
    witnesses = sorted(witnesses)
    assert len(witnesses) == 25, len(witnesses)
    signatures = sorted({(middle - row, target - row, p, i, q)
                         for row, p, middle, i, target, q in witnesses})
    assert len(signatures) == 23, len(signatures)
    return witnesses, signatures


def source_constraints(witnesses, n):
    matrix, rhs = [], []
    for row, p, middle, i, target, q in witnesses:
        first = np.zeros(n)
        first[row:middle] = 1
        matrix.append(first)
        rhs.append(396 + p - i)
        second = np.zeros(n)
        second[row:target] = 1
        matrix.append(second)
        rhs.append(623 + p - q)
    return np.vstack(matrix), np.asarray(rhs, dtype=float)


def solve_feasible(A, b, lower, upper, extra=()):
    if extra:
        extra_A = np.vstack([item[0] for item in extra])
        extra_b = np.asarray([item[1] for item in extra], dtype=float)
        A = np.vstack([A, extra_A])
        b = np.r_[b, extra_b]
    result = milp(np.zeros(A.shape[1]), integrality=np.ones(A.shape[1]),
                  bounds=Bounds(lower, upper), constraints=LinearConstraint(A, b, b),
                  options={"time_limit": 20})
    if result.status not in (0, 2):
        raise RuntimeError(f"MILP inconclusive: {result.status} {result.message}")
    return result.x is not None


def range_of_sum(A, b, lower, upper, start, end):
    objective = np.zeros(A.shape[1])
    objective[start:end] = 1
    lo = milp(objective, integrality=np.ones(A.shape[1]), bounds=Bounds(lower, upper),
              constraints=LinearConstraint(A, b, b), options={"time_limit": 20})
    hi = milp(-objective, integrality=np.ones(A.shape[1]), bounds=Bounds(lower, upper),
              constraints=LinearConstraint(A, b, b), options={"time_limit": 20})
    if lo.x is None or hi.x is None:
        raise RuntimeError("Could not bound target stage sum")
    return int(round(lo.fun)), int(round(-hi.fun))


def main():
    words, states = read_rows()
    witnesses, signatures = discover_witnesses(words)
    n = len(words)
    A, b = source_constraints(witnesses, n)

    # A direct 4-word ACK packet consumes >=4 MT outputs. REQUESTED rows may
    # consume zero or more outputs; their state does not prove zero draws.
    lower = np.full(n, 4.0)
    upper = np.full(n, 100.0)
    for row, state in enumerate(states):
        if state == "REQUESTED":
            lower[row] = 0.0
    assert solve_feasible(A, b, lower, upper), "Source witness system should be feasible"

    gap1 = range_of_sum(A, b, lower, upper, 45, 99)
    gap2 = range_of_sum(A, b, lower, upper, 45, TARGET_ROW)
    feasible_signatures = []
    for dk, dl, p, i, q in signatures:
        start = TARGET_ROW - dl
        middle = start + dk
        first = np.zeros(n); first[start:middle] = 1
        second = np.zeros(n); second[start:TARGET_ROW] = 1
        if solve_feasible(A, b, lower, upper,
                          ((first, 396 + p - i), (second, 623 + p - q))):
            feasible_signatures.append((dk, dl, p, i, q))

    # Sensitivity: even if ACK rows may consume zero draws, four signatures
    # become feasible; none is one of the two duplicated twin signatures.
    zero_lower = np.zeros(n)
    zero_upper = np.full(n, 100.0)
    zero_feasible = []
    for dk, dl, p, i, q in signatures:
        start = TARGET_ROW - dl
        middle = start + dk
        first = np.zeros(n); first[start:middle] = 1
        second = np.zeros(n); second[start:TARGET_ROW] = 1
        if solve_feasible(A, b, zero_lower, zero_upper,
                          ((first, 396 + p - i), (second, 623 + p - q))):
            zero_feasible.append((dk, dl, p, i, q))

    # Existing p951 schedule: constructive positive control for all historical
    # equations, not a claim that the schedule is source-authenticated.
    starts = [0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963]
    assert len(starts) == n
    draws = np.diff(starts + [starts[-1] + starts[-1] - starts[-2]])
    assert min(draws) >= 4 and max(draws) <= 17
    assert all(sum(draws[row:middle]) == 396 + p - i and
               sum(draws[row:target]) == 623 + p - q
               for row, p, middle, target, q in
               [(r,p,k,l,q) for r,p,k,i,l,q in witnesses])
    p951_target_gaps = (int(sum(draws[45:99])), int(sum(draws[45:TARGET_ROW])))
    assert p951_target_gaps == (401, 609), p951_target_gaps
    pc1 = np.zeros(n); pc1[45:99] = 1
    pc2 = np.zeros(n); pc2[45:TARGET_ROW] = 1
    assert solve_feasible(A, b, lower, upper,
                          ((pc1, p951_target_gaps[0]), (pc2, p951_target_gaps[1])))

    twins = [(54, 84, 1, 1, 2), (54, 84, 2, 2, 3)]
    assert all(twin not in feasible_signatures for twin in twins)
    print(f"source SHA256: {EXPECTED_SHA256}")
    print(f"withheld target row: {TARGET_ROW}; intact source rows: {sum(x is not None for x in words)}")
    print(f"historical witnesses/signatures: {len(witnesses)}/{len(signatures)}")
    print(f"duplicated twins: {twins}")
    print(f"target gap1 S99-S45 range: {gap1}; twin requires 396")
    print(f"target gap2 S129-S45 range: {gap2}; all signatures require 621..626")
    print(f"source-constrained target signatures feasible (ACK 4..100, REQUESTED 0..100): {len(feasible_signatures)}/23")
    print(f"over-permissive all-row 0..100 sensitivity: {len(zero_feasible)}/23; feasible={zero_feasible}")
    print(f"p951 schedule: historical equations PASS; S129={starts[TARGET_ROW]}, target gaps={p951_target_gaps}")
    print("p951 target-gap positive control: PASS")


if __name__ == "__main__":
    main()
