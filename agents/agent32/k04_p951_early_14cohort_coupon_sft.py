"""K04 early 14-native-output quartet-donor original commitment sieve.

Portable Python 3. No dependencies beyond the neighboring Agent49 symbolic
source builder. Native stage placements are explicitly hypothetical.
The official evidence, K04 mask, K04 commitment and selected printer packet
are never edited or used to select candidate donor stages.
"""
import hashlib
import itertools
import json
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "resources"
sys.path.insert(0, str(REPO / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, get, source, temper

REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
PTW_SHA = "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32"
GROUP_STAGES = (
    (-1087, -1086, -1085, -1084),
    (-1027, -1026),
    (-918, -917, -916, -915),
    (-860, -859, -858, -857),
)
STAGES = tuple(t for group in GROUP_STAGES for t in group)
assert len(STAGES) == 14
ORIGINAL_MASK = bytes.fromhex("8556C8CB6140A7F9A5123AC7571BEE1C")
TARGET_HASH = bytes.fromhex(json.loads(
    (ROOT / "acceptance.json").read_text(encoding="utf-8")
)["slot_sha256"]["K04"])
original, symbolic = source(ROOT)
assert original.rank == 15365

def original_quotient(vector):
    residual, rhs = 0, 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot in original.rows:
            row, value = original.rows[pivot]
            vector ^= row
            rhs ^= value
        else:
            residual ^= 1 << pivot
            vector ^= 1 << pivot
    return residual, rhs

DONOR_Q = [
    [original_quotient(v) for v in temper(get(symbolic, stage))]
    for stage in STAGES
]
TARGET_Q = [
    original_quotient(v)
    for stage in range(951, 955)
    for v in temper(get(symbolic, stage))
]

def source_compatible(words):
    """Exact original spool plus 448 donor equations, or source contradiction."""
    q = Basis()
    try:
        for vectors, word in zip(DONOR_Q, words):
            for bit, (remaining, original_rhs) in enumerate(vectors):
                q.insert(remaining, ((word >> bit) & 1) ^ original_rhs)
    except AssertionError:
        return None
    assert q.rank == 445
    return q

def selected_expressions(q):
    """128 tempered output bits as affine forms in eight free target variables."""
    unresolved = {}
    expressions = []
    for vector, rhs in TARGET_Q:
        # Reduce against *all* already known donor equation pivots.
        residual = 0
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in q.rows:
                row, value = q.rows[pivot]
                vector ^= row
                rhs ^= value
            else:
                residual ^= 1 << pivot
                vector ^= 1 << pivot
        coefficient = 0
        while residual:
            pivot = residual.bit_length() - 1
            if pivot in unresolved:
                row, mask = unresolved[pivot]
                residual ^= row
                coefficient ^= mask
            else:
                assert len(unresolved) < 8
                mask = 1 << len(unresolved)
                unresolved[pivot] = (residual, mask)
                coefficient ^= mask
                residual = 0
        expressions.append((coefficient, rhs))
    assert len(expressions) == 128 and len(unresolved) == 8
    return expressions

def hash_all_256(q, planted_payload=None):
    expressions = selected_expressions(q)
    matches = 0
    synthetic_seen = False
    for guess in range(256):
        payload = bytearray(16)
        for bit, (mask, known) in enumerate(expressions):
            payload[bit // 8] |= (
                known ^ ((mask & guess).bit_count() & 1)
            ) << (bit % 8)
        if planted_payload is not None and bytes(payload) == planted_payload:
            synthetic_seen = True
        component = bytes(a ^ b for a, b in zip(payload, ORIGINAL_MASK))
        if hashlib.sha256(component).digest() == TARGET_HASH:
            matches += 1
            print("ORIGINAL_K04_HIT", payload.hex().upper(), component.hex().upper())
    return matches, synthetic_seen

# Genuine *source-consistent* full 624-word state and withheld-coupon positive.
state = 0
for pivot, (vector, value) in sorted(original.rows.items()):
    state |= (value ^ ((vector & state).bit_count() & 1)) << pivot
assert all(
    ((vector & state).bit_count() & 1) == rhs
    for vector, rhs in original.rows.values()
)

def synthetic_word(stage):
    return sum(
        (((vector & state).bit_count() & 1) << bit)
        for bit, vector in enumerate(temper(get(symbolic, stage)))
    )

plant = b"".join(
    synthetic_word(stage).to_bytes(4, "little")
    for stage in range(951, 955)
)
assert plant.hex().upper() == "054AD23723EAFB47DDF71A422DD941CB"
q = source_compatible([synthetic_word(t) for t in STAGES])
assert q is not None
control_hits, control_seen = hash_all_256(q, plant)
assert control_seen and control_hits == 0
print("GENUINE_SOURCE_STATE_14_DONOR_WITHHELD_COUPON_PASS")

def run_family(variants):
    assigned, compatible, tested, found = 0, 0, 0, 0
    for groups in variants:
        for order in itertools.permutations(groups):
            for views in itertools.product(range(4), repeat=4):
                encoded = []
                for label, view in zip(order, views):
                    raw = list(groups[label])
                    if view & 1:
                        raw.reverse()
                    encoded.append([
                        int.from_bytes(chunk, "big" if view & 2 else "little")
                        for chunk in raw
                    ])
                for start in (0, 2):
                    assigned += 1
                    words = (
                        encoded[0] + encoded[1][start:start+2]
                        + encoded[2] + encoded[3]
                    )
                    q = source_compatible(words)
                    if q is None:
                        continue
                    compatible += 1
                    hits, _ = hash_all_256(q)
                    found += hits
                    tested += 256
    return (assigned, compatible, tested, found)

# Family A: four real node49/event82 4-control cohorts.
raw = (ROOT / "evidence" / "recorder" / "trip-recorder.raw").read_bytes()
assert hashlib.sha256(raw).hexdigest() == REC_SHA
recorder = {group: {} for group in (200, 300, 900, 990)}
for index in range(88):
    at = 16 + 24 * index
    timestamp, node, event, latch, seq, control, aux, crc = struct.unpack_from(
        "<IHBBI4sII", raw, at
    )
    if (node, event) != (49, 82):
        continue
    group = next(
        (g for g in recorder if g <= seq < g + 4), None
    )
    if group is not None:
        recorder[group][seq - group] = (
            control,
            zlib.crc32(raw[at:at+20]) == crc,
        )
assert all(len(group) == 4 for group in recorder.values())
assert all(
    recorder[group][i][1] == (group != 900)
    for group in recorder for i in range(4)
)
recorder_quartets = {
    group: [recorder[group][i][0] for i in range(4)]
    for group in recorder
}
recorder_result = run_family([recorder_quartets])
assert recorder_result == (12288, 1560, 399360, 0), recorder_result
print("RECORDER_14_DONOR_ORIGINAL", recorder_result)

# Family B: four real PTW417 bay-order revision quartets. Rev1 has two
# different original bay-A receipts; test each without silently selecting one.
receipts = (ROOT / "evidence" / "maintenance" / "seal-receipts.jsonl").read_bytes()
assert hashlib.sha256(receipts).hexdigest() == PTW_SHA
by_revision_bay = defaultdict(list)
for line in receipts.decode("utf-8").splitlines():
    row = json.loads(line)
    if row["permit"] == "PTW-417":
        by_revision_bay[(row["revision"], row["bay"])].append(
            bytes.fromhex(row["serial"][3:])
        )
assert len(by_revision_bay) == 16
assert len(by_revision_bay[(1, "A")]) == 2
assert sum(map(len, by_revision_bay.values())) == 17

def maintenance_variants():
    for first_A in by_revision_bay[(1, "A")]:
        yield {
            revision: [
                first_A if (revision, bay) == (1, "A")
                else by_revision_bay[(revision, bay)][0]
                for bay in "ABCD"
            ]
            for revision in range(1, 5)
        }

maintenance_result = run_family(maintenance_variants())
assert maintenance_result == (24576, 3216, 823296, 0), maintenance_result
print("MAINTENANCE_14_DONOR_ORIGINAL", maintenance_result)
print("COMBINED_FULL_K04_COMMITMENT_CHECKS", recorder_result[2] + maintenance_result[2])
print("ALL ORIGINAL_K04_MATCHES", recorder_result[3] + maintenance_result[3])
print("Original 6 PASS, K04/K08 MISSING, combined INCOMPLETE")
