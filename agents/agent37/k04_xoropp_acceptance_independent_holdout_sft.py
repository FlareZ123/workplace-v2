#!/usr/bin/env python3
"""Source-free synthetic K04 coupon reducer: acceptance is independent of retry-3 replay.

Historical source and K04 target are NEVER imported or read. A complete predicted
missing coupon is tested against a synthetic SHA256 commitment for EVERY firstpair
state. A separately withheld later packet is reported independently; it cannot
prefilter commitment candidates, since retry-3 producer continuity is unproven.

The two genuine synthetic states collide on both complete first-packet words AND
all 12 search-anchor bits. Z3 enumerates both exactly and returns terminal UNSAT.
Requires system libz3.so.4 and Agent27's existing source-free circuit.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent37.k04_xoropp_samebucket_collision_sft import (
    WITNESSES, anchor, independent_forward, query_models,
)


def packet_bytes(words: tuple[int, int], endian: str, order: str) -> bytes:
    assert endian in ("big", "little") and order in ("ab", "ba")
    pair = list(words)
    if order == "ba":
        pair.reverse()
    return b"".join(word.to_bytes(8, endian) for word in pair)


def aggregate_only(
    states: list[tuple[int, int]],
    first: tuple[int, int],
    later: tuple[int, int],
    route_mask: bytes,
    acceptance_sha256: bytes,
    endian: str,
    order: str,
) -> tuple[int, int, int]:
    """Return commitment hits, whole-later-packet replays, and both, separately.

    All complete first-packet SAT states are evaluated, even when the
    independently retained later packet is inconsistent with the state.
    No state, coupon, component or source bytes are output.
    """
    assert len(route_mask) == 16 and len(acceptance_sha256) == 32
    accepted, replays, joint = 0, 0, 0
    for state in states:
        outputs = independent_forward(*state)
        assert tuple(outputs[:2]) == tuple(first)
        middle = packet_bytes(tuple(outputs[2:4]), endian, order)
        component = bytes(x ^ y for x, y in zip(middle, route_mask))
        a = hashlib.sha256(component).digest() == acceptance_sha256
        h = tuple(outputs[4:6]) == tuple(later)
        accepted += int(a)
        replays += int(h)
        joint += int(a and h)
    return accepted, replays, joint


def main() -> None:
    source_only = [independent_forward(*state) for state in WITNESSES]
    first = tuple(source_only[0][:2])
    assert tuple(source_only[1][:2]) == first
    assert tuple(source_only[0][2:4]) != tuple(source_only[1][2:4])
    assert tuple(source_only[0][4:6]) != tuple(source_only[1][4:6])
    assert anchor(WITNESSES[0][0]) == anchor(WITNESSES[1][0])
    states, terminal = query_models(list(first), anchor(WITNESSES[0][0]))
    assert terminal == "unsat" and len(states) == 2
    assert set(states) == set(WITNESSES)

    # This is a synthetic route XOR mask, NOT an original H-17 mask.
    mask = bytes((53 + 17 * i) & 255 for i in range(16))
    controls = 0
    distinct_mismatch_acceptances = 0
    for endian in ("big", "little"):
        for order in ("ab", "ba"):
            for actual in (0, 1):
                middle = packet_bytes(tuple(source_only[actual][2:4]), endian, order)
                synthetic_component = bytes(a ^ b for a, b in zip(middle, mask))
                digest = hashlib.sha256(synthetic_component).digest()
                for later_index in (0, 1):
                    got = aggregate_only(
                        states, first, tuple(source_only[later_index][4:6]),
                        mask, digest, endian, order,
                    )
                    expected = (1, 1, int(actual == later_index))
                    assert got == expected, (endian, order, actual, later_index, got)
                    distinct_mismatch_acceptances += int(actual != later_index)
                    controls += 1
                # Even a fully poisoned later packet cannot veto a complete
                # synthetic coupon that passes the independent commitment.
                poison = (source_only[0][4] ^ 1, source_only[0][5])
                got = aggregate_only(states, first, poison, mask, digest, endian, order)
                assert got == (1, 0, 0), (endian, order, actual, got)
                controls += 1

    assert controls == 24 and distinct_mismatch_acceptances == 8
    print({
        "source_free": True,
        "same_firstpair_and_same_P12_cube": True,
        "exact_cube_models": len(states),
        "terminal_model_blocker": terminal,
        "serializers": 4,
        "whole_coupon_commitment_controls": controls,
        "correct_commitment_with_conflicting_later_packet": distinct_mismatch_acceptances,
        "commitment_target_and_holdout_independently_evaluated": True,
        "original_K04_component_recovered": False,
    })


if __name__ == "__main__":
    main()
