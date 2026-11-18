"""Evaluate a proposed printer MT stage map and search complete K04 coupon candidates.

The original selected ACK2 payload is not decoded. The history is an unverified
single-native-MT physical-coupon assumption; real acceptance uses unchanged
resources/acceptance.json and does not modify original files.

Run from repository: python agents/agent27/k04_mt_hypothesis_coupon_search.py
Optionally pass a JSON stage-map path, shaped {"origin":-1100, "starts":[133 ints]}.
"""

import hashlib
import json
from pathlib import Path
import re
import sys

from k04_mt_knownstage_holdout_rank_sft import SOURCE_SHA256, linear_mt_vectors, untemper
from k04_mt_knownstage_affine_completion_sft import (
    MASK, LinearModel, pack_tempered, target_affine, xor,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "resources/evidence/print/spool-reconstruction.log"
ACCEPTANCE = REPO_ROOT / "resources/acceptance.json"


def spool_values():
    content = SOURCE.read_bytes()
    assert hashlib.sha256(content).hexdigest() == SOURCE_SHA256
    records = [line for line in content.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(records) == 133
    packets = []
    selected = []
    for index, line in enumerate(records):
        match = re.match(
            r"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+)(?=\s|$)",
            line,
        )
        assert match is not None
        stamp, job, attempt, state, group = match.groups()
        is_selected = (
            job == "PS-261003-0417" and attempt == "2" and state == "ACK"
            and group == "RECOVER" and stamp == "2026-10-03T18:02:00Z"
        )
        if is_selected:
            selected.append(index)
            packets.append(None)  # Critical: do not extract or decode selected ACK payload.
            continue
        payload = re.search(r"\bPAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
        assert payload is not None
        raw = bytes.fromhex(payload.group(1))
        packets.append(tuple(untemper(int.from_bytes(raw[4 * k:4 * k + 4], "little")) for k in range(4)))
    assert selected == [129]
    return packets


def stage_map(filename=None):
    if filename is None:
        sys.path.insert(0, str(REPO_ROOT / "agents/agent49"))
        from k04_p951_symbolic_basis import ORIGIN, STARTS
        origin, starts = ORIGIN, STARTS
    else:
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
        origin, starts = data["origin"], data["starts"]
    assert isinstance(origin, int) and len(starts) == 133
    assert all(isinstance(s, int) and not isinstance(s, bool) for s in starts)
    assert all(starts[i + 1] >= starts[i] + 4 for i in range(132))
    assert origin <= starts[0]
    shifted = [s - origin for s in starts]
    return origin, starts, shifted


def main(filename=None, max_rank=18):
    packets = spool_values()
    origin, starts, shifted = stage_map(filename)
    symbolic = linear_mt_vectors(shifted[-1] + 4)
    basis = LinearModel()
    for row, (packet, s) in enumerate(zip(packets, shifted)):
        if row == 129:
            assert packet is None
            continue
        for lane, word in enumerate(packet):
            for bit, vector in enumerate(symbolic[s + lane]):
                basis.add(vector, (word >> bit) & 1)
    base, directions = target_affine(basis, symbolic, shifted[129])
    rank = len(directions)
    print("SOURCE_SHA256", SOURCE_SHA256, "historical_map", filename or "agent49-p951")
    print("source_basis_rank", len(basis.basis), "dependent_observed_bits", basis.dependent_rows,
          "origin", origin, "selected_start", starts[129], "residual_bits", rank)
    if rank > max_rank:
        print("NO_SEARCH: unbounded candidate space (2^" + str(rank) + ") exceeds max_rank=" + str(max_rank))
        print("K04_NOT_RECOVERED")
        return None
    commitments = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))["slot_sha256"]
    k04_sha = commitments["K04"]
    matches = []
    current = base
    prev_gray = 0
    for n in range(1 << rank):
        gray = n ^ (n >> 1)
        if n:
            changed = (gray ^ prev_gray).bit_length() - 1
            current ^= directions[changed]
        component = xor(pack_tempered(current), MASK)
        if hashlib.sha256(component).hexdigest() == k04_sha:
            matches.append(component.hex().upper())
        prev_gray = gray
    print("complete_original_commitment_checks", 1 << rank, "exact_hits", len(matches))
    for component in matches:
        print("K04_ORIGINAL_COMMITMENT_HIT", component)
    if not matches:
        print("K04_NOT_RECOVERED")
    return matches


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
