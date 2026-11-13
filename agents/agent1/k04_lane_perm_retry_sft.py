#!/usr/bin/env python3
"""Source-only test of a fixed 16-bit-lane permutation/XOR retry transition.

Run from any directory after checkout:
    python agents/agent1/k04_lane_perm_retry_sft.py

The selected PS-261003-0417 ATTEMPT=2 STATE=ACK row is deliberately excluded
before parsing the spool log. The K04 commitment is consulted only if the
independent source-only endpoint test finds a complete model.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESOURCES = REPO / "resources"
SPOOL_PATH = RESOURCES / "evidence/print/spool-reconstruction.log"
ROUTE_PATH = RESOURCES / "evidence/recovery-routing.json"
ACCEPTANCE_PATH = RESOURCES / "acceptance.json"


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def permute_lanes(block: bytes, permutation: tuple[int, ...], swap_bytes: bool) -> bytes:
    """Permute eight 16-bit lanes, optionally reversing bytes in every lane."""
    lanes = [block[i * 2 : i * 2 + 2] for i in range(8)]
    if swap_bytes:
        lanes = [lane[::-1] for lane in lanes]
    return b"".join(lanes[i] for i in permutation)


def parse_source_rows() -> list[dict]:
    rows = []
    for line in SPOOL_PATH.read_text(encoding="utf-8").splitlines():
        fields = dict(re.findall(r"([A-Z_]+)=([^\s]+)", line))
        if not {"JOB", "ATTEMPT", "STATE", "CLASS", "DEST", "PAYLOAD"} <= fields.keys():
            continue
        # Do not parse or use the selected ACK2 payload at all.
        if (
            fields["JOB"] == "PS-261003-0417"
            and fields["ATTEMPT"] == "2"
            and fields["STATE"] == "ACK"
        ):
            continue
        rows.append(
            {
                "job": fields["JOB"],
                "attempt": int(fields["ATTEMPT"]),
                "state": fields["STATE"],
                "class": fields["CLASS"],
                "dest": fields["DEST"],
                "payload": bytes.fromhex(fields["PAYLOAD"]),
            }
        )
    return rows


def get_one(rows: list[dict], job: str, attempt: int, state: str, cls: str, dest: str) -> bytes:
    found = [
        r["payload"]
        for r in rows
        if (r["job"], r["attempt"], r["state"], r["class"], r["dest"])
        == (job, attempt, state, cls, dest)
    ]
    if len(found) != 1:
        raise RuntimeError(f"Expected one source row for {(job, attempt, state, cls, dest)}, found {len(found)}")
    if len(found[0]) != 16:
        raise RuntimeError("Expected 16-byte payload")
    return found[0]


def source_only_fits():
    rows = parse_source_rows()
    # The 0420 complete ACK transition trains F(x)=P(x) XOR c.
    train_a = get_one(rows, "PS-261003-0420", 1, "ACK", "STORES", "desk")
    train_b = get_one(rows, "PS-261003-0420", 2, "ACK", "RECOVER", "bench")
    # The two 0417 REQUESTED endpoints are an independent two-step holdout.
    held_a = get_one(rows, "PS-261003-0417", 1, "REQUESTED", "RECOVER", "bench")
    held_c = get_one(rows, "PS-261003-0417", 3, "REQUESTED", "RECOVER", "bench")

    fits = []
    models = 0
    for swap_bytes in (False, True):
        for permutation in itertools.permutations(range(8)):
            p_train_a = permute_lanes(train_a, permutation, swap_bytes)
            pad = xor(train_b, p_train_a)
            predicted_mid = xor(permute_lanes(held_a, permutation, swap_bytes), pad)
            predicted_c = xor(permute_lanes(predicted_mid, permutation, swap_bytes), pad)
            models += 1
            if predicted_c == held_c:
                fits.append((swap_bytes, permutation, pad, predicted_mid))
    return models, fits


def planted_positive_controls() -> int:
    """Check that the search recovers planted transitions with independent endpoints."""
    passed = 0
    for seed in range(16):
        rng = random.Random(seed)
        train_a = rng.randbytes(16)
        held_a = rng.randbytes(16)
        permutation = list(range(8))
        rng.shuffle(permutation)
        permutation = tuple(permutation)
        swap_bytes = bool(seed & 1)
        pad = rng.randbytes(16)

        def transition(x: bytes) -> bytes:
            return xor(permute_lanes(x, permutation, swap_bytes), pad)

        train_b = transition(train_a)
        held_mid = transition(held_a)
        held_c = transition(held_mid)
        recovered = []
        for swap in (False, True):
            for perm in itertools.permutations(range(8)):
                candidate_pad = xor(train_b, permute_lanes(train_a, perm, swap))
                middle = xor(permute_lanes(held_a, perm, swap), candidate_pad)
                endpoint = xor(permute_lanes(middle, perm, swap), candidate_pad)
                if endpoint == held_c:
                    recovered.append(middle)
        if held_mid in recovered:
            passed += 1
    return passed


def main() -> None:
    models, fits = source_only_fits()
    print("selected 0417 ACK2 excluded before parsing: yes")
    print("source-only model: F(x) = P_16bit_lanes(x) XOR fixed_128bit_pad")
    print(f"models tested: {models}")
    print(f"complete 0417 endpoint fits: {len(fits)}")

    # The commitment is not consulted unless the source-only holdout succeeds.
    if fits:
        route = json.loads(ROUTE_PATH.read_text(encoding="utf-8"))["K04"]
        target = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))["slot_sha256"]["K04"]
        mask = bytes.fromhex(route["masked_component"])
        for index, (swap, permutation, pad, predicted_mid) in enumerate(fits):
            candidate = xor(predicted_mid, mask)
            hit = hashlib.sha256(candidate).hexdigest() == target
            print(
                f"fit {index}: swap={swap}, permutation={permutation}, "
                f"predicted_ACK2={predicted_mid.hex().upper()}, "
                f"K04_candidate={candidate.hex().upper()}, commitment_hit={hit}"
            )

    print(f"planted positive controls: {planted_positive_controls()}/16")


if __name__ == "__main__":
    main()
