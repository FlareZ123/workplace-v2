"""Conditional original-source MT halfword DP for four AX transfer chains.
The selected printer job ACK2 is excluded. Four source order layouts and both
endiannesses, MT low16/high16, and 1..20-draw irregular monotonic gaps.
A genuine original-source positive (AX-7778) must score 122 fixed printer bits.
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent49"))
from k04_p951_symbolic_basis import ORIGIN, MAG, source, temper

LAST = 1800
basis, states = source(ROOT / "resources")
assert basis.rank == 15365
for i in range(len(states), LAST - ORIGIN + 1):
    t = i - 624
    states.append([
        states[t + 397][bit]
        ^ (states[t][31] if bit == 30 else
           (states[t + 1][bit + 1] if bit < 30 else 0))
        ^ (states[t + 1][0] if (MAG >> bit) & 1 else 0)
        for bit in range(32)
    ])

halves = {16: {}, 0: {}}
for stage in range(ORIGIN, LAST + 1):
    bits = temper(states[stage - ORIGIN])
    for shift in (0, 16):
        mask = value = 0
        for bit, vector in enumerate(bits[shift:shift + 16]):
            predicted = basis.predict(vector)
            if predicted is not None:
                mask |= 1 << bit
                value |= predicted << bit
        halves[shift][stage] = mask, value

original = [
    json.loads(line)
    for line in (ROOT / "resources/evidence/transfers/transfer-audit.jsonl").read_text().splitlines()
]
checkpoint = collections.defaultdict(dict)
for row in original:
    if row["kind"] == "CHUNK":
        checkpoint[row["transfer"]][(row["seq"], row["attempt"])] = row["checkpoint"]
layouts = {
    "seq_attempt": [(seq, attempt) for seq in range(8) for attempt in (1, 2)],
    "attempt_seq": [(seq, attempt) for attempt in (1, 2) for seq in range(8)],
    "attempt1": [(seq, 1) for seq in range(8)],
    "attempt2": [(seq, 2) for seq in range(8)],
}

def max_exact_agreement(values, source_half):
    previous = {
        stage: (mask.bit_count(), (stage,))
        for stage, (mask, value) in source_half.items()
        if (values[0] ^ value) & mask == 0
    }
    for index, checkpoint_value in enumerate(values[1:], 1):
        next_states = {}
        for stage in range(ORIGIN + index, LAST + 1):
            mask, value = source_half[stage]
            if (checkpoint_value ^ value) & mask:
                continue
            donors = [
                previous[prior]
                for prior in range(stage - 20, stage)
                if prior in previous
            ]
            if donors:
                score, chain = max(donors, key=lambda v: v[0])
                next_states[stage] = (score + mask.bit_count(), chain + (stage,))
        previous = next_states
        if not previous:
            return None
    return max(previous.values(), key=lambda v: v[0])

expected = {
    "AX-7778": 122, "AX-7781": 35,
    "AX-7782": 33, "AX-7783": 36,
}
for transfer, expected_score in expected.items():
    alternatives = []
    for shift in (0, 16):
        for endian in ("little", "big"):
            for name, layout in layouts.items():
                checkpoints = [
                    int.from_bytes(bytes.fromhex(checkpoint[transfer][pair]), endian)
                    for pair in layout
                ]
                best = max_exact_agreement(checkpoints, halves[shift])
                if best:
                    alternatives.append((best[0], shift, endian, name, best[1]))
    strongest = max(alternatives)
    print(transfer, "best_fixed_bits", strongest[0], "halfword", strongest[1],
          "endian", strongest[2], "layout", strongest[3],
          "native_indices", strongest[4])
    assert strongest[0] == expected_score, (transfer, strongest[0], expected_score)
assert max(expected[name] for name in ("AX-7781", "AX-7782", "AX-7783")) < 40
print("SOURCE_PINNED_IRREGULAR_AX_DP_PASS; K04 K08 unresolved")
