"""Source-only K03 seal serial → MT19937 printer ancestor discriminator.

Holds out selected RECOVER attempt 2. No hashes, mask, or target consulted.
Designed as an early kill test for a previously untested original control class.
Run from the checked-out repository with standard Python 3.
"""
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
KNOWN_HASHES = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "maintenance/seal-receipts.jsonl": "c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32",
    "recorder/trip-recorder.raw": "5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba",
}


def source_bytes(path):
    value = (ROOT / path).read_bytes()
    assert hashlib.sha256(value).hexdigest() == KNOWN_HASHES[path], path
    return value


def untemper(value):
    original = value
    for shift, mask, direction in ((18, 0xFFFFFFFF, "right"),
                                   (15, 0xEFC60000, "left"),
                                   (7, 0x9D2C5680, "left"),
                                   (11, 0xFFFFFFFF, "right")):
        x = original
        for _ in range(6):
            if direction == "right":
                x = original ^ (x >> shift)
            else:
                x = original ^ ((x << shift) & mask)
        original = x & 0xFFFFFFFF
    return original


def successor_low31(middle, end):
    """Inverse twist: X[k+397] and X[k+624] fix X[k+1].low31."""
    delta = middle ^ end
    bit = delta >> 31
    shifted = delta ^ (0x9908B0DF if bit else 0)
    return (((shifted << 1) & 0xFFFFFFFF) | bit) & 0x7FFFFFFF


def spool_rows():
    rows = {}
    lines = source_bytes("print/spool-reconstruction.log").decode().splitlines()
    assert len(lines) == 134
    for index, line in enumerate(lines[1:]):
        if index == 129:  # exact disputed selected ACK line: never add its words
            assert "PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER" in line
            continue
        m = re.search(r"PAYLOAD=([0-9A-F]{32})", line)
        assert m, (index, line)
        b = bytes.fromhex(m.group(1))
        rows[index] = tuple(untemper(int.from_bytes(b[j:j + 4], "little"))
                            for j in (0, 4, 8, 12))
    assert len(rows) == 132
    return rows


def printer_fingerprints(rows):
    seen = {}
    for i, words_i in rows.items():
        for j, words_j in rows.items():
            if j <= i:
                continue
            for a, middle in enumerate(words_i):
                for b, end in enumerate(words_j):
                    key = successor_low31(middle, end)
                    seen.setdefault(key, []).append((i, a, j, b))
    assert sum(len(v) for v in seen.values()) == 138336
    return seen


def fullword_tokens():
    seals = []
    rows = source_bytes("maintenance/seal-receipts.jsonl").decode().splitlines()
    for row in rows:
        record = json.loads(row)
        serial = record["serial"]
        assert serial.startswith("SG-") and len(serial) == 11
        b = bytes.fromhex(serial[3:])
        for endian in ("little", "big"):
            seals.append((serial, endian,
                          untemper(int.from_bytes(b, endian)) & 0x7FFFFFFF))
    assert len(rows) == 44 and len(set(x[0] for x in seals)) == 44
    return seals


def original_recorder_control():
    raw = source_bytes("recorder/trip-recorder.raw")
    assert raw[:8] == b"TRP2DUMP" and len(raw) == 16 + 88 * 24
    # Previously established original full-source positive witness:
    # little-endian TRP2 record 28 -> printer row 10 word 0 / row 41 word 0
    b = raw[16 + 28 * 24 + 12:16 + 28 * 24 + 16]
    return untemper(int.from_bytes(b, "little")) & 0x7FFFFFFF


def synthetic_positive_control():
    rng = random.Random(20261020)
    words = [untemper(rng.getrandbits(32)) for _ in range(625)]
    assert successor_low31(words[397], words[624]) == (words[1] & 0x7FFFFFFF)


def main():
    synthetic_positive_control()
    fingerprints = printer_fingerprints(spool_rows())
    control = original_recorder_control()
    assert (10, 0, 41, 0) in fingerprints.get(control, []), (
        "historical withheld cross-carrier positive control failed"
    )
    seals = fullword_tokens()
    matches = [(serial, endian, fingerprints[low31])
               for serial, endian, low31 in seals if low31 in fingerprints]
    print(f"source: 132 original intact spool rows, 44 independently recorded seal serials")
    print(f"index: {sum(map(len, fingerprints.values()))} distinct ordered printer-pair / word comparisons")
    print("control: synthetic MT and original independent TRP2 record28 PASS")
    print(f"seal checks: {len(seals)} (44 IDs × two byte orientations)")
    print(f"seal→printer low31 recurrence matches: {len(matches)}")
    for row in matches:
        print(row)
    assert matches == [], "a new candidate independent donor must be investigated"


if __name__ == "__main__":
    main()
