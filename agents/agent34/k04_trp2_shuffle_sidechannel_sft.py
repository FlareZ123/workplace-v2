"""K04 hypothesis test: TRP2 export ordering as a shared MT19937 shuffle side channel.

Read-only single-file test. Run from workplace-v2 repository root:
    python agents/agent34/k04_trp2_shuffle_sidechannel_sft.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import random
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "resources/evidence/recorder/trip-recorder.raw"
REC_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
MODEL = ROOT / "agents/agent2/20261102_k04_multicarrier_p951_sft.py"
SELECTED_START = 951
SELECTED_LAST = 954


def source_model():
    spec = importlib.util.spec_from_file_location("p951_model_for_shuffle_test", MODEL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    words, known, offset = module.source_closure(ROOT / "resources")
    assert len(words) == len(known) == 6000
    assert all(known[offset + idx] == 0 for idx in range(951, 955))
    return words, known, offset, module.temper


def get_records():
    data = REC.read_bytes()
    assert hashlib.sha256(data).hexdigest() == REC_SHA
    assert data[:8] == b"TRP2DUMP"
    assert struct.unpack_from("<HHI", data, 8) == (2, 24, 88)
    out = []
    for i in range(88):
        pos = 16 + 24 * i
        _, node, _, _, seq, _, _, crc = struct.unpack_from("<IHBBI4sII", data, pos)
        good = zlib.crc32(data[pos:pos+20]) == crc
        out.append((node, seq, good))
    assert len(set((n, seq) for n, seq, _ in out)) == 88
    assert sum(n == 49 for n, _, _ in out) == 16
    assert sum(n == 50 for n, _, _ in out) == 72
    assert sum(not good for _, _, good in out) == 4
    return [(n, seq) for n, seq, _ in out]


def swap_trace(initial, final):
    """Uniquely invert descending-index Fisher-Yates from initial to final."""
    a = list(initial)
    result = {}
    for i in range(len(a)-1, 0, -1):
        j = a.index(final[i], 0, i+1)
        a[i], a[j] = a[j], a[i]
        result[i] = j
    assert a == final
    return result


def possible_high7(native, words, known, offset, temper):
    """All possible top-seven MT-output codes given a partial native word."""
    mask = known[offset + native]
    value = words[offset + native]
    span = {0}
    for bit in range(32):
        if not (mask >> bit) & 1:
            d = temper(1 << bit) >> 25
            if d:
                span.update(code ^ d for code in list(span))
    base = temper(value) >> 25
    return sum(1 << (base ^ code) for code in span)


def allowed(code_bits, bound, value=None):
    """Python random._randbelow_with_getrandbits: reject code >= bound."""
    shift = 7 - bound.bit_length()
    if value is None:
        return bool(code_bits >> (bound << shift))
    width = 1 << shift
    return bool((code_bits >> (value << shift)) & ((1 << width) - 1))


def fisher_yates_survivors(high7, start_index, trace, max_rejections):
    """DP over future stages: one accepted and 0..max_rejections rejected draws."""
    length = len(high7)
    dp = [True] * (length + 1)
    for i in range(1, 88):
        bound, wanted = i+1, trace[i]
        new = [False] * (length+1)
        for pos in range(length-1, -1, -1):
            for count in range(min(max_rejections, length-pos-1) + 1):
                at = pos + count
                if allowed(high7[at], bound, wanted) and dp[at+1]:
                    new[pos] = True
                    break
                if not allowed(high7[at], bound):
                    break
        dp = new
    return [start_index + i for i, valid in enumerate(dp[:-1]) if valid]


def natural_orders():
    """4 cohort orders, intra-cohort direction, node50 order and placement."""
    groups = [[(49, i) for i in range(base, base+4)]
              for base in (200, 300, 900, 990)]
    common = [(50, i) for i in range(72)]
    for perm in itertools.permutations(range(4)):
        for reverse_common in (False, True):
            for reverse_cohorts in (False, True):
                tail = sum((groups[i][::-1] if reverse_cohorts else groups[i]
                            for i in perm), [])
                ordered_common = common[::-1] if reverse_common else common
                for first_common in (False, True):
                    yield (ordered_common + tail if first_common
                           else tail + ordered_common)



def chronological_orders():
    """Additional source-defined acquisition timestamp pre-export orders.

    The original TRP2 timestamps are independent of the file's physical row
    sequence. Duplicate timestamps are resolved with six deterministic,
    source-field tie policies; ascending and descending time are both tested.
    """
    raw = REC.read_bytes()
    rows = []
    for i in range(88):
        at = 16 + 24 * i
        ts, node, event, latch, seq, _, _, _ = struct.unpack_from(
            "<IHBBI4sII", raw, at)
        rows.append((ts, node, event, latch, seq, i))
    assert len({(node, seq) for _, node, _, _, seq, _ in rows}) == 88
    def tie(row, mode):
        ts, node, event, latch, seq, index = row
        if mode == "seq":
            return (seq, node)
        if mode == "node-seq":
            return (node, seq)
        if mode == "seq-node":
            return (seq, node)
        if mode == "latch-seq":
            return (latch, seq, node)
        if mode == "event-seq":
            return (event, seq, node)
        return (index,)
    distinct = {}
    for direction in (1, -1):
        for mode in ("seq", "node-seq", "seq-node", "latch-seq",
                     "event-seq", "original"):
            ordering = sorted(rows, key=lambda row: (direction * row[0],
                                                    *tie(row, mode)))
            source_ids = tuple((row[1], row[4]) for row in ordering)
            distinct[source_ids] = (direction, mode)
    assert len(distinct) == 10
    return [list(source_ids) for source_ids in distinct]


def positive_control():
    class LoggingRNG(random.Random):
        def __init__(self, seed):
            super().__init__(seed)
            self.draws = []
        def getrandbits(self, k):
            word = super().getrandbits(32)
            self.draws.append(word)
            return word >> (32 - k)

    rng = LoggingRNG(9372)
    source = list(range(88))
    scrambled = source.copy()
    rng.shuffle(scrambled)
    trace = swap_trace(source, scrambled)
    observed = [1 << (word >> 25) for word in rng.draws]
    assert 0 in fisher_yates_survivors(observed, 0, trace, 8)
    observed[0] = 1 << ((trace[87] + 1) % 88)
    assert 0 not in fisher_yates_survivors(observed, 0, trace, 8)
    print("positive control: exact Python shuffle recovered; corrupted first draw rejected")


def run():
    positive_control()
    actual = get_records()
    word, known, offset, temper = source_model()
    assert offset == 2000
    hi7 = [possible_high7(i, word, known, offset, temper)
           for i in range(168, 2201)]
    hi7_16 = hi7[600-168:]
    orders = list(natural_orders())
    assert len(orders) == 192 and len({tuple(x) for x in orders}) == 192
    time_orders = chronological_orders()
    assert len(time_orders) == 10 and len({tuple(x) for x in time_orders}) == 10
    assert all(set(order) == set(actual) for order in time_orders)
    orders.extend(time_orders)
    import sys
    extended = "--extended" in sys.argv[1:]
    assert all(x == "--extended" for x in sys.argv[1:])
    count = 0
    for order in orders:
        trace = swap_trace(order, actual)
        if extended:
            # Sixteen rejected draws per step: limited start window only.
            starts = fisher_yates_survivors(hi7_16, 600, trace, 16)
            count += sum(600 <= s <= SELECTED_LAST for s in starts)
        else:
            # Eight rejected draws per step: full target-intersecting
            # start domain 951 - 87 * 9 = 168 through 954.
            starts = fisher_yates_survivors(hi7, 168, trace, 8)
            count += sum(168 <= s <= SELECTED_LAST for s in starts)
    assert count == 0
    print("original: 192 cohort and 10 timestamp pre-shuffle orders; no surviving target-range start")
    print("mode:", "extended R16, starts 600..954" if extended
          else "default R8, starts 168..954")
    print("No recovered K04 coupon; shared-p951 shuffle model not source-supported.")


if __name__ == "__main__":
    run()
