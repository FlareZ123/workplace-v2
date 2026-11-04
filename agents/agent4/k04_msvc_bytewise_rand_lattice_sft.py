"""Original H17 MSVC rand()&255 producer, exact lattice source negative.

Requires SymPy and companion k04_java_bytewise_lcg_lattice_sft.py,
which supplies the complete integer-lattice enumeration algorithm.

MSVC/UCRT's internal 32-bit state is (state*214013+2531011) mod 2^32;
rand() yields (state>>16)&32767. Truncating rand() to uint8 extracts
(state>>16)&255: the top eight bits of the state *modulo 2^24*.
Thus exact recovery needs only a 24-bit modular LCG, not all 2^32 seeds.
"""
from hashlib import sha256
from pathlib import Path
import os
import re

import k04_java_bytewise_lcg_lattice_sft as lattice

lattice.A = 214013
lattice.C = 2531011
lattice.M = 1 << 24
lattice.SHIFT = 16

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT",
    str(Path(__file__).resolve().parents[2] / "resources")))
SOURCE = ROOT / "evidence/print/spool-reconstruction.log"
PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def reference_msvc(seed, count):
    """Independent 32-bit native-CRT arithmetic, not the 24-bit lattice."""
    state = seed & 0xffffffff
    full, raw = [], bytearray()
    for _ in range(count):
        state = (state * 214013 + 2531011) & 0xffffffff
        output = (state >> 16) & 32767
        full.append(output)
        raw.append(output & 255)
    return full, bytes(raw)

def main():
    raw = SOURCE.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    records = [line for line in raw.decode("ascii").splitlines()
               if "PAYLOAD=" in line]
    assert len(records) == 133
    packets = []
    for j, line in enumerate(records[:128]):
        assert f"JOB=PS-261003-{j+300:04d} " in line
        assert "ATTEMPT=1 STATE=ACK " in line
        match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert match
        packets.append(bytes.fromhex(match[1]))

    values, bytes16 = reference_msvc(1, 16)
    assert values[:5] == [41, 18467, 6334, 26500, 19169]
    assert bytes16.hex().upper() == "2923BE84E16CD6AE529049F1F1BBE9EB"
    assert lattice.emit(1, 16, 1) == bytes16
    positives = 0
    for stride in range(1,17):
        for seed in (0,1,42,424242,0x12345678):
            state = seed & 0xFFFFFF
            true = lattice.emit(state, 8, stride)
            recovered, _ = lattice.exact_states(true, stride)
            assert state in recovered, (seed,stride)
            positives += 1
    print("MSVC_native_reference PASS; 24bit_exact_state_positives", positives)

    attempts, hits = 0, []
    for stride in range(1,17):
        examined = 0
        for row, packet in enumerate(packets):
            for orientation, arranged in lattice.views(packet):
                recovered, n = lattice.exact_states(arranged[:8], stride)
                attempts += 1
                examined += n
                for state in recovered:
                    hits.append((row,orientation,stride,state))
        print("stride",stride,"source_packet_views",len(packets)*4,
              "exact_lattice_points",examined,flush=True)
    assert attempts == 128 * 4 * 16
    assert not hits, hits
    print("complete_source_assignments",attempts,
          "original_compatible_states",len(hits),"source_sha256",PIN)

if __name__=="__main__":
    main()
