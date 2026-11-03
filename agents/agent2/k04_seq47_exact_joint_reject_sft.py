"""Exact joint source-GF2 feasibility of seq47 EVENT, LATCH, AUX rejection stages.

Extends Agent47's independent fixed-bit stage test by enforcing every field
bit jointly with printer + 56 original CONTROL constraints. No disputed ACK,
K04/K08 commitments, route mask or candidate components are read.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
sys.path.insert(0, str(ROOT / "agents" / "agent2"))
sys.path.insert(0, str(ROOT / "agents" / "agent47"))
from k04_p951_symbolic_basis import source, get, temper
from k04_conditional_onebit_parity_sft import PATH, joint_basis
from k04_node50_full_syndrome_gap_sft import recorder_controls
from k04_seq47_event_aux_joint_sft import recorder_metadata, ANCHORS


def patterns(k: int, threshold: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    """Disjoint prefix-cube cover of every unsigned code >= threshold."""
    assert 0 < threshold < 1 << k
    cubes = [tuple((i, (threshold >> i) & 1) for i in range(k))]
    for bit in range(k):
        if (threshold >> bit) & 1 == 0:
            cubes.append(tuple((i, (threshold >> i) & 1)
                               for i in range(k - 1, bit, -1)) + ((bit, 1),))
    for code in range(1 << k):
        covers = sum(all((code >> i) & 1 == v for i, v in p) for p in cubes)
        assert covers == int(code >= threshold), (k, threshold, code, covers)
    return tuple(cubes)


REJECT = {6: patterns(6, 39), 3: patterns(3, 4), 13: patterns(13, 6000)}


def accepted(k: int, value: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    assert 0 <= value < (1 << k)
    return (tuple((i, (value >> i) & 1) for i in range(k)),)


class State:
    def __init__(self, basis):
        self.rows = dict(basis.rows)
        self.rank = basis.rank

    def push(self, equations):
        inserted = []
        for vector, bit in equations:
            while vector:
                p = vector.bit_length() - 1
                if p not in self.rows:
                    self.rows[p] = (vector, bit)
                    inserted.append(p)
                    self.rank += 1
                    break
                row, v = self.rows[p]
                vector ^= row
                bit ^= v
            if vector == 0 and bit:
                self.pop(inserted)
                return None
        return inserted

    def pop(self, inserted):
        for pivot in inserted:
            del self.rows[pivot]
        self.rank -= len(inserted)


def solvable(model, vectors, items, first_only=True):
    """Exact joint satisfiability, treating each rejection as a range."""
    state = State(model)
    expansions = 0
    witness = []

    def dfs(i):
        nonlocal expansions
        if i == len(items):
            return tuple(witness)
        stage, k, choices = items[i]
        bits = temper(get(vectors, stage))[32 - k:]
        for cube in choices:
            expansions += 1
            additions = state.push((bits[bit], value) for bit, value in cube)
            if additions is not None:
                witness.append((stage, k, cube))
                result = dfs(i + 1)
                witness.pop()
                state.pop(additions)
                if result is not None and first_only:
                    return result
        return None

    answer = dfs(0)
    return answer, expansions


def history(stage, er, lr, ar, observed):
    event, latch, aux = observed
    assert event == 4 and latch == 1 and aux == 3075
    first = stage - er - lr - 2
    if first <= -531 or stage + ar + 1 >= -512:
        return None
    items = []
    for s in range(first, first + er):
        items.append((s, 6, REJECT[6]))
    items.append((first + er, 6, accepted(6, event - 1)))
    for s in range(first + er + 1, stage - 1):
        items.append((s, 3, REJECT[3]))
    items.append((stage - 1, 3, accepted(3, latch)))
    for s in range(stage + 1, stage + ar + 1):
        items.append((s, 13, REJECT[13]))
    items.append((stage + ar + 1, 13, accepted(13, aux - 2000)))
    assert len(items) == er + lr + ar + 3
    return items


def calibration(printer, vectors, controls, metadata):
    """Whole-field no-rejection consistency, separately for source anchors."""
    model = joint_basis(printer, vectors, controls, PATH)
    samples = {"anchors": [], "other": []}
    for seq, pos in PATH:
        if seq == 47:
            continue
        event, latch, aux = metadata[seq]
        if not (1 <= event <= 39 and 0 <= latch <= 3
                and 2000 <= aux < 8000):
            continue
        rows = [(pos - 2, 6, accepted(6, event - 1)),
                (pos - 1, 3, accepted(3, latch)),
                (pos + 1, 13, accepted(13, aux - 2000))]
        answer, _ = solvable(model, vectors, rows)
        samples["anchors" if seq in ANCHORS else "other"].append((seq, answer is not None))
    for label, data in samples.items():
        print("CALIBRATION", label, "joint_direct_compatible",
              sum(ok for _, ok in data), "out_of", len(data),
              "incompatible_seqs", [seq for seq, ok in data if not ok], flush=True)


def all_accepted_positions(model, vectors, stage, observed):
    """Necessary exact GF2 test for ALL field-rejection lengths within neighboring CONTROL boundaries.

    Accepted EVENT draw can lie at any stage strictly after seq46=-531
    and at least two stages before current CONTROL. Accepted LATCH remains
    at stage-1 under the no-intervening-draw field-order hypothesis.
    AUX accepted draw can lie anywhere after CONTROL and before seq48=-512.
    If no joint accepted triple survives, no number of rejections can rescue
    this candidate CONTROL stage in the stated producer order.
    """
    event, latch, aux = observed
    options = []
    for e_stage in range(-530, stage - 1):
        for a_stage in range(stage + 1, -512):
            rows = [(e_stage, 6, accepted(6, event - 1)),
                    (stage - 1, 3, accepted(3, latch)),
                    (a_stage, 13, accepted(13, aux - 2000))]
            answer, _ = solvable(model, vectors, rows)
            if answer is not None:
                options.append((e_stage, stage - 1, a_stage))
    return options


def main():
    printer, vectors = source(ROOT / "resources")
    controls = recorder_controls()
    metadata = recorder_metadata()
    assert printer.rank == 15365 and metadata[47] == (4, 1, 3075)
    other = tuple((seq, pos) for seq, pos in PATH if seq != 47)
    print("EXACT rejection-prefix sizes",
          {k: len(v) for k, v in REJECT.items()}, flush=True)
    for stage in (-523, -522, -521, -520):
        model = joint_basis(printer, vectors, controls, other + ((47, stage),))
        accepted_positions = all_accepted_positions(model, vectors, stage, metadata[47])
        print("UNBOUNDED_ACCEPTED_POSITIONS",stage,"joint_triples",len(accepted_positions),"first",accepted_positions[:12],flush=True)
        stats = Counter()
        sample = []
        expansions = 0
        for er in range(3):
            for lr in range(3):
                for ar in range(3):
                    items = history(stage, er, lr, ar, metadata[47])
                    if items is None:
                        continue
                    solution, tried = solvable(model, vectors, items)
                    expansions += tried
                    if solution is not None:
                        stats[(er, lr, ar)] += 1
                        if len(sample) < 6:
                            sample.append((er, lr, ar,
                                           tuple((s, n, len(cube))
                                                 for s, n, cube in solution)))
        print("STAGE", stage, "source_rank", model.rank,
              "exact_joint_feasible_histories", sum(stats.values()),
              "minimum_total_rejections",
              min((sum(k) for k in stats), default=None),
              "no_rejection_survives", (0, 0, 0) in stats,
              "expansions", expansions,
              "sample_witnesses", sample, flush=True)
    # The only remaining accepted-code placements for -522 have the EVENT
    # accept draw at -530 and the LATCH accept draw at -523: six rejected
    # LATCH outputs between them. Test those with exact inter-field GF2.
    stage = -522
    model = joint_basis(printer, vectors, controls, other + ((47, stage),))
    # Independent human-readable cut at the very first mandatory reject.
    accepted_event = accepted(6, metadata[47][0] - 1)[0]
    event_equations = temper(get(vectors, -530))[26:]
    for bit, value in accepted_event:
        model.insert(event_equations[bit], value)
    forced = tuple(model.predict(q) for q in temper(get(vectors, -529))[29:])
    print("SIX_LATCH_FIRST_REJECTION", "stage",-529,"high3_fixed",forced,
          "reject_requires_code_at_least_4", flush=True)
    assert all(v is not None for v in forced) and sum(v << i for i,v in enumerate(forced)) < 4
    model = joint_basis(printer, vectors, controls, other + ((47, stage),))
    for ar in range(4):
        items = history(stage, 0, 6, ar, metadata[47])
        assert items is not None
        witness, expansions = solvable(model, vectors, items)
        print("SIX_LATCH_REJECTS",stage,"aux_rejects",ar,
              "feasible",witness is not None,
              "prefix_expansions",expansions,
              "sample",tuple((s,n,len(c)) for s,n,c in witness) if witness else None,
              flush=True)
    calibration(printer, vectors, controls, metadata)
    print("Original selected K04 coupon and K08 phrase remain unknown.", flush=True)


if __name__ == "__main__":
    main()
