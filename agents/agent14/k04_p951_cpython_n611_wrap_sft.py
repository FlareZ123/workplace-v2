"""Exact source-pinned CPython n611 repeated-key bridge, selected K04 row withheld.

Runs against the original resources/ using the independent Agent39 CPython-p951
GF(2) source model. Only source constraints determine the 4 possible S7 values.
A true 611-word integer-seeded Python control exercises both inverse chains.
No copied selected ACK, route mask, commitment, or candidate is accessed.
Usage: python agents/agent14/k04_p951_cpython_n611_wrap_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951_source", ROOT / "agents/agent39/k04_p951_gf2_seed_cross_sft.py"
)
gf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gf)
U = 0xffffffff
A, B = 1664525, 1566083941
INV_A = pow(A, -1, 1 << 32)
INV_B = pow(B, -1, 1 << 32)
BASE = gf.prior.BASE
SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def mix(x: int, factor: int) -> int:
    return ((x ^ (x >> 30)) * factor) & U


def unmix(y: int, inv: int) -> int:
    t = (y * inv) & U
    return t ^ (t >> 30)


def state_a(s: list[int], i: int) -> int:
    return ((s[i] + i) & U) ^ mix(s[i - 1], B)


def cascade_and_s1(source_state: list[int]) -> tuple[dict[int, int], int]:
    """Invert CPython first pass from index623 down through repeated key11..3.

    Repeated absolute steps j=622..614 refer to key[j%611]=key11..3;
    their first-pass key values are independently determined by S2..S12,
    except S7, whose complete source-consistent alternatives are enumerated.
    """
    s = source_state.copy()
    a_next = state_a(s, 623)
    inferred = {623: s[623], 622: s[622]}
    for j in range(622, 613, -1):
        residue = j % 611
        assert 3 <= residue <= 11
        key = (
            state_a(s, residue + 1)
            - (BASE[residue + 1] ^ mix(state_a(s, residue), A))
            - residue
        ) & U
        a_prev = unmix(
            BASE[j + 1] ^ ((a_next - key - residue) & U), INV_A
        )
        s[j - 1] = unmix(a_prev ^ ((s[j] + j) & U), INV_B)
        inferred[j - 1] = s[j - 1]
        a_next = a_prev

    # Use the repeated key2 at absolute step j=613, the near-full S612,
    # and the first-pass S3 equation. S1 is updated LAST in CPython's
    # second pass, after S623, so the final step must use that S623.
    a614 = state_a(s, 614)
    a613 = state_a(s, 613)
    key2 = (a614 - (BASE[614] ^ mix(a613, A)) - 2) & U
    a2 = unmix(BASE[3] ^ ((state_a(s, 3) - key2 - 2) & U), INV_A)
    firstpass_s1 = unmix(a2 ^ ((s[2] + 2) & U), INV_B)
    final_s1 = ((firstpass_s1 ^ mix(s[623], B)) - 1) & U
    return inferred, final_s1


def seeded_controls() -> None:
    rng = random.Random(0x611BEEF)
    for trial in range(32):
        key = [rng.getrandbits(32) for _ in range(611)]
        key[-1] |= 0x80000000
        seed = sum(word << (32 * j) for j, word in enumerate(key))
        observed = list(random.Random(seed).getstate()[1][:624])
        inferred, s1 = cascade_and_s1(observed)
        assert s1 == observed[1], trial
        assert all(observed[i] == w for i, w in inferred.items()), trial
    print("32/32 genuine seeded CPython n611 complete inverse controls PASS")


def source_constraints() -> tuple[list[int], list[int], dict, list]:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(fields) == len(gf.prior.STARTS) == 133
    assert gf.prior.STARTS[129] == 951
    packets = [
        b"" if row == 129 else bytes.fromhex(value.decode())
        for row, value in enumerate(fields)
    ]
    expr = gf.symbolic_states()
    base = gf.seed_base(packets, expr)
    val, mask = gf.individually_fixed(base, expr)
    assert len(base) == 15397
    assert sum(m.bit_count() for m in mask) == 9770
    assert (val[7], mask[7]) == (0x81441000, 0x89cc1c00)
    assert (val[612], mask[612]) == (0x42c42558, 0x7fffffff)
    assert (val[623], mask[623]) == (0x04710790, 0x7fffffff)
    assert (val[621], mask[621]) == (0, 0x80000000)
    assert (val[1], mask[1]) == (1, 0x80000001)
    return val, mask, base, expr


def full_s7_domain(base: dict, expr: list) -> list[int]:
    """22 unknown *individual* S7 bits span only TWO linear dimensions."""
    vals = []
    for pick in range(4):
        augmented = base.copy()
        for bit in (0, 1):
            equation = gf.reduce(
                (expr[7][bit] << 1) | ((pick >> bit) & 1), augmented
            )
            assert equation != 1
            if equation > 1:
                augmented[equation.bit_length() - 1] = equation
        word = 0
        for bit, term in enumerate(expr[7]):
            reduced = gf.reduce(term << 1, augmented)
            assert reduced in (0, 1)
            word |= reduced << bit
        vals.append(word)
    assert len(set(vals)) == 4
    return vals


def main() -> None:
    seeded_controls()
    val, mask, base, expr = source_constraints()
    s7_values = full_s7_domain(base, expr)
    assert set(s7_values) == {
        0xb575b1d8, 0xe3461319, 0xd15772a6, 0x8764d067
    }
    counters = {"S1": 0, "S621": 0}
    for s7 in s7_values:
        for s612top in (0, 0x80000000):
            for s623top in (0, 0x80000000):
                s = val.copy()
                s[7] = s7
                s[612] |= s612top
                s[623] |= s623top
                inferred, s1 = cascade_and_s1(s)
                if (inferred[621] ^ val[621]) & mask[621]:
                    counters["S621"] += 1
                else:
                    assert (s1 ^ val[1]) & mask[1], (
                        "source-consistent n611 state remains", hex(s7),
                        s612top, s623top, hex(s1)
                    )
                    counters["S1"] += 1
    assert counters == {"S1": 8, "S621": 8}
    print("Original four possible S7 words:", [f"{x:08X}" for x in s7_values])
    print("Exhausted 4 S7 x 2 S612.high x 2 S623.high = 16 original cases")
    print("Original contradictions: 8 S1, 8 S621; source-compatible cases ZERO")
    print("CPython integer seed length611 excluded under conditional p951 model")
    print("K04 selected coupon not recovered; K08 author-final words unknown")


if __name__ == "__main__":
    main()
