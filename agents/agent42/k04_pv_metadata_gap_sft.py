"""Conditional p951 historian PV metadata-stage falsifiers.

Run: python agents/agent42/k04_pv_metadata_gap_sft.py
Imports Agent50's source-pinned MT projection. No selected ACK or K04/K08
commitment, route mask, or candidate enters this source-only experiment.
"""
from itertools import permutations, product
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent50"))
from k04_pv_early_float_triple_sft import HIST, HIST_PIN, source_pairs, compatible
import hashlib


def matches_schedule(order, word_top2):
    """Can T(1 draw), U(randbelow(3)), Q(randbelow(2)) occupy four draws?"""
    for counts in product(range(1, 5), repeat=3):
        if sum(counts) != 4:
            continue
        pos = 0
        valid = True
        for field, count in zip(order, counts):
            observed = word_top2[pos:pos + count]
            pos += count
            if field == "T":
                valid = count == 1
            else:
                limit = 3 if field == "U" else 2
                # CPython's _randbelow(n) uses n.bit_length() high bits.
                # Any preceding draws must be rejected; the final accepted.
                valid = all(x is None or x >= limit for x in observed[:-1])
                valid &= observed[-1] is None or observed[-1] < limit
            if not valid:
                break
        if valid:
            return True
    return False


def run():
    raw = HIST.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == HIST_PIN
    pv = {r["seq"]: r for r in map(json.loads, raw.splitlines()) if r["field"] == "PV"}
    assert pv[174]["value"] == 41.339
    assert (pv[175]["value"], pv[176]["value"], pv[177]["value"]) == (
        83.33, 29.968, 16.133
    )

    pair = source_pairs()
    # The *first* native word of each two-word MT random.random() pair
    # supplies its high two bits in v53 positions 51..52.
    def top2(stage):
        value, mask = pair[stage]
        return (value >> 51) & 3, (mask >> 51) & 3

    assert top2(-1562) == (3, 3), top2(-1562)
    assert top2(-1556) == (3, 3), top2(-1556)
    assert compatible(41339, *pair[-1574]) is False
    assert pair[-1574][1].bit_count() == 4
    for seq, stage in ((175, -1567), (176, -1560), (177, -1553)):
        assert compatible(round(pv[seq]["value"] * 1000), *pair[stage])
    print("historical source PV175-177 positive: PASS")
    print("source-fixed high2: stage -1562=3; stage -1556=3")

    # First four post-PV stages: -1565,-1564,-1563,-1562.
    # Second four: -1558,-1557,-1556,-1555.
    # Unknown high2 codes are deliberately free, making this a conservative
    # (rather than over-constrained) exclusion.
    first = [None, None, None, top2(-1562)[0]]
    second = [None, None, top2(-1556)[0], None]
    outcomes = {
        "".join(order): (matches_schedule(order, first),
                         matches_schedule(order, second))
        for order in permutations("TUQ")
    }
    assert not any(a and b for a, b in outcomes.values())
    print("all six fixed T/U/Q orders rejected across both intervals:", outcomes)

    # Positive control: an allowed ordinary high2 code in the two positions
    # recovers at least one schedule, demonstrating the gate is falsifiable.
    positive = ([None, None, None, 1], [None, None, 1, None])
    assert any(all(matches_schedule(o, w) for w in positive)
               for o in permutations("TUQ"))
    print("planted common-schedule positive: PASS")

    print("seven-stride backward PV174 holdout: INCOMPATIBLE at stage -1574")
    print("K04 selected coupon remains 128/128 unverified; K08 unchanged")


if __name__ == "__main__":
    run()
