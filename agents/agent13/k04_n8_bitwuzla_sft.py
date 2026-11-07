"""Bitwuzla n=8 inverse for a full K08-HMAC32 integer-seeded CPython stream.

Distinct from the n20 bytes-seed and n24 full-digest bytes-seed models: this
tests whether the complete 32-byte K08 HMAC digest was converted to a big-endian
integer and used as random.Random's seed. The selected ACK2 row129 is withheld.
A SAT projection is accepted only after exact replay of all 132 intact packets
and the original K08/K04 slot commitments.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent13"))
import k04_n20_bitwuzla_sft as shared  # noqa: E402

base = shared.base
MASK32 = 0xFFFFFFFF
TEST_NONCE = bytes.fromhex("102132435465768798A9BACBDCEDFE0F")
RESULT_PATH = ROOT / "agent13-n8-bitwuzla-result.json"


def key_words_from_digest(digest: bytes) -> list[int]:
    assert len(digest) == 32
    integer = int.from_bytes(digest, "big")
    return [(integer >> (32 * index)) & MASK32 for index in range(8)]


def digest_from_key_words(key_words: list[int]) -> bytes:
    assert len(key_words) == 8
    return b"".join(word.to_bytes(4, "big") for word in reversed(key_words))


def write_result(value: dict) -> None:
    temporary = RESULT_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, RESULT_PATH)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout-seconds", type=int, default=3300)
    ap.add_argument("--control-timeout-seconds", type=int, default=120)
    args = ap.parse_args()
    assert 60 <= args.timeout_seconds <= 3500
    assert 10 <= args.control_timeout_seconds <= 600

    original_packets = base.original_packets()
    assert len(original_packets) == len(base.mt.STARTS) == 133
    assert base.mt.STARTS[129] == 951
    symbols = base.words(base.OFFSET)
    original_equations = base.source_rows(original_packets, symbols)
    original_constraints = base.lowweight_equations(original_equations)
    smt = shared.initializer_smt(8, args.timeout_seconds * 1000)
    print(
        "ORIGINAL_SOURCE_PIN",
        "source_rows", len(original_equations),
        "selected_row129", "WITHHELD",
        "source_constraints", len(original_constraints),
        "seed_words", 8,
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    # Positive and negative controls for the full-HMAC integer seed layout.
    test_digest = hmac.digest(
        TEST_NONCE, b"independent HMAC32 integer-seed control", "sha256"
    )
    test_words = key_words_from_digest(test_digest)
    assert digest_from_key_words(test_words) == test_digest
    assert shared.key_integer(test_words) == int.from_bytes(test_digest, "big")
    test_state = shared.base.native_initialized(test_words)
    assert test_state == __import__("random").Random(
        int.from_bytes(test_digest, "big")
    ).getstate()[1][:624]
    fixed_state = [
        f"(assert (= s{index} #x{word:08x}))"
        for index, word in enumerate(test_state)
    ]
    print("SYNTHETIC_HMAC32_INTEGER_SEED_LAYOUT_PASS", flush=True)

    positive_packets = shared.packets_from_key(test_words)
    positive_equations = base.source_rows(positive_packets, symbols)
    positive_constraints = base.lowweight_equations(positive_equations)
    fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(test_words)
    ]
    positive_formula = "\n".join(
        smt + positive_constraints + fixed + fixed_state + ["(check-sat)"]
    )
    positive, positive_keys, positive_elapsed, positive_timeout = shared.solve(
        positive_formula, 8, args.control_timeout_seconds
    )
    assert (
        positive == "SAT"
        and positive_keys == test_words
        and not positive_timeout
    ), ("synthetic positive failed", positive, positive_keys, positive_elapsed)
    print(
        "SYNTHETIC_GENUINE_HMAC32_INTEGER_SEED_SAT_PASS",
        positive_elapsed,
        flush=True,
    )

    wrong_words = list(test_words)
    wrong_words[0] ^= 1
    wrong_fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(wrong_words)
    ]
    negative_formula = "\n".join(
        smt + positive_constraints + wrong_fixed + fixed_state + ["(check-sat)"]
    )
    negative, _, negative_elapsed, negative_timeout = shared.solve(
        negative_formula, 8, args.control_timeout_seconds
    )
    assert negative == "UNSAT" and not negative_timeout, (
        "synthetic wrong-seed negative failed", negative, negative_elapsed
    )
    print("SYNTHETIC_WRONG_SEED_UNSAT_PASS", negative_elapsed, flush=True)

    original_formula = "\n".join(
        smt + original_constraints + ["(check-sat)"]
    )
    verdict, key_words, elapsed, timed_out = shared.solve(
        original_formula, 8, args.timeout_seconds
    )
    result = {
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "seed_words": 8,
        "source_rows": len(original_equations),
        "source_constraints": len(original_constraints),
        "selected_row129_withheld": True,
        "verdict": verdict,
        "elapsed_seconds": elapsed,
        "terminator_fired": timed_out,
        "full_132_source_match": False,
        "k04_commitment_match": False,
        "k04_seed_prefix_fixed_point": False,
        "k08_commitment_match": False,
        "k08_phrase_commitment_match": False,
    }
    print(
        "ORIGINAL_N8_BITWUZLA",
        "verdict", verdict,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        "selected_row129", "WITHHELD",
        flush=True,
    )
    if verdict != "SAT" or key_words is None:
        result["interpretation"] = (
            "UNSAT under the frozen conditional CPython/k2496/n8 model"
            if verdict == "UNSAT"
            else "UNKNOWN; no exclusion or recovery"
        )
        write_result(result)
        print(result["interpretation"], flush=True)
        return

    generated = shared.packets_from_key(key_words)
    exact_indices = [
        index for index, (actual, expected) in enumerate(
            zip(generated, original_packets)
        )
        if index != 129 and actual == expected
    ]
    digest = digest_from_key_words(key_words)
    component = digest[:16]
    result.update({
        "seed_words_hex": [f"{word:08X}" for word in key_words],
        "intact_packet_matches": len(exact_indices),
        "full_132_source_match": len(exact_indices) == 132,
        "mismatching_source_rows": [
            index for index in range(133) if index != 129 and index not in exact_indices
        ],
        "hmac32_digest_D": digest.hex().upper(),
        "derived_k08_component": component.hex().upper(),
    })
    print("FULL_SOURCE_REPLAY", f"{len(exact_indices)}/132", flush=True)

    if len(exact_indices) == 132:
        route = json.loads(
            (ROOT / "resources/evidence/recovery-routing.json").read_text(
                encoding="utf-8"
            )
        )
        acceptance = json.loads(
            (ROOT / "resources/acceptance.json").read_text(encoding="utf-8")
        )
        mask = bytes.fromhex(route["K04"]["masked_component"])
        coupon = generated[129]
        k04_component = bytes(left ^ right for left, right in zip(coupon, mask))
        k04_sha = hashlib.sha256(k04_component).hexdigest()
        k08_sha = hashlib.sha256(component).hexdigest()
        result.update({
            "predicted_selected_coupon": coupon.hex().upper(),
            "derived_k04_component": k04_component.hex().upper(),
            "derived_k04_sha256": k04_sha,
            "k04_commitment_match": k04_sha == acceptance["slot_sha256"]["K04"],
            "k04_seed_prefix_fixed_point": digest[:16] == k04_component,
            "derived_k08_sha256": k08_sha,
            "k08_commitment_match": k08_sha == acceptance["slot_sha256"]["K08"],
        })
        try:
            phrase_seed = digest.decode("utf-8")
        except UnicodeDecodeError:
            phrase_seed = None
        if phrase_seed is not None:
            normalized = " ".join(
                re.sub(r"[^a-z0-9\\s]", " ", phrase_seed.lower()).split()
            )
            nonce = bytes.fromhex(route["K08"]["desk_nonce"])
            phrase_component = hmac.digest(
                nonce, normalized.encode("utf-8"), "sha256"
            )[:16]
            phrase_sha = hashlib.sha256(phrase_component).hexdigest()
            result.update({
                "seed_bytes_as_normalized_phrase": normalized,
                "k08_phrase_sha256": phrase_sha,
                "k08_phrase_commitment_match": (
                    phrase_sha == acceptance["slot_sha256"]["K08"]
                ),
            })
            if result["k08_phrase_commitment_match"]:
                print("K08_PHRASE_FROM_PRINTER_SEED", normalized, flush=True)
        print(
            "FULL_SOURCE_VERIFIED",
            "K04_SHA_MATCH", result["k04_commitment_match"],
            "K08_SHA_MATCH", result["k08_commitment_match"],
            flush=True,
        )
        if result["k04_commitment_match"]:
            print("COMPLETE_K04_CANDIDATE", k04_component.hex().upper(), flush=True)
        if result["k08_commitment_match"]:
            print("COMPLETE_K08_COMPONENT", component.hex().upper(), flush=True)
        result["interpretation"] = (
            "Exact 132-packet CPython source fit; commitment outcomes recorded."
        )
    else:
        result["interpretation"] = (
            "SAT projection only: it does not reproduce all 132 intact packets; "
            "no candidate is accepted."
        )

    write_result(result)
    print("RESULT_JSON", RESULT_PATH.name, flush=True)


if __name__ == "__main__":
    main()
