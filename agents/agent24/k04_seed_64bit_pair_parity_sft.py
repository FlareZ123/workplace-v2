"""Conditional H-17 K04 binary-seed producer: invertible 64-bit source pair.
The p951 CPython Random(bytes) seed fingerprint is a HYPOTHESIS, not history.
Entire selected ACK2, verifier, commitments and route mask are withheld.
Reads original printer evidence without modifying any archival artifact.
"""
import hashlib
import os
from pathlib import Path

MASK = (1 << 64) - 1
MOD = 1 << 64
GAMMA = 0x9E3779B97F4A7C15
MIX_A = 0xBF58476D1CE4E5B9
MIX_B = 0x94D049BB133111EB
XOR_MULT = 2685821657736338717
LCG_A = 6364136223846793005
LCG_C = 1442695040888963407
INVERSE_XOR_MULT = pow(XOR_MULT, -1, MOD)
INVERSE_LCG_A = pow(LCG_A, -1, MOD)
ORIGINAL_SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
# Conditional source-fitted B words, from Agent 15's November 4
# p951 CPython SHA512-binary-seed fingerprint, not an original witness.
SOURCE_WORD_DOMAINS = {
    0: (0x64589C88, 0xE4589C88),
    1: (0x49342EC0,),
    12: (0x6425CF5B, 0xE425CF5B),
    579: (0x06EDCDAD,),
    580: (0xFD6A4CF7,),
}
ENGINES = ("splitmix64", "xorshift64star", "lcg64-native-full-state")


def undo_right(value: int, shift: int) -> int:
    original = value
    for _ in range(7):
        original = value ^ (original >> shift)
    return original & MASK


def undo_left(value: int, shift: int) -> int:
    original = value
    for _ in range(7):
        original = value ^ ((original << shift) & MASK)
    return original & MASK


def splitmix_mix(value: int) -> int:
    value = ((value ^ (value >> 30)) * MIX_A) & MASK
    value = ((value ^ (value >> 27)) * MIX_B) & MASK
    return (value ^ (value >> 31)) & MASK


def splitmix_unmix(value: int) -> int:
    value = undo_right(value, 31)
    value = value * pow(MIX_B, -1, MOD) & MASK
    value = undo_right(value, 27)
    value = value * pow(MIX_A, -1, MOD) & MASK
    return undo_right(value, 30)


def xorshift_next(state: int) -> int:
    state ^= state >> 12
    state ^= (state << 25) & MASK
    state ^= state >> 27
    return state & MASK


def xorshift_previous(state: int) -> int:
    state = undo_right(state, 27)
    state = undo_left(state, 25)
    return undo_right(state, 12)


def nth_output(engine: str, output0: int, steps: int) -> int:
    if engine == "splitmix64":
        state = splitmix_unmix(output0)
        return splitmix_mix((state + steps * GAMMA) & MASK)
    if engine == "xorshift64star":
        state = output0 * INVERSE_XOR_MULT & MASK
        move = xorshift_next if steps >= 0 else xorshift_previous
        for _ in range(abs(steps)):
            state = move(state)
        return state * XOR_MULT & MASK
    if engine == "lcg64-native-full-state":
        a = LCG_A if steps >= 0 else INVERSE_LCG_A
        b = LCG_C if steps >= 0 else (-INVERSE_LCG_A * LCG_C) & MASK
        state = output0
        exponent = abs(steps)
        while exponent:
            if exponent & 1:
                state = (a * state + b) & MASK
            b = b * (a + 1) & MASK
            a = a * a & MASK
            exponent >>= 1
        return state
    raise ValueError(engine)


def split_words(value: int, byte_order: str, swapped: bool) -> tuple[int, int]:
    b = value.to_bytes(8, byte_order)
    words = (int.from_bytes(b[:4], "big"), int.from_bytes(b[4:], "big"))
    return words[::-1] if swapped else words


def join_words(words: tuple[int, int], byte_order: str, swapped: bool) -> int:
    parts = words[::-1] if swapped else words
    return int.from_bytes(b"".join(v.to_bytes(4, "big") for v in parts), byte_order)


def word_at(engine: str, value0: int, anchor: int, idx: int, order: str, swapped: bool) -> int:
    step, half = divmod(idx - anchor, 2)
    return split_words(nth_output(engine, value0, step), order, swapped)[half]


def controls() -> None:
    seeds = (0, 1, 0x9CB82B118DAA2783, MASK)
    for engine in ENGINES:
        for value in seeds:
            for distance in (-290, -284, -1, 0, 1, 6, 289, 290):
                new = nth_output(engine, value, distance)
                assert nth_output(engine, new, -distance) == value
            for anchor in (0, 579):
                for order in ("big", "little"):
                    for swapped in (False, True):
                        observed = {i: word_at(engine, value, anchor, i, order, swapped)
                                    for i in SOURCE_WORD_DOMAINS}
                        recovered = join_words((observed[anchor], observed[anchor + 1]), order, swapped)
                        assert recovered == value
                        assert all(word_at(engine, recovered, anchor, i, order, swapped) == w
                                   for i, w in observed.items())
    print("SYNTHETIC POSITIVES PASS: bidirectional inverse; both phases; all layouts; 3 families")


def run() -> None:
    resource = Path(os.environ.get("H17_RESOURCE_ROOT", "resources/evidence"))
    spool = resource / "print" / "spool-reconstruction.log"
    assert hashlib.sha256(spool.read_bytes()).hexdigest() == ORIGINAL_SPOOL_SHA256
    controls()
    print("ORIGINAL SOURCE SHA256 PASS; selected packet and hash never read")
    print("Indexed seed words: relative positions 0, 1, 12, 579, 580")
    for engine in ENGINES:
        total = 0
        full = 0
        word12 = 0
        best_independent = 0
        for anchor in (0, 579):
            word0_options = SOURCE_WORD_DOMAINS[0] if anchor == 0 else (None,)
            for order in ("big", "little"):
                for swapped in (False, True):
                    for first in word0_options:
                        pair = (first, SOURCE_WORD_DOMAINS[1][0]) if anchor == 0 else (
                            SOURCE_WORD_DOMAINS[579][0], SOURCE_WORD_DOMAINS[580][0])
                        value = join_words(pair, order, swapped)
                        preds = {idx: word_at(engine, value, anchor, idx, order, swapped)
                                 for idx in SOURCE_WORD_DOMAINS}
                        holds = [preds[idx] in domains for idx, domains in SOURCE_WORD_DOMAINS.items()]
                        unseen = holds[2:] if anchor == 0 else holds[:3]
                        count = sum(unseen)
                        total += 1
                        word12 += int(holds[2])
                        best_independent = max(best_independent, count)
                        full += int(all(holds))
                        print(f"{engine} phase={anchor} order={order} swap={int(swapped)} "
                              f"first={first} blind={count}/3 "
                              f"predicted={[f'{preds[i]:08X}' for i in SOURCE_WORD_DOMAINS]}")
        print(f"SUMMARY {engine}: candidates={total} complete_source={full} "
              f"word12_matches={word12} best_blind_holdout={best_independent}/3")
        assert total == 12 and full == 0 and word12 == 0 and best_independent == 0


if __name__ == "__main__":
    run()
