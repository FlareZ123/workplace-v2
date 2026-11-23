"""K04 all-42 independent native chronology: seeded CPython short-key producer.

Use new all-42 original-source stage assignment, withholding selected row129.
Project original 528 full native words backwards through the first true MT
twist into 624 initialized register words, then use CPython init_by_array
key-residue compatibility to test genuine seed-key array lengths n=1..623
at all 624 actual startup output offsets 0..623.

A source-compatible short seed would permit complete selected coupon emission
once recovered. Negative results exclude only the specified chronology,
warmups and seed family, not the physical target.

Run: python agents/agent50/k04_all42_cpython_shortseed_sft.py
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent28"))
sys.path.insert(0, str(ROOT / "agents/agent11"))

from k04_cpython_real_output_offset_sft import Basis, words, mt, term_domains, consistent
from k04_all42_fullsource_alternative_sft import STAGES, SOURCE_SHA

U = 0xFFFFFFFF
assert len(STAGES) == 133 and STAGES[129] == 952


def projected_initial_state(offset: int, packets: list[bytes | None]):
    assert len(packets) == len(STAGES) == 133 and packets[129] is None
    expressions = words(offset)
    basis = Basis()
    for row, (packet, start) in enumerate(zip(packets, STAGES)):
        if row == 129:
            continue
        assert packet is not None and len(packet) == 16
        for lane in range(4):
            native = mt.untemper(int.from_bytes(packet[4*lane:4*lane+4], "little"))
            for bit, term in enumerate(expressions[624 + offset + start + lane]):
                basis.add(term, (native >> bit) & 1)
    assert len(basis.rows) == 15434, len(basis.rows)
    state = []
    for register_word in expressions[:624]:
        mask = value = 0
        for bit, expression in enumerate(register_word):
            known = basis.known(expression)
            if known is not None:
                mask |= 1 << bit
                value |= known << bit
        state.append((mask, value))
    return state


def planted(seed: int, offset: int):
    generator = random.Random(seed)
    initialized = generator.getstate()[1][:624]
    emitted = [generator.getrandbits(32) for _ in range(offset + STAGES[-1] + 4)]
    packets = [
        None if row == 129 else
        b"".join(emitted[offset + stage + lane].to_bytes(4,"little")
                 for lane in range(4))
        for row, stage in enumerate(STAGES)
    ]
    return initialized, packets


def main():
    positives = 0
    for n in (1, 4, 16, 128, 623):
        seed = sum(((0x1BADF00D + 31*i) & U) << (i*32) for i in range(n))
        for offset in (0, 5, 31, 623):
            actual, packets = planted(seed, offset)
            states = projected_initial_state(offset, packets)
            assert all(value == (mask & word)
                       for (mask, value), word in zip(states, actual))
            assert consistent(term_domains(states, 0), n)
            assert ((states[0][1] ^ 0x80000000) & states[0][0]) == 0
            positives += 1
    assert positives == 20
    print("SYNTHETIC_NATIVE_ALL42_SEEDED_PRODUCER", positives, "PASS", flush=True)

    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    lines = re.findall(
        rb"^(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)$",
        raw, re.M,
    )
    assert len(lines) == 133
    assert lines[129][:5] == (
        b"2026-10-03T18:02:00Z", b"PS-261003-0417", b"2", b"ACK", b"RECOVER"
    )
    # Disputed ACK2 payload is erased prior to hex parsing or source fitting.
    packets = [None if i == 129 else bytes.fromhex(line[5].decode())
               for i, line in enumerate(lines)]
    compatible = {n: [] for n in range(1, 624)}
    hist = {}
    for offset in range(624):
        states = projected_initial_state(offset, packets)
        if ((states[0][1] ^ 0x80000000) & states[0][0]) != 0:
            if offset % 64 == 0:
                print("ORIGINAL", offset, "CPYTHON_S0_CONTRADICTION", flush=True)
            continue
        domains = term_domains(states, 0)
        survivors = [n for n in compatible if consistent(domains, n)]
        hist[offset] = {"domains": len(domains), "first_n": min(survivors) if survivors else None}
        for n in survivors:
            compatible[n].append(offset)
        if offset % 64 == 0:
            print("ORIGINAL", offset, "SOURCE_KEY_TERMS", len(domains),
                  "SHORTEST_LENGTH", min(survivors) if survivors else None,
                  "SURVIVORS_N1_623", len(survivors), flush=True)
    summary = {
        "source": SOURCE_SHA,
        "selected_ACK2_payload_parsed": False,
        "stage_model": "alternative all42 native MT original-source exact chronology",
        "native_source_rank": 15434,
        "synthetic_seeded_positive": positives,
        "tested_real_output_offsets": "0..623",
        "tested_seed_key_lengths": "1..623",
        "live_offset_seedlen_pairs": sum(len(v) for v in compatible.values()),
        "shortest_surviving_seed_length": min(
            (n for n,v in compatible.items() if v), default=None
        ),
        "compatible_offsets_by_seedlen": {
            str(n): {"count": len(v), "first_offsets": v[:12]}
            for n,v in compatible.items() if v
        },
        "eligible_offsets": len(hist),
        "max_source_key_term_count": max((h["domains"] for h in hist.values()), default=0),
    }
    print("RESULT", json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
