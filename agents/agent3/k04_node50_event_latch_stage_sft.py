"""SFT: source-only node50 event/latch stages immediately before MT control.

Read-only, selected printer row129 and all acceptance inputs excluded.
Synthetic control: native CPython randrange(39), randrange(4), randrange(6000)
rejection conventions. Independent original event/latch fields predict three
retained matched node50 control predecessors, without AUX fitted bits.
Run: python agents/agent3/k04_node50_event_latch_stage_sft.py resources
"""
import random
import sys
from pathlib import Path

from k04_aux_sampler_p951_sft import source, original_node50, U


def main(root):
    for seed in range(100):
        rng, test = random.Random(seed), random.Random(seed)
        for n, k in ((39, 6), (4, 3), (6000, 13)):
            value = rng.randrange(n)
            candidate = test.getrandbits(k)
            while candidate >= n:
                candidate = test.getrandbits(k)
            assert value == candidate
    print("PASS original CPython 6/3/13-bit sampler synthetic controls")

    word, known, offset = source.source_closure(root)
    node = original_node50(root, word, known, offset)
    import hashlib
    import struct
    import zlib
    raw = (root / "evidence/recorder/trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source.REC_SHA
    lookup = {}
    for row in range(88):
        i = 16 + 24 * row
        ts, label, event, latch, seq, control, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, i)
        if label == 50 and zlib.crc32(raw[i:i+20]) == crc:
            lookup[seq] = (event, latch, control, aux)
    expected = {
        24: (-683, 7, 1, 8, 1),
        45: (-540, 25, 0, 26, 0),
        70: (-339, 57, 0, 8, 0),
    }
    for seq, (pos, event_code, latch_code, event, latch) in expected.items():
        assert node[seq][0] == pos
        assert lookup[seq][:2] == (event, latch)
        first, second = offset + pos - 2, offset + pos - 1
        assert known[first] == U and known[second] == U
        observed_event = source.temper(word[first]) >> 26
        observed_latch = source.temper(word[second]) >> 29
        assert (observed_event, observed_latch) == (event_code, latch_code)
        assert observed_latch == latch
        if seq in (24, 45):
            assert observed_event == event - 1
            print("SEQ", seq, "original event/latch independently predicted",
                  event, latch, "from source states at", pos-2, pos-1)
        else:
            assert observed_event >= 39
            print("SEQ 70 original EVENT sampler rejects", event_code,
                  "at", pos-2, "then original latch predicted", latch)
    # Independent LATCH held out from AUX-based tentative seq63 placement.
    # The p=-397 control location was identified using AUX+1 source bit;
    # its original latch was not used in that placement selection.
    assert lookup[63][1] == 0
    predecessor = offset - 398
    assert known[predecessor] == 0x7fffffff
    low = source.temper(word[predecessor] & 0x7fffffff) >> 29
    high = source.temper((word[predecessor] & 0x7fffffff) |
                         0x80000000) >> 29
    assert (low, high) == (0, 4)
    print("tentative seq63 at -397: source predecessor LATCH", low,
          "matches original 0; alternate code4 would reject,",
          "conditional missing MSB=0")
    assert [known[offset+source.STARTS[129]+j] for j in range(4)] == [0]*4
    print("CONDITIONAL source event/latch stage consistent, K04 still absent")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] / "resources")
