"""Bounded K04 test of the +300/+304 PTW predecessor quartets with PTW-417.

The 7 source-derived 16-byte blocks are tested as ordered pairs of native MT
donors for the existing p951 eight-stage bridge. Each donor independently
gets little/big word byte order, forward/reversed word order, and native/
inverse-tempered interpretation. This is a finite hypothesis test, not a
claim that PTW serials are MT state words or that either ST offset is true.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from itertools import permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.agent49.k04_p951_symbolic_basis import ORIGIN, source, temper, untemper


STAGES = (328, 329, 330, 331, 724, 725, 726, 727)


def source_blocks():
    evidence = ROOT / "resources" / "evidence"
    receipts = {}
    for line in (evidence / "maintenance" / "seal-receipts.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            pid = int(row["permit"].split("-")[1])
            receipts.setdefault(pid, []).append(row)

    def serial(pid: int) -> bytes:
        rows = receipts[pid]
        if len(rows) != 1:
            raise AssertionError(f"PTW-{pid} is not a singleton receipt")
        return bytes.fromhex(rows[0]["serial"].removeprefix("SG-"))

    north_ticket_order = (94, 106, 99, 112)
    old300_ticket = b"".join(serial(ticket + 300) for ticket in north_ticket_order)
    old300_bay = b"".join(serial(pid) for pid in (394, 412, 406, 399))
    old300_field = b"".join(serial(pid) for pid in (412, 399, 394, 406))

    old304_ticket = b"".join(serial(ticket + 304) for ticket in north_ticket_order)
    old304_field = b"".join(serial(pid) for pid in (410, 416, 398, 403))

    current_by_bay = {}
    for row in receipts[417]:
        if row.get("state") == "CLOSED" and row.get("fitment") == "AS_LEFT" and row.get("signed") is True:
            bay = row["bay"]
            if bay not in current_by_bay or int(row["revision"]) > int(current_by_bay[bay]["revision"]):
                current_by_bay[bay] = row
    if set(current_by_bay) != set("ABCD"):
        raise AssertionError("PTW-417 does not provide one latest signed as-left serial per bay")

    new_field = b"".join(bytes.fromhex(current_by_bay[bay]["serial"].removeprefix("SG-")) for bay in "BDAC")
    new_bays = b"".join(bytes.fromhex(current_by_bay[bay]["serial"].removeprefix("SG-")) for bay in "ABCD")

    blocks = {
        "old300_ticket_order": old300_ticket,
        "old300_bay_ABCD": old300_bay,
        "old300_field_BDAC": old300_field,
        "old304_ticket_order": old304_ticket,
        "old304_field_BDAC": old304_field,
        "new417_field_BDAC": new_field,
        "new417_bay_ABCD": new_bays,
    }
    if any(len(value) != 16 for value in blocks.values()):
        raise AssertionError("Each donor candidate must be 16 bytes")
    return blocks, receipts


def target_formulas():
    base_basis, symbolic = source(ROOT / "resources")
    if base_basis.rank != 15365:
        raise AssertionError(f"Unexpected p951 source rank: {base_basis.rank}")

    basis = copy.deepcopy(base_basis)
    for index, stage in enumerate(STAGES):
        for bit, expression in enumerate(symbolic[stage - ORIGIN]):
            basis.insert(expression, 1 << (1 + 32 * index + bit))
    if basis.rank != 15621:
        raise AssertionError(f"Unexpected eight-native-word donor rank: {basis.rank}")

    formulas = []
    for stage in range(951, 955):
        projected = [basis.predict(expression) for expression in temper(symbolic[stage - ORIGIN])]
        if any(value is None for value in projected):
            raise AssertionError("The eight native donor words do not determine the selected payload")
        formulas.append(projected)
    return base_basis, symbolic, formulas


def ptw_bay_selector_check(base_basis, symbolic, receipts):
    anchors = ((405, -964, "D"), (412, -944, "B"), (414, -937, "C"))
    constrained = copy.deepcopy(base_basis)
    for permit, serial_stage, bay in anchors:
        row = receipts[permit][0]
        serial_bytes = bytes.fromhex(row["serial"].removeprefix("SG-"))
        observed_output = int.from_bytes(serial_bytes, "little")
        serial_forms = temper(symbolic[serial_stage - ORIGIN])
        predicted_bits = [base_basis.predict(form) for form in serial_forms]
        if any(value is None for value in predicted_bits):
            raise AssertionError(f"PTW-{permit} serial stage is not fully source-predicted")
        predicted_output = sum(value << bit for bit, value in enumerate(predicted_bits))
        if predicted_output != observed_output:
            raise AssertionError(f"PTW-{permit} serial does not match its source-predicted stage")

        bay_stage = serial_stage - 1
        bay_forms = temper(symbolic[bay_stage - ORIGIN])[29:32]
        prior_bits = [base_basis.predict(form) for form in bay_forms]
        bay_value = ord(bay) - ord("A")
        for bit, form in enumerate(bay_forms):
            constrained.insert(form, (bay_value >> bit) & 1)
        print(f"PTW-{permit}: serial_stage={serial_stage}, bay_stage={bay_stage}, prior_top3={prior_bits}, recorded_bay={bay}({bay_value})")

    target_known = sum(
        constrained.predict(form) is not None
        for stage in range(951, 955)
        for form in temper(symbolic[stage - ORIGIN])
    )
    print(f"bay_constraint_rank={constrained.rank}, rank_gain={constrained.rank - base_basis.rank}, target_bits_known={target_known}/128")


def parse_donor(raw: bytes, endian: str, reverse_words: bool, inverse_temper: bool) -> list[int]:
    words = [int.from_bytes(raw[index:index + 4], endian) for index in range(0, 16, 4)]
    if reverse_words:
        words.reverse()
    if inverse_temper:
        words = [untemper(word) for word in words]
    return words


def complete_coupon(left: list[int], right: list[int], formulas) -> bytes:
    donor_bits = sum(word << (32 * index) for index, word in enumerate(left + right))
    output = []
    for formula in formulas:
        native = sum(
            (((term & 1) ^ (((term >> 1) & donor_bits).bit_count() & 1)) << bit)
            for bit, term in enumerate(formula)
        )
        tempered = temper([(native >> bit) & 1 for bit in range(32)])
        output.append(sum(value << bit for bit, value in enumerate(tempered)))
    return b"".join(word.to_bytes(4, "little") for word in output)


def main() -> None:
    blocks, receipts = source_blocks()
    base_basis, symbolic, formulas = target_formulas()
    ptw_bay_selector_check(base_basis, symbolic, receipts)
    evidence = ROOT / "resources" / "evidence"
    route = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ROOT / "resources" / "acceptance.json").read_text(encoding="utf-8"))
    mask = bytes.fromhex(route["K04"]["masked_component"])
    target_digest = acceptance["slot_sha256"]["K04"].lower()

    views = list(product(("little", "big"), (False, True), (False, True)))
    models = 0
    components = set()
    hits = []

    for left_name, right_name in permutations(blocks, 2):
        for left_endian, left_reverse, left_inverse in views:
            left = parse_donor(blocks[left_name], left_endian, left_reverse, left_inverse)
            for right_endian, right_reverse, right_inverse in views:
                right = parse_donor(blocks[right_name], right_endian, right_reverse, right_inverse)
                coupon = complete_coupon(left, right, formulas)
                component = bytes(value ^ mask[index] for index, value in enumerate(coupon))
                models += 1
                components.add(component)
                digest = hashlib.sha256(component).hexdigest()
                if digest == target_digest:
                    hits.append((left_name, right_name, coupon.hex().upper(), component.hex().upper()))

    expected_models = len(blocks) * (len(blocks) - 1) * 64
    if models != expected_models or len(components) != models:
        raise AssertionError(f"Unexpected donor enumeration: models={models}, distinct={len(components)}")

    print("p951_source_rank=15365")
    print(f"native_donor_stages={STAGES}")
    for name, block in blocks.items():
        print(f"{name}={block.hex().upper()}")
    print(f"ordered_donor_pairs={models}, distinct_components={len(components)}, K04_matches={len(hits)}")
    if hits:
        print("MATCHES:", hits)
    else:
        print("No tested PTW predecessor/current quartet pair matches the official K04 commitment.")


if __name__ == "__main__":
    main()
