"""Bitwuzla n=20 inverse for a K08-component-seeded CPython MT printer model.

Tests a distinct cross-slot hypothesis: the retained 16-byte K08 HMAC component
itself was supplied as a CPython bytes seed (version 2), so CPython expands it
to 20 32-bit init_by_array words via D || SHA512(D). The selected printer ACK2
row129 is withheld. A SAT projection is accepted only after exact replay of
all 132 intact packets and the original K08/K04 slot commitments.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent9"))
import k04_n24_mt_source_bitpair_smt_sft as base  # noqa: E402

from bitwuzla import Option, Options, Parser, TermManager  # noqa: E402

MASK32 = 0xFFFFFFFF
TEST_COMPONENT = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
RESULT_PATH = ROOT / "agent13-n20-bitwuzla-result.json"


class Deadline:
    def __init__(self, seconds: int) -> None:
        self.deadline = time.monotonic() + seconds
        self.expired = False

    def __call__(self) -> bool:
        self.expired = time.monotonic() >= self.deadline
        return self.expired


def key_words_from_component(component: bytes) -> list[int]:
    """CPython version-2 bytes seed: int.from_bytes(D || SHA512(D), 'big')."""
    assert len(component) == 16
    integer = int.from_bytes(component + hashlib.sha512(component).digest(), "big")
    return [(integer >> (32 * index)) & MASK32 for index in range(20)]


def component_from_key_words(key_words: list[int]) -> tuple[bytes, bytes]:
    assert len(key_words) == 20
    component = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[16:20])
    )
    sha512_part = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[0:16])
    )
    return component, sha512_part


def key_integer(key_words: list[int]) -> int:
    return sum(word << (32 * index) for index, word in enumerate(key_words))


def packets_from_key(key_words: list[int]) -> list[bytes]:
    rng = random.Random(key_integer(key_words))
    draws = [rng.getrandbits(32) for _ in range(base.OFFSET + 974)]
    return [
        b"".join(
            draws[base.OFFSET + position + index].to_bytes(4, "little")
            for index in range(4)
        )
        for position in base.mt.STARTS
    ]


def initializer_smt(key_count: int, timeout_ms: int) -> list[str]:
    """CPython MT19937 init_by_array, parameterized for 20 or 24 key words."""
    assert key_count in (8, 20, 24)
    initial = [19650218]
    for index in range(1, 624):
        previous = initial[-1]
        initial.append((1812433253 * (previous ^ (previous >> 30)) + index) & MASK32)

    def f(expression: str, multiplier: int) -> str:
        return (
            f"(bvmul #x{multiplier:08x} "
            f"(bvxor {expression} (bvlshr {expression} #x0000001e)))"
        )

    lines = ["(set-logic QF_BV)", f"(set-option :timeout {timeout_ms})"]
    for index in range(key_count):
        lines.append(f"(declare-fun k{index} () (_ BitVec 32))")

    before = f"(bvxor #x{initial[1]:08x} {f(f'#x{initial[0]:08x}', 1664525)})"
    lines.append(f"(define-fun a1first () (_ BitVec 32) (bvadd {before} k0))")
    for index in range(2, 624):
        key_index = (index - 1) % key_count
        prior = "a1first" if index == 2 else f"a{index - 1}"
        before = f"(bvxor #x{initial[index]:08x} {f(prior, 1664525)})"
        body = f"(bvadd (bvadd {before} k{key_index}) #x{key_index:08x})"
        lines.append(f"(define-fun a{index} () (_ BitVec 32) {body})")

    # The 624th first-pass iteration revisits state[1].
    last_key_index = 623 % key_count
    before = f"(bvxor a1first {f('a623', 1664525)})"
    lines.append(
        f"(define-fun a1last () (_ BitVec 32) "
        f"(bvadd (bvadd {before} k{last_key_index}) #x{last_key_index:08x}))"
    )

    # Second pass updates S2..S623, then S1, then resets S0.
    for index in range(2, 624):
        previous = "a1last" if index == 2 else f"s{index - 1}"
        before = f"(bvxor a{index} {f(previous, 1566083941)})"
        lines.append(
            f"(define-fun s{index} () (_ BitVec 32) "
            f"(bvsub {before} #x{index:08x}))"
        )
    lines.append(
        f"(define-fun s1 () (_ BitVec 32) "
        f"(bvsub (bvxor a1last {f('s623', 1566083941)}) #x00000001))"
    )
    lines.append("(define-fun s0 () (_ BitVec 32) #x80000000)")
    assert len(lines) == 1250 + key_count
    return lines


def make_solver(formula: str):
    cleaned = "\n".join(
        line for line in formula.splitlines()
        if not line.lstrip().startswith("(set-option")
    )
    manager = TermManager()
    options = Options()
    options.set(Option.PRODUCE_MODELS, True)
    options.set(Option.SAT_SOLVER, "cadical")
    parser = Parser(manager, options)
    parser.parse(cleaned, True, False)
    return parser, parser.bitwuzla()


def solve(formula: str, key_count: int, timeout_seconds: int):
    parser, solver = make_solver(formula)
    deadline = Deadline(timeout_seconds)
    solver.configure_terminator(deadline)
    started = time.monotonic()
    result = str(solver.check_sat()).strip().lower()
    elapsed = round(time.monotonic() - started, 3)
    if result in {"result.sat", "sat"}:
        verdict = "SAT"
    elif result in {"result.unsat", "unsat"}:
        verdict = "UNSAT"
    elif result in {"result.unknown", "unknown"}:
        verdict = "UNKNOWN"
    else:
        raise RuntimeError(f"Unexpected Bitwuzla result {result!r}")
    keys = None
    if verdict == "SAT":
        keys = []
        for index in range(key_count):
            value = str(solver.get_value(parser.parse_term(f"k{index}")).value(16)).lower()
            value = value.removeprefix("0x").removeprefix("#x")
            keys.append(int(value, 16))
    return verdict, keys, elapsed, deadline.expired


def write_result(value: dict) -> None:
    temporary = RESULT_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, RESULT_PATH)


def main() -> None:
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
    smt = initializer_smt(20, args.timeout_seconds * 1000)
    print(
        "ORIGINAL_SOURCE_PIN",
        "source_rows", len(original_equations),
        "selected_row129", "WITHHELD",
        "source_constraints", len(original_constraints),
        "seed_words", 20,
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    # Synthetic positive and negative controls for the exact 16-byte seed layout.
    test_words = key_words_from_component(TEST_COMPONENT)
    recovered, sha512_part = component_from_key_words(test_words)
    assert recovered == TEST_COMPONENT
    assert sha512_part == hashlib.sha512(TEST_COMPONENT).digest()
    integer = key_integer(test_words)
    test_state = base.native_initialized(test_words)
    assert random.Random(integer).getstate()[1][:624] == test_state
    fixed_state = [
        f"(assert (= s{index} #x{word:08x}))"
        for index, word in enumerate(test_state)
    ]
    print("SYNTHETIC_K08_COMPONENT_CPTHON_VERSION2_LAYOUT_PASS", flush=True)

    positive_packets = packets_from_key(test_words)
    positive_equations = base.source_rows(positive_packets, symbols)
    positive_constraints = base.lowweight_equations(positive_equations)
    fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(test_words)
    ]
    positive_formula = "\n".join(
        smt + positive_constraints + fixed + fixed_state + ["(check-sat)"]
    )
    positive, positive_keys, positive_elapsed, positive_timeout = solve(
        positive_formula, 20, args.control_timeout_seconds
    )
    assert positive == "SAT" and positive_keys == test_words and not positive_timeout, (
        "synthetic positive failed", positive, positive_keys, positive_elapsed
    )
    print("SYNTHETIC_GENUINE_K08_COMPONENT_SEED_SAT_PASS", positive_elapsed, flush=True)

    wrong_words = list(test_words)
    wrong_words[0] ^= 1
    wrong_fixed = [
        f"(assert (= k{index} #x{word:08x}))"
        for index, word in enumerate(wrong_words)
    ]
    negative_formula = "\n".join(
        smt + positive_constraints + wrong_fixed + fixed_state + ["(check-sat)"]
    )
    negative, _, negative_elapsed, negative_timeout = solve(
        negative_formula, 20, args.control_timeout_seconds
    )
    assert negative == "UNSAT" and not negative_timeout, (
        "synthetic wrong-seed negative failed", negative, negative_elapsed
    )
    print("SYNTHETIC_WRONG_SEED_UNSAT_PASS", negative_elapsed, flush=True)

    original_formula = "\n".join(smt + original_constraints + ["(check-sat)"])
    verdict, key_words, elapsed, timed_out = solve(
        original_formula, 20, args.timeout_seconds
    )
    result = {
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "seed_words": 20,
        "source_rows": len(original_equations),
        "source_constraints": len(original_constraints),
        "selected_row129_withheld": True,
        "verdict": verdict,
        "elapsed_seconds": elapsed,
        "terminator_fired": timed_out,
        "full_132_source_match": False,
        "k04_commitment_match": False,
        "k04_seed_fixed_point": False,
        "k08_commitment_match": False,
        "k08_phrase_commitment_match": False,
    }
    print(
        "ORIGINAL_N20_BITWUZLA",
        "verdict", verdict,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        "selected_row129", "WITHHELD",
        flush=True,
    )
    if verdict != "SAT" or key_words is None:
        result["interpretation"] = (
            "UNSAT under the frozen conditional CPython/k2496/n20 model"
            if verdict == "UNSAT"
            else "UNKNOWN; no exclusion or recovery"
        )
        write_result(result)
        print(result["interpretation"], flush=True)
        return

    generated = packets_from_key(key_words)
    exact_indices = [
        index for index, (actual, expected) in enumerate(zip(generated, original_packets))
        if index != 129 and actual == expected
    ]
    component, sha512_part = component_from_key_words(key_words)
    result.update({
        "seed_words_hex": [f"{word:08X}" for word in key_words],
        "intact_packet_matches": len(exact_indices),
        "full_132_source_match": len(exact_indices) == 132,
        "mismatching_source_rows": [
            index for index in range(133) if index != 129 and index not in exact_indices
        ],
        "seed_component": component.hex().upper(),
        "seed_sha512_layout_match": sha512_part == hashlib.sha512(component).digest(),
    })
    print("FULL_SOURCE_REPLAY", f"{len(exact_indices)}/132", flush=True)

    if len(exact_indices) == 132:
        route = json.loads(
            (ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8")
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
            "derived_k08_sha256": k08_sha,
            "k08_commitment_match": (
                result["seed_sha512_layout_match"]
                and k08_sha == acceptance["slot_sha256"]["K08"]
            ),
        })
        try:
            phrase_seed = component.decode("utf-8")
        except UnicodeDecodeError:
            phrase_seed = None
        if phrase_seed is not None:
            normalized = " ".join(
                re.sub(r"[^a-z0-9\s]", " ", phrase_seed.lower()).split()
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
