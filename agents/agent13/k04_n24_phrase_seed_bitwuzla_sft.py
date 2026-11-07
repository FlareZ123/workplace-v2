"""Phrase-constrained n=24 CPython source inverse.

Tests whether the normalized 32-byte K08 phrase itself was passed as a
CPython version-2 bytes seed, expanding to phrase || SHA512(phrase) (24 words).
The final ACK2 packet row129 is withheld. A SAT projection is never accepted
without exact 132-packet replay, the SHA512 seed-layout check, all three
ancestral PTW source anchors, and the original K08/K04 commitments.
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
RESULT_PATH = ROOT / "agent13-n24-phrase-bitwuzla-result.json"


def key_words_from_phrase(phrase: bytes) -> list[int]:
    assert len(phrase) == 32
    integer = int.from_bytes(phrase + hashlib.sha512(phrase).digest(), "big")
    return [(integer >> (32 * index)) & MASK32 for index in range(24)]


def phrase_from_key_words(key_words: list[int]) -> tuple[bytes, bytes]:
    assert len(key_words) == 24
    phrase = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[16:24])
    )
    sha512_part = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[:16])
    )
    return phrase, sha512_part


def normalized_phrase_constraints() -> list[str]:
    """Require the 32 seed bytes to already be K08-normalized ASCII."""
    chars = [
        f"((_ extract {high} {low}) k{word_index})"
        for word_index in reversed(range(16, 24))
        for high, low in ((31, 24), (23, 16), (15, 8), (7, 0))
    ]
    assert len(chars) == 32
    constraints = []
    for char in chars:
        constraints.append(
            "(assert (or "
            f"(= {char} #x20) "
            f"(and (bvuge {char} #x30) (bvule {char} #x39)) "
            f"(and (bvuge {char} #x61) (bvule {char} #x7a))))"
        )
    constraints.append(f"(assert (not (= {chars[0]} #x20)))")
    constraints.append(f"(assert (not (= {chars[-1]} #x20)))")
    for left, right in zip(chars, chars[1:]):
        constraints.append(
            f"(assert (not (and (= {left} #x20) (= {right} #x20))))"
        )
    return constraints


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
    smt = shared.initializer_smt(24, args.timeout_seconds * 1000)
    phrase_constraints = normalized_phrase_constraints()
    print(
        "ORIGINAL_SOURCE_PIN",
        "source_rows", len(original_equations),
        "selected_row129", "WITHHELD",
        "source_constraints", len(original_constraints),
        "phrase_bytes", 32,
        "seed_words", 24,
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    # Full initializer-state positive control with a normalized 32-byte phrase.
    test_phrase = b"a quiet room waits for the watch"
    assert len(test_phrase) == 32
    test_words = key_words_from_phrase(test_phrase)
    recovered, recovered_sha = phrase_from_key_words(test_words)
    assert recovered == test_phrase
    assert recovered_sha == hashlib.sha512(test_phrase).digest()
    test_state = base.native_initialized(test_words)
    fixed_state = [
        f"(assert (= s{index} #x{word:08x}))"
        for index, word in enumerate(test_state)
    ]
    positive_packets = shared.packets_from_key(test_words)
    positive_equations = base.source_rows(positive_packets, symbols)
    positive_constraints = base.lowweight_equations(positive_equations)
    fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(test_words)
    ]
    positive_formula = "\n".join(
        smt + phrase_constraints + positive_constraints + fixed + fixed_state
        + ["(check-sat)"]
    )
    positive, positive_keys, positive_elapsed, positive_timeout = shared.solve(
        positive_formula, 24, args.control_timeout_seconds
    )
    assert (
        positive == "SAT"
        and positive_keys == test_words
        and not positive_timeout
    ), ("synthetic phrase positive failed", positive, positive_keys, positive_elapsed)
    print("SYNTHETIC_NORMALIZED_PHRASE_SEED_SAT_PASS", positive_elapsed, flush=True)

    wrong_words = list(test_words)
    wrong_words[0] ^= 1
    wrong_fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(wrong_words)
    ]
    negative_formula = "\n".join(
        smt + phrase_constraints + positive_constraints + wrong_fixed + fixed_state
        + ["(check-sat)"]
    )
    negative, _, negative_elapsed, negative_timeout = shared.solve(
        negative_formula, 24, args.control_timeout_seconds
    )
    assert negative == "UNSAT" and not negative_timeout, (
        "synthetic phrase wrong-seed negative failed", negative, negative_elapsed
    )
    print("SYNTHETIC_WRONG_PHRASE_SEED_UNSAT_PASS", negative_elapsed, flush=True)

    original_formula = "\n".join(
        smt + original_constraints + phrase_constraints + ["(check-sat)"]
    )
    verdict, key_words, elapsed, timed_out = shared.solve(
        original_formula, 24, args.timeout_seconds
    )
    result = {
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "seed_words": 24,
        "phrase_bytes": 32,
        "source_rows": len(original_equations),
        "source_constraints": len(original_constraints),
        "selected_row129_withheld": True,
        "verdict": verdict,
        "elapsed_seconds": elapsed,
        "terminator_fired": timed_out,
        "full_132_source_match": False,
        "sha512_seed_layout_match": False,
        "k04_commitment_match": False,
        "k08_commitment_match": False,
    }
    print(
        "ORIGINAL_N24_NORMALIZED_PHRASE_BITWUZLA",
        "verdict", verdict,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        "selected_row129", "WITHHELD",
        flush=True,
    )
    if verdict != "SAT" or key_words is None:
        result["interpretation"] = (
            "UNSAT under the frozen k2496/n24 normalized-phrase seed model"
            if verdict == "UNSAT"
            else "UNKNOWN; no exclusion or recovery"
        )
        write_result(result)
        print(result["interpretation"], flush=True)
        return

    phrase, sha512_part = phrase_from_key_words(key_words)
    phrase_text = phrase.decode("ascii")
    normalized = " ".join(
        re.sub(r"[^a-z0-9\s]", " ", phrase_text.lower()).split()
    )
    generated = shared.packets_from_key(key_words)
    exact_indices = [
        index for index, (actual, expected) in enumerate(
            zip(generated, original_packets)
        )
        if index != 129 and actual == expected
    ]
    ancestry = shared.ancestral_anchor_check(key_words)
    result.update({
        "seed_words_hex": [f"{word:08X}" for word in key_words],
        "recovered_phrase_seed": phrase_text,
        "normalized_phrase": normalized,
        "sha512_seed_layout_match": sha512_part == hashlib.sha512(phrase).digest(),
        "ancestral_anchor_matches": ancestry,
        "ancestral_anchors_all_match": all(row["match"] for row in ancestry),
        "intact_packet_matches": len(exact_indices),
        "full_132_source_match": len(exact_indices) == 132,
        "mismatching_source_rows": [
            index for index in range(133) if index != 129 and index not in exact_indices
        ],
    })
    print(
        "FULL_SOURCE_REPLAY",
        f"{len(exact_indices)}/132",
        "ANCESTRAL_ANCHORS",
        sum(row["match"] for row in ancestry), "/3",
        flush=True,
    )

    if len(exact_indices) == 132:
        route = json.loads(
            (ROOT / "resources/evidence/recovery-routing.json").read_text(
                encoding="utf-8"
            )
        )
        acceptance = json.loads(
            (ROOT / "resources/acceptance.json").read_text(encoding="utf-8")
        )
        nonce = bytes.fromhex(route["K08"]["desk_nonce"])
        k08_component = hmac.digest(
            nonce, normalized.encode("utf-8"), "sha256"
        )[:16]
        k08_sha = hashlib.sha256(k08_component).hexdigest()
        mask = bytes.fromhex(route["K04"]["masked_component"])
        coupon = generated[129]
        k04_component = bytes(left ^ right for left, right in zip(coupon, mask))
        k04_sha = hashlib.sha256(k04_component).hexdigest()
        result.update({
            "derived_k08_component": k08_component.hex().upper(),
            "derived_k08_sha256": k08_sha,
            "k08_commitment_match": (
                result["sha512_seed_layout_match"]
                and k08_sha == acceptance["slot_sha256"]["K08"]
            ),
            "predicted_selected_coupon": coupon.hex().upper(),
            "derived_k04_component": k04_component.hex().upper(),
            "derived_k04_sha256": k04_sha,
            "k04_commitment_match": k04_sha == acceptance["slot_sha256"]["K04"],
        })
        print(
            "FULL_SOURCE_VERIFIED",
            "SHA512_LAYOUT", result["sha512_seed_layout_match"],
            "ANCESTRAL_ANCHORS", result["ancestral_anchors_all_match"],
            "K08_SHA_MATCH", result["k08_commitment_match"],
            "K04_SHA_MATCH", result["k04_commitment_match"],
            flush=True,
        )
        if result["k08_commitment_match"]:
            print("RECOVERED_K08_PHRASE", normalized, flush=True)
            print("COMPLETE_K08_COMPONENT", k08_component.hex().upper(), flush=True)
        if result["k04_commitment_match"]:
            print("COMPLETE_K04_COMPONENT", k04_component.hex().upper(), flush=True)
        result["interpretation"] = (
            "Exact source fit; phrase, SHA512 layout and slot commitments recorded."
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
