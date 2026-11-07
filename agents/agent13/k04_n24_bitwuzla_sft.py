"""Bitwuzla n=24 inverse for the conditional CPython MT printer model.

This advances Agent9's 15-second Z3 n=24 frontier with an independent
Bitwuzla/CaDiCaL backend and model extraction. It preserves the selected
PS-261003-0417 ACK2 row as a complete holdout. A SAT projection is never
reported as a recovery unless all 132 intact source packets reproduce exactly.

The 24-word seed is also checked for the CPython bytes-version-2 layout
D || SHA512(D), where D is a hypothetical 32-byte K08 HMAC output. This is a
cross-slot hypothesis, not a historical assertion.
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
TEST_NONCE = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
RESULT_PATH = ROOT / "agent13-n24-bitwuzla-result.json"


class Deadline:
    """Monotonic Bitwuzla termination callback."""

    def __init__(self, seconds: int) -> None:
        self.deadline = time.monotonic() + seconds
        self.expired = False

    def __call__(self) -> bool:
        self.expired = time.monotonic() >= self.deadline
        return self.expired


def key_integer(key_words: list[int]) -> int:
    return sum(word << (32 * index) for index, word in enumerate(key_words))


def packets_from_key(key_words: list[int]) -> list[bytes]:
    """Generate the original 133 packet positions from a CPython integer seed."""
    rng = random.Random(key_integer(key_words))
    draws = [rng.getrandbits(32) for _ in range(base.OFFSET + 974)]
    return [
        b"".join(
            draws[base.OFFSET + position + index].to_bytes(4, "little")
            for index in range(4)
        )
        for position in base.mt.STARTS
    ]


def ancestral_anchor_check(key_words: list[int]) -> list[dict]:
    """Post-hoc check of the three published PTW full-word source anchors."""
    rng = random.Random(key_integer(key_words))
    draws = [rng.getrandbits(32) for _ in range(base.OFFSET + 974)]
    receipts_path = ROOT / "resources/evidence/maintenance/seal-receipts.jsonl"
    receipts = [
        json.loads(line)
        for line in receipts_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    targets = [
        ("PTW-405", "D", -964),
        ("PTW-412", "B", -944),
        ("PTW-414", "C", -937),
    ]
    output = []
    for permit, bay, stage in targets:
        record = next(
            row for row in receipts
            if row["permit"] == permit
            and row["bay"] == bay
            and row["revision"] == 1
            and row["state"] == "CLOSED"
            and row["fitment"] == "AS_LEFT"
            and row["signed"] is True
        )
        serial = bytes.fromhex(record["serial"].split("-", 1)[1])
        predicted = draws[base.OFFSET + stage]
        expected = int.from_bytes(serial, "little")
        output.append({
            "permit": permit,
            "stage": stage,
            "serial": record["serial"],
            "predicted_word_le": f"{predicted:08X}",
            "expected_word_le": f"{expected:08X}",
            "match": predicted == expected,
        })
    return output


def words_from_hmac32(digest: bytes) -> list[int]:
    """CPython version-2 byte seed D: integer is big-endian D || SHA512(D)."""
    assert len(digest) == 32
    seed_integer = int.from_bytes(digest + hashlib.sha512(digest).digest(), "big")
    return [(seed_integer >> (32 * index)) & MASK32 for index in range(24)]


def hmac32_parts(key_words: list[int]) -> tuple[bytes, bytes]:
    """Recover D and the SHA512(D) half from CPython's little-endian key words."""
    assert len(key_words) == 24
    digest = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[16:24])
    )
    sha512_part = b"".join(
        word.to_bytes(4, "big") for word in reversed(key_words[0:16])
    )
    return digest, sha512_part


def make_solver(formula: str):
    """Parse SMT-LIB with model generation and CaDiCaL enabled."""
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


def verdict_name(result) -> str:
    value = str(result).strip().lower()
    if value in {"sat", "result.sat"}:
        return "SAT"
    if value in {"unsat", "result.unsat"}:
        return "UNSAT"
    if value in {"unknown", "result.unknown"}:
        return "UNKNOWN"
    raise RuntimeError(f"Unexpected Bitwuzla result: {result!r}")


def solve(formula: str, timeout_seconds: int) -> tuple[str, list[int] | None, float, bool]:
    parser, solver = make_solver(formula)
    deadline = Deadline(timeout_seconds)
    solver.configure_terminator(deadline)
    started = time.monotonic()
    result = verdict_name(solver.check_sat())
    elapsed = round(time.monotonic() - started, 3)
    keys = None
    if result == "SAT":
        keys = []
        for index in range(24):
            term = parser.parse_term(f"k{index}")
            value = str(solver.get_value(term).value(16)).lower()
            value = value.removeprefix("0x").removeprefix("#x")
            keys.append(int(value, 16))
    return result, keys, elapsed, deadline.expired


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
    smt = base.smt_firstpass_secondpass(args.timeout_seconds * 1000)
    print(
        "ORIGINAL_SOURCE_PIN",
        "source_rows", len(original_equations),
        "selected_row129", "WITHHELD",
        "source_constraints", len(original_constraints),
        "seed_words", 24,
        "solver", "Bitwuzla 0.9.1 / CaDiCaL",
        flush=True,
    )

    # Verify the hypothesized K08-HMAC32 -> CPython version-2 byte-seed layout.
    test_digest = hmac.digest(TEST_NONCE, b"independent synthetic control", "sha256")
    test_words = words_from_hmac32(test_digest)
    recovered_digest, recovered_sha = hmac32_parts(test_words)
    assert recovered_digest == test_digest
    assert recovered_sha == hashlib.sha512(test_digest).digest()
    test_integer = key_integer(test_words)
    test_state = base.native_initialized(test_words)
    assert random.Random(test_integer).getstate()[1][:624] == test_state
    fixed_state = [
        f"(assert (= s{index} #x{word:08x}))"
        for index, word in enumerate(test_state)
    ]
    print("SYNTHETIC_HMAC32_CPTHON_VERSION2_LAYOUT_PASS", flush=True)

    # Positive and negative controls validate Bitwuzla model extraction.
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
        positive_formula, args.control_timeout_seconds
    )
    assert (
        positive == "SAT"
        and positive_keys == test_words
        and not positive_timeout
    ), ("synthetic positive failed", positive, positive_keys, positive_elapsed)
    print(
        "SYNTHETIC_GENUINE_HMAC32_SEEDED_SOURCE_SAT_PASS",
        "seconds", positive_elapsed,
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
    negative, _, negative_elapsed, negative_timeout = solve(
        negative_formula, args.control_timeout_seconds
    )
    assert negative == "UNSAT" and not negative_timeout, (
        "synthetic wrong-seed negative failed",
        negative,
        negative_elapsed,
    )
    print(
        "SYNTHETIC_WRONG_SEED_UNSAT_PASS",
        "seconds", negative_elapsed,
        flush=True,
    )

    original_formula = "\n".join(smt + original_constraints + ["(check-sat)"])
    verdict, key_words, elapsed, timed_out = solve(
        original_formula, args.timeout_seconds
    )
    result = {
        "solver": "Bitwuzla 0.9.1 / CaDiCaL",
        "seed_words": 24,
        "source_rows": len(original_equations),
        "source_constraints": len(original_constraints),
        "selected_row129_withheld": True,
        "verdict": verdict,
        "elapsed_seconds": elapsed,
        "terminator_fired": timed_out,
        "full_132_source_match": False,
        "k04_commitment_match": False,
        "hmac32_seed_layout_match": False,
        "k08_commitment_match": False,
        "k08_phrase_commitment_match": False,
    }

    print(
        "ORIGINAL_N24_BITWUZLA",
        "verdict", verdict,
        "elapsed_seconds", elapsed,
        "terminator_fired", timed_out,
        "selected_row129", "WITHHELD",
        flush=True,
    )
    if verdict != "SAT" or key_words is None:
        result["interpretation"] = (
            "UNSAT under the frozen conditional CPython/k2496/n24 model"
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
    result["seed_words_hex"] = [f"{word:08X}" for word in key_words]
    ancestry = ancestral_anchor_check(key_words)
    result["ancestral_anchor_matches"] = ancestry
    result["ancestral_anchors_all_match"] = all(row["match"] for row in ancestry)
    result["intact_packet_matches"] = len(exact_indices)
    result["full_132_source_match"] = len(exact_indices) == 132
    result["mismatching_source_rows"] = [
        index for index in range(133) if index != 129 and index not in exact_indices
    ]
    print(
        "FULL_SOURCE_REPLAY",
        f"{len(exact_indices)}/132",
        "selected_row129", "WITHHELD",
        flush=True,
    )

    # Only consult original acceptance commitments after an exact full-source fit.
    if len(exact_indices) == 132:
        route = json.loads(
            (ROOT / "resources/evidence/recovery-routing.json").read_text(encoding="utf-8")
        )
        acceptance = json.loads(
            (ROOT / "resources/acceptance.json").read_text(encoding="utf-8")
        )
        mask = bytes.fromhex(route["K04"]["masked_component"])
        coupon = generated[129]
        component = bytes(left ^ right for left, right in zip(coupon, mask))
        k04_sha = hashlib.sha256(component).hexdigest()
        result.update({
            "predicted_selected_coupon": coupon.hex().upper(),
            "derived_k04_component": component.hex().upper(),
            "derived_k04_sha256": k04_sha,
            "k04_commitment_match": k04_sha == acceptance["slot_sha256"]["K04"],
        })
        digest, sha512_part = hmac32_parts(key_words)
        layout_match = sha512_part == hashlib.sha512(digest).digest()
        k08_component = digest[:16]
        k08_sha = hashlib.sha256(k08_component).hexdigest()
        result.update({
            "hmac32_digest_D": digest.hex().upper(),
            "hmac32_seed_layout_match": layout_match,
            "derived_k08_component": k08_component.hex().upper(),
            "derived_k08_sha256": k08_sha,
            "k08_commitment_match": (
                layout_match and k08_sha == acceptance["slot_sha256"]["K08"]
            ),
        })
        try:
            phrase_seed = digest.decode("utf-8")
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
            "HMAC32_LAYOUT_MATCH", layout_match,
            "K08_SHA_MATCH", result["k08_commitment_match"],
            flush=True,
        )
        if result["k04_commitment_match"]:
            print("COMPLETE_K04_CANDIDATE", component.hex().upper(), flush=True)
        if result["k08_commitment_match"]:
            print("COMPLETE_K08_COMPONENT", k08_component.hex().upper(), flush=True)
        if result["k04_commitment_match"] and result["k08_commitment_match"]:
            result["interpretation"] = (
                "Both K04 and K08 components pass their original slot commitments "
                "under the conditional common CPython source model."
            )
        else:
            result["interpretation"] = (
                "Exact 132-packet CPython source fit, but one or both component "
                "commitments or the HMAC32 seed relation failed."
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
