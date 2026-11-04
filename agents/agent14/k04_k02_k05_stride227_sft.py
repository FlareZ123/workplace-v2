"""H-17 K04 original-target checks for sparse K05 writer stride of 227 MT words.

Selected K02 telemetry and the four selected CRC-valid K05 recorder latches
are source-pinned. The K04 copied selected ACK and its acceptance commitment
are entirely withheld during stage, rank and writer-format selection.
The exact original commitment is used only after an entire component exists.

Run: python agents/agent14/k04_k02_k05_stride227_sft.py
"""
from collections import Counter
from pathlib import Path
import hashlib
import itertools
import json
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 2700
SOURCE = ROOT / "resources"
PINS = {
    "telemetry/freeze-export.jsonl": "3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f",
    "recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
}
for name, want in PINS.items():
    assert hashlib.sha256((SOURCE / "evidence" / name).read_bytes()).hexdigest() == want

k02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
raw = (SOURCE / "evidence/recorder/trip-recorder.raw").read_bytes()
controls = {}
for i in range(88):
    r = raw[16 + 24*i:16 + 24*(i+1)]
    _, node, event, latch, sequence = struct.unpack_from("<IHBBI", r)
    if node == 49 and event == 82 and 300 <= sequence <= 303:
        assert zlib.crc32(r[:20]) == struct.unpack_from("<I", r, 20)[0]
        controls[latch] = r[12:16]
assert sorted(controls) == [0, 1, 2, 3]
k05 = b"".join(controls[i] for i in range(4))
assert k05.hex().upper() == "FF8B78200A56E8586DCDA00EF01E4572"
accepted = json.loads((SOURCE / "acceptance.json").read_text())["slot_sha256"]
assert hashlib.sha256(hashlib.sha256(k02).digest()[:16]).hexdigest() == accepted["K02"]
assert hashlib.sha256(k05).hexdigest() == accepted["K05"]
target = bytes.fromhex(accepted["K04"])
assert target.hex() == "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
route = json.loads((SOURCE / "evidence/recovery-routing.json").read_text())
mask = bytes.fromhex(route["K04"]["masked_component"])
assert mask.hex().upper() == "8556C8CB6140A7F9A5123AC7571BEE1C"

printer, symbolic = mt.source(SOURCE)
assert printer.rank == 15365
selected = [equation for stage in range(951, 955) for equation in mt.get(symbolic, stage)]


def donor_modes():
    for endian in ("big", "little"):
        for reverse, swap_halves, native in itertools.product((False, True), repeat=3):
            chunks = [k02[k:k+4] for k in (0, 4, 8, 12)]
            if swap_halves:
                chunks = [p[2:]+p[:2] for p in chunks]
            if reverse:
                chunks.reverse()
            values = [int.from_bytes(p, endian) for p in chunks]
            yield (endian, reverse, swap_halves, native), [
                w if native else mt.untemper(w) for w in values
            ]


def k05_modes(value):
    candidates = [int.from_bytes(value, endian) for endian in ("little", "big")]
    return candidates + [mt.untemper(w) for w in candidates]


variants = [k05_modes(k05[4*i:4*i+4]) for i in range(4)]


def residual(base, expression):
    r = c = 0
    while expression:
        pivot = expression.bit_length() - 1
        if pivot in base.rows:
            vector, value = base.rows[pivot]
            expression ^= vector
            c ^= value
        else:
            r ^= 1 << pivot
            expression ^= 1 << pivot
    return r, c


def extend(base, assignments):
    result = mt.Basis()
    result.rows = base.rows.copy()
    result.rank = base.rank
    for stage, word in assignments:
        for bit, equation in enumerate(mt.get(symbolic, stage)):
            result.insert(equation, (word >> bit) & 1)
    return result


def nullspace_checks(base, stages):
    """Return exact necessary and sufficient parity checks on four K05 words."""
    pivots = {}
    checks = []
    for lane, stage in enumerate(stages):
        for bit, equation in enumerate(mt.get(symbolic, stage)):
            residual_value, parity = residual(base, equation)
            tag = 1 << (32 * lane + bit)
            while residual_value:
                pivot = residual_value.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = (residual_value, tag, parity)
                    break
                v, t, c = pivots[pivot]
                residual_value ^= v
                tag ^= t
                parity ^= c
            if residual_value == 0:
                checks.append((tag, parity))
    assert len(checks) + len(pivots) == 128
    return checks


def consistent(value, checks):
    return all(((value & tag).bit_count() & 1) == rhs for tag, rhs in checks)


def temper_scalar(word):
    word ^= word >> 11
    word ^= (word << 7) & 0x9D2C5680
    word ^= (word << 15) & 0xEFC60000
    word ^= word >> 18
    return word & 0xFFFFFFFF


def make_component(bits):
    data = b"".join(
        temper_scalar(sum(bits[32*k+j] << j for j in range(32))).to_bytes(4, "little")
        for k in range(4)
    )
    return bytes(x ^ y for x, y in zip(data, mask))


def complete_candidates(base):
    pivots = {}
    free = []
    coefficients = []
    constants = []
    for equation in selected:
        remainder, constant = residual(base, equation)
        coefficient = 0
        while remainder:
            pivot = remainder.bit_length() - 1
            if pivot in pivots:
                v, tag = pivots[pivot]
                remainder ^= v
                coefficient ^= tag
            else:
                tag = 1 << len(free)
                pivots[pivot] = (remainder, tag)
                free.append(remainder)
                coefficient ^= tag
                break
        coefficients.append(coefficient)
        constants.append(constant)
    for variant in range(1 << len(free)):
        bits = [
            constant ^ ((coeff & variant).bit_count() & 1)
            for coeff, constant in zip(coefficients, constants)
        ]
        yield make_component(bits), len(free)


def state_from_basis(base):
    state = 0
    for pivot, (equation, bit) in sorted(base.rows.items()):
        if bit ^ ((equation & state).bit_count() & 1):
            state |= 1 << pivot
    return state


# These source-only rank-reducing layouts were identified before looking at
# original K05 values. The remaining higher-dimensional layouts are omitted.
layouts = [(1178, 169, 2), (1178, 338, 3), (1405, 111, 3), (1405, 338, 3)]
totals = Counter()
for free_order in (False, True):
    orders = list(itertools.permutations(range(4))) if free_order else [(0, 1, 2, 3)]
    for donor, offset, expected_dimension in layouts:
        stages = [donor + offset + 227 * i for i in range(4)]
        counts = Counter()
        unique = set()
        for _, donor_words in donor_modes():
            source = extend(printer, [(donor+i, w) for i, w in enumerate(donor_words)])
            assert source.rank == 15493
            checks = nullspace_checks(source, stages)
            for order in orders:
                for formats in itertools.product(range(4), repeat=4):
                    chosen = [variants[order[i]][formats[i]] for i in range(4)]
                    packed = sum(w << (32*i) for i, w in enumerate(chosen))
                    counts["source_assignments"] += 1
                    if not consistent(packed, checks):
                        continue
                    counts["compatible"] += 1
                    joint = extend(source, zip(stages, chosen))
                    full = list(complete_candidates(joint))
                    assert full[0][1] == expected_dimension
                    counts["complete_checks"] += len(full)
                    if not counts["synthetic_positive"]:
                        state = state_from_basis(joint)
                        planted = make_component([((v & state).bit_count() & 1) for v in selected])
                        assert planted in {v for v, _ in full}
                        planted_hash = hashlib.sha256(planted).digest()
                        assert sum(hashlib.sha256(v).digest() == planted_hash for v, _ in full) == 1
                        counts["synthetic_positive"] += 1
                    for coupon, _ in full:
                        unique.add(coupon)
                        if hashlib.sha256(coupon).digest() == target:
                            counts["original_hits"] += 1
                            print("ORIGINAL_K04_MATCH", coupon.hex().upper())
        expected = {
            (1178, 169): 0, (1178, 338): 2432,
            (1405, 111): 2432, (1405, 338): 0,
        }[(donor, offset)] if free_order else {
            (1178, 169): 0, (1178, 338): 192,
            (1405, 111): 192, (1405, 338): 0,
        }[(donor, offset)]
        assert counts["source_assignments"] == (98304 if free_order else 4096)
        assert counts["compatible"] == expected
        assert counts["synthetic_positive"] == (1 if expected else 0)
        assert not counts["original_hits"]
        if free_order:
            assert counts["complete_checks"] == (19456 if expected else 0)
            assert len(unique) == (2944 if expected else 0)
            totals.update(counts)
        print("ORDER_PERMUTED", int(free_order), "K02_STAGE", donor,
              "K05_STAGES", stages, "DIMENSION", expected_dimension,
              "SOURCE_COMPATIBLE", counts["compatible"],
              "COMPLETE_HASHES", counts["complete_checks"],
              "UNIQUE_COMPONENTS", len(unique), "ORIGINAL_HITS", counts["original_hits"],
              "PLANTED_CONTROL", counts["synthetic_positive"])
assert totals["complete_checks"] == 38912
assert totals["original_hits"] == 0
print("ORIGINAL K04 UNSOLVED; TWO SOURCE-COMPATIBLE 3-BIT MODELS EXHAUSTED")
