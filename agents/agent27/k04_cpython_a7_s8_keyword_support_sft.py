"""Exact CPython k2496 A7/S7/S8 source-only key-word sieve.

The original printer issuer is hypothetical, and selected ACK2 row129 is
excluded from the 132-packet source projection. This script does not read
the K04 route mask, acceptance hash, or disputed selected payload.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_k2496_shortforward_source_sft import original_source
from k04_cpython_initarray_wrap_sft import direct_initialized, F1, F2, t, U

G = [19650218]
for i in range(1, 9):
    G.append((1812433253 * t(G[-1]) + i) & U)


def allowed_high_words(a7: int, s7: int, mask: int, value: int,
                       key_index: int) -> tuple[list[int], int]:
    """Exact inversion without enumerating all 2**32 key words.

    S8 = (((G8 xor F1*t(A7)) + key[j] + j) xor F2*t(S7)) - 8,
    all unsigned modulo 2**32. Split 16+16 and propagate carry/borrow.
    """
    C = ((G[8] ^ (F1 * t(a7) & U)) + key_index) & U
    D = F2 * t(s7) & U
    c0, c1 = C & 65535, C >> 16
    d0, d1 = D & 65535, D >> 16
    m0, m1 = mask & 65535, mask >> 16
    v0, v1 = value & 65535, value >> 16
    groups: dict[tuple[int, int], int] = {}
    for low in range(65536):
        raw = c0 + low
        carry = raw >> 16
        mixed = (raw & 65535) ^ d0
        borrow = int(mixed < 8)
        if ((mixed - 8) & 65535) & m0 == v0:
            pair = carry, borrow
            groups[pair] = groups.get(pair, 0) + 1
    counts = [0] * 65536
    for high in range(65536):
        for (carry, borrow), nlow in groups.items():
            upper = (((c1 + high + carry) & 65535) ^ d1) - borrow
            if (upper & m1) == v1:
                counts[high] += nlow
    return counts, sum(counts)



def s5_from_key_word(key: int, s6: int, s7: int, key_index: int) -> int:
    """Reverse genuine first- and second-pass CPython steps at i7 and i6.

    With S6/S7 known, A7 is known. For any candidate key[6 mod n],
    derive A6 and S5 exactly; the original S5 six-bit source mask is
    an independent necessary condition on this word, regardless of
    all other seed words and the first-pass index-1 wrap.
    """
    a7 = ((s7 + 7) & U) ^ (F2 * t(s6) & U)
    inv_f1 = pow(F1, -1, 1 << 32)
    inv_f2 = pow(F2, -1, 1 << 32)
    a6 = t((inv_f1 * (((a7 - key - key_index) & U) ^ G[7])) & U)
    return t((inv_f2 * (a6 ^ ((s6 + 6) & U))) & U)


def control():
    for words in ([0x1234, 0x5678], [0xABCD, 0xFEDC],
                  [0, 1], [0x11111111, 0x22222222, 0x33333333, 0x44444444]):
        a, _, state = direct_initialized(words)
        seed = sum(k << (32 * j) for j, k in enumerate(words))
        assert state == list(random.Random(seed).getstate()[1][:624])
        a7 = ((state[7] + 7) & U) ^ (F2 * t(state[6]) & U)
        assert a7 == a[7]
        assert s5_from_key_word(words[6 % len(words)], state[6], state[7],
                                6 % len(words)) == state[5]
        mask = 0x09CC1C00
        j = 7 % len(words)
        counts, total = allowed_high_words(a7, state[7],
                                           mask, state[8] & mask, j)
        assert counts[words[j] >> 16] > 0
        assert total == (1 << (32 - mask.bit_count()))
        reconstructed = (((G[8] ^ (F1 * t(a7) & U)) + words[j] + j) & U)
        reconstructed = ((reconstructed ^ (F2 * t(state[7]) & U)) - 8) & U
        assert reconstructed == state[8]
    print("GENUINE_CPYTHON_COMPLETE_STATE_AND_S8_CONTROLS=4/4 PASS")


def main():
    control()
    source = original_source()
    s6, s7 = source[6][1], source[7][1]
    a7 = ((s7 + 7) & U) ^ (F2 * t(s6) & U)
    assert a7 == 0x2AED5290
    mask5, value5 = source[5]
    assert (mask5, value5) == (0x8000001F, 0x00000011)
    # T(x) is involutory and both odd multiplication constants invert mod 2^32.
    # Therefore the S5 six-bit mask selects exactly 2^26 key[6 mod n] words.
    s5_small_j0 = sum((s5_from_key_word(k, s6, s7, 0) & mask5) == value5
                      for k in range(65536))
    assert s5_small_j0 == 1070
    print(f"S5_BACKINVERSE_KEYWORD_COUNT={1 << (32 - mask5.bit_count())}"
          f" S5_SMALL16_KEYWORDS_J0={s5_small_j0}"
          f" N2_CARTESIAN_PAIR_AFTER_S5_S8={1 << 49}")
    mask, value = source[8]
    assert mask == 0x09CC1C00 and value == 0x008C1000
    for j in range(8):
        counts, total = allowed_high_words(a7, s7, mask, value, j)
        supported = [h for h, n in enumerate(counts) if n]
        ascii_pairs = sum(counts[(b << 8) | a] > 0
                          for a in range(0x20, 0x7F)
                          for b in range(0x20, 0x7F))
        assert total == 8_388_608
        assert len(supported) == 1280
        assert counts[0] == 0
        assert ascii_pairs == 0
        possible_byte2 = sorted({h & 255 for h in supported})
        assert possible_byte2 == ([*range(0x0B, 0x10), *range(0x1B, 0x20),
                                  *range(0xEB, 0xF0), *range(0xFB, 0x100)])
        C = ((G[8] ^ (F1 * t(a7) & U)) + j) & U
        D = F2 * t(s7) & U
        upper = min(supported)
        minimum = next(((upper << 16) | lower) for lower in range(65536)
                       if (((((C + ((upper << 16) | lower)) & U) ^ D) - 8)
                           & U & mask) == value)
        assert minimum == 0x02EB23A2 - j
        print(f"KEY_INDEX={j} K1_TOTAL={total} HIGH16_SUPPORTED={len(supported)}"
              f" MIN_KEY_WORD={minimum:08X} BYTE2_VALUES={len(possible_byte2)}"
              f" MIN_WORD_LEFT32={(minimum << 32)}")
        print(f"KEY_INDEX={j} K1_TOTAL={total} HIGH16_SUPPORTED={len(supported)}"
              f" MIN_HIGH16={min(supported):04X} MAX_HIGH16={max(supported):04X}"
              f" ZERO_HIGH16_ALLOWED={counts[0]} ASCII_PAIR_SUPPORTED={ascii_pairs}")
    print("SOURCE_S8_EXCLUDES_SHORT_WORD_AND_PRINTABLE_WORD_AT_INDEX_7_MOD_N")
    print("Conditional CPython/k2496 producer only; no K04 or K08 accepted")


if __name__ == "__main__":
    main()
