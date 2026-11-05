"""K04 producer: XORWOW with 32-bit additive pad constant per packet.

Attempt 1: 4 native words + d0; attempt2 missing: +d0+step;
attempt3 original: +d0+2*step, all modulo 2^32.
The original copied 18:02 ACK2 is excluded from source inference.
Run: python agents/agent3/k04_xorwow_packet_pad_sft.py
"""
from hashlib import sha256
from itertools import product
from k04_xorwow_gap_weyl_sft import (
    LAYOUTS, MASK32, component, decode, encode, original_inputs,
    parity, relations, xorwow_step,
)


def native(observed, start, increment):
    return [
        (value - start - increment * (2 if index >= 4 else 0)) & MASK32
        for index, value in enumerate(observed)
    ]


def invert(observed, checks):
    groups = [[] for _ in range(32)]
    for check in checks:
        high = max(index % 32 for index in range(256) if check >> index & 1)
        groups[high].append(check)
    possible = [(0, 0)]
    depth = -1
    for bit in range(32):
        mask = 1 << bit
        next_possible = []
        for start, step in possible:
            for a, b in product((0, mask), repeat=2):
                current_start, current_step = start | a, step | b
                words = native(observed, current_start, current_step)
                if all(parity(check, words) == 0 for check in groups[bit]):
                    next_possible.append((current_start, current_step))
        possible = next_possible
        depth = bit
        if not possible:
            break
    return possible, depth


def reconstruct(observed, projections, start, step):
    source_native = native(observed, start, step)
    return [
        (
            sum(parity(projections[32 * word + bit], source_native) << bit
                for bit in range(32))
            + start + step
        ) & MASK32
        for word in range(4)
    ]


def main():
    checks, projections = relations()
    original_left, original_right, mask, authentic_target = original_inputs()
    seed = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    original_start, original_step = 0x00ABCDEF, 0xA5A5BEEF
    state = seed
    sequence = []
    for t in range(12):
        state, value = xorwow_step(state)
        sequence.append(
            (value + original_start + original_step * (t // 4)) & MASK32
        )

    tested = 0
    positives = 0
    for layout in LAYOUTS:
        before = encode(sequence[:4], *layout)
        after = encode(sequence[8:], *layout)
        observed = decode(before, *layout) + decode(after, *layout)
        candidates, depth = invert(observed, checks)
        assert len(candidates) == 2 and (original_start, original_step) in candidates
        assert {start for start, _ in candidates} == {original_start}
        assert {step for _, step in candidates} == {
            original_step, original_step ^ 0x80000000,
        }

        true_coupon = encode(sequence[4:8], *layout)
        true_hash = sha256(component(true_coupon, mask)).digest()
        predicted = [
            encode(reconstruct(observed, projections, start, step), *layout)
            for start, step in candidates
        ]
        assert len(set(predicted)) == 2
        assert predicted.count(true_coupon) == 1
        assert sum(
            sha256(component(coupon, mask)).digest() == true_hash
            for coupon in predicted
        ) == 1
        positives += 1

        original = decode(original_left, *layout) + decode(original_right, *layout)
        roots, failed_bit = invert(original, checks)
        print("ORIGINAL_SOURCE", layout,
              "compatible_attemptwise_additive_issuers", len(roots),
              "failed_at_parameter_bit", failed_bit)
        assert not roots, (layout, roots)
        tested += 1

    assert tested == positives == 8
    print("PASS eight source-only exclusions and eight whole-coupon planted"
          " positives with two 32bit-step branch candidates."
          " Authentic K04 remains unresolved.")


if __name__ == "__main__":
    main()
