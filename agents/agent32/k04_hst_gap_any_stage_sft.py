"""Source-only test: every native MT float placement within the HST/job-index gap.

Run from the workplace-v2 repository root: python agents/agent32/k04_hst_gap_any_stage_sft.py
Reads original records; excludes selected PS-0417 ACK2 bytes and all commitments.
"""
import hashlib
import json
import random
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agents.agent49.k04_p951_symbolic_basis import (
    STARTS, ORIGIN, Basis, source, untemper, temper,
)

EVIDENCE = ROOT / "resources" / "evidence"
PV_HASH = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
DEN = 152000


def load_pv():
    raw = (EVIDENCE / "telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PV_HASH
    rows = [json.loads(line) for line in raw.splitlines()]
    pv = {int(x["seq"]): x for x in rows if x["field"] == "PV"}
    assert len(pv) == 112 and sorted(pv) == list(range(100, 212))
    return pv


def fixed_prefix(m):
    # Round-to-nearest millivalue: (m-0.5)/1000 <= 12+76U < (m+0.5)/1000.
    lower = ((2*m-24001) << 16) // DEN
    upper = (((2*m-23999) << 16)-1) // DEN
    assert 0 <= lower <= upper < 1 << 16
    count = 16 - (lower ^ upper).bit_length()
    return [(lower >> (15-j)) & 1 for j in range(count)]


def predicted_high_bits(basis, words, stage):
    vectors = temper(words[stage - ORIGIN])
    return [basis.predict(vectors[31-j]) for j in range(16)]


def compare(basis, words, stage, millivalue):
    predicted = predicted_high_bits(basis, words, stage)
    observed = fixed_prefix(millivalue)
    pairs = [(predicted[j], bit) for j, bit in enumerate(observed)]
    fixed = sum(p is not None for p, _ in pairs)
    matches = sum(p == b for p, b in pairs if p is not None)
    return fixed, matches


def gap_stages(index):
    # Two native words must lie entirely after this spool packet and before the next.
    return range(STARTS[index] + 4, STARTS[index + 1] - 1)


def actual():
    assert hashlib.sha256((EVIDENCE / "print/spool-reconstruction.log").read_bytes()).hexdigest() == SPOOL_HASH
    pv = load_pv()
    basis, words = source(ROOT)  # source() withholds selected row129 completely.
    assert basis.rank == 15365
    excluded, excluded_good, first, late, zero_information = [], [], 0, 0, 0
    for seq in sorted(pv):
        i = seq - 100
        millivalue = int(round(float(pv[seq]["value"]) * 1000))
        candidates = list(gap_stages(i))
        assert candidates
        outcomes = [compare(basis, words, pos, millivalue) for pos in candidates]
        if any(f == 0 for f, _ in outcomes):
            zero_information += 1
        if all(f != matched for f, matched in outcomes):
            excluded.append(seq)
            if pv[seq]["quality"] == "GOOD":
                excluded_good.append(seq)
            if seq < 180:
                first += 1
            else:
                late += 1
    print("ORIGINAL_ROWS", len(pv), "PRINTER_RANK", basis.rank)
    print("ANY_GAP_POSITION_CONTRADICTIONS", len(excluded), "GOOD", len(excluded_good),
          "EARLY_100_179", first, "WITHHELD_LATE_180_211", late)
    print("ROWS_WITH_ZERO_FIXED_BIT_POSITION", zero_information)
    print("CONTRADICTED_SEQUENCES", excluded)
    assert (len(excluded), len(excluded_good), first, late) == (29, 18, 15, 14)
    return words


def synthetic(words):
    # Genuine CPython random() source, with printer target omitted from calibration.
    rng = random.Random(0x4A17C9)
    native = [rng.getrandbits(32) for _ in range(967)]
    basis = Basis()
    for i, pos in enumerate(STARTS):
        if i == 129:
            continue
        for lane in range(4):
            value = native[pos + lane]
            state = untemper(value)
            for bit, vector in enumerate(words[pos + lane - ORIGIN]):
                basis.insert(vector, (state >> bit) & 1)
    assert basis.rank == 15365
    tested, informative = 0, 0
    for i in range(112):
        stage = STARTS[i] + 4
        u = ((native[stage] >> 5) * (1 << 26) +
             (native[stage + 1] >> 6)) / (1 << 53)
        millivalue = round((12 + 76*u) * 1000)
        fixed, matched = compare(basis, words, stage, millivalue)
        assert fixed == matched, (i, stage, fixed, matched)
        informative += fixed > 0
        tested += 1
    print("SYNTHETIC_TRUE_GAP_PRODUCER_PASS", tested, "INFORMATIVE", informative)
    assert (tested, informative) == (112, 42)


if __name__ == "__main__":
    synthetic(actual())
