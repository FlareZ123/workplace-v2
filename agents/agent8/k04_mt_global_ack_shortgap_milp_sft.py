"""Source-stage MT19937 short-gap count across 130 ACK events; SciPy MILP.

Run: python agents/agent8/k04_mt_global_ack_shortgap_milp_sft.py
Requires numpy, scipy. Original selected ACK2 PAYLOAD is never decoded.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
import re
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import hstack, csr_matrix, lil_matrix

from k04_mt_all42_shortgap_sft import firstword_witnesses
from k04_mt_packet_boundary_sft import find_witnesses, source_words

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133
    assert rows[129][1:5] == (b"PS-261003-0417", b"2", b"ACK", b"RECOVER")
    native = source_words(
        [None if i == 129 else bytes.fromhex(row[5].decode()) for i, row in enumerate(rows)],
        "little", False,
    )
    full, _ = find_witnesses(native)
    partial = firstword_witnesses(native)
    assert len(full) == 25 and len(partial) == 17
    num = len(rows) - 1
    ack = tuple(i for i, row in enumerate(rows[:-1]) if row[3] != b"REQUESTED")
    count_ack = len(ack)
    assert count_ack == 130
    ordinary_min = np.array(
        [0 if row[3] == b"REQUESTED" else 4 for row in rows[:-1]], dtype=float
    )
    short_matrix = lil_matrix((count_ack, num + count_ack))
    for j, event in enumerate(ack):
        short_matrix[j, event] = 1
        short_matrix[j, num + j] = 3
    short_constraint = LinearConstraint(
        short_matrix.tocsr(), np.full(count_ack, 7.), np.full(count_ack, np.inf)
    )
    objective = np.r_[np.zeros(num), np.ones(count_ack)]
    integral = np.ones(num + count_ack, dtype=int)

    def solve(witnesses: list[tuple[int, ...]], selected: str | None = None):
        equations = []
        values = []
        for r, k, l, p, i, q in witnesses:
            for stop, offset in ((k, 396 + p - i), (l, 623 + p - q)):
                row = np.zeros(num)
                row[r:stop] = 1
                equations.append(row)
                values.append(offset)
        matrix = hstack([
            csr_matrix(np.array(equations)), csr_matrix((len(values), count_ack))
        ]).tocsr()
        lower = np.r_[ordinary_min, np.zeros(count_ack)]
        upper = np.r_[np.full(num, 100.), np.ones(count_ack)]
        if selected == "short":
            lower[num + ack.index(129)] = 1
        elif selected == "long":
            upper[num + ack.index(129)] = 0
        result = milp(
            objective,
            integrality=integral,
            bounds=Bounds(lower, upper),
            constraints=[LinearConstraint(matrix, values, values), short_constraint],
            options={"mip_rel_gap": 0.0, "time_limit": 60.0},
        )
        assert result.success and result.mip_gap == 0, result.message
        steps = np.rint(result.x[:num]).astype(int)
        count = int(round(result.fun))
        assert count == sum(steps[j] < 7 for j in ack)
        assert np.array_equal(np.array(equations) @ steps, np.array(values))
        return count, int(steps[129]), [j for j in ack if steps[j] < 7]

    baseline = solve(full)
    strict = solve(full + partial)
    strict_short = solve(full + partial, "short")
    strict_long = solve(full + partial, "long")
    assert baseline[0] == 5, baseline
    assert strict[0] == 9, strict
    assert strict_short[0] == 9, strict_short
    assert strict_long[0] == 10, strict_long
    print(json.dumps({
        "historical_fullword_witnesses": 25,
        "historical_partial_firstword_witnesses": 17,
        "original_intact_words": 528,
        "ack_gap_count": count_ack,
        "baseline25_min_short_ACKs": baseline[0],
        "all42_min_short_ACKs": strict[0],
        "all42_selected_ACK2_short_min_total": strict_short[0],
        "all42_selected_ACK2_long_min_total": strict_long[0],
        "all42_short_event_example": strict[2],
        "selected_payload_withheld": True,
        "original_K04_recovered": False,
    }, indent=2))


if __name__ == "__main__":
    main()
