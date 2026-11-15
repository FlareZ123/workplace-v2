#!/usr/bin/env python3
"""Test the direct K08-HMAC16 == K04 ESC-N coupon hypothesis.

The phrase family is imported unchanged from Agent9's frozen
k08_hmac32_printer_coupling_sft.py grammar. For each phrase:
  h = HMAC-SHA256(desk_nonce, phrase)[:16]
  proposed_K04 = h XOR masked_component
  accept only if SHA256(proposed_K04) == acceptance.K04.

The optimized local run used an OpenSSL C++ implementation of this exact
transform. This Python reference is slower but independently reproducible.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import importlib.util
import itertools
import json
import time
from pathlib import Path


def load_phrase_family(repo_root: Path):
    path = repo_root / "agents/agent9/k08_hmac32_printer_coupling_sft.py"
    spec = importlib.util.spec_from_file_location("agent9_k08_phrase_family", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load phrase family: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SEA, module.NIGHT, module.HUMAN, module.OPENING, module.JOIN


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-opening", type=int, default=0)
    parser.add_argument("--end-opening", type=int, default=8)
    parser.add_argument("--check-k08", action="store_true",
                        help="also recheck the K08 commitment for each phrase")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    routing = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target4 = bytes.fromhex(acceptance["slot_sha256"]["K04"])
    target8 = bytes.fromhex(acceptance["slot_sha256"]["K08"])

    SEA, NIGHT, HUMAN, OPENING, JOIN = load_phrase_family(root)
    assert (len(SEA), len(NIGHT), len(HUMAN), len(OPENING), len(JOIN)) == (32, 25, 50, 8, 6)
    assert 0 <= args.start_opening < args.end_opening <= len(OPENING)
    expected_total = len(SEA) * len(NIGHT) * len(HUMAN) * len(OPENING) * 6 * len(JOIN) ** 2
    assert expected_total == 69_120_000

    def transform(phrase: str) -> tuple[bytes, bytes]:
        digest = hmac.digest(nonce, phrase.encode("ascii"), "sha256")
        hmac16 = digest[:16]
        proposed4 = bytes(a ^ b for a, b in zip(hmac16, mask))
        return hmac16, proposed4

    # Positive control through the same HMAC/XOR/SHA-256 transformation.
    planted = f"{OPENING[1]} {SEA[0]} {JOIN[0]} {NIGHT[0]} {JOIN[1]} {HUMAN[0]}"
    h1, c1 = transform(planted)
    h2 = hmac.new(nonce, planted.encode("ascii"), hashlib.sha256).digest()[:16]
    c2 = bytes(a ^ b for a, b in zip(h2, mask))
    assert h1 == h2 and hashlib.sha256(c1).digest() == hashlib.sha256(c2).digest()
    print("SYNTHETIC_K04_JOINT_CONTROL_PASS", flush=True)

    checked = hits4 = hits8 = both = 0
    started = time.perf_counter()
    for oi in range(args.start_opening, args.end_opening):
        before = checked
        for first, second, third in itertools.permutations((SEA, NIGHT, HUMAN)):
            for a in first:
                for b in second:
                    for c in third:
                        for j0 in JOIN:
                            for j1 in JOIN:
                                phrase = f"{a} {j0} {b} {j1} {c}"
                                if OPENING[oi]:
                                    phrase = OPENING[oi] + " " + phrase
                                hmac16, proposed4 = transform(phrase)
                                ok4 = hashlib.sha256(proposed4).digest() == target4
                                ok8 = args.check_k08 and hashlib.sha256(hmac16).digest() == target8
                                checked += 1
                                if ok4:
                                    hits4 += 1
                                    print("K04_JOINT_CARRIER_HIT", repr(phrase), proposed4.hex().upper(), flush=True)
                                if ok8:
                                    hits8 += 1
                                    print("K08_COMMITMENT_HIT", repr(phrase), hmac16.hex().upper(), flush=True)
                                if ok4 and ok8:
                                    both += 1
                                    print("BOTH_SLOT_HIT", repr(phrase), flush=True)
        assert checked - before == expected_total // len(OPENING)
        print("PROGRESS", oi, "checked", checked, "K04", hits4,
              "K08", hits8, "both", both, flush=True)

    expected_chunk = expected_total * (args.end_opening - args.start_opening) // len(OPENING)
    assert checked == expected_chunk
    print("COMPLETE", "checked", checked, "K04", hits4, "K08", hits8,
          "both", both, "seconds", round(time.perf_counter() - started, 2))
    if hits4 or hits8 or both:
        raise RuntimeError("commitment hit requires independent verification")


if __name__ == "__main__":
    main()
