"""K04 conditional p951 alternative-generation-stage recovery SFT.

Scans 16-byte MT19937 coupons at every source-indexed four-draw window,
including unprinted metadata/gap windows. Only zero/one-bit residual
coupons are enumerated. This is a speculative alternate output-stage
hypothesis, not an authenticated historical printer-generation law.

Usage: python agents/agent44/k04_p951_hidden_stage_coupon_sft.py
From the workplace-v2 repository root, no extra packages.
"""
from __future__ import annotations

import configparser
import hashlib
import json
import re
import struct
from pathlib import Path

SOURCE_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
STARTS = (
    0,7,16,22,30,37,45,54,64,72,80,88,95,108,116,122,130,136,142,148,
    154,164,170,176,182,188,194,203,209,218,224,230,237,244,250,257,
    265,272,284,294,301,307,314,324,335,342,348,354,360,366,372,378,
    384,394,401,408,416,423,429,435,446,454,460,470,477,485,491,503,
    511,518,524,531,539,556,562,568,576,582,588,595,602,608,617,624,
    632,638,644,650,658,666,672,678,686,693,701,710,717,729,736,743,
    755,762,770,776,782,788,795,801,813,819,825,831,837,846,853,861,
    870,876,884,891,899,905,912,918,924,930,936,942,947,951,955,959,963,
)
MASK32 = 0xFFFFFFFF
MAG = 0x9908B0DF


def unshift_right(value: int, shift: int) -> int:
    result = value
    for _ in range(6):
        result = value ^ (result >> shift)
    return result & MASK32


def unshift_left(value: int, shift: int, mask: int) -> int:
    result = value
    for _ in range(6):
        result = value ^ ((result << shift) & mask)
    return result & MASK32


def untemper(value: int) -> int:
    return unshift_right(
        unshift_left(
            unshift_left(unshift_right(value, 18), 15, 0xEFC60000),
            7,
            0x9D2C5680,
        ),
        11,
    )


def temper(value: int) -> int:
    value ^= value >> 11
    value ^= (value << 7) & 0x9D2C5680
    value ^= (value << 15) & 0xEFC60000
    return (value ^ (value >> 18)) & MASK32


def state_expressions(max_position: int) -> list[list[int]]:
    expressions = [[1 << (32 * t + b) for b in range(32)] for t in range(624)]
    for t in range(624, max_position + 1):
        predecessor = expressions[t - 624]
        next_word = expressions[t - 623]
        middle = expressions[t - 227]
        expressions.append([
            middle[bit]
            ^ (predecessor[31] if bit == 30 else next_word[bit + 1] if bit < 30 else 0)
            ^ (next_word[0] if (MAG >> bit) & 1 else 0)
            for bit in range(32)
        ])
    return expressions


def reduce_row(row: int, basis: dict[int, int]) -> int:
    while row:
        pivot = row.bit_length() - 1
        existing = basis.get(pivot)
        if existing is None:
            break
        row ^= existing
    return row


def source_basis(expressions: list[list[int]], rows: list[list[int]]) -> dict[int, int]:
    basis: dict[int, int] = {}
    for r, row in enumerate(rows):
        for j, word in enumerate(row):
            for bit, expr in enumerate(expressions[STARTS[r] + j]):
                residue = reduce_row((expr << 1) | ((word >> bit) & 1), basis)
                assert residue != 1, ("inconsistent source", r, j, bit)
                if residue > 1:
                    basis[residue.bit_length() - 1] = residue
    return basis


def source_fixed_words(
    expressions: list[list[int]],
    basis: dict[int, int],
) -> list[tuple[int, int]]:
    values = []
    for word in expressions:
        known_mask = known_value = 0
        for bit, expr in enumerate(word):
            residue = reduce_row(expr << 1, basis)
            if residue <= 1:
                known_mask |= 1 << bit
                known_value |= residue << bit
        values.append((known_mask, known_value))
    return values


def coupons_for_stage(values: list[tuple[int, int]], stage: int):
    selected = values[stage:stage + 4]
    free = [(word, bit) for word, (mask, _) in enumerate(selected)
            for bit in range(32) if not (mask >> bit) & 1]
    if len(free) > 1:
        return
    for choice in range(1 << len(free)):
        native = [value for _, value in selected]
        for free_index, (word, bit) in enumerate(free):
            native[word] |= ((choice >> free_index) & 1) << bit
        coupon = b"".join(temper(word).to_bytes(4, "little") for word in native)
        yield coupon



def select_escrow_ack(lines: list[str], route_job: str):
    """Select the latest acknowledged RECOVER attempt from header fields only."""
    entries = []
    for index, line in enumerate(lines):
        matched = re.match(
            r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)",
            line,
        )
        if matched is None:
            continue
        timestamp, job, attempt, state, job_class = matched.groups()
        if job == route_job and state == "ACK" and job_class == "RECOVER":
            entries.append((int(attempt), timestamp, index))
    if not entries:
        raise ValueError("No historical ESC-N RECOVER ACK found")
    attempt, timestamp, index = max(entries, key=lambda item: (item[0], item[1]))
    return index, {"job": route_job, "attempt": attempt, "state": "ACK",
                   "class": "RECOVER", "timestamp": timestamp}


def source_rows(raw: bytes, root: Path):
    """Parse training payloads only after retaining the payload-independent selector."""
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == len(STARTS) == 133
    label = configparser.ConfigParser()
    label.read(root / "resources/evidence/archive-labels.ini", encoding="utf-8")
    route_job = label["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    selected_index, selected = select_escrow_ack(lines, route_job)
    assert selected_index == 129, selected
    assert (selected["attempt"], selected["timestamp"], STARTS[selected_index]) == (
        2, "2026-10-03T18:02:00Z", 951
    )
    rows = []
    for index, line in enumerate(lines):
        if index == selected_index:
            rows.append([])
            continue
        match = re.search(r"(?:^|\s)PAYLOAD=([0-9A-F]{32})(?=\s|$)", line)
        assert match is not None, ("missing intact training payload", index)
        rows.append([
            untemper(word)
            for word in struct.unpack("<4I", bytes.fromhex(match.group(1)))
        ])
    return lines, rows, selected_index, selected


def selector_adversarial_controls(raw: bytes, root: Path) -> None:
    lines = [line for line in raw.decode("ascii").splitlines()
             if line.startswith("2026-")]
    label = configparser.ConfigParser()
    label.read(root / "resources/evidence/archive-labels.ini", encoding="utf-8")
    route_job = label["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    selected_index, _ = select_escrow_ack(lines, route_job)
    assert selected_index == 129
    original = lines[selected_index]
    payload_match = re.search(r"\sPAYLOAD=[^ ]+", original)
    dest_match = re.search(r"\sDEST=[^ ]+", original)
    assert payload_match and dest_match

    variants = {
        "payload corrupted": original.replace(payload_match.group(0), " PAYLOAD=CORRUPT"),
        "payload absent": original.replace(payload_match.group(0), ""),
        "destination absent": original.replace(dest_match.group(0), ""),
        "payload and destination absent": original.replace(payload_match.group(0), "").replace(dest_match.group(0), ""),
        "destination changed": original.replace(dest_match.group(0), " DEST=desk"),
    }
    for name, changed in variants.items():
        altered = list(lines)
        altered[selected_index] = changed
        assert select_escrow_ack(altered, route_job)[0] == selected_index, name

    altered = list(lines)
    altered[selected_index] = original.replace("STATE=ACK", "STATE=REQUESTED")
    try:
        select_escrow_ack(altered, route_job)
    except ValueError:
        pass
    else:
        raise AssertionError("A REQUESTED event must not be selected as an ACK")

    # If a later attempt becomes ACK, the selector must follow that new ACK.
    altered = list(lines)
    altered[130] = altered[130].replace("STATE=REQUESTED", "STATE=ACK")
    assert select_escrow_ack(altered, route_job)[0] == 130

def main():
    root = Path(__file__).resolve().parents[2]
    raw = (root / "resources/evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    selector_adversarial_controls(raw, root)
    logs, rows, selected_index, selected_record = source_rows(raw, root)
    assert selected_index == 129 and STARTS[selected_index] == 951
    for value in (0, 1, 0xDEADBEEF, 0xFFFFFFFF):
        assert untemper(temper(value)) == value

    expressions = state_expressions(STARTS[-1] + 3)
    basis = source_basis(expressions, rows)
    assert len(basis) == 15365, len(basis)
    values = source_fixed_words(expressions, basis)

    # Retrospective original-metadata check on four inferred, never printed draws.
    hidden = list(coupons_for_stage(values, 697))
    assert len(hidden) == 1
    assert hidden[0].hex().upper() == "C9304FE833674EFD67B213839E4BA01D"
    printed = struct.unpack("<4I", hidden[0])
    assert [word >> 30 for word in printed[:3]] == [3, 3, 2]
    assert printed[3] >> 29 == 0
    assert "DEST=bench" in logs[93] and "CLASS=LABEL" in logs[94]

    route = json.loads((root / "resources/evidence/recovery-routing.json").read_text())
    acceptance = json.loads((root / "resources/acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    wanted = acceptance["slot_sha256"]["K04"]
    counts = {0: 0, 1: 0}
    checked = 0
    hits = []
    candidate_windows = []
    # Every possible complete four-draw start through the final intact source row.
    for stage in range(STARTS[-1] + 1):
        candidate_set = list(coupons_for_stage(values, stage) or ())
        if not candidate_set:
            continue
        unknown_bits = 0 if len(candidate_set) == 1 else 1
        counts[unknown_bits] += 1
        candidate_windows.append((stage, candidate_set))
        for coupon in candidate_set:
            reduced = bytes(a ^ b for a, b in zip(coupon, mask))
            checked += 1
            if hashlib.sha256(reduced).hexdigest() == wanted:
                hits.append((stage, coupon.hex().upper(), reduced.hex().upper()))

    assert counts == {0: 253, 1: 73}, counts
    assert checked == 399, checked

    # Independent synthetic commitment targeting one of the two stage-888 branches.
    stage888 = dict(candidate_windows)[888]
    assert len(stage888) == 2 and stage888[0] != stage888[1]
    planted = hashlib.sha256(stage888[1]).hexdigest()
    assert sum(hashlib.sha256(c).hexdigest() == planted for _, cs in candidate_windows
               for c in cs) == 1

    print("SELECTED_HEADER_ONLY", selected_index, selected_record)
    print("SELECTOR_ADVERSARIAL_CONTROLS", "PASS: payload corrupt/absent, destination absent/changed, ACK status and attempt controls")
    print("SOURCE_SHA", SOURCE_SHA)
    print("MT_SOURCE_RANK", len(basis))
    print("HIDDEN_697", hidden[0].hex().upper(), "DEST_reject,reject,bench CLASS_label PASS")
    print("WINDOWS_FULLY_DETERMINED", counts[0])
    print("WINDOWS_ONE_UNKNOWN_BIT", counts[1])
    print("ORIGINAL_K04_CANDIDATES", checked)
    print("ORIGINAL_K04_MATCHES", len(hits), hits)
    print("PLANTED_STAGE888_POSITIVE", "PASS")


if __name__ == "__main__":
    main()
