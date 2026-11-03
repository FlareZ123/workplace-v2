"""Source-only extended AX transfer checkpoint alignment against p951 printer basis.
Run from the repo with python agents/agent4/k04_future_ax_stage_sft.py.
Selected printer ACK2 is excluded by the imported original source basis.
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import source, temper, ORIGIN, MAG

LAST = 1800
basis, words = source(ROOT / "resources")
assert basis.rank == 15365
for idx in range(len(words), LAST - ORIGIN + 1):
    t = idx - 624
    words.append([
        words[t + 397][bit]
        ^ (words[t][31] if bit == 30 else
           (words[t + 1][bit + 1] if bit < 30 else 0))
        ^ (words[t + 1][0] if ((MAG >> bit) & 1) else 0)
        for bit in range(32)
    ])

def output_bits(stage):
    return temper(words[stage - ORIGIN])

raw = (ROOT / "resources/evidence/transfers/transfer-audit.jsonl").read_text()
groups = collections.defaultdict(dict)
for record in map(json.loads, raw.splitlines()):
    if record["kind"] == "CHUNK":
        groups[record["transfer"]][(record["seq"], record["attempt"])] = record["checkpoint"]

pairs = [(seq, attempt) for seq in range(8) for attempt in (1, 2)]
source_fixed = 0
for index, pair in enumerate(pairs):
    checkpoint = int.from_bytes(bytes.fromhex(groups["AX-7778"][pair]), "little")
    for bit, row in enumerate(output_bits(-157 + index)[16:]):
        predicted = basis.predict(row)
        if predicted is not None:
            source_fixed += 1
            assert predicted == ((checkpoint >> bit) & 1)
assert source_fixed == 122, source_fixed

for index, pair in enumerate(pairs):
    checkpoint = int.from_bytes(bytes.fromhex(groups["AX-7778"][pair]), "little")
    for bit, row in enumerate(output_bits(-157 + index)[16:]):
        basis.insert(row, (checkpoint >> bit) & 1)
assert basis.rank == 15495, basis.rank

fixed = {}
for stage in range(ORIGIN, LAST + 1):
    mask = value = 0
    for bit, row in enumerate(output_bits(stage)[16:]):
        predicted = basis.predict(row)
        if predicted is not None:
            mask |= 1 << bit
            value |= predicted << bit
    fixed[stage] = (mask, value)

layouts = {
    "seq_attempt": pairs,
    "attempt_seq": [(seq, attempt) for attempt in (1, 2) for seq in range(8)],
    "attempt_1": [(seq, 1) for seq in range(8)],
    "attempt_2": [(seq, 2) for seq in range(8)],
}
for transfer in ("AX-7781", "AX-7782", "AX-7783"):
    checks = passing = 0
    best = None
    for order in ("big", "little"):
        for layout_name, layout in layouts.items():
            values = [
                int.from_bytes(bytes.fromhex(groups[transfer][pair]), order)
                for pair in layout
            ]
            for stride in range(1, 9):
                for start in range(ORIGIN, LAST - stride * (len(values) - 1) + 1):
                    checks += 1
                    support = mismatches = 0
                    for index, checkpoint in enumerate(values):
                        mask, value = fixed[start + stride * index]
                        support += mask.bit_count()
                        mismatches += ((checkpoint ^ value) & mask).bit_count()
                    if support >= 40:
                        if mismatches == 0:
                            passing += 1
                        candidate = (mismatches, -support, order, layout_name, stride, start)
                        if best is None or candidate < best:
                            best = candidate
    assert checks == 182496, (transfer, checks)
    assert passing == 0, (transfer, passing)
    print(transfer, "scans", checks, "matches >=40 fixed bits", passing, "best", best)

def extend_rank(existing, vectors):
    pivots = dict(existing)
    gained = 0
    for vector in vectors:
        while vector:
            position = vector.bit_length() - 1
            if position not in pivots:
                pivots[position] = vector
                gained += 1
                break
            vector ^= pivots[position]
    return pivots, gained

base = {position: row for position, (row, value) in basis.rows.items()}
target = [row for stage in range(951, 955) for row in output_bits(stage)]
_, unknown = extend_rank(base, target)
assert unknown == 128, unknown

def future_rows(stage):
    return [
        row
        for position in range(stage, stage + 16)
        for row in output_bits(position)[16:]
    ]

start_triple = (1179, 1347, 1574)
future, added = extend_rank(base, [row for stage in start_triple for row in future_rows(stage)])
_, unknown = extend_rank(future, target)
assert (added, unknown) == (325, 16), (added, unknown)
print("conditional future starts", start_triple, "rank added", added,
      "remaining K04 bits", unknown)
print("SOURCE-ONLY SFT PASS; no authentic K04 bit or final K08 word recovered")
