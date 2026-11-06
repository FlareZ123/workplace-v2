"""Original printer five two-candidate leave-one-job-out witness, read-only.

Under the conditional p951 fourword MT source map, 132 nonselected packets
provide a linear source model. Each of five selected-withheld source holdouts
has one missing native-state bit, producing exactly two complete payloads.
This does not predict the missing physical coupon at selected row129.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents/agent49"))
from k04_p951_symbolic_basis import STARTS, ORIGIN, Basis, get, untemper, words

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
FIVE = (12, 41, 66, 95, 125)
FREE_BITS = {12: 127, 41: 127, 66: 30, 95: 30, 125: 30}
ACTUAL_CHOICES = {12: 1, 41: 0, 66: 1, 95: 0, 125: 0}
U = 0xFFFFFFFF


def temper(y: int) -> int:
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & U


def main() -> None:
    raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    packets = [bytes.fromhex(v.decode()) for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == len(STARTS) == 133
    packets[129] = b""  # no selected ACK2 bytes enter model or candidate fits

    symbolic = words()
    all_bits = {}
    for row, (payload, start) in enumerate(zip(packets, STARTS)):
        if row == 129:
            continue
        bits = []
        for lane in range(4):
            native = untemper(int.from_bytes(payload[4 * lane:4 * lane + 4], "little"))
            for pos, vector in enumerate(get(symbolic, start + lane)):
                bits.append((vector, (native >> pos) & 1))
        all_bits[row] = bits

    full = Basis()
    for row, bits in all_bits.items():
        for vector, bit in bits:
            full.insert(vector, bit)
    assert full.rank == 15365

    for withheld in FIVE:
        basis = Basis()
        for row, bits in all_bits.items():
            if row == withheld:
                continue
            for vector, bit in bits:
                basis.insert(vector, bit)
        assert full.rank - basis.rank == 1, (withheld, basis.rank)
        predictions = [basis.predict(v) for v, bit in all_bits[withheld]]
        missing = [j for j, value in enumerate(predictions) if value is None]
        assert missing == [FREE_BITS[withheld]], (withheld, missing)

        candidates = []
        for free in (0, 1):
            native_bits = [free if v is None else v for v in predictions]
            candidate = b"".join(
                temper(sum(native_bits[j * 32 + k] << k for k in range(32))).to_bytes(4, "little")
                for j in range(4)
            )
            candidates.append(candidate)
        assert candidates[0] != candidates[1]
        assert packets[withheld] in candidates
        assert candidates.index(packets[withheld]) == ACTUAL_CHOICES[withheld]
        print(f"ROW={withheld} START={STARTS[withheld]} "
              f"FREE_NATIVE_BIT={missing[0]} "
              f"CAND0={candidates[0].hex().upper()} "
              f"CAND1={candidates[1].hex().upper()} "
              f"TRUE_CHOICE={ACTUAL_CHOICES[withheld]} "
              f"2_COMPLETE_CANDIDATES_PASS")
    print("FIVE_ORIGINAL_SOURCE_WITHHELD_WHOLE_PACKET_TWO_CANDIDATE_SETS_PASS")
    print("SELECTED_ROW129_0_PREDICTED_BITS__K04_K08_MISSING")


if __name__ == "__main__":
    main()
