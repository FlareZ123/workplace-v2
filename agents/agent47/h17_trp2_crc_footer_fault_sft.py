"""Original-source TRP2 CRC-invalid row fingerprint and conditional K04 copier test.

Read-only single runnable Python 3 test. It discovers a shared single-bit
CRC-footer defect in four node49 recorder rows, withholding the fourth as
a control. A speculative printer word-lane transfer is tested separately.
"""
import hashlib
import itertools
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
raw = (ROOT / "evidence/recorder/trip-recorder.raw").read_bytes()
spool = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == (
    "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba"
)
assert hashlib.sha256(spool).hexdigest() == (
    "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
)
assert struct.unpack_from("<8sHHI", raw) == (b"TRP2DUMP", 2, 24, 88)
records = [bytearray(raw[16 + 24 * i:16 + 24 * (i + 1)]) for i in range(88)]


def crc_valid(record):
    return zlib.crc32(record[:20]) == struct.unpack_from("<I", record, 20)[0]


def one_bit_repairs(record):
    out = []
    for position in range(24):
        for bit in range(8):
            repaired = record.copy()
            repaired[position] ^= 1 << bit
            if crc_valid(repaired):
                out.append((position, bit))
    return out


bad = []
for row in records:
    if crc_valid(row):
        continue
    seq = struct.unpack_from("<I", row, 8)[0]
    stored_crc = struct.unpack_from("<I", row, 20)[0]
    syndrome = stored_crc ^ zlib.crc32(row[:20])
    bad.append((seq, syndrome, one_bit_repairs(row)))

assert len(bad) == 4 and sum(map(crc_valid, records)) == 84
assert [seq for seq, _, _ in bad] == [900, 901, 902, 903]
assert all(syndrome == 0x00000100 and repairs == [(21, 0)]
           for _, syndrome, repairs in bad)
learned = {(position, bit) for seq, _, repairs in bad
           if seq in (900, 901, 902) for position, bit in repairs}
assert learned == {(21, 0)}
assert bad[-1][2] == sorted(learned)
print("TRP2_original_sha256=PASS records=88 good_CRC=84 bad_CRC=4")
for seq, syndrome, repairs in bad:
    print(f"seq={seq} syndrome=0x{syndrome:08X} "
          f"only_single_bit_repair={repairs}")
print("blinded_fourth_bad_CRC_seq903_single_bit_prediction=PASS")

route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
accept = json.loads((ROOT / "acceptance.json").read_text())
rows = []
for line in spool.decode("utf-8").splitlines():
    if not line.startswith("2026"):
        continue
    _, *fields = line.split()
    rows.append(dict(item.split("=", 1) for item in fields))
selected = [row for row in rows if
            (row["JOB"], row["ATTEMPT"], row["STATE"], row["CLASS"]) ==
            ("PS-261003-0417", "2", "ACK", "RECOVER")]
assert len(rows) == 133 and len(selected) == 1
copied = bytes.fromhex(selected[0]["PAYLOAD"])
mask = bytes.fromhex(route["K04"]["masked_component"])
wanted = accept["slot_sha256"]["K04"]
assert copied.hex().upper() == "A9A9DC5731A5E2AE879C47215C2559D5"
assert len(mask) == 16


def masked_component(printed):
    return bytes(a ^ b for a, b in zip(printed, mask))


def flip_common_recorder_lane(indices):
    printed = bytearray(copied)
    for word_index in indices:
        printed[4 * word_index + 1] ^= 1
    return bytes(printed)


# This extrapolation is speculative and its sixteen candidates are already
# contained in predecessor exhaustive <=4 whole-byte copier repairs.
source_hit = []
planted_hit = []
plant_pattern = (0, 2)
plant_hash = hashlib.sha256(
    masked_component(flip_common_recorder_lane(plant_pattern))).hexdigest()
for toggles in itertools.product((False, True), repeat=4):
    pattern = tuple(i for i, enabled in enumerate(toggles) if enabled)
    digest = hashlib.sha256(
        masked_component(flip_common_recorder_lane(pattern))).hexdigest()
    if digest == wanted:
        source_hit.append(pattern)
    if digest == plant_hash:
        planted_hit.append(pattern)
assert source_hit == [] and planted_hit == [plant_pattern]
print("speculative_printer_transfer_assignments=16 original_K04_hits=0 "
      "synthetic_recovery_hits=1 (prior copier radius subset)")
