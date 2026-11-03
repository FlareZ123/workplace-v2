"""Source-only conditional CPython historian sampler bridge.

Run from repository root:
    python agents/agent42/k04_historian_tag_rejection_bridge_sft.py

This test imports Agent50's source-pinned, selected-ACK-erased p951 printer
projection, and reads the untouched original historian PV observations.
The timestamp base and producer fields are hypotheses, never source facts.
No K04/K08 acceptance commitment, route mask or candidate is accessed.
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent50"))
from k04_pv_early_float_triple_sft import (
    HIST, HIST_PIN, compatible, source_pairs
)


def run():
    source = HIST.read_bytes()
    assert hashlib.sha256(source).hexdigest() == HIST_PIN
    pv = {r["seq"]: r for r in map(json.loads, source.splitlines())
          if r["field"] == "PV"}
    assert len(pv) == 112
    projection = source_pairs()

    def code(stage, width):
        value, mask = projection[stage]
        shift = 53 - width
        return value >> shift, mask >> shift

    def agrees(stage, width, observed):
        value, mask = code(stage, width)
        return (observed & mask) == value

    base = datetime.fromisoformat("2026-10-03T21:12:30+00:00")

    def elapsed(seq):
        return int((datetime.fromisoformat(pv[seq]["ts"]) - base).total_seconds())

    # Original PV175-177 anchors and one weak, explicitly conditional
    # forward placement for PV178 (its high 17 precision bits are not fixed).
    for seq, tag, index in [(175, 2, -1568), (176, 1, -1561),
                            (177, 1, -1554), (178, 2, -1547)]:
        assert agrees(index, 3, tag)
        assert compatible(round(pv[seq]["value"] * 1000),
                          *projection[index + 1])
        print("source-compatible row", seq, "tag_index", index,
              "tag_fixed3", code(index, 3)[1].bit_count(),
              "pv_fixed53", projection[index + 1][1].bit_count())

    # The 7-draw interval contains two exact CPython rejection attempts:
    # randbelow(4) uses three random high bits; values 4..7 retry.
    assert code(-1562, 3) == (6, 7)
    assert code(-1555, 3) == (4, 7)
    assert code(-1561, 3) == code(-1554, 3) == (1, 7)
    print("tag rejections: stage -1562 code6 and -1555 code4: PASS")

    # This 7-bit source-fixed MT output equals the timestamp offset for
    # seq177 only if the hypothesized clock base is 21:12:30 UTC.
    assert elapsed(177) == 97
    assert code(-1556, 7) == (97, 127)
    print("PV177 timestamp offset 97 equals source-fixed stage -1556: PASS")

    # A fixed no-rejection extension to PV178 would timestamp it with
    # stage -1549, whereas actual offset64 contradicts this source word.
    assert elapsed(178) == 64
    assert not agrees(-1549, 7, 64)
    print("PV178 no-extra-retry stage -1549 timestamp: REJECTED")

    # One additional *post-PV177* categorical rejection instead shifts
    # timestamp178 to -1548, leaving one conditional source placement.
    assert agrees(-1548, 7, 64)
    assert code(-1548, 7)[1].bit_count() == 3
    assert code(-1549, 2) == (2, 3)
    assert pv[177]["unit"] == "percent"
    # If the last post-PV177 stage -1549 is the selected unit draw,
    # CPython randbelow(3) accepts code2 (=percent in this hypothesis).
    # That word cannot complete the quality randbelow(2) call, for
    # which only zero and one are accepted. Thus Q→U rather than U→Q
    # fits the *single-extra-rejection* placement.
    assert not agrees(-1549, 2, 0) and not agrees(-1549, 2, 1)
    print("conditional Q then U field order; index2 unit=percent: PASS")

    # Planted exact-53-bit original generator control for the numeric
    # reduction used above; verifies quantization/interval implementation.
    rng = random.Random(11030922)
    a, b = rng.getrandbits(32), rng.getrandbits(32)
    fraction = ((a >> 5) << 26) | (b >> 6)
    quantized = round(12000 + 76000 * fraction / (1 << 53))
    assert compatible(quantized, fraction, (1 << 53) - 1)
    print("planted PV exact-double compatibility: PASS")
    print("K04 selected coupon: unresolved; K08 caption: unresolved")


if __name__ == "__main__":
    run()
