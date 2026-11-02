"""Exact CPython integer-seed length 623 wrap parity falsifier for hypothetical p951.
Original selected row129 is withheld before fitting; neither acceptance nor candidate is read.
Run: python agents/agent39/k04_p951_seed623_wrap_parity_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "source_model", ROOT / "agents/agent39/k04_p951_gf2_seed_cross_sft.py"
)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
U = 0xffffffff
M1 = 1664525
M2 = 1566083941
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"


def mix(x: int, multiplier: int) -> int:
    return ((x ^ (x >> 30)) * multiplier) & U


def predict_s1_bit0_n623(s622: int, s623: int) -> int:
    """Eliminate repeated key[0] at the 1st and 624th first-pass updates."""
    initial = model.prior.BASE
    c = initial[1] ^ mix(initial[0], M1)
    before_second_623 = ((s623 + 623) & U) ^ mix(s622, M2)
    return (c ^ mix(before_second_623, M1) ^ mix(s623, M2) ^ 1) & 1


def source_fixes(packets, expressions):
    basis = model.seed_base(packets, expressions)
    values, masks = model.individually_fixed(basis, expressions)
    return basis, values, masks


def main():
    data = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(data).hexdigest() == SPOOL_SHA
    fields = re.findall(rb"PAYLOAD=([0-9A-F]{32})", data)
    assert len(fields) == len(model.prior.STARTS) == 133
    assert model.prior.STARTS[129] == 951
    packets = [b"" if i == 129 else bytes.fromhex(v.decode())
               for i, v in enumerate(fields)]
    expressions = model.symbolic_states()
    basis, values, masks = source_fixes(packets, expressions)
    assert len(basis) == 15397
    assert values[1] & masks[1] & 1 == 1
    assert (values[622], masks[622]) == (0xbbd5a4ab, U)
    assert (values[623], masks[623]) == (0x04710790, 0x7fffffff)
    predicted = [
        predict_s1_bit0_n623(values[622], values[623] | top)
        for top in (0, 0x80000000)
    ]
    assert predicted == [0, 0]
    assert all(v != (values[1] & 1) for v in predicted)
    print("Original source excludes CPython key-array length 623:",
          "source S1[0]=1, n623 wrap predicts", predicted)

    for trial in range(8):
        key = [((0xa9131b7 + trial * 0x35b + j * 0x3f1f1) & U)
               for j in range(623)]
        key[-1] |= 0x80000000
        seed = sum(x << (32*j) for j, x in enumerate(key))
        rng = random.Random(seed)
        register = rng.getstate()[1][:624]
        assert predict_s1_bit0_n623(register[622], register[623]) == (register[1] & 1)
        draws = [rng.getrandbits(32) for _ in range(967)]
        fixture = [
            b"".join(draws[start + j].to_bytes(4, "little") for j in range(4))
            for start in model.prior.STARTS
        ]
        fixture[129] = b""
        _, fvals, fmasks = source_fixes(fixture, expressions)
        assert all(not ((x ^ v) & m) for x, v, m in zip(register, fvals, fmasks))
    print("Eight actual seeded, selected-withheld p951 full-spool controls: PASS")
    print("Conditional n623 exclusion; no K04 bits or K08 phrase recovered")


if __name__ == "__main__":
    main()
