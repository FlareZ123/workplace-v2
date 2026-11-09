"""K04 original-source test of indexed HST 32-bit quantized MT draws in printer gaps.

Model: for each HST PV record indexed to the corresponding spool job, allow
any one native 32-bit output word in that job's following inter-packet gap.
PV = round(12 + 76 * native_word/2**32, 3).
Only source-fixed printer bits are compared. Selected ACK2 is completely omitted.

Run: python agents/agent32/k04_hst_gap_uint32_sft.py
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent49.k04_p951_symbolic_basis import STARTS, ORIGIN, Basis, source, untemper, temper

EVIDENCE = ROOT / "resources" / "evidence"
PV_HASH = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
DEN = 152000


def load_source():
    assert hashlib.sha256((EVIDENCE / "print/spool-reconstruction.log").read_bytes()).hexdigest() == SPOOL_HASH
    raw = (EVIDENCE / "telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PV_HASH
    pv = {int(row["seq"]): row for line in raw.splitlines()
          if (row := json.loads(line))["field"] == "PV"}
    assert sorted(pv) == list(range(100, 212))
    basis, word_vectors = source(ROOT)
    assert basis.rank == 15365
    return pv, basis, word_vectors


def prefix_bits(millivalue):
    lower_numerator = (2 * millivalue - 24001) << 32
    upper_numerator = (2 * millivalue - 23999) << 32
    low = (lower_numerator + DEN - 1) // DEN
    high = (upper_numerator + DEN - 1) // DEN - 1
    assert 0 <= low <= high < 1 << 32
    length = 32 - (low ^ high).bit_length()
    return [(low >> (31 - j)) & 1 for j in range(length)]


def fixed_check(basis, word_vectors, stage, millivalue):
    predicted = temper(word_vectors[stage - ORIGIN])
    needed = prefix_bits(millivalue)
    fixed, matched = 0, 0
    for j, want in enumerate(needed):
        actual = basis.predict(predicted[31 - j])
        if actual is not None:
            fixed += 1
            matched += actual == want
    return fixed, matched


def stages(row_index):
    return range(STARTS[row_index] + 4, STARTS[row_index + 1])


def original(pv, basis, word_vectors):
    contradictions = []
    informative = 0
    for seq, row in sorted(pv.items()):
        i = seq - 100
        millivalue = int(round(float(row["value"]) * 1000))
        choices = [fixed_check(basis, word_vectors, stage, millivalue)
                   for stage in stages(i)]
        assert choices
        informative += any(fixed > 0 for fixed, _ in choices)
        if all(fixed != matched for fixed, matched in choices):
            contradictions.append((seq, row["quality"], row["value"]))
    early = sum(seq < 180 for seq, _, _ in contradictions)
    late = len(contradictions) - early
    good = sum(quality == "GOOD" for _, quality, _ in contradictions)
    print("ORIGINAL_PV", len(pv), "SPOOL_RANK", basis.rank,
          "INFORMATIVE", informative,
          "EVERY_STAGE_CONTRADICTIONS", len(contradictions),
          "GOOD", good, "EARLY", early, "LATE", late, flush=True)
    print("CONTRADICTED_ROWS", contradictions, flush=True)
    return contradictions


def planted(word_vectors):
    rng = random.Random(0x4A17C9)
    native = [rng.getrandbits(32) for _ in range(967)]
    basis = Basis()
    for i, start in enumerate(STARTS):
        if i == 129:
            continue
        for lane in range(4):
            state = untemper(native[start + lane])
            for bit, vector in enumerate(word_vectors[start + lane - ORIGIN]):
                basis.insert(vector, (state >> bit) & 1)
    assert basis.rank == 15365
    n = 0
    informative = 0
    for i in range(112):
        stage = STARTS[i] + 4
        millivalue = round((12 + 76 * native[stage] / (1 << 32)) * 1000)
        fixed, matched = fixed_check(basis, word_vectors, stage, millivalue)
        assert fixed == matched, (i, stage, fixed, matched)
        informative += fixed > 0
        n += 1
    print("SYNTHETIC_32BIT_TRUE_POSITIVE", n, "INFORMATIVE", informative, flush=True)
    assert n == 112 and informative > 0


if __name__ == "__main__":
    original_pv, print_basis, vectors = load_source()
    original(original_pv, print_basis, vectors)
    planted(vectors)
