"""Source-first K04 bridge: earlier K01/K06 against later K02 MT stages.

Full original source selection and acceptance read-only. The disputed K04
copied ACK, K04 mask and K04 commitment are excluded from donor selection.
Uses Agent49's original source-pinned p951 symbolic printer model.
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import sys

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "resources"
sys.path.insert(0, str(REPO / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt

mt.LAST = 3000
printer, symbolic = mt.source(ROOT)
assert printer.rank == 15365

accepted = json.loads((ROOT / "acceptance.json").read_text())["slot_sha256"]
selected = {
    "K01": bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A"),
    "K06": bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A"),
}
for name, raw in selected.items():
    assert hashlib.sha256(raw).hexdigest() == accepted[name]

k02 = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
assert hashlib.sha256(k02).digest()[:16].hex().upper() == (
    "0D7E3AB56FB75DA3EB0E2E06786D239E"
)

def k02_formats():
    for endian in ("little", "big"):
        for backwards, swap_halves, native in product((False, True), repeat=3):
            chunks = [k02[i:i+4] for i in range(0, 16, 4)]
            if swap_halves:
                chunks = [part[2:] + part[:2] for part in chunks]
            if backwards:
                chunks.reverse()
            values = [int.from_bytes(part, endian) for part in chunks]
            yield [v if native else mt.untemper(v) for v in values]

def residual(base, expression):
    remainder = rhs = 0
    while expression:
        pivot = expression.bit_length() - 1
        if pivot in base.rows:
            vector, bit = base.rows[pivot]
            expression ^= vector
            rhs ^= bit
        else:
            remainder ^= 1 << pivot
            expression ^= 1 << pivot
    return remainder, rhs

def extend(base, assignments):
    result = mt.Basis()
    result.rows = base.rows.copy()
    result.rank = base.rank
    for stage, native in assignments:
        for i, expression in enumerate(mt.get(symbolic, stage)):
            result.insert(expression, (native >> i) & 1)
    return result

def state_from_basis(base):
    state = 0
    for pivot, (expression, bit) in sorted(base.rows.items()):
        if bit ^ ((expression & state).bit_count() & 1):
            state |= 1 << pivot
    return state

def parity_checks(base, stages):
    pivots = {}
    checks = []
    for lane, stage in enumerate(stages):
        for i, expression in enumerate(mt.get(symbolic, stage)):
            remainder, rhs = residual(base, expression)
            tag = 1 << (lane * 32 + i)
            while remainder:
                pivot = remainder.bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = (remainder, tag, rhs)
                    break
                vector, old_tag, old_rhs = pivots[pivot]
                remainder ^= vector
                tag ^= old_tag
                rhs ^= old_rhs
            if remainder == 0:
                checks.append((tag, rhs))
    assert len(checks) + len(pivots) == 128
    return checks

def rank(vectors):
    basis = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = vector
                break
            vector ^= basis[pivot]
    return len(basis)

def quartet_forms(raw):
    forms = []
    for i in range(0, 16, 4):
        choices = [int.from_bytes(raw[i:i+4], endian) for endian in ("little", "big")]
        forms.append(choices + [mt.untemper(value) for value in choices])
    for order in permutations(range(4)):
        for formats in product(range(4), repeat=4):
            yield sum(forms[order[i]][formats[i]] << (32 * i) for i in range(4))

presentations = {name: list(quartet_forms(raw)) for name, raw in selected.items()}
assert all(len(forms) == 6144 for forms in presentations.values())
target_expressions = [
    expression for stage in range(951, 955)
    for expression in mt.get(symbolic, stage)
]

for donor_stage in (1178, 1405):
    for early_start in (-240, -239, -238, -237):
        early_stages = list(range(early_start, early_start + 4))
        counts = Counter()
        for k02_words in k02_formats():
            base = extend(printer, zip(range(donor_stage, donor_stage+4), k02_words))
            assert base.rank == 15493
            checks = parity_checks(base, early_stages)

            # Actual full source-consistent printer state gives a planted
            # fourword donor. Every parity test must accept it.
            state = state_from_basis(base)
            planted_words = [
                sum(
                    ((expression & state).bit_count() & 1) << i
                    for i, expression in enumerate(mt.get(symbolic, stage))
                )
                for stage in early_stages
            ]
            planted_packed = sum(value << (32*i) for i, value in enumerate(planted_words))
            assert all(((planted_packed & tag).bit_count() & 1) == rhs for tag, rhs in checks)

            if counts["source_modes"] == 0:
                before = rank(residual(base, x)[0] for x in target_expressions)
                joint = extend(base, zip(early_stages, planted_words))
                after = rank(residual(joint, x)[0] for x in target_expressions)
                assert before == 33
                counts["conditional_K04_residual_bits"] = after
            counts["source_modes"] += 1
            counts["parity_checks"] = len(checks)
            for name, values in presentations.items():
                for packed in values:
                    counts[name + "_assignments"] += 1
                    if all(((packed & tag).bit_count() & 1) == rhs for tag, rhs in checks):
                        counts[name + "_source_compatible"] += 1

        assert counts["source_modes"] == 16
        assert counts["K01_assignments"] == counts["K06_assignments"] == 98304
        assert not counts["K01_source_compatible"]
        assert not counts["K06_source_compatible"]
        print("K02_STAGE", donor_stage, "EARLY_STAGE", early_start,
              "SOURCE_TEST", dict(counts), flush=True)
print("ORIGINAL K01 AND K06 EARLY DONORS INCOMPATIBLE; PLANTED CONTROLS PASS")
