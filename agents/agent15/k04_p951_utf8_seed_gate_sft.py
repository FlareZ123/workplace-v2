"""Original-source K04 p951 CPython UTF-8 string-seed falsifier.

Run from checkout: python agents/agent15/k04_p951_utf8_seed_gate_sft.py
Uses the existing, independently reproduced Agent39 source-only GF2 basis.
The selected printer row, K04/K08 commitments, XOR mask and verifier are never read.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "resources/evidence/print/spool-reconstruction.log"
SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MOD = (1 << 32) - 1
spec = importlib.util.spec_from_file_location(
    "source_model", ROOT / "agents/agent39/k04_p951_gf2_seed_cross_sft.py"
)
model = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(model)


def test_utf8_synthetic() -> None:
    # CPython seed(str, version=2) appends a 64-byte SHA512 digest to UTF-8
    # bytes and imports their big-endian integer as 32-bit little-endian words.
    for n in (249, 606, 623):
        source = "A" * (4 * n - 64)
        raw = source.encode("utf-8")
        key_integer = int.from_bytes(raw + hashlib.sha512(raw).digest(), "big")
        key_word_22 = (key_integer >> (32 * 22)) & MOD
        state = random.Random(source).getstate()[1][:624]
        term = model.prior.key_term(23, *state[21:24])
        assert key_word_22 == 0x41414141
        assert term == (key_word_22 + 22) & MOD, (n, term)
    print("Synthetic actual CPython UTF-8 string seeds: 3/3 PASS")


def main() -> None:
    test_utf8_synthetic()
    raw = SRC.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    tokens = re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)
    assert len(tokens) == len(model.prior.STARTS) == 133
    assert model.prior.STARTS[129] == 951
    # Crucial original-data isolation: never decode the selected copied ACK2.
    payloads = [
        b"" if i == 129 else bytes.fromhex(token.decode("ascii"))
        for i, token in enumerate(tokens)
    ]
    expressions = model.symbolic_states()
    basis = model.seed_base(payloads, expressions)
    values, masks = model.individually_fixed(basis, expressions)
    terms = model.prior.source_terms(values, masks)
    assert len(terms) == 94
    possible = sorted(terms[22])
    assert possible == [0x7D6A4D0D, 0xFD6A4D0D], [
        f"{t:08X}" for t in possible
    ]
    decoded = [((t - 22) & MOD).to_bytes(4, "little") for t in possible]
    assert all(b[0] == 0xF7 for b in decoded)
    assert all(not is_possible_utf8_fragment(b) for b in decoded)
    print(json.dumps({
        "source_word": "T[22]",
        "possible_terms_hex": [f"{t:08X}" for t in possible],
        "seed_word_22_little_endian_hex": [b.hex().upper() for b in decoded],
        "utf8_possible": False,
        "scope": ("p951 first-cycle first-output CPython seed(str/UTF-8 bytes); "
                  "lengths <=363 already source-rejected independently; "
                  "for seed lengths 364..623 word22 comes from UTF-8 text, not the SHA512 tail"),
        "k04_new_authenticated_bits": 0,
    }, indent=2))


def is_possible_utf8_fragment(b: bytes) -> bool:
    # UTF-8 never permits F5..FF anywhere, irrespective of character boundary.
    return all(v <= 0xF4 for v in b)


if __name__ == "__main__":
    main()
