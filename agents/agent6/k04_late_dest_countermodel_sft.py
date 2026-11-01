"""SFT: competing late-DEST bit-slice models for the original H-17 printer.

Read-only. The selected row129 PAYLOAD and all acceptance data are excluded
from feature selection and ordinary/late control scoring. The copied row is
opened only afterward for a countermodel comparison.
"""
import hashlib
import re
import sys
from zipfile import ZipFile

SPOOL = "evidence/print/spool-reconstruction.log"
SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
DEST = {"store": 0, "desk": 1, "bench": 2}
LATE_CONTROL_EDGES = (127, 128, 130, 131)
SELECTED = 129


def field(line: str, name: str) -> str:
    match = re.search(r"\b" + re.escape(name) + r"=([A-Za-z0-9]+)", line)
    assert match is not None, (name, line)
    return match.group(1)


def code(payload: bytes, byte_index: int, shift: int) -> int:
    return (payload[byte_index] >> shift) & 3


def main(zip_path: str) -> None:
    with ZipFile(zip_path) as archive:
        spool = archive.read(SPOOL)
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    lines = [line for line in spool.decode("ascii").splitlines()
             if line.startswith("2026-")]
    assert len(lines) == 133
    dest = [DEST[field(line, "DEST")] for line in lines]
    klass = [field(line, "CLASS") for line in lines]

    # Strict selected-target holdout while testing all 112 simple two-bit slices.
    payload = [bytes.fromhex(field(line, "PAYLOAD")) if i != SELECTED else None
               for i, line in enumerate(lines)]
    assert all(len(raw) == 16 for raw in payload if raw is not None)
    assert code(bytes.fromhex("00000000000020000000000000000080"), 6, 4) == 2
    assert code(bytes.fromhex("00000000000020000000000000000080"), 15, 6) == 2

    same_recover = [i for i in range(127)
                    if klass[i] == klass[i + 1] == "RECOVER"]
    assert len(same_recover) == 11

    perfect = []
    histogram = [0] * 5
    for byte_index in range(16):
        for shift in range(7):
            late_hits = sum(
                code(payload[i], byte_index, shift) == dest[i + 1]
                for i in LATE_CONTROL_EDGES
            )
            histogram[late_hits] += 1
            if late_hits == 4:
                early_hits = sum(
                    code(payload[i], byte_index, shift) == dest[i + 1]
                    for i in same_recover
                )
                perfect.append((byte_index, shift, early_hits))

    assert histogram == [36, 52, 18, 4, 2], histogram
    assert perfect == [(6, 4, 4), (15, 6, 2)], perfect
    print("source_spool_sha256", SPOOL_SHA)
    print("four_late_controls", LATE_CONTROL_EDGES)
    print("tested_simple_two_bit_slices", 16 * 7)
    print("late_control_match_histogram_0_to_4", histogram)
    print("perfect_late_control_features_and_ordinary_sameclass_hits", perfect)

    # Diagnostic only. The copied selected bytes are not integrity-certified.
    selected_copied = bytes.fromhex(field(lines[SELECTED], "PAYLOAD"))
    assert dest[SELECTED + 1] == DEST["bench"]
    for byte_index, shift, early_hits in perfect:
        value = code(selected_copied, byte_index, shift)
        print("conditional_feature", (byte_index, shift),
              "ordinary_RECOVER_to_RECOVER", f"{early_hits}/{len(same_recover)}",
              "selected_copied_code", value,
              "next_record_dest", dest[SELECTED + 1],
              "selected_copied_agrees", value == dest[SELECTED + 1])

    assert code(selected_copied, 6, 4) == 2
    assert code(selected_copied, 15, 6) == 3
    print("historically_authenticated_selected_bits", "0/128")
    print("K04_component_recovered", False)
    print("acceptance_or_mask_consulted", False)


if __name__ == "__main__":
    assert len(sys.argv) == 2, "usage: python k04_late_dest_countermodel_sft.py original.zip"
    main(sys.argv[1])
