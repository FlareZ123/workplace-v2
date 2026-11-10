"""H-17 original-source gate for every affine GF(2)^32 stride-four initializer.

Hypothesis: S[i+4] = A*S[i] xor c for unknown binary 32x32 matrix A
and unknown 32-bit constant c. Uses *only* the source-derived 624-word
native MT register, with the selected 18:02 ACK2 payload withheld.

Original 32 fully observed input/output pairs fix A conditional on c.
The 52 additional partially observed pairs test every possible c
without enumerating the 2^32 constants or querying the K04 commitment.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
import k04_p951_symbolic_basis as mt

source, native = mt.source(ROOT)
assert source.rank == 15365 and mt.STARTS[129] == 951
WORD_MASK = (1 << 32) - 1

masks = []
values = []
for i in range(624):
    bits = [source.predict(1 << (32*i + j)) for j in range(32)]
    masks.append(sum(1 << j for j, v in enumerate(bits) if v is not None))
    values.append(sum((v or 0) << j for j, v in enumerate(bits)))

assert sum(m == WORD_MASK for m in masks) == 166


def test_affine_stride4(register, visibility):
    complete = {i: register[i] for i in range(624) if visibility[i] == WORD_MASK}
    training = [i for i in range(620) if i in complete and i+4 in complete]
    assert len(training) == 32

    # Rows store a reduced input vector, its reduced output and the parity
    # of original full-pair basis coefficients used in that linear form.
    rows = {}
    for i in training:
        x, y, parity = complete[i], complete[i+4], 1
        while x:
            pivot = x.bit_length()-1
            if pivot not in rows:
                rows[pivot] = (x, y, parity)
                break
            u, v, pv = rows[pivot]
            x ^= u
            y ^= v
            parity ^= pv
        else:
            assert y == 0, ("inconsistent complete-pair training", i)
    assert len(rows) == 32, "full-pair source inputs fail to span 32 dimensions"

    def project(x):
        y, coefficient_parity = 0, 0
        while x:
            pivot = x.bit_length()-1
            u, v, pv = rows[pivot]
            x ^= u
            y ^= v
            coefficient_parity ^= pv
        return y, coefficient_parity

    conditional_constants = {}
    exact_failures = []
    checked = 0
    partly_visible = 0
    part_bits = 0
    for i in sorted(complete):
        if i + 4 >= 624 or not visibility[i+4]:
            continue
        checked += 1
        outmask = visibility[i+4]
        if outmask != WORD_MASK:
            partly_visible += 1
            part_bits += outmask.bit_count()
        y, coeff_parity = project(complete[i])
        observed = register[i+4] & outmask
        discrepancy = (y ^ observed) & outmask
        if coeff_parity == 1:
            # Under the affine model the constant c cancels exactly.
            if discrepancy:
                exact_failures.append((i, discrepancy.bit_count()))
        else:
            # Every visible bit is an exact equation on the same c bit.
            for bit in range(32):
                if (outmask >> bit) & 1:
                    conditional_constants.setdefault(bit, set()).add(
                        (discrepancy >> bit) & 1)
    contradicted_bits = [
        bit for bit, bits in conditional_constants.items() if len(bits) > 1
    ]
    return {
        "full_words": len(complete),
        "training_pairs": len(training),
        "projected_checks": checked,
        "additional_partially_visible_pairs": partly_visible,
        "additional_visible_bits": part_bits,
        "constant_bit_equations": len(conditional_constants),
        "unconditional_failures": len(exact_failures),
        "contradictory_constant_bits": len(contradicted_bits),
        "first_unconditional_witness": exact_failures[0][0] if exact_failures else None,
    }


original = test_affine_stride4(values, masks)
print("ORIGINAL", original)
assert original == {
    "full_words": 166,
    "training_pairs": 32,
    "projected_checks": 84,
    "additional_partially_visible_pairs": 52,
    "additional_visible_bits": 353,
    "constant_bit_equations": 32,
    "unconditional_failures": 21,
    "contradictory_constant_bits": 27,
    "first_unconditional_witness": 101,
}

# Genuine independent known-producer positives: the *same* original
# visibility pattern is imposed on two actual affine binary-step states.
# All 624 synthetic native words are created before source projection.
def xorshift32(x):
    x ^= (x << 13) & WORD_MASK
    x ^= x >> 17
    x ^= (x << 5) & WORD_MASK
    return x & WORD_MASK

for c in (0, 0xD6C6C5C0):
    synthetic = [0x12345678, 0x91ABCDEF, 0xBADA55AA, 0xE17EABCD]
    for i in range(4, 624):
        synthetic.append(xorshift32(synthetic[i-4]) ^ c)
    positive = test_affine_stride4(synthetic, masks)
    print("SYNTHETIC_CONSTANT", hex(c), positive)
    assert positive["training_pairs"] == 32
    assert positive["projected_checks"] == 84
    assert positive["unconditional_failures"] == 0
    assert positive["contradictory_constant_bits"] == 0
    assert positive["constant_bit_equations"] == 32
print("ORIGINAL_STRIDE4_AFFINE_FAMILY_EXCLUDED; SELECTED_COUPON_WITHHELD")
