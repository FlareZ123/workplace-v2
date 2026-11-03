"""Original H-17 PV/tag stage follow-on to Agent50's early shared-MT triple.

Runnable from the repository root:
    python agents/agent7/k04_pv_tag_rejection_followon_sft.py
Read-only. Imports the existing source-pinned MT model from agent50.
"""
from pathlib import Path
import hashlib
import json
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent50"))
from k04_pv_early_float_triple_sft import (  # source-pinned peer model
    SPOOL, HIST, SPOOL_PIN, HIST_PIN, STARTS, ORIGIN, LAST,
    mt_words, untemper, temper, Basis,
)


def tag_codes(words: dict, stage: int) -> set[int]:
    value, mask = words[stage]
    mask &= 0xE0000000
    return {code for code in range(8)
            if (((code << 29) ^ value) & mask) == 0}


def pv_possible(words: dict, stage: int, observed: float) -> tuple[bool, int]:
    a, am = words[stage]
    b, bm = words[stage + 1]
    value = ((a >> 5) << 26) | (b >> 6)
    mask = ((am >> 5) << 26) | (bm >> 6)
    q = round(observed * 1000)
    scale = 1 << 53

    def ceildiv(x: int, y: int) -> int:
        return (x + y - 1) // y

    low = max(0, ceildiv((2 * q - 24001) * scale, 152000))
    high = min(scale - 1, ceildiv((2 * q - 23999) * scale, 152000) - 1)

    def count_leq(bound: int) -> int:
        if bound < 0:
            return 0
        total = 0
        for j in range(52, -1, -1):
            vbit = (value >> j) & 1
            fixed = (mask >> j) & 1
            if (bound >> j) & 1:
                if not fixed or not vbit:
                    total += 1 << ((((1 << j) - 1) & ~mask).bit_count())
                if fixed and not vbit:
                    return total
            elif fixed and vbit:
                return total
        return total + 1

    return count_leq(high) > count_leq(low - 1), mask.bit_count()


def successors(words: dict, previous: int, accepted_code: int) -> list[int]:
    """Three post-PV draws and first accepted 3-bit randrange(4) tag code."""
    out = []
    for stage in range(previous + 6, previous + 20):
        if stage not in words or stage + 2 not in words:
            break
        if not all(any(c >= 4 for c in tag_codes(words, k))
                   for k in range(previous + 6, stage)):
            break
        if accepted_code in tag_codes(words, stage):
            out.append(stage)
    return out


def synthetic_test() -> None:
    rng = random.Random(20261003)
    words = []
    true_stages = []
    tags = []
    values = []
    for _ in range(16):
        while True:
            index = len(words)
            draw = rng.getrandbits(32)
            words.append(draw)
            code = draw >> 29
            if code < 4:
                break
        true_stages.append(index)
        tags.append(code)
        a, b = rng.getrandbits(32), rng.getrandbits(32)
        words.extend((a, b))
        fraction = ((a >> 5) << 26) | (b >> 6)
        values.append(round(12000 + 76000 * fraction / (1 << 53)) / 1000)
        words.extend(rng.getrandbits(32) for _ in range(3))

    complete = {index: (value, 0xFFFFFFFF) for index, value in enumerate(words)}
    for index, stage in enumerate(true_stages):
        assert pv_possible(complete, stage + 1, values[index])[0]
        if index:
            assert successors(complete, true_stages[index - 1], tags[index]) == [stage]
    rejects = sum(true_stages[i + 1] - true_stages[i] - 6 for i in range(15))
    assert rejects == 10
    print("synthetic 16/16 genuine random tag+PV controls PASS; rejections=", rejects)


def main() -> None:
    spool, history = SPOOL.read_bytes(), HIST.read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_PIN
    assert hashlib.sha256(history).hexdigest() == HIST_PIN
    packets = [bytes.fromhex(v.decode())
               for v in re.findall(rb"PAYLOAD=([0-9A-F]{32})", spool)]
    assert len(packets) == len(STARTS) == 133
    model = mt_words()
    basis = Basis()
    for row, (packet, pos) in enumerate(zip(packets, STARTS)):
        if row == 129:
            continue
        for lane in range(4):
            u = untemper(int.from_bytes(packet[4 * lane:4 * lane + 4], "little"))
            for bit, vector in enumerate(model[pos + lane - ORIGIN]):
                basis.insert(vector, (u >> bit) & 1)
    assert basis.rank == 15365

    predicted = {}
    for stage in range(-1570, -1400):
        value = mask = 0
        for bit, vector in enumerate(temper(model[stage - ORIGIN])):
            observed = basis.predict(vector)
            if observed is not None:
                value |= observed << bit
                mask |= 1 << bit
        predicted[stage] = value, mask
    pv = {r["seq"]: r for r in map(json.loads, history.splitlines())
          if r["field"] == "PV"}
    assert len(pv) == 112
    assert [tag_codes(predicted, t) for t in (-1568, -1561, -1554)] == [
        {2}, {1}, {1}
    ]
    assert [tag_codes(predicted, t) for t in (-1562, -1555)] == [
        {6}, {4}
    ]
    for seq, stage in ((175, -1568), (176, -1561), (177, -1554)):
        assert pv_possible(predicted, stage + 1, pv[seq]["value"])[0]
        print("source anchor", seq, "tag stage", stage)

    choices = successors(predicted, -1554, 2)
    assert choices == [-1547, -1546], choices
    selected = [stage for stage in choices
                if pv_possible(predicted, stage + 1, pv[178]["value"])[0]]
    assert selected == [-1547], selected
    print("seq178 tag-only stages", choices,
          "withheld original PV selects", selected)

    for ft_code in (0, 3):
        tags = {"LT-204": 2, "TT-92": 1,
                "FT-13": ft_code, "PT-118": 3 - ft_code}
        stages = {-1554: 1}
        for seq in range(178, 185):
            following = {}
            for prev, count in stages.items():
                for stage in successors(predicted, prev, tags[pv[seq]["tag"]]):
                    if pv_possible(predicted, stage + 1, pv[seq]["value"])[0]:
                        following[stage] = following.get(stage, 0) + count
            stages = following
            print("seq", seq, "FT_code", ft_code,
                  "stage_count", len(stages), "path_count", sum(stages.values()))
            if seq == 178:
                assert stages == {-1547: 1}
        assert len(stages) == 18 and sum(stages.values()) == 1024

    synthetic_test()
    print("PASS: original selected coupon withheld; no K04 bits recovered")


if __name__ == "__main__":
    main()
