"""K02 donor source-predictivity test; imports the original exact MT basis and never tests K04 target."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import hashlib
import json
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

TELE_SHA = "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f"
STAGES = (1178, 1179, 1405, 1406)


def words_from_raw(raw, endian, reverse, halves, native):
    parts = [raw[i:i+4] for i in (0, 4, 8, 12)]
    if halves:
        parts = [p[2:] + p[:2] for p in parts]
    if reverse:
        parts.reverse()
    values = [int.from_bytes(p, endian) for p in parts]
    return values if native else [mt.untemper(v) for v in values]


def reduce_against(rows, vector):
    remainder = constant = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in rows:
            remainder ^= 1 << pivot
            vector ^= 1 << pivot
        else:
            row, rhs = rows[pivot]
            vector ^= row
            constant ^= rhs
    return remainder, constant


def constraints(rows, bank, stage, mode):
    # Each native output bit is an explicit GF(2) mask of the 128 donor bits.
    masks = [0] * 128
    for bit in range(128):
        decoded = words_from_raw((1 << bit).to_bytes(16, "little"), *mode)
        for lane, word in enumerate(decoded):
            while word:
                low = word & -word
                masks[32 * lane + low.bit_length() - 1] |= 1 << bit
                word -= low

    vectors = [v for lane in range(4) for v in mt.get(bank, stage + lane)]
    pivots = {}
    checks = []
    for vector, mask in zip(vectors, masks):
        rem, rhs = reduce_against(rows, vector)
        while rem:
            pivot = rem.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (rem, mask, rhs)
                break
            row, donor_mask, constant = pivots[pivot]
            rem ^= row
            mask ^= donor_mask
            rhs ^= constant
        if rem == 0:
            checks.append((mask, rhs))
    assert len(pivots) + len(checks) == 128
    return len(pivots), checks


def compatible(checks, donor):
    return all(((mask & donor).bit_count() & 1) == bit for mask, bit in checks)


def exact_uniform_distribution(group):
    # Every uniform 128bit donor produces one of 2^r equally likely
    # 16bit response syndromes, where r is the rank of these masks.
    columns = {}
    for bit in range(128):
        v = sum(((checks[0][0] >> bit) & 1) << i for i, (_, checks) in enumerate(group))
        while v:
            pivot = v.bit_length() - 1
            if pivot not in columns:
                columns[pivot] = v
                break
            v ^= columns[pivot]
    values = [0]
    for v in columns.values():
        values += [x ^ v for x in values]
    expected = sum((checks[0][1] & 1) << i for i, (_, checks) in enumerate(group))
    histogram = Counter(16 - (x ^ expected).bit_count() for x in values)
    return len(columns), histogram


def selected_k02(root):
    data = (root / "evidence/telemetry/freeze-export.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == TELE_SHA
    selected = {}
    start = datetime.fromisoformat("2026-10-03T21:13:40+00:00")
    end = datetime.fromisoformat("2026-10-03T21:13:48+00:00")
    for line in data.splitlines():
        entry = json.loads(line)
        if any((entry.get("tag") != "LT-204",
                entry.get("field") != "DIAG_WORD",
                entry.get("quality") != "GOOD",
                entry.get("state") != "HOLD",
                entry.get("seq") not in range(8))):
            continue
        if not start <= datetime.fromisoformat(entry["ts"]) < end:
            continue
        index = entry["seq"]
        if index not in selected or entry["revision"] > selected[index]["revision"]:
            selected[index] = entry
    raw = b"".join(int(selected[i]["value"]).to_bytes(2, "big") for i in range(8))
    assert raw.hex().upper() == "E1A5E474BAD7E853A2E8C71D3317D507"
    return raw


def main(root):
    mt.LAST = 3500
    basis, bank = mt.source(root)
    raw = selected_k02(root)
    donor = int.from_bytes(raw, "little")
    modes = [(e, r, h, n) for e in ("big", "little")
             for r in (False, True) for h in (False, True)
             for n in (False, True)]
    assert basis.rank == 15365
    rng = random.Random(0x481406)
    halves = [raw[i:i+2] for i in range(0, 16, 2)]
    placeholders = [
        int.from_bytes(b"".join(rng.sample(halves, 8)), "little")
        for _ in range(10000)
    ]
    for stage in STAGES:
        group = [constraints(basis.rows, bank, stage, m) for m in modes]
        ranks = {rank for rank, _ in group}
        predicted = {len(checks) for _, checks in group}
        observed = sum(compatible(checks, donor) for _, checks in group)
        expected = {1178: (128, 0, 16), 1179: (96, 32, 0),
                    1405: (128, 0, 16), 1406: (127, 1, 10)}[stage]
        assert (next(iter(ranks)), next(iter(predicted)), observed) == expected
        print("STAGE", stage, "donor_new_rank", *ranks,
              "donor_predicted_bits", *predicted,
              "original_compatible", observed, "/16", flush=True)
        perm_scores = Counter(
            sum(compatible(c, x) for _, c in group) for x in placeholders
        )
        tail = sum(n for score, n in perm_scores.items() if score >= observed)
        print("HALFWORD_PERMUTATION_PLACEBOS", stage, tail,
              "/10000 at_least_original", flush=True)
        if stage == 1406:
            rank, hist = exact_uniform_distribution(group)
            assert rank == 16
            tail = sum(n for score, n in hist.items() if score >= observed)
            assert tail == 14893 and sum(hist.values()) == 65536
            print("EXACT_UNIFORM", "rank", rank, "at_least_original",
                  tail, "/65536", "histogram", sorted(hist.items()), flush=True)
    print("SOURCE_ONLY_CALIBRATION_COMPLETE no K04 or K08 hash queries")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "resources"))
