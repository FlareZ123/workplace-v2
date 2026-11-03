"""H-17 source-only AX transfer two-index MT stage test.

Each of the four historical transfers contains eight CHUNK seq values with
two attempts each. A specified shared-output hypothesis is:
    native_mt_index = base + seq * stride + (attempt - 1) * retry_offset
The first-attempt eight checkpoints train (without consulting attempts 2).
The second-attempt eight are held out. We search stride -64..64 excluding
0, base -1100..1300, global byte orientation both choices, and a
retry_offset -256..256 excluding 0. Require >=24 printer-fixed upper
bits with zero contradictions separately in training and holdout.

The genuine AX-7778 checkpoint sequence (known conditional positive)
is recovered at base -157, seq stride 2, attempt offset 1, byte swapped.
The target K04 ACK2 and SHA commitments are excluded from this test.

Uses NumPy and the original-source-pinned Agent2 p951 closure.
Reproduce: python agents/agent38/k04_ax_transfer_grid_stage_sft.py
"""
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np

TRANSFER_SHA = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
MASK = (1 << 32) - 1


def observed_upper(state, known, temper):
    """Bits provably fixed by independent known native state bits."""
    missing = MASK ^ known
    mask = MASK
    while missing:
        bit = missing & -missing
        mask &= MASK ^ temper(bit)
        missing ^= bit
    return (mask >> 16) & 0xffff, (temper(state) >> 16) & 0xffff


def checkpoints(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == TRANSFER_SHA
    data = [json.loads(line) for line in raw.splitlines()]
    values = {}
    for transfer in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        rows = sorted(
            (x for x in data if x["kind"] == "CHUNK" and x["transfer"] == transfer),
            key=lambda x: (x["seq"], x["attempt"]),
        )
        assert len(rows) == 16
        assert [(x["seq"], x["attempt"]) for x in rows] == [
            (seq, attempt) for seq in range(8) for attempt in (1, 2)
        ]
        values[transfer] = [
            [int(rows[2 * seq + attempt]["checkpoint"], 16) for seq in range(8)]
            for attempt in range(2)
        ]
    return values


def swapped16(value):
    return ((value & 255) << 8) | (value >> 8)


def main():
    repo = Path(__file__).resolve().parents[2]
    closure = runpy.run_path(
        str(repo / "agents/agent2/20261102_k04_multicarrier_p951_sft.py")
    )
    words, known, offset = closure["source_closure"](repo / "resources")
    assert all(known[offset + 951 + i] == 0 for i in range(4))
    bits = [observed_upper(w, m, closure["temper"])
            for w, m in zip(words, known)]
    fixed = np.array([v[0] for v in bits], dtype=np.uint16)
    observed = np.array([v[1] for v in bits], dtype=np.uint16)
    bases = np.arange(-1100, 1301, dtype=np.int32)
    results = {}

    for name, pair in checkpoints(
        repo / "resources/evidence/transfers/transfer-audit.jsonl"
    ).items():
        trained = []
        for swap in (False, True):
            codes = [swapped16(v) if swap else v for v in pair[0]]
            for stride in range(-64, 65):
                if stride == 0:
                    continue
                fit, disagreement = (
                    np.zeros(len(bases), dtype=np.uint16)
                    for _ in range(2)
                )
                for seq, code in enumerate(codes):
                    indices = offset + bases + seq * stride
                    masks = fixed[indices]
                    fit += np.bitwise_count(masks).astype(np.uint16)
                    disagreement += np.bitwise_count(
                        (observed[indices] ^ code) & masks
                    ).astype(np.uint16)
                good = (fit >= 24) & (disagreement == 0)
                for j in np.flatnonzero(good):
                    trained.append((swap, stride, int(bases[j]), int(fit[j])))

        heldout = []
        for swap, stride, base, train_bits in trained:
            codes = [swapped16(v) if swap else v for v in pair[1]]
            for retry_offset in range(-256, 257):
                if retry_offset == 0:
                    continue
                indices = [offset + base + retry_offset + j * stride
                           for j in range(8)]
                if any(i < 0 or i >= len(known) for i in indices):
                    continue
                test_bits = sum(int(fixed[i]).bit_count() for i in indices)
                violations = sum(
                    ((int(observed[i]) ^ code) & int(fixed[i])).bit_count()
                    for i, code in zip(indices, codes)
                )
                if test_bits >= 24 and violations == 0:
                    heldout.append((swap, stride, base,
                                    train_bits, retry_offset, test_bits))
        print(name, "first_attempt_fits", trained[:5],
              "count", len(trained), "heldout", heldout[:5],
              "count", len(heldout))
        results[name] = (trained, heldout)

    expected = (True, 2, -157, 45, 1, 61)
    assert results["AX-7778"] == (
        [(True, 2, -157, 45)], [expected]
    )
    for name in ("AX-7781", "AX-7782", "AX-7783"):
        assert results[name] == ([], [])
    print("SOURCE AX-7778 holdout positive PASS; other transfers no fit.")
    print("Conditional stage model only; selected K04 still unconstrained.")


if __name__ == "__main__":
    main()
