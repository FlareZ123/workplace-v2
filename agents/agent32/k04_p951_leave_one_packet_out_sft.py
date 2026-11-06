"""Full-packet leave-one-out benchmark for the conditional p951 MT printer model.

The selected 0417 row129 payload is never decoded or retained. Every other
packet is withheld once, while row129 remains excluded from every fit.
"""
from __future__ import annotations

import collections
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "resources"
sys.path.insert(0, str(REPO / "agents" / "agent49"))
from k04_p951_symbolic_basis import (
    ORIGIN, LAST, MAG, STARTS, Basis, get, temper, untemper, words,
)

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED_ROW = 129
SAME_ROLE_ROWS = (131, 132)


def metadata(prefix: str) -> dict[str, str]:
    fields = {}
    for token in prefix.split():
        if "=" in token:
            key, value = token.split("=", 1)
            fields[key.lower()] = value
    return fields


def load_rows():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    rows = []
    packet_index = 0
    for line_index, line in enumerate(raw.decode("utf-8").splitlines()):
        if "PAYLOAD=" not in line:
            continue
        prefix = line.split(" PAYLOAD=", 1)[0]
        # STARTS indexes payload records, not physical text-file lines.
        # Do not capture, decode, or retain the selected row129 PAYLOAD.
        if packet_index == SELECTED_ROW:
            payload = None
        else:
            match = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
            assert match is not None
            payload = bytes.fromhex(match.group(1))
        rows.append({
            "payload": payload,
            "metadata": metadata(prefix),
            "line_index": line_index,
        })
        packet_index += 1
    assert len(rows) == len(STARTS) == 133
    assert rows[SELECTED_ROW]["payload"] is None
    assert rows[131]["metadata"]["class"] == "RECOVER"
    assert rows[132]["metadata"]["class"] == "RECOVER"
    return rows


def build_basis(rows, symbolic, heldout):
    basis = Basis()
    for index, row in enumerate(rows):
        if index in (SELECTED_ROW, heldout):
            continue
        payload = row["payload"]
        assert payload is not None
        start = STARTS[index]
        for lane in range(4):
            observed = untemper(
                int.from_bytes(payload[lane * 4:lane * 4 + 4], "little")
            )
            for bit, vector in enumerate(get(symbolic, start + lane)):
                basis.insert(vector, (observed >> bit) & 1)
    return basis


def assess_packet(basis, symbolic, row_index, actual_payload=None):
    fixed_bits = wrong_bits = 0
    lanes = []
    for lane in range(4):
        fixed = wrong = predicted = 0
        actual = (
            int.from_bytes(actual_payload[lane * 4:lane * 4 + 4], "little")
            if actual_payload is not None else None
        )
        for bit, vector in enumerate(temper(get(symbolic, STARTS[row_index] + lane))):
            value = basis.predict(vector)
            if value is None:
                continue
            fixed += 1
            fixed_bits += 1
            predicted |= value << bit
            if actual is not None and value != ((actual >> bit) & 1):
                wrong += 1
                wrong_bits += 1
        lanes.append({
            "lane": lane,
            "fixed_bits": fixed,
            "wrong_fixed_bits": wrong,
            "predicted_fixed_masked_word": f"{predicted:08X}",
            "actual_word": f"{actual:08X}" if actual is not None else None,
        })
    return {
        "fixed_bits": fixed_bits,
        "wrong_fixed_bits": wrong_bits,
        "lanes": lanes,
    }


def temper32(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF


def synthetic_outputs(seed=20261106):
    rng = random.Random(seed)
    concrete = [rng.getrandbits(32) for _ in range(624)]
    for i in range(624, LAST - ORIGIN + 1):
        t = i - 624
        y = (concrete[t] & 0x80000000) | (concrete[t + 1] & 0x7FFFFFFF)
        value = concrete[t + 397] ^ (y >> 1) ^ (MAG if y & 1 else 0)
        concrete.append(value & 0xFFFFFFFF)
    return [
        {
            "payload": b"".join(
                temper32(concrete[start + lane - ORIGIN]).to_bytes(4, "little")
                for lane in range(4)
            ),
            "metadata": {},
        }
        for start in STARTS
    ]


def synthetic_control(symbolic):
    rows = synthetic_outputs()
    tested = []
    for heldout in (12, 131, 132):
        basis = build_basis(rows, symbolic, heldout)
        result = assess_packet(basis, symbolic, heldout, rows[heldout]["payload"])
        assert result["wrong_fixed_bits"] == 0
        tested.append({
            "row": heldout,
            "fixed_bits": result["fixed_bits"],
            "wrong_fixed_bits": 0,
        })
    return tested


def main():
    rows = load_rows()
    assert STARTS[SELECTED_ROW] == 951
    symbolic = words()

    # The selected row is excluded from the full source basis as well.
    full_basis = build_basis(rows, symbolic, SELECTED_ROW)
    assert full_basis.rank == 15365
    target_shape = assess_packet(full_basis, symbolic, SELECTED_ROW)
    assert target_shape["fixed_bits"] == 0

    records = []
    started = time.time()
    for heldout, row in enumerate(rows):
        if heldout == SELECTED_ROW:
            continue
        basis = build_basis(rows, symbolic, heldout)
        result = assess_packet(basis, symbolic, heldout, row["payload"])
        assert result["wrong_fixed_bits"] == 0
        records.append({
            "row": heldout,
            "stage": STARTS[heldout],
            "rank": basis.rank,
            "nullity": 19968 - basis.rank,
            "fixed_bits": result["fixed_bits"],
            "wrong_fixed_bits": result["wrong_fixed_bits"],
            "lane_fixed_bits": [lane["fixed_bits"] for lane in result["lanes"]],
            "metadata": row["metadata"],
        })
    elapsed = round(time.time() - started, 3)

    histogram = {
        str(k): v for k, v in sorted(
            collections.Counter(row["fixed_bits"] for row in records).items()
        )
    }
    full_packets = [row for row in records if row["fixed_bits"] == 128]
    assert not full_packets
    assert all(row["wrong_fixed_bits"] == 0 for row in records)

    same_role = [
        next(row for row in records if row["row"] == index)
        for index in SAME_ROLE_ROWS
    ]
    best = sorted(records, key=lambda row: (-row["fixed_bits"], row["row"]))[:8]

    result = {
        "source_sha256": SPOOL_SHA256,
        "stage_map_sha256": hashlib.sha256(
            ",".join(map(str, STARTS)).encode()
        ).hexdigest(),
        "rows": len(rows),
        "withheld_selected_row": SELECTED_ROW,
        "selected_stage": STARTS[SELECTED_ROW],
        "selected_target_fixed_bits": target_shape["fixed_bits"],
        "training_packets_per_leave_one_out": 131,
        "leave_one_out_packets": len(records),
        "fixed_bit_histogram": histogram,
        "complete_128_bit_packet_predictions": len(full_packets),
        "all_fixed_bits_correct": True,
        "same_role_RECOVER_ACK_controls": same_role,
        "best_partial_predictions": best,
        "synthetic_positive_controls": synthetic_control(symbolic),
        "leave_one_out_seconds": elapsed,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
