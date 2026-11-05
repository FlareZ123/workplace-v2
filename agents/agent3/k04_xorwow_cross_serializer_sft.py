"""H17 K04: independent copy-byte layouts for each intact REQUESTED source.

Read-only original selected 18:02 printer ACK withheld. Gap g=0 and g=2.
Run: python agents/agent3/k04_xorwow_cross_serializer_sft.py
Imports its existing source-pinned canonical XORWOW and GF2 exact solver SFT.
"""
from itertools import product
from hashlib import sha256
from k04_xorwow_gap_weyl_sft import (
    LAYOUTS, MASK32, component, decode, encode, original_inputs, xorwow_step,
)
from k04_xorwow_four_extra_gap_sft import derive, lift, recover, symbolic_rows


def main():
    left, right, mask, target = original_inputs()
    rows = symbolic_rows()
    initial = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    d0, increment = 0x00ABCDEF, 0xA5A5BEEF
    tested = 0
    control = 0

    for gap in (0, 2):
        stages, checks, projections = derive(rows, gap)
        state = initial
        sequence = []
        for stage in range(12 + gap):
            state, value = xorwow_step(state)
            sequence.append((value + d0 + increment * stage) & MASK32)

        for first_layout, last_layout in product(LAYOUTS, repeat=2):
            before = encode(sequence[:4], *first_layout)
            after = encode(sequence[8+gap:12+gap], *last_layout)
            planted = decode(before, *first_layout) + decode(after, *last_layout)
            roots, _ = lift(planted, stages, checks)
            assert roots == [(d0, increment)], (gap, first_layout, last_layout, roots)
            truth = encode(sequence[4:8], *first_layout)
            reconstructed = encode(
                recover(planted, stages, projections, d0, increment),
                *first_layout,
            )
            assert reconstructed == truth
            commitment = sha256(component(truth, mask)).digest()
            assert sha256(component(reconstructed, mask)).digest() == commitment
            control += 1

            observed = decode(left, *first_layout) + decode(right, *last_layout)
            candidates, _ = lift(observed, stages, checks)
            assert not candidates, (gap, first_layout, last_layout, candidates)
            tested += 1
        print("K04_XORWOW", "gap", gap,
              "independent_serializers=64", "source_compatible=0",
              "planted_complete_coupons=64")

    assert tested == 128 and control == 128
    print("PASS: 128 source-only exact full-parameter exclusions and "
          "128 genuine synthetic complete-coupon recoveries. "
          "Original K04 remains missing.")


if __name__ == "__main__":
    main()
