#!/usr/bin/env python3
"""Source-pinned p951 MT GF(2) quotient gate for promising negative stage windows.

The original selected row129 / PS-261003-0417 ACK2 is withheld before payload
parsing. All donor values are idealized oracles, not recovered historical bytes.
An original-source equation basis and a coefficient-only basis are both built.
No K04/K08 digest, mask, candidate, key or PDF content is used.

Run from the repository root:
    python agents/agent46/k04_negative_window_source_quotient_sft.py
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, STARTS, get, temper, untemper, words

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED_ROW = 129
TARGET = range(951, 955)


def clone(b):
    out = Basis()
    out.rows = b.rows.copy()
    out.rank = b.rank
    return out


def original_source():
    raw = (ROOT / "resources" / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines) == len(STARTS) == 133
    assert STARTS[SELECTED_ROW] == 951
    selected = lines[SELECTED_ROW]
    assert "JOB=PS-261003-0417" in selected
    assert "ATTEMPT=2" in selected and "STATE=ACK" in selected
    assert "CLASS=RECOVER" in selected
    state = words()
    structural = Basis()
    historical = Basis()
    intact_words = 0
    for row, line in enumerate(lines):
        if row == SELECTED_ROW:
            # Crucial: do not parse or use the disputed selected payload.
            continue
        match = re.search(r"(?:^|\\s)PAYLOAD=([0-9A-F]{32})(?=\\s|$)", line)
        assert match is not None, row
        payload = bytes.fromhex(match.group(1))
        for lane in range(4):
            native = untemper(int.from_bytes(payload[lane*4:lane*4+4], "little"))
            for j, vec in enumerate(get(state, STARTS[row] + lane)):
                historical.insert(vec, (native >> j) & 1)
                structural.insert(vec, 0)
            intact_words += 1
    assert intact_words == 528
    assert structural.rank == historical.rank == 15365
    return state, structural


def quotient(b, state):
    trial = clone(b)
    for p in TARGET:
        for vec in get(state, p):
            trial.insert(vec, 0)
    return trial.rank - b.rank


def grant_native(b, state, start, end):
    trial = clone(b)
    for p in range(start, end + 1):
        for vec in get(state, p):
            trial.insert(vec, 0)
    return trial


def grant_fields(b, state, starts, order="ATELC"):
    widths = {"A":13, "T":9, "E":6, "L":3, "C":32}
    trial = clone(b)
    for start in starts:
        for offset, field in enumerate(order):
            for vec in temper(get(state, start + offset))[32-widths[field]:]:
                trial.insert(vec, 0)
    return trial


def main():
    state, source = original_source()
    assert quotient(source, state) == 128
    print("ORIGINAL_SOURCE_RANK", source.rank)
    print("SELECTED_TARGET_QUOTIENT", quotient(source, state))

    first = grant_native(source, state, -861, -857)
    second = grant_native(source, state, -465, -461)
    both = grant_native(first, state, -465, -461)
    assert (first.rank-source.rank, second.rank-source.rank,
            both.rank-source.rank) == (160, 160, 287)
    assert [quotient(b, state) for b in (first, second, both)] == [128]*3
    print("ORACLE_NATIVE_NEG861_857", first.rank-source.rank, quotient(first, state))
    print("ORACLE_NATIVE_NEG465_461", second.rank-source.rank, quotient(second, state))
    print("ORACLE_NATIVE_BOTH", both.rank-source.rank, quotient(both, state))

    for order in ("ATELC", "AETLC", "CATEL", "TELAC"):
        accepted = grant_fields(source, state, [-861, -465], order)
        assert quotient(accepted, state) == 128
        print("ACCEPTED_FIELD_ORACLE", order, accepted.rank-source.rank,
              quotient(accepted, state))

    control = grant_native(source, state, -859, -859)
    assert quotient(control, state) == 128
    print("SINGLE_FULL_CONTROL_NEG859", control.rank-source.rank, quotient(control, state))

    # Source-independent rank-positive regression: the original published
    # fullword printer-gap donor pair IS sufficient under this p951 model.
    positive = grant_native(source, state, 328, 334)
    positive = grant_native(positive, state, 721, 728)
    assert quotient(positive, state) == 0
    print("POSITIVE_GAPS_328_334_AND_721_728", positive.rank-source.rank,
          quotient(positive, state))
    print("K04_PHYSICAL_BITS_AUTHENTICATED", 0)


if __name__ == "__main__":
    main()
