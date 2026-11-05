"""H17 K04, exact same-job XORWOW with unrestricted 32-bit Weyl increment.

Run from repo: python agents/agent3/k04_xorwow_any_weyl_sft.py
Imports its companion deterministic five-register GF2 SFT in same folder.
No original source or acceptance mutation. 8 x 2**64 parameters are
covered algebraically through exact bit-prefix branching, not brute force.
"""
import hashlib
from k04_xorwow_gap_weyl_sft import (
    LAYOUTS, MASK32, STAGES, component, decode, encode, original_inputs,
    parity, relations, xorwow_step,
)


def native(observed, d0, increment):
    return [
        (value - d0 - increment * stage) & MASK32
        for value, stage in zip(observed, STAGES)
    ]


def pair_lift(observed, equations):
    """The b-th bit of a modular linear term uses only low b+1 parameter bits."""
    by_high_bit = [[] for _ in range(32)]
    for eq in equations:
        highest = max(i % 32 for i in range(256) if (eq >> i) & 1)
        by_high_bit[highest].append(eq)
    assert [len(row) for row in by_high_bit] == [0, 0, 0, 0] + [3] * 26 + [6, 12]
    survivors = [(0, 0)]
    counts = []
    for bit in range(32):
        bitmask = 1 << bit
        next_survivors = []
        for d0, increment in survivors:
            for add_d, add_w in ((0, 0), (0, bitmask), (bitmask, 0), (bitmask, bitmask)):
                a, b = d0 | add_d, increment | add_w
                deweyled = native(observed, a, b)
                if all(parity(eq, deweyled) == 0 for eq in by_high_bit[bit]):
                    next_survivors.append((a, b))
        survivors = next_survivors
        counts.append(len(survivors))
        if not survivors:
            break
    return survivors, counts


def recover(observed, d0, increment, projections):
    values = native(observed, d0, increment)
    return [
        (
            sum(parity(projections[word * 32 + bit], values) << bit
                for bit in range(32))
            + d0 + increment * (word + 4)
        ) & MASK32
        for word in range(4)
    ]


def main():
    checks, projections = relations()
    original_first, original_last, mask, official_hash = original_inputs()
    seeded_state = (0x12345678, 0xABCDEF19, 0xDEADBEEF, 0xCAFEBABE, 0x875B29D4)
    planted_d0 = 0x00ABCDEF
    passed = 0
    for actual_step in (362437, 0xA5A5BEEF):
        state = seeded_state
        all_outputs = []
        for stage in range(12):
            state, value = xorwow_step(state)
            all_outputs.append(
                (value + planted_d0 + actual_step * stage) & MASK32
            )
        for layout in LAYOUTS:
            raw_before = encode(all_outputs[:4], *layout)
            raw_after = encode(all_outputs[8:], *layout)
            observed = decode(raw_before, *layout) + decode(raw_after, *layout)
            pairs, counts = pair_lift(observed, checks)
            assert pairs == [(planted_d0, actual_step)], (actual_step, layout, pairs, counts)
            missing = recover(observed, planted_d0, actual_step, projections)
            assert missing == all_outputs[4:8]
            generated = component(encode(missing, *layout), mask)
            reference = component(encode(all_outputs[4:8], *layout), mask)
            assert generated == reference
            assert hashlib.sha256(generated).digest() == hashlib.sha256(reference).digest()
            passed += 1
    assert passed == 16
    print("PASS", passed, "complete genuine XORWOW withheld-coupon controls, two step values and all eight layouts", flush=True)

    orig_candidates = 0
    for layout in LAYOUTS:
        observed = decode(original_first, *layout) + decode(original_last, *layout)
        compatible, sizes = pair_lift(observed, checks)
        print("ORIGINAL", layout, "UNRESTRICTED_WEYL_PAIRS", len(compatible), "LOWBIT_PREFIX_COUNT", sizes, flush=True)
        for initial, increment in compatible:
            physical = encode(recover(observed, initial, increment, projections), *layout)
            candidate = component(physical, mask)
            orig_candidates += 1
            if hashlib.sha256(candidate).digest() == official_hash:
                raise AssertionError(("ORIGINAL_K04_MATCH", layout, initial, increment, physical.hex().upper(), candidate.hex().upper()))
        assert not compatible, (layout, compatible)
    assert orig_candidates == 0
    print("ORIGINAL_EXCLUDED all 8 x 2**64 Weyl initial/increment combinations; zero source-compatible issuers; K04 missing")


if __name__ == "__main__":
    main()
