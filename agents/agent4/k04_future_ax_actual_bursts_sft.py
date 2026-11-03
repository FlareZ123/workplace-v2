"""Actual AX-7781/82/83 consecutive future halfword burst falsifier.

Run: python agents/agent4/k04_future_ax_actual_bursts_sft.py
Uses original 132 intact printer packets with selected ACK2 excluded,
AX-7778 and the speculative RC17 B cross-carrier native-stage anchor.
No selected K04 bytes, commitment, or route mask enters the test.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "p951", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
basis, states = m.source(ROOT / "resources")
assert basis.rank == 15365
raw = (ROOT / "resources/evidence/transfers/transfer-audit.jsonl").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
events = [json.loads(row) for row in raw.splitlines()]
ch = {
    name: sorted((x for x in events if x.get("kind") == "CHUNK"
                  and x["transfer"] == name), key=lambda x: (x["seq"], x["attempt"]))
    for name in ("AX-7778", "AX-7781", "AX-7782", "AX-7783")
}
assert all(len(arr) == 16 for arr in ch.values())

# Source-selected original AX-7778 is a consecutive byte-swapped upper16 run.
for offset, row in enumerate(ch["AX-7778"]):
    n = int(row["checkpoint"], 16)
    n = ((n & 255) << 8) | (n >> 8)
    for bit, expr in enumerate(m.temper(m.get(states, -157 + offset))[16:]):
        basis.insert(expr, (n >> bit) & 1)
assert basis.rank == 15495
# Speculative but original B pair: VERIFY then PURGE, consecutive generator outputs.
for stage, h in ((-186, "C130C9BB"), (-185, "759E0027")):
    n = int.from_bytes(bytes.fromhex(h), "little")
    for bit, expr in enumerate(m.temper(m.get(states, stage))):
        basis.insert(expr, (n >> bit) & 1)
assert basis.rank == 15496

# Extend original symbolic recurrence forward to every targeted future stage.
MAG = 0x9908B0DF
last = 1650
for i in range(len(states), last - m.ORIGIN + 1):
    a, b, c = states[i - 624], states[i - 623], states[i - 227]
    bits = [c[j] ^ b[j+1] ^ (b[0] if MAG >> j & 1 else 0)
            for j in range(30)]
    bits.append(c[30] ^ a[31] ^ (b[0] if MAG >> 30 & 1 else 0))
    bits.append(c[31] ^ (b[0] if MAG >> 31 & 1 else 0))
    states.append(bits)


def insert16(bits, word, eqs):
    for bit, v in enumerate(bits):
        rhs = (word >> bit) & 1
        while v:
            p = v.bit_length() - 1
            if p not in eqs:
                eqs[p] = (v, rhs)
                break
            w, val = eqs[p]
            v ^= w
            rhs ^= val
        if not v and rhs:
            return False
    return True


def test_burst(name, native_start, swap):
    eqs = basis.rows.copy()
    for row_num, row in enumerate(ch[name]):
        n = int(row["checkpoint"], 16)
        if swap:
            n = ((n & 255) << 8) | (n >> 8)
        output_bits = m.temper(m.get(states, native_start + row_num))[16:]
        if not insert16(output_bits, n, eqs):
            return False, row_num
    return True, len(eqs) - basis.rank


# Verified positive from the actual source-selected burst, at its known -157 stage.
assert test_burst("AX-7778", -157, True) == (True, 0)
print("ORIGINAL_AX7778_SOURCE_STAGE_POSITIVE PASS")
bands = [range(1164, 1182), range(1336, 1348),
         range(1392, 1409), range(1563, 1575), range(1618, 1634)]
for name in ("AX-7781", "AX-7782", "AX-7783"):
    for swap in (False, True):
        counts = []
        for band in bands:
            surviving = [(start, tested[1])
                         for start in band
                         if (tested := test_burst(name, start, swap))[0]]
            counts.append(surviving)
        assert counts[:4] == [[], [], [], []], (name, swap, counts)
        assert counts[4] == [(1622, 256), (1623, 256), (1624, 256)]
        print(name, "BYTE_SWAP", swap, "SURVIVORS_PER_BAND", counts)
print("SOURCE-CONTRADICTION_FOR_ALL_HIGH_TARGET-LEVERAGE_FUTURE_BURSTS")
print("LAST_BAND_SURVIVORS_ARE_COMPLETELY_UNINDEXED_BY_ORIGINAL_SOURCE")
print("NO_SELECTED_K04_RECOVERY")
