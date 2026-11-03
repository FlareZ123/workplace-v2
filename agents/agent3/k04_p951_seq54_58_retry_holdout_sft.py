"""Independent source-heldout falsifier for a seq54..58 fixed-seven MT stage.

This tests a narrowly defined recorder writer implied by two retrospectively
AUX-matched p951 node50 controls. Seq56 AUX and seq58 LATCH are withheld
before source-index predictions. No K04 target or selected spool ACK is read.
Run: python agents/agent3/k04_p951_seq54_58_retry_holdout_sft.py resources
"""
import hashlib
import importlib.util
import random
import struct
import sys
import zlib
from pathlib import Path

SOURCE_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "agent2/20261102_k04_multicarrier_p951_sft.py"
)
spec = importlib.util.spec_from_file_location("p951_source", SOURCE_SCRIPT)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

def node50_records(root):
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source.REC_SHA
    records = {}
    for i in range(88):
        start = 16 + i * 24
        _, node, event, latch, seq, control, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, start
        )
        if node == 50 and zlib.crc32(raw[start:start+20]) == crc:
            assert seq not in records
            records[seq] = (event, latch, control, aux)
    return records


def main(root):
    # Actual seeded 32-bit output, checked through an independent mask/temper
    # roundtrip; the heldout test reuses this exact top-bit readout.
    rng = random.Random(7)
    seeded = [rng.getrandbits(32) for _ in range(24)]
    assert seeded[15] >> 19 == 1758
    assert seeded[20] >> 29 == 0
    assert source.temper(source.untemper(seeded[15])) == seeded[15]
    assert 2000 + (seeded[15] >> 19) == 3758
    print("PASS seeded 13-bit AUX and 3-bit LATCH extraction controls")

    word, known, offset = source.source_closure(root)
    records = node50_records(root)
    full = 0xffffffff

    def code(at, shift):
        pos = offset + at
        assert known[pos] == full, (at, known[pos])
        return source.temper(word[pos]) >> shift

    # Retrospectively discovered from their own AUX and one printer-known
    # original CONTROL bit: genuine matches, weak indexes. These two rows
    # are never used to fit printer state or to choose holdout values.
    for seq, index, aux in ((54, -459, 2876), (55, -452, 6663)):
        event, latch, control, actual_aux = records[seq]
        assert actual_aux == aux
        pos = offset + index
        assert known[pos] == 0x80000000
        original_control_state = source.untemper(
            int.from_bytes(control, "little")
        )
        assert ((original_control_state ^ word[pos]) & known[pos]) == 0
        assert code(index + 1, 19) == aux - 2000
        print("CONDITIONAL anchor", seq, "at", index,
              "AUX predicted", aux, "source CONTROL fixed bits=1")

    # Freeze 7 outputs between successive controls, with immediate +1
    # accepted AUX and immediate -1 accepted LATCH. This predicts
    # indexed fields of other original CRC-valid records BEFORE reading them.
    assert -452 + 7 == -445  # seq56 control
    predicted_aux56 = 2000 + code(-444, 19)
    assert predicted_aux56 == 4624
    actual_aux56 = records[56][3]
    assert actual_aux56 == 6362
    assert predicted_aux56 != actual_aux56
    print("BLINDED seq56 AUX:", "predicted", predicted_aux56,
          "original", actual_aux56, "CONTRADICTION")

    assert -452 + 3 * 7 == -431  # seq58 control
    predicted_latch58 = code(-432, 29)
    assert predicted_latch58 == 2
    actual_latch58 = records[58][1]
    assert actual_latch58 == 0
    assert predicted_latch58 != actual_latch58
    print("BLINDED seq58 LATCH:", "predicted", predicted_latch58,
          "original", actual_latch58, "CONTRADICTION")

    selected_masks = [
        known[offset + source.STARTS[129] + i] for i in range(4)
    ]
    assert selected_masks == [0, 0, 0, 0]
    print("Seven-draw continuation rejected under stated writer model.")
    print("Selected K04 physical coupon remains wholly unauthenticated.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1
         else Path(__file__).resolve().parents[2] / "resources")
