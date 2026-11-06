"""K04 k2496: source-exact CPython S7..S623 forward corridor, no K04 target.

Original source projection excludes row129 before GF(2) fitting; uses Agent28's
native MT source model and Agent1's real CPython initializer. No generator
family is presumed historically authenticated.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent28"))
from k04_cpython_real_output_offset_sft import source_states, mt

sys.path.insert(0, str(ROOT / "agents/agent1"))
from k04_cpython_initarray_wrap_sft import direct_initialized, U, F2, t

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
OFFSET = 2496
POSITIONS = (8, 15, 16, 17, 26, 27, 40, 41, 83)
PINNED = {
    6: (U, 0xE403BB7D),
    7: (U, 0x1F7B301F),
    8: (0x09CC1C00, 0x008C1000),
    15: (0x000000FF, 0x000000B6),
    16: (0x5398BA7D, 0x4010A820),
    17: (0x01800800, 0x00000800),
}


def original_source():
    spool = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    packets = [bytes.fromhex(v.decode()) for v in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(mt.STARTS) == 133
    assert mt.STARTS[129] == 951
    masks = source_states(OFFSET, packets)
    assert sum(mask.bit_count() for mask, value in masks) == 711
    for index, expected in PINNED.items():
        assert masks[index] == expected, (index, masks[index])
    return masks


def synthetic_controls():
    passed = 0
    for n in (1, 2, 3, 4, 5, 8, 16):
        for trial in range(12):
            keys = [((0x12345678 + j*0x30158DA + trial*0x4F89D7) & U)
                    for j in range(n)]
            a, b1, real = direct_initialized(keys)
            a7 = (((real[7] + 7) & U) ^ (F2*t(real[6]) & U))
            assert a7 == a[7]
            previous = real[7]
            for index in range(8, 624):
                previous = ((a[index] ^ (F2*t(previous))) - index) & U
                assert previous == real[index], (n, trial, index)
            passed += 1
    assert passed == 84
    print("GENUINE_CPYTHON_FULL_S7_TO_S623_CORRIDOR=84/84 PASS")


if __name__ == "__main__":
    synthetic_controls()
    masks = original_source()
    print("ORIGINAL_SOURCE_INITIAL_REGISTER_RANK=15365; KNOWN_BITS=711")
    for index in POSITIONS:
        mask, value = masks[index]
        print(f"S{index}_MASK={mask:08X} S{index}_VALUE={value:08X} BITS={mask.bit_count()}")
    print("ORIGINAL_SOURCE_SELECTED_ROW129_EXCLUDED; K04 K08 STILL MISSING")
