"""H17 K04 exact conditional four-carrier MT donor frontier; original sources only.

Reproducer:
    python agents/agent5/k04_p951_fourcarrier_donor_frontier_sft.py

No source values from selected printer ACK row129, K04 commitment or candidate enter
the equations. The native index chronology is an unverified producer hypothesis.
"""
from pathlib import Path
import importlib.util
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
spec = importlib.util.spec_from_file_location("h17_p951_basis", LIB)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
mt.LAST = 2020
basis, symbolic = mt.source(ROOT / "resources")
assert basis.rank == 15365
original_rank = basis.rank

def get(index):
    return mt.get(symbolic, index)

def clone(source):
    result = mt.Basis()
    result.rows = source.rows.copy()
    result.rank = source.rank
    return result

def add_word(b, position, data):
    value = mt.untemper(int.from_bytes(data, "little"))
    for bit, expr in enumerate(get(position)):
        b.insert(expr, (value >> bit) & 1)

def target_residual(b):
    temporary = clone(b)
    old_rank = temporary.rank
    for position in range(951, 955):
        for expression in get(position):
            if temporary.predict(expression) is None:
                temporary.insert(expression, 0)
    return temporary.rank - old_rank

def temper_forms(v):
    a = [v[j] ^ (v[j+11] if j+11<32 else 0) for j in range(32)]
    b = [a[j] ^ (a[j-7] if j>=7 and (0x9d2c5680>>j)&1 else 0) for j in range(32)]
    c = [b[j] ^ (b[j-15] if j>=15 and (0xefc60000>>j)&1 else 0) for j in range(32)]
    return [c[j] ^ (c[j+18] if j+18<32 else 0) for j in range(32)]

recorder = (ROOT/"resources/evidence/recorder/trip-recorder.raw").read_bytes()
records = []
for i in range(88):
    offset = 16 + i*24
    timestamp, node, event, latch, seq, control, aux, crc = struct.unpack_from(
        "<IHBBI4sII", recorder, offset
    )
    records.append({
        "node": node, "seq": seq, "latch": latch, "control": control,
        "crc_valid": zlib.crc32(recorder[offset:offset+20]) == crc,
    })
node50 = {
    7:-810, 9:-793, 12:-775, 13:-769, 14:-759,
    24:-683, 25:-677, 41:-568, 43:-552, 44:-545,
    45:-540, 61:-417, 63:-397, 64:-390, 70:-339,
}
for rec in records:
    if rec["node"] == 50 and rec["seq"] in node50:
        assert rec["crc_valid"]
        position = node50[rec["seq"]]
        native = mt.untemper(int.from_bytes(rec["control"], "little"))
        predicted_bits = 0
        for j, expr in enumerate(get(position)):
            observed = basis.predict(expr)
            if observed is not None:
                predicted_bits += 1
                assert observed == ((native >> j) & 1)
        assert predicted_bits >= 16
        add_word(basis, position, rec["control"])
assert basis.rank == 15375
assert target_residual(basis) == 128

node49_count = 0
for rec in records:
    if rec["node"] != 49:
        continue
    seq = rec["seq"]
    if 200 <= seq <= 203:
        position = -324 + 3*(seq-200)
    elif 900 <= seq <= 903:
        position = -323 + 3*(seq-900)
    elif 990 <= seq <= 993:
        position = -322 + 3*(seq-990)
    else:
        continue
    # The four source CRC-invalid node49 seq900..903 values are expressly
    # hypothetical auxiliary raw observations, never accepted K05 evidence.
    add_word(basis, position, rec["control"])
    node49_count += 1
assert node49_count == 12
assert basis.rank == 15503
assert target_residual(basis) == 128

audit = (ROOT/"resources/evidence/transfers/transfer-audit.jsonl").read_text()
rows = [json.loads(line) for line in audit.splitlines()]
checkpoints = {
    2*row["seq"]+row["attempt"]-1: int(row["checkpoint"], 16)
    for row in rows if row["kind"]=="CHUNK" and row["transfer"]=="AX-7778"
}
assert len(checkpoints) == 16
heldout_matches = 0
for i in range(16):
    value = checkpoints[i]
    value = (value & 255)*256 + (value >> 8)  # preserve raw two-byte orientation
    for bit, expression in enumerate(temper_forms(get(-157+i))[16:]):
        known = basis.predict(expression)
        if known is not None:
            heldout_matches += 1
            assert known == ((value >> bit)&1)
        basis.insert(expression, (value >> bit)&1)
assert heldout_matches >= 100
assert basis.rank == 15632
assert target_residual(basis) == 128
print("Original source ranks:", original_rank, 15375, 15503, basis.rank)
print("AX-7778 source-fixed bits before insertion:", heldout_matches)

# Compute exact source-quotient residues before trying any hypothetical donor.
def remainder(v):
    residue = 0
    while v:
        pivot = v.bit_length()-1
        equation = basis.rows.get(pivot)
        if equation is None:
            v ^= (1<<pivot)
            residue |= 1<<pivot
        else:
            v ^= equation[0]
    return residue

def rank_insert(rows, v):
    while v:
        pivot = v.bit_length()-1
        existing = rows.get(pivot)
        if existing is None:
            rows[pivot] = v
            return 1
        v ^= existing
    return 0

target = {}
target_rank = 0
for position in range(951, 955):
    for expression in get(position):
        target_rank += rank_insert(target, remainder(expression))
assert target_rank == 128

frontier = []
for index in range(mt.ORIGIN, mt.LAST+1):
    donor = {}
    total = target.copy()
    donor_rank = 0
    total_rank = target_rank
    for expression in get(index):
        reduced = remainder(expression)
        donor_rank += rank_insert(donor, reduced)
        total_rank += rank_insert(total, reduced)
    information_gain = target_rank + donor_rank - total_rank
    if information_gain:
        frontier.append((index, information_gain))

expected = [
    (-523,1), (724,1), (951,32), (952,32), (953,32), (954,32),
    (1179,31), (1180,32), (1181,32), (1406,31), (1407,32),
    (1408,32), (1633,31), (1634,2)
]
assert frontier == expected, (frontier, expected)
print("Full-native-donor target-informative positions:", frontier)
print("Other", len(symbolic)-len(frontier), "positions contribute zero single-word target rank.")

# Purely synthetic positive control, not a source witness: adding all 32 raw
# bits at index1407 collapses exactly 32 of the 128 selected dimensions.
synthetic = clone(basis)
for expression in get(1407):
    synthetic.insert(expression, 0)
assert target_residual(synthetic) == 96
print("Synthetic donor +32-bit target gain PASS; no original K04 key recovered.")
