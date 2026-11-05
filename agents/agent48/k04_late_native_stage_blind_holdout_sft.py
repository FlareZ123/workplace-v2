"""Source-heldout K04 printer neighbor stage locator; original target ACK2 excluded.

Run from repository: python agents/agent48/k04_late_native_stage_blind_holdout_sft.py
Optional argument: root directory containing evidence/ (default: resources).
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent49"))
import k04_p951_symbolic_basis as mt

PRINT_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
LATE_ROWS = (128, 130, 131, 132)
EXPECTED = {128: (947, 63), 130: (955, 31), 131: (959, 64), 132: (963, 63)}
START = 946
END = 3496


def native_words(payload):
    return [mt.untemper(int.from_bytes(payload[i:i + 4], "little"))
            for i in range(0, 16, 4)]


def number_from_words(words):
    return sum(word << (32 * lane) for lane, word in enumerate(words))


def source_basis(bank, get_packet):
    basis = mt.Basis()
    for i in range(128):
        words = get_packet(i)
        for lane in range(4):
            for bit, symbolic in enumerate(mt.get(bank, mt.STARTS[i] + lane)):
                basis.insert(symbolic, (words[lane] >> bit) & 1)
    assert basis.rank == 15074
    return basis


def projects(basis, bank):
    projections = []
    for stage in range(START, END + 1):
        known_mask = known_value = 0
        for lane in range(4):
            for bit, symbolic in enumerate(mt.get(bank, stage + lane)):
                value = basis.predict(symbolic)
                if value is not None:
                    offset = 32 * lane + bit
                    known_mask |= 1 << offset
                    known_value |= value << offset
        if known_mask.bit_count() >= 16:
            projections.append((stage, known_mask, known_value))
    return projections


def matching(projections, words):
    value = number_from_words(words)
    return [(stage, mask.bit_count()) for stage, mask, expected in projections
            if not ((value ^ expected) & mask)]


def residual_rank(basis, vectors):
    quotients = {}
    for v in vectors:
        residual = 0
        while v:
            pivot = v.bit_length() - 1
            if pivot in basis.rows:
                v ^= basis.rows[pivot][0]
            else:
                residual ^= 1 << pivot
                v ^= 1 << pivot
        while residual:
            pivot = residual.bit_length() - 1
            if pivot not in quotients:
                quotients[pivot] = residual
                break
            residual ^= quotients[pivot]
    return len(quotients)


def main(root):
    raw = (root / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PRINT_SHA
    lines = [line for line in raw.splitlines() if b"PAYLOAD=" in line]
    assert len(lines) == len(mt.STARTS) == 133
    assert b"JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in lines[129]
    assert [mt.STARTS[i] for i in range(128)][-1] == 942

    # Row129's disputed PAYLOAD is never parsed or used, even as a negative test.
    parsed = {}
    for i in list(range(128)) + list(LATE_ROWS):
        match = re.search(rb"PAYLOAD=([0-9A-F]{32})", lines[i])
        assert match
        parsed[i] = native_words(bytes.fromhex(match.group(1).decode()))

    mt.LAST = max(mt.LAST, END + 3)
    bank = mt.words()
    basis = source_basis(bank, lambda i: parsed[i])
    projection = projects(basis, bank)
    result = {}
    for i in LATE_ROWS:
        matches = matching(projection, parsed[i])
        assert matches == [EXPECTED[i]], (i, matches)
        assert matching(projection, parsed[i][::-1]) == [], "reversed fourword negative"
        result[i] = {"native_stage": matches[0][0], "source_predicted_bits": matches[0][1]}

    # Two original retained 4word requests flank exactly one unknown 4word
    # selected ACK2 in a no-extra-draw continuous printer producer.
    assert result[130]["native_stage"] - result[128]["native_stage"] == 8
    selected_stage = result[128]["native_stage"] + 4
    assert selected_stage == result[130]["native_stage"] - 4 == 951

    # The row128/130/131/132 source bits remain independent of the erased ACK2.
    all_source = mt.Basis()
    for i in list(range(128)) + list(LATE_ROWS):
        for lane, native in enumerate(parsed[i]):
            for bit, symbolic in enumerate(mt.get(bank, mt.STARTS[i] + lane)):
                all_source.insert(symbolic, (native >> bit) & 1)
    assert all_source.rank == 15365
    selected_vectors = [symbolic for stage in range(selected_stage, selected_stage + 4)
                        for symbolic in mt.get(bank, stage)]
    assert residual_rank(all_source, selected_vectors) == 128
    assert all(all_source.predict(v) is None for v in selected_vectors)

    # Genuine synthetic MT state, independent of original late packet contents.
    synthetic_state = random.Random(0x48A5).getrandbits(624 * 32)
    def synthetic_words(stage):
        return [sum(((synthetic_state & symbolic).bit_count() & 1) << bit
                    for bit, symbolic in enumerate(mt.get(bank, stage + lane)))
                for lane in range(4)]
    planted = source_basis(bank, lambda i: synthetic_words(mt.STARTS[i]))
    planted_projects = projects(planted, bank)
    for i in LATE_ROWS:
        assert matching(planted_projects, synthetic_words(EXPECTED[i][0])) == [EXPECTED[i]]

    print(json.dumps({
        "original_printer_sha256": PRINT_SHA,
        "heldout_original_selected_ACK2": "entire row129 never decoded",
        "routine_training_packets": 128,
        "routine_source_rank": basis.rank,
        "blind_future_stages_tested_per_holdout": END - START + 1,
        "late_original_only_unique_matches": result,
        "source_predicted_original_late_bits_total": sum(v["source_predicted_bits"] for v in result.values()),
        "native_interstitial_selected_start_conditional": selected_stage,
        "selected_packet_target_quotient_rank": residual_rank(all_source, selected_vectors),
        "synthetic_mt_heldout_stage_positives": 4,
        "original_fourword_reverse_negative_controls": 4,
        "conclusion": "SOURCE_STAGE_ANCHORED_TARGET_BYTES_STILL_FULLY_UNKNOWN"
    }, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else
         Path(__file__).resolve().parents[2] / "resources")
