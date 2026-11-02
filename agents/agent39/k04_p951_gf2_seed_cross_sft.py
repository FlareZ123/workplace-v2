"""Exact GF(2) printer register constraints intersect CPython first-cycle seed terms.

Source original: 132 intact printer packets; row129 explicitly withheld.
No selected copied ACK, REC8 commitments, masks, keys or verifier are read.
Run: python agents/agent39/k04_p951_gf2_seed_cross_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "agent39_middle", ROOT / "agents/agent39/k04_p951_middle_inverse_sft.py"
)
middle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(middle)
prior = middle.prior
U = 0xffffffff
MAGIC = 0x9908b0df
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def symbolic_states():
    """Origin S[0..623] is the *initialized* CPython register.

    Crucially do not continue the recurrence backward to a fictitious MT
    prehistory. CPython initialization forces S[0]=0x80000000; an
    arbitrary initialized register is not necessarily reachable from a
    previous 624-word MT state. First tempered draw is native index 624.
    """
    out = [[1 << (32 * i + bit) for bit in range(32)] for i in range(624)]
    for i in range(624, 1601):
        p, n, q = out[i - 624], out[i - 623], out[i - 227]
        out.append([
            q[bit]
            ^ (p[31] if bit == 30 else n[bit + 1] if bit < 30 else 0)
            ^ (n[0] if (MAGIC >> bit) & 1 else 0)
            for bit in range(32)
        ])
    return out


def reduce(equation, basis):
    while equation:
        pivot = equation.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            break
        equation ^= row
    return equation


def source_basis(payloads, expressions):
    basis = {}
    for row, start in enumerate(prior.STARTS):
        if row == 129:
            continue
        assert len(payloads[row]) == 16
        for lane in range(4):
            word = prior.untemper(int.from_bytes(
                payloads[row][4*lane:4*lane+4], "little"
            ))
            for bit, expr in enumerate(expressions[624 + start + lane]):
                remainder = reduce((expr << 1) | ((word >> bit) & 1), basis)
                assert remainder != 1, "intact-source contradiction"
                if remainder > 1:
                    basis[remainder.bit_length() - 1] = remainder
    return basis


def add_fixed_words(basis, expressions, vals, masks):
    updated = basis.copy()
    independent = 0
    for i in range(624):
        for bit, expr in enumerate(expressions[i]):
            if (masks[i] >> bit) & 1:
                remainder = reduce(
                    (expr << 1) | ((vals[i] >> bit) & 1), updated
                )
                if remainder == 1:
                    return None, independent
                if remainder > 1:
                    updated[remainder.bit_length() - 1] = remainder
                    independent += 1
    return updated, independent


def individually_fixed(basis, expressions):
    values, masks = [], []
    for i in range(624):
        word = mask = 0
        for bit, expr in enumerate(expressions[i]):
            residue = reduce(expr << 1, basis)
            if residue <= 1:
                mask |= 1 << bit
                word |= residue << bit
        values.append(word)
        masks.append(mask)
    return values, masks


def residue_domains(n, vals, masks):
    result = {}
    for j, choices in prior.source_terms(vals, masks).items():
        residue = j % n
        result[residue] = (
            result[residue] & choices if residue in result else set(choices)
        )
        if not result[residue]:
            return None
    return result


def central_inverse_fixes(n, vals, masks):
    residues = residue_domains(n, vals, masks)
    if residues is None:
        return None
    fixes = []
    for i in range(4, 624):
        keys = residues.get((i - 1) % n)
        if not keys or masks[i - 1] == U:
            continue
        first = prior.near_complete_domain(vals[i - 2], masks[i - 2])
        third = prior.near_complete_domain(vals[i], masks[i])
        if not first or not third:
            continue
        options = {
            w for key in keys for a in first for c in third
            for w in middle.inverse_middle(i, a, c, key)
            if not ((w ^ vals[i - 1]) & masks[i - 1])
        }
        if not options:
            return None
        pivot = next(iter(options))
        invariant = U
        for w in options:
            invariant &= ~(pivot ^ w) & U
        additional = invariant & ~masks[i - 1]
        if additional:
            fixes.append((i - 1, pivot, additional))
    return fixes


def target_quotient(basis, expressions):
    linear = {p-1:row>>1 for p, row in basis.items()}
    gain = fixed = 0
    for lane in range(4):
        for term in expressions[624 + 951 + lane]:
            if reduce(term << 1, basis) <= 1:
                fixed += 1
            while term:
                pivot = term.bit_length() - 1
                known = linear.get(pivot)
                if known is None:
                    linear[pivot] = term
                    gain += 1
                    break
                term ^= known
    return gain, fixed


def run_length(n, seed_basis, expressions):
    basis = seed_basis
    for _ in range(8):
        vals, masks = individually_fixed(basis, expressions)
        good, inferred, inferred_masks, reason = prior.infer_near(n, vals, masks)
        if not good:
            return None
        fixes = central_inverse_fixes(n, inferred, inferred_masks)
        if fixes is None:
            return None
        for index, word, newmask in fixes:
            assert not ((inferred[index] ^ word) & inferred_masks[index] & newmask)
            inferred[index] = (inferred[index] & ~newmask) | (word & newmask)
            inferred_masks[index] |= newmask
        refined, gain = add_fixed_words(
            basis, expressions, inferred, inferred_masks
        )
        if refined is None:
            return None
        if gain == 0:
            return basis
        basis = refined
    raise AssertionError("GF2/seed inference failed to converge")


def seed_base(payloads, expressions):
    basis = source_basis(payloads, expressions)
    assert len(basis) == 15365
    # CPython init_by_array overwrites register 0 with this exact word.
    canonical = [0x80000000] + [0] * 623
    masks = [U] + [0] * 623
    basis, gained = add_fixed_words(basis, expressions, canonical, masks)
    assert basis is not None and gained == 32
    return basis


def synthetic_controls(expressions):
    trials = 0
    for n in (1, 32, 249, 364, 588, 606, 611, 618, 623):
        for variant in range(2):
            seed = sum(
                ((0x5910acd3 + variant*0xb143 + j*0x7d3) & U) << (32*j)
                for j in range(n)
            )
            rng = random.Random(seed)
            register = rng.getstate()[1][:624]
            assert register[0] == 0x80000000
            draws = [rng.getrandbits(32) for _ in range(967)]
            payloads = [
                b"".join(draws[start + lane].to_bytes(4, "little")
                         for lane in range(4))
                for start in prior.STARTS
            ]
            payloads[129] = b""
            source = seed_base(payloads, expressions)
            vals, masks = individually_fixed(source, expressions)
            assert all(not ((a ^ b) & mask)
                       for a, b, mask in zip(vals, register, masks))
            inferred = run_length(n, source, expressions)
            assert inferred is not None, (n, variant)
            values, masks = individually_fixed(inferred, expressions)
            assert all(not ((a ^ b) & mask)
                       for a, b, mask in zip(values, register, masks))
            for lane in range(4):
                true_native = prior.untemper(draws[951+lane])
                for bit, term in enumerate(expressions[624+951+lane]):
                    rem = reduce(term << 1, inferred)
                    assert rem > 1 or rem == ((true_native >> bit) & 1)
            trials += 1
    assert trials == 18
    print("Synthetic CPython seed-first-cycle positive controls: 18/18 PASS")


def main():
    expressions = symbolic_states()
    synthetic_controls(expressions)
    source = ROOT / "resources/evidence/print/spool-reconstruction.log"
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(prior.STARTS) == 133
    assert prior.STARTS[129] == 951
    payloads = [
        b"" if i == 129 else bytes.fromhex(field.decode())
        for i, field in enumerate(fields)
    ]
    original = seed_base(payloads, expressions)
    values, masks = individually_fixed(original, expressions)
    assert sum(m.bit_count() for m in masks) == 9770
    assert len(prior.source_terms(values, masks)) == 94
    baseline = [
        n for n in range(1, 624)
        if residue_domains(n, values, masks) is not None
    ]
    assert len(baseline) == 42
    near = []
    complete = []
    for n in baseline:
        ok, vals, known, _ = prior.infer_near(n, values, masks)
        if not ok:
            continue
        basis, _ = add_fixed_words(original, expressions, vals, known)
        if basis is None:
            continue
        near.append(n)
        candidate = run_length(n, original, expressions)
        if candidate is not None:
            complete.append(n)
            assert target_quotient(candidate, expressions) == (128, 0)
    assert near == [588,606,607,608,609,610,611,613,614,615,616,
                    618,619,620,621,622,623], near
    assert complete == [606,607,608,609,610,611,613,614,615,616,
                        618,619,620,621,622,623], complete
    print("Original p951 conditional 144 -> 42 -> 17 -> 16 lengths")
    print("Survivors:", complete)
    print("Original selected native bits fixed: 0 / 128; quotient 128")
    print("No K04/K08 accepted candidate, selected payload or verifier used")


if __name__ == "__main__":
    main()
