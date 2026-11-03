"""Constructive CPython n613 non-identifiability from authentic H-17 printer packets.

Produces four genuinely seeded random.Random(integer) histories of EXACTLY
613 seed words; each regenerates all 132 intact original printer ACK payloads
under the conditional p951 first-cycle interpretation, while the 16-byte
selected coupon is different in every history. Row129 is explicitly withheld
from fitting; no K04 route mask, commitments or verifier accessed.

Depends on Agent14 n609/610 inverse and Agent39 source model.
Usage: python agents/agent14/k04_p951_cpython_n613_constructive_sft.py
"""
from __future__ import annotations

import hashlib
import random
import re

import k04_p951_cpython_n609_610_wrap_sft as wrap

gf = wrap.gf
prior = wrap.prior
U = prior.U
A, B = prior.A, prior.B
INV_A, INV_B = prior.INV_A, prior.INV_B
BASE = prior.BASE

# (case, complete S7, complete S623, complete S1, complete S612).
# These two branches came from the exact exhaustive 8 x 2**30 cyclic
# closure against original source-fixed S612[0..30], never the K04 hash.
BRANCHES = (
    (1, 0xB575B1D8, 0x84710790, 0x6A1F8B63, 0xC2C42558),
    (5, 0xD15772A6, 0x84710790, 0x4FE06869, 0x42C42558),
)
EXPECTED_COUPONS = (
    "8BF049C7F934A6FE4D212C82A939BF3D",
    "5FDF9C14F8A08A465E7ABA650E7F18E4",
    "58609BBF64B48FC8E1299170750F34FD",
    "2832E96FF4065B0348A80E2D0499B381",
)


def make_late_words(state: list[int], late: dict[int, int], s1: int) -> dict[int, int]:
    s = state.copy()
    s[1] = s1
    a = lambda i: prior.state_a(s, i)
    a623 = a(623)
    a1end = ((s1 + 1) & U) ^ prior.mix(s[623], B)
    a2 = ((s[2] + 2) & U) ^ prior.mix(a1end, B)
    key10 = (a(11) - (BASE[11] ^ prior.mix(a(10), A)) - 10) & U
    a1first = ((a1end - key10 - 10) & U) ^ prior.mix(a623, A)
    key0 = (a1first - (BASE[1] ^ prior.mix(BASE[0], A))) & U
    key1 = (a2 - (BASE[2] ^ prior.mix(a1first, A)) - 1) & U
    key2 = (a(3) - (BASE[3] ^ prior.mix(a2, A)) - 2) & U
    a616 = ((late[616] + 616) & U) ^ prior.mix(late[615], B)
    a615 = prior.unmix(BASE[616] ^ ((a616 - key2 - 2) & U), INV_A)
    s614 = prior.unmix(a615 ^ ((late[615] + 615) & U), INV_B)
    a614 = prior.unmix(BASE[615] ^ ((a615 - key1 - 1) & U), INV_A)
    s613 = prior.unmix(a614 ^ ((s614 + 614) & U), INV_B)
    a613 = prior.unmix(BASE[614] ^ ((a614 - key0) & U), INV_A)
    s612 = prior.unmix(a613 ^ ((s613 + 613) & U), INV_B)
    return {1: s1, 7: s[7], 612: s612, 613: s613, 614: s614, **late}


def add_source_constraints(basis: dict, expressions: list, known: dict) -> dict:
    result = basis.copy()
    for i, word in sorted(known.items()):
        for bit, expr in enumerate(expressions[i]):
            residue = gf.reduce((expr << 1) | ((word >> bit) & 1), result)
            assert residue != 1, ("original-source contradiction", i, bit)
            if residue > 1:
                result[residue.bit_length() - 1] = residue
    return result


def solve_full_register(basis: dict, choice: int) -> list[int]:
    rng = random.Random(choice)
    assignment = 0
    for pivot in range(1, 624 * 32 + 1):
        if pivot in basis:
            equation = basis[pivot]
            bit = ((equation & assignment).bit_count() & 1) ^ (equation & 1)
        else:
            bit = rng.getrandbits(1)
        if bit:
            assignment |= 1 << pivot
    assert all(
        ((row & assignment).bit_count() & 1) == (row & 1)
        for row in basis.values()
    )
    words = [(assignment >> (1 + i * 32)) & U for i in range(624)]
    assert words[0] == 0x80000000
    return words


def reverse_seed(initialized: list[int]) -> int:
    """Invert BOTH original CPython init_by_array passes, including S1 wrap."""
    s = initialized
    state_a = [0] * 624
    state_a[1] = ((s[1] + 1) & U) ^ prior.mix(s[623], B)
    state_a[2] = ((s[2] + 2) & U) ^ prior.mix(state_a[1], B)
    for i in range(3, 624):
        state_a[i] = ((s[i] + i) & U) ^ prior.mix(s[i - 1], B)

    key10 = (
        state_a[11] - (BASE[11] ^ prior.mix(state_a[10], A)) - 10
    ) & U
    first1 = ((state_a[1] - key10 - 10) & U) ^ prior.mix(state_a[623], A)
    keys = [0] * 613
    keys[0] = (first1 - (BASE[1] ^ prior.mix(BASE[0], A))) & U
    keys[1] = (
        state_a[2] - (BASE[2] ^ prior.mix(first1, A)) - 1
    ) & U
    for j in range(2, 613):
        keys[j] = (
            state_a[j + 1] - (BASE[j + 1] ^ prior.mix(state_a[j], A)) - j
        ) & U

    for j in range(613, 623):
        expected = (
            state_a[j + 1]
            - (BASE[j + 1] ^ prior.mix(state_a[j], A))
            - (j % 613)
        ) & U
        assert expected == keys[j % 613], ("repeated seed contradiction", j)

    assert keys[612] != 0
    seed = sum(word << (32 * j) for j, word in enumerate(keys))
    assert ((seed.bit_length() + 31) // 32) == 613
    assert tuple(s) == random.Random(seed).getstate()[1][:624]
    return seed


def verify_printer(seed: int, original: list[bytes]) -> bytes:
    rng = random.Random(seed)
    outputs = [rng.getrandbits(32) for _ in range(967)]
    assert len(original) == len(gf.prior.STARTS) == 133
    for row, start in enumerate(gf.prior.STARTS):
        if row == 129:
            continue
        regenerated = b"".join(
            outputs[start + k].to_bytes(4, "little") for k in range(4)
        )
        assert regenerated == original[row], ("packet mismatch", row)
    return b"".join(outputs[951 + k].to_bytes(4, "little") for k in range(4))


def planted_controls() -> None:
    rng = random.Random(0x613222)
    for j in range(8):
        keys = [rng.getrandbits(32) for _ in range(613)]
        keys[-1] |= 0x80000000
        seed = sum(w << (32 * k) for k, w in enumerate(keys))
        actual = list(random.Random(seed).getstate()[1][:624])
        assert reverse_seed(actual) == seed, j
    print("8/8 genuine independent CPython n613 seeded full-inverse controls PASS")


def main() -> None:
    planted_controls()
    vals, masks, original_basis, expressions = prior.source_constraints()
    raw = (prior.ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == prior.SOURCE_SHA
    payloads = [bytes.fromhex(x) for x in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(payloads) == 133
    results = []
    for branch, s7, s623, s1, s612 in BRANCHES:
        state = vals.copy()
        state[7], state[623] = s7, s623
        late = wrap.invert_repeat(613, state)
        observed = make_late_words(state, late, s1)
        assert observed[612] == s612
        augmented = add_source_constraints(original_basis, expressions, observed)
        assert len(augmented) == 15718
        for trial in range(2):
            full_state = solve_full_register(augmented, 12345 + 17 * branch + trial)
            assert all(full_state[i] == word for i, word in observed.items())
            seed = reverse_seed(full_state)
            selected = verify_printer(seed, payloads)
            results.append(selected.hex().upper())
            print(
                "ORIGINAL_SOURCE_EXACT", "branch", branch, "trial", trial,
                "seed_words", (seed.bit_length() + 31) // 32,
                "seed_sha256", hashlib.sha256(
                    seed.to_bytes((seed.bit_length() + 7) // 8, "little")
                ).hexdigest(),
                "selected_hidden_coupon", selected.hex().upper()
            )
    assert tuple(results) == EXPECTED_COUPONS
    assert len(set(results)) == 4
    print("PASS four genuine CPython n613 seeds regenerate ALL 132 intact")
    print("original printer packets yet have FOUR DIFFERENT missing coupons")
    print("This proves conditional source non-identifiability; historical K04 unresolved")


if __name__ == "__main__":
    main()
