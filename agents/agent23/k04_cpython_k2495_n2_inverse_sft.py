"""K04 CPython genuine n=2 seed inverse at prior-output offset 2495.

Run: python agents/agent23/k04_cpython_k2495_n2_inverse_sft.py [start stop].
All authentic source masks exclude selected row129 before fitting.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
U = 0xFFFFFFFF
F1 = 1664525
F2 = 1566083941
INVERSE_F1 = pow(F1, -1, 1 << 32)
INVERSE_F2 = pow(F2, -1, 1 << 32)
ORIGINAL = {
    4: (0x8000001F, 0x00000011),
    5: (U, 0xE403BB7D),
    6: (U, 0x1F7B301F),
    7: (0x09CC1C00, 0x008C1000),
    14: (0x000000FF, 0x000000B6),
    15: (0x5398BA7D, 0x4010A820),
    16: (0x01800800, 0x00000800),
}

def f(multiplier: int, x: int) -> int:
    return (multiplier * (x ^ (x >> 30))) & U

def inverse(multiplier_inverse: int, y: int) -> int:
    z = (y * multiplier_inverse) & U
    return z ^ (z >> 30)

def genuine_controls() -> None:
    g = [19650218]
    for i in range(1, 17):
        g.append((1812433253 * (g[-1] ^ (g[-1] >> 30)) + i) & U)
    seeds = ((0x12345678, 0x23456789), (1, 1), (U, U),
             (0x00001FC3, 0x00001092), (0, 0x80000000))
    for k0, k1 in seeds:
        state = random.Random((k1 << 32) | k0).getstate()[1][:624]
        a6 = (((state[6] + 6) & U) ^ f(F2, state[5]))
        firstpass = ((g[1] ^ f(F1, g[0])) + k0) & U
        for i in range(2, 7):
            firstpass = ((g[i] ^ f(F1, firstpass))
                         + (k0 if i & 1 else k1 + 1)) & U
        assert a6 == firstpass
        a5 = inverse(INVERSE_F1, g[6] ^ ((a6 - k1 - 1) & U))
        s4 = inverse(INVERSE_F2, a5 ^ ((state[5] + 5) & U))
        assert s4 == state[4]
        a7 = ((g[7] ^ f(F1, a6)) + k0) & U
        s7 = ((a7 ^ f(F2, state[6])) - 7) & U
        assert s7 == state[7]
    print("GENUINE_CPYTHON_N2_ALGEBRAIC_SOURCE_CONTROLS=5/5 PASS")

def source_masks():
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    packets = [bytes.fromhex(v.decode("ascii"))
               for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(mt.STARTS) == 133 and mt.STARTS[129] == 951
    source = source_states(2495, packets)
    for index, expected in ORIGINAL.items():
        assert source[index] == expected, (index, source[index], expected)
    print("SOURCE_132_SELECTED_WITHHELD_RANK15365_MASKS=PASS")
    return source, packets

def main():
    start = int(sys.argv[1]) if len(sys.argv) >= 2 else 0
    stop = int(sys.argv[2]) if len(sys.argv) >= 3 else 65536
    assert 0 <= start < stop <= (1 << 32)
    source, packets = source_masks()
    genuine_controls()
    src = ROOT / "agents/agent23/k04_cpython_k2495_n2_inverse.cpp"
    with tempfile.TemporaryDirectory(prefix="h17_k2495_n2_") as folder:
        binary = Path(folder) / ("k2495.exe" if os.name == "nt" else "k2495")
        subprocess.run(["g++", "-O3", "-std=c++17", "-fopenmp",
                        str(src), "-o", str(binary)], check=True)
        for k0, k1 in ((0x12345678, 0x23456789), (1, 1), (U, U),
                       (8131, 4242), (0, 0x80000000)):
            done = subprocess.run([str(binary), "synthetic", f"{k0:08X}",
                                   f"{k1:08X}"], check=True, capture_output=True,
                                  text=True)
            assert "refound=1" in done.stdout, done.stdout
        print("GENUINE_CPYTHON_TWO_WORD_COMPLETE_INVERSE=5/5 PASS")
        outcome = subprocess.run([str(binary), str(start), str(stop)],
                                 check=True, capture_output=True, text=True,
                                 env={**os.environ, "OMP_NUM_THREADS":
                                      os.environ.get("OMP_NUM_THREADS", "4")})
    print(outcome.stdout.strip())
    survivors = re.findall(r"SOURCE_FORWARD_SURVIVOR k0=([0-9A-F]{8}) k1=([0-9A-F]{8})",
                           outcome.stdout)
    assert outcome.stdout.count("K2495_N2_SHARD range=") == 1
    assert f"scanned={stop-start} " in outcome.stdout
    for key0, key1 in survivors:
        k0, k1 = int(key0, 16), int(key1, 16)
        rng = random.Random((k1 << 32) | k0)
        state = rng.getstate()[1][:624]
        full_source = all((state[i] & mask) == value
                          for i, (mask, value) in enumerate(source))
        print(f"FORWARD_SURVIVOR k0={key0} k1={key1} full132source={full_source}")
        if not full_source:
            continue
        draws = [rng.getrandbits(32) for _ in range(2495 + 975)]
        for row, (packet, position) in enumerate(zip(packets, mt.STARTS)):
            if row == 129:
                continue
            predicted = b"".join(draws[2495 + position + i].to_bytes(4, "little")
                                 for i in range(4))
            assert predicted == packet, (row, position)
        selected = b"".join(draws[2495 + 951 + i].to_bytes(4, "little")
                            for i in range(4))
        routing = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text())
        mask = bytes.fromhex(routing["K04"]["masked_component"])
        key = bytes(x ^ y for x, y in zip(selected, mask))
        targets = json.loads((ROOT / "resources/acceptance.json").read_text())
        passed = hashlib.sha256(key).hexdigest() == targets["slot_sha256"]["K04"]
        print(f"FULL_ORIGINAL_SOURCE_MATCH k0={key0} k1={key1} "
              f"selectedcoupon={selected.hex().upper()} "
              f"candidateK04={key.hex().upper()} officialK04pass={passed}")
    if not survivors:
        print("SHARD_NO_SOURCE_FORWARD_SURVIVORS; conditional K04 model only")

if __name__ == "__main__":
    main()
