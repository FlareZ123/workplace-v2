"""Stage-unknown original printer holdout test for conditional p951 MT19937.

No target hash, mask or selected ACK2 payload is used. Native stage starts
are a retrospectively inferred conditional chronology, not historical proof.
Execute from repository root:
  python agents/agent2/k04_p951_stage_selector_rank_holdout_sft.py
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, ORIGIN, STARTS, get, untemper, words

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def tempered(y: int) -> int:
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & 0xFFFFFFFF


def additional_rank(basis: Basis, vectors: list[int]) -> int:
    pivots = {k: v for k, (v, _) in basis.rows.items()}
    extra = 0
    for vector in vectors:
        while vector:
            lead = vector.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = vector
                extra += 1
                break
            vector ^= pivots[lead]
    return extra


def main() -> None:
    spool = (ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SOURCE_SHA
    records = re.findall(
        rb"CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)", spool
    )
    assert len(records) == len(STARTS) == 133
    symbolic = words()
    native = {}
    for i, (_, payload, _) in enumerate(records):
        if i == 129:
            continue  # disputed selected ACK2 is never decoded or fitted
        p = bytes.fromhex(payload.decode("ascii"))
        equations = []
        for lane in range(4):
            v = untemper(int.from_bytes(p[4 * lane:4 * lane + 4], "little"))
            equations.extend(
                (source_vector, (v >> bit) & 1)
                for bit, source_vector in enumerate(get(symbolic, STARTS[i] + lane))
            )
        native[i] = equations

    total = truth_minimal = truth_unique = rank0 = 0
    demonstrable_false = []
    for withheld in range(1, 128):
        fit = Basis()
        for row, equations in native.items():
            if row == withheld:
                continue
            for vector, bit in equations:
                fit.insert(vector, bit)

        # Target row's stage and bytes are withheld. Neighbor stages remain
        # conditioned on the retrospective Agent49 stage map.
        alternatives = []
        for start in range(STARTS[withheld - 1] + 4, STARTS[withheld + 1] - 3):
            vectors = [
                v for lane in range(4) for v in get(symbolic, start + lane)
            ]
            alternatives.append((start, additional_rank(fit, vectors)))
        assert alternatives and any(s == STARTS[withheld] for s, _ in alternatives)
        best_rank = min(rank for _, rank in alternatives)
        minimizers = [s for s, rank in alternatives if rank == best_rank]
        correct = STARTS[withheld] in minimizers
        total += 1
        truth_minimal += correct
        truth_unique += correct and len(minimizers) == 1
        rank0 += best_rank == 0

        if best_rank != 0 or correct:
            continue
        # This alternative is 128/128 native bits fixed, yet is historically
        # the wrong *stage*; reconstruct the exact wrong complete 16-byte value.
        start = minimizers[0]
        full = bytearray()
        for lane in range(4):
            bits = [fit.predict(v) for v in get(symbolic, start + lane)]
            assert all(bit is not None for bit in bits)
            register = sum(bit << j for j, bit in enumerate(bits))
            full.extend(tempered(register).to_bytes(4, "little"))
        actual = bytes.fromhex(records[withheld][1].decode("ascii"))
        assert bytes(full) != actual
        demonstrable_false.append((withheld, STARTS[withheld], start, len(minimizers)))
        print(f"ROW={withheld} TRUE_STAGE={STARTS[withheld]} "
              f"FALSE_STAGE={start} TIED_ZERO_STAGE_COUNT={len(minimizers)} "
              f"PREDICTED={full.hex().upper()} ACTUAL={actual.hex().upper()}")

    assert (total, truth_minimal, truth_unique, rank0) == (127, 26, 5, 6)
    assert [row for row, *_ in demonstrable_false] == [44, 92, 93, 94, 95, 96]
    print(f"STAGE_UNKNOWN_HOLDOUTS={total} "
          f"TRUE_IN_MINIMUM={truth_minimal} TRUE_UNIQUE={truth_unique} "
          f"FALSE_ZERO_FREEDOM={len(demonstrable_false)}")
    print("TARGET_ACK2_ROW129_EXCLUDED__K04_K08_UNRESOLVED")


if __name__ == "__main__":
    main()
