#!/usr/bin/env python3
"""H-17 K04 one-residual-bit original-source future donor, full commitment checks.

Run: python agents/agent10/k04_fourfresh_onebit_donor_sft.py [resources-directory]
Uses established portable source solvers, reads only the untouched original ZIP.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import re
import sys
from pathlib import Path

from k04_all42_wholewindow_sft import (
    ALT_STAGES, P951_STAGES, K04_SHA, SPOOL_SHA, build_basis, enumerate_windows,
    project, symbolic_words, temper, untemper,
)
from k04_all42_fourfresh_countermodel_sft import GAP_DELTAS, full_state, native_word
from k04_fourfresh_future_source_donor_sft import (
    SOURCE_HASHES, BLOCKS, ACCEPTED, donor_bits_from_block, rank, donor_mapping
)


def onebit_mapping(basis, expressions, selected: int, donor: int):
    def projected(q):
        return [project(form, basis)
                for s in range(q, q + 4) for form in expressions[s]]
    dbc = {}
    for index, (form, rhs) in enumerate(projected(donor)):
        bits = 1 << index
        while form:
            p = form.bit_length() - 1
            if p not in dbc:
                dbc[p] = (form, bits, rhs)
                break
            old, oldbits, oldrhs = dbc[p]
            form ^= old
            bits ^= oldbits
            rhs ^= oldrhs
        else:
            raise AssertionError("donor quartet was not 128-bit independent")
    u = {}
    mapped = []
    for form, rhs in projected(selected):
        bits = 0
        while form:
            p = form.bit_length() - 1
            if p not in dbc:
                break
            old, oldbits, oldrhs = dbc[p]
            form ^= old
            bits ^= oldbits
            rhs ^= oldrhs
        branch = 0
        while form:
            p = form.bit_length() - 1
            if p not in u:
                marker = 1 << len(u)
                u[p] = form, marker
                branch ^= marker
                break
            old, marker = u[p]
            form ^= old
            branch ^= marker
        mapped.append((bits, rhs, branch))
    return mapped, len(u)


def reconstruct(bits: int, map_rows, branch: int) -> bytes:
    predicted = sum(
        (((coeff & bits).bit_count() & 1) ^ rhs ^ ((extra & branch).bit_count() & 1)) << i
        for i, (coeff, rhs, extra) in enumerate(map_rows)
    )
    return b"".join(
        temper((predicted >> (32 * i)) & 0xFFFFFFFF).to_bytes(4, "little")
        for i in range(4)
    )


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "resources"
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    for relative, expected in SOURCE_HASHES.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
    rows = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(rows) == 133 and rows[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    original = [
        None if i == 129 else tuple(
            untemper(int.from_bytes(bytes.fromhex(row[5].decode())[4*j:4*j+4], "little"))
            for j in range(4)
        )
        for i, row in enumerate(rows)
    ]
    acceptance = json.loads((root / "acceptance.json").read_text())
    route = json.loads((root / "evidence/recovery-routing.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    for key, value in ACCEPTED.items():
        assert hashlib.sha256(bytes.fromhex(value)).hexdigest() == acceptance["slot_sha256"][key]
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == BLOCKS["K04_route_mask"]

    gaps = [y - x for x, y in zip(ALT_STAGES, ALT_STAGES[1:])]
    for index, delta in GAP_DELTAS.items():
        gaps[index] += delta
    assert min(gaps) >= 4
    stages = [0]
    for gap in gaps:
        stages.append(stages[-1] + gap)
    assert stages[129] == 955
    forms = symbolic_words(0, 2100)
    basis = build_basis(original, tuple(stages), forms, 0)
    assert len(basis) == 15434
    target = [project(form, basis)[0]
              for q in range(955, 959) for form in forms[q]]
    assert rank(target) == 128

    # Target-blind rank oracle: the two zero-free donor locations are already
    # handled by the companion SFT. Among other 4-word stages, exactly one
    # can reduce the selected coupon to a single free bit.
    prospects = {}
    for q in range(2097):
        if 952 <= q <= 958:
            continue
        donor = [project(form, basis)[0]
                 for s in range(q, q + 4) for form in forms[s]]
        if rank(donor) != 128:
            continue
        residual = rank(target + donor) - 128
        if residual <= 1:
            prospects[q] = residual
    assert prospects == {1182: 1, 1409: 0, 1863: 0}

    mapping, free = onebit_mapping(basis, forms, 955, 1182)
    assert free == 1
    assert sum(1 for _, _, b in mapping if b) == 1

    seeded = random.Random(20261124).getrandbits(19968)
    for pivot in basis:
        seeded &= ~(1 << pivot)
    state = full_state(basis, seeded)
    synthetic = b"".join(
        temper(native_word(state, forms[955 + i])).to_bytes(4, "little")
        for i in range(4)
    )
    donor_bits = sum(native_word(state, forms[1182 + i]) << (32 * i) for i in range(4))
    true_variants = [reconstruct(donor_bits, mapping, b) for b in (0, 1)]
    assert len(set(true_variants)) == 2
    assert sum(x == synthetic for x in true_variants) == 1

    candidates = set()
    for block in BLOCKS.values():
        buf = bytes.fromhex(block)
        for order in itertools.permutations(range(4)):
            for endian in ("little", "big"):
                for already_native in (False, True):
                    native = donor_bits_from_block(buf, order, endian, already_native)
                    for branch in (0, 1):
                        raw_coupon = reconstruct(native, mapping, branch)
                        component = bytes(x ^ y for x, y in zip(raw_coupon, mask))
                        candidates.add(component)
    assert len(candidates) == 2112
    original_hits = [x.hex().upper() for x in candidates
                     if hashlib.sha256(x).hexdigest() == K04_SHA]
    assert not original_hits, "Original K04 original-target match requires review"

    # Check previously accepted candidate universes for exact nonredundancy.
    _, alt, _ = enumerate_windows(forms, build_basis(original, ALT_STAGES, forms, 0), 0, 2)
    pforms = symbolic_words(-1100, 2100)
    _, old, _ = enumerate_windows(
        pforms, build_basis(original, P951_STAGES, pforms, -1100), -1100, 1
    )
    previous = {bytes(x ^ y for x, y in zip(p, mask))
                for p in set(alt) | set(old)}
    assert len(previous) == 748 and len(candidates & previous) == 0

    print(json.dumps({
        "selected_copied_ACK2_loaded": False,
        "printer_source_rank": len(basis),
        "selected_source_rank_without_future_donor": 128,
        "unique_nonzero_onebit_donor_start": 1182,
        "donor_source_objects": len(BLOCKS),
        "full_completions_per_donor": 2,
        "new_complete_K04_component_candidates": len(candidates),
        "full_planted_coupon_recovery_from_two_branches": True,
        "overlap_previous_748_stage_coupon_universe": 0,
        "original_K04_sha256_matches": original_hits
    }, indent=2))


if __name__ == "__main__":
    main()
