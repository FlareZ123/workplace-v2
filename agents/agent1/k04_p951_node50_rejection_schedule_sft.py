"""Source-only falsifier for a CPython MT node50 record-emission schedule.

The selected printer ACK row 129 is withheld. This tests only whether the
published conditional p951 MT basis can continue the node50 seq44->45 field
alignment into seq46 under the explicit CPython randrange rejection rules.
It does not inspect K04/K08 commitments, masks, or candidate values.

Run from the repository root:
    python agents/agent1/k04_p951_node50_rejection_schedule_sft.py
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import re
import struct
import sys
import zlib

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "agents" / "agent49"))
from k04_p951_symbolic_basis import Basis, ORIGIN, STARTS, get, temper, untemper, words

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
RECORDER_SHA = "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
SELECTED_ROW = 129
AUX_BASE = 2000
TIMESTAMP_BASE = 1791061742


def build_basis(resources):
    raw = (resources / "evidence" / "print" / "spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA
    lines = [line for line in raw.decode("ascii").splitlines() if line.startswith("2026-")]
    assert len(lines) == len(STARTS) == 133
    assert STARTS[SELECTED_ROW] == 951

    state = words()
    basis = Basis()
    for row, line in enumerate(lines):
        if row == SELECTED_ROW:
            # Deliberately do not parse or use the disputed selected ACK payload.
            continue
        match = re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
        assert match is not None, row
        payload = bytes.fromhex(match.group(1))
        for lane in range(4):
            native = untemper(int.from_bytes(payload[lane * 4:lane * 4 + 4], "little"))
            for bit, expression in enumerate(get(state, STARTS[row] + lane)):
                basis.insert(expression, (native >> bit) & 1)
    assert basis.rank == 15365, basis.rank
    return state, basis


def recorder_rows(resources):
    raw = (resources / "evidence" / "recorder" / "trip-recorder.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == RECORDER_SHA
    assert raw[:8] == b"TRP2DUMP"
    assert len(raw) == 16 + 88 * 24
    rows = {}
    for i in range(88):
        at = 16 + 24 * i
        timestamp, node, event, latch, seq, control, aux, crc = struct.unpack_from(
            "<IHBBI4sII", raw, at
        )
        if node != 50 or zlib.crc32(raw[at:at + 20]) != crc:
            continue
        assert seq not in rows
        rows[seq] = {
            "timestamp": timestamp,
            "event": event,
            "latch": latch,
            "control": control,
            "aux": aux,
        }
    assert set(rows) == set(range(72)), sorted(rows)
    return rows


def main():
    resources = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "resources"
    state, basis = build_basis(resources)
    rows = recorder_rows(resources)

    @lru_cache(maxsize=None)
    def predicted_word(position):
        return tuple(basis.predict(expression) for expression in temper(get(state, position)))

    @lru_cache(maxsize=None)
    def sample(position, bits):
        predicted = predicted_word(position)
        value = known_mask = 0
        for output_bit, bit_index in enumerate(range(32 - bits, 32)):
            bit = predicted[bit_index]
            if bit is not None:
                known_mask |= 1 << output_bit
                value |= bit << output_bit
        return value, known_mask

    def check_exact_sample(label, position, bits, bound, target):
        value, known_mask = sample(position, bits)
        assert known_mask == (1 << bits) - 1, (label, position, known_mask)
        assert value == target, (label, position, value, target)
        assert 0 <= target < bound
        print("POSITIVE_FIELD", label, "index", position, "bits", bits, "value", value)

    # Positive control: this reproduces the previously reported seq44 -> seq45
    # alignment without using the selected printer ACK.
    control44 = int.from_bytes(rows[44]["control"], "little")
    control44_bits = predicted_word(-545)
    assert all(bit is not None for bit in control44_bits)
    assert sum(bit << j for j, bit in enumerate(control44_bits)) == control44
    print("POSITIVE_CONTROL", "seq44_control", "index", -545, "bits", 32)

    check_exact_sample("seq44_aux", -544, 13, 6000, rows[44]["aux"] - AUX_BASE)
    check_exact_sample(
        "seq45_timestamp", -543, 9, 400,
        rows[45]["timestamp"] - TIMESTAMP_BASE
    )
    check_exact_sample("seq45_event", -542, 6, 39, rows[45]["event"] - 1)
    check_exact_sample("seq45_latch", -541, 3, 4, rows[45]["latch"])

    control45 = int.from_bytes(rows[45]["control"], "little")
    control45_bits = predicted_word(-540)
    control45_known = sum(bit is not None for bit in control45_bits)
    control45_mismatches = sum(
        bit is not None and bit != ((control45 >> j) & 1)
        for j, bit in enumerate(control45_bits)
    )
    assert control45_known >= 20, control45_known
    assert control45_mismatches == 0
    print("PARTIAL_CONTROL", "seq45_control", "index", -540,
          "known_bits", control45_known, "mismatches", control45_mismatches)

    # Between control[n] and control[n+1], the hypothesized record order
    # [timestamp, event, latch, control, aux] leaves these randrange calls:
    # aux[n], timestamp[n+1], event[n+1], latch[n+1].
    # CPython _randbelow_with_getrandbits uses n.bit_length(), including
    # three bits for randrange(4), and rejects samples >= n.
    fields = [
        ("seq45_aux", 13, 6000, rows[45]["aux"] - AUX_BASE),
        ("seq46_timestamp", 9, 400, rows[46]["timestamp"] - TIMESTAMP_BASE),
        ("seq46_event", 6, 39, rows[46]["event"] - 1),
        ("seq46_latch", 3, 4, rows[46]["latch"]),
    ]

    def can_be_rejected(position, bits, bound):
        value, known_mask = sample(position, bits)
        max_completion = value | (((1 << bits) - 1) & ~known_mask)
        return max_completion >= bound

    def can_be_accepted(position, bits, target):
        value, known_mask = sample(position, bits)
        return ((value ^ target) & known_mask) == 0

    # This is deliberately permissive: an accepted sample need only agree
    # with every source-fixed bit; a rejected sample need only have at least
    # one completion >= its rejection bound. Correlations between unknown
    # bits at different positions are ignored, so zero paths is a strong
    # necessary-condition failure, not an overfit exact-state claim.
    cursor0 = -539  # immediately after the compatible seq45 control at -540
    paths = [(cursor0, [])]
    trace = []
    max_rejections_per_field = 32
    max_span = 132
    for label, bits, bound, target in fields:
        next_paths = []
        for cursor, events in paths:
            for rejected in range(max_rejections_per_field + 1):
                accepted_at = cursor + rejected
                if accepted_at > cursor0 + max_span:
                    continue
                if any(
                    not can_be_rejected(position, bits, bound)
                    for position in range(cursor, accepted_at)
                ):
                    continue
                if can_be_accepted(accepted_at, bits, target):
                    next_paths.append((
                        accepted_at + 1,
                        events + [(label, accepted_at, rejected)]
                    ))
        paths = next_paths
        trace.append((label, len(paths)))
        print("PATHS_AFTER_FIELD", label, len(paths))

    assert trace == [
        ("seq45_aux", 3),
        ("seq46_timestamp", 3),
        ("seq46_event", 1),
        ("seq46_latch", 0),
    ], trace
    assert paths == []
    print(
        "NO_CPYTHON_CONTINUATION",
        "max_rejections_per_field", max_rejections_per_field,
        "max_span", max_span,
    )
    print("SEQ47_MINUS523_REMAINS_UNINDEXED")
    print("K04_BITS_RECOVERED 0; K08_WORDS_RECOVERED 0")


if __name__ == "__main__":
    main()
