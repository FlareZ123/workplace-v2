"""H-17: exact MT source-only test of independently consumed terminal metadata draws.

Read-only SFT. Selected copied ACK2 row129 and original K04 acceptance are withheld.
Requires standard-library Python and the existing Ag49 symbolic MT module.
"""
from __future__ import annotations
import hashlib
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, STARTS, get, untemper, words

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SPOOL = REPO / "resources" / "evidence" / "print" / "spool-reconstruction.log"


def observe(base, symbolic, packet, start):
    """Insert a complete 16-byte packet; returns exact source-bit contradiction count."""
    bad = 0
    for lane in range(4):
        native = untemper(int.from_bytes(packet[4 * lane:4 * lane + 4], "little"))
        for bit, vector in enumerate(get(symbolic, start + lane)):
            value = (native >> bit) & 1
            known = base.predict(vector)
            if known is not None:
                bad += known != value
            else:
                base.insert(vector, value)
    return bad


def prefix_basis(packets, symbolic):
    base = Basis()
    for i in range(129):
        assert observe(base, symbolic, packets[i], STARTS[i]) == 0, i
    assert base.rank == 15139, base.rank
    return base


def shifts(mask):
    starts = STARTS.copy()
    count = 0
    for i in range(129, 133):
        count += bool(mask & (1 << (i - 129)))
        starts[i] += count
    return starts


def heldout(base, symbolic, packets, starts):
    """Evaluate each retained terminal packet against the same frozen prefix."""
    detail = []
    for index in (130, 131, 132):
        contradictions = fixed = 0
        for lane in range(4):
            native = untemper(int.from_bytes(
                packets[index][4 * lane:4 * lane + 4], "little"))
            for bit, vector in enumerate(get(symbolic, starts[index] + lane)):
                known = base.predict(vector)
                if known is not None:
                    fixed += 1
                    contradictions += known != ((native >> bit) & 1)
        detail.append([contradictions, fixed])
    return detail


def synthetic_control(symbolic):
    """A genuinely seeded Python MT history with four independently skipped draws."""
    rng = random.Random(0xA341C1)
    from k04_p951_symbolic_basis import ORIGIN, LAST
    stream = [rng.getrandbits(32) for _ in range(LAST - ORIGIN + 1)]
    positions = shifts(15)
    packets = [
        b"".join(stream[positions[i] + j - ORIGIN].to_bytes(4, "little")
                 for j in range(4))
        for i in range(133)
    ]
    base = prefix_basis(packets, symbolic)
    for index in (130, 131, 132):
        assert observe(base, symbolic, packets[index], positions[index]) == 0
    assert sum(x[0] for x in heldout(prefix_basis(packets, symbolic),
                                    symbolic, packets, positions)) == 0
    return True


def main():
    raw = SPOOL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    packets = [bytes.fromhex(value.decode()) for value in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(STARTS) == 133
    symbolic = words()
    base = prefix_basis(packets, symbolic)
    outcomes = []
    for mask in range(16):
        positions = shifts(mask)
        detail = heldout(base, symbolic, packets, positions)
        total = sum(item[0] for item in detail)
        outcomes.append({
            "mask": format(mask, "04b"),
            "selected_stage_withheld": positions[129],
            "holdout_stages": positions[130:133],
            "contradictions": total,
            "frozen_prefix_bad_fixed": detail,
        })
        assert (total == 0) == (mask == 0), (mask, detail)
    # Baseline source model exact consistency; do not trust the disputed row129.
    baseline = prefix_basis(packets, symbolic)
    for index in (130, 131, 132):
        assert observe(baseline, symbolic, packets[index], STARTS[index]) == 0
    assert baseline.rank == 15365
    assert synthetic_control(symbolic)
    print(json.dumps({
        "source_pin_pass": True,
        "frozen_prefix_rank": base.rank,
        "unshifted_full_source_rank": baseline.rank,
        "synthetic_four_extra_draws_positive": True,
        "outcomes": outcomes,
    }, indent=2))


if __name__ == "__main__":
    main()
