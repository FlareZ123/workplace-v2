"""Source-withheld two-bit same-payload CLASS/DEST classifier falsifier.

This is deliberately narrower than the cross-draw MT19937 metadata models.
It excludes a direct contiguous two-bit selector within the corresponding payload.
"""
import hashlib
import re
from pathlib import Path

SPOOL_SHA256 = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED = ("PS-261003-0417", "2", "ACK", "RECOVER")
FIELDS = ("CLASS", "DEST")


def eligible_offsets(rows, field):
    matches = []
    for offset in range(127):
        codes = {}
        for row in rows:
            code = (int.from_bytes(row["payload"], "little") >> offset) & 3
            codes.setdefault(code, set()).add(row[field])
        if all(len(labels) == 1 for labels in codes.values()):
            matches.append(offset)
    return matches


def synthetic_control():
    rows = []
    for i in range(132):
        payload = bytearray(hashlib.sha256(str(i).encode("ascii")).digest()[:16])
        class_code, dest_code = i % 3, (i // 3) % 3
        payload[0] = (payload[0] & 0xFC) | class_code
        payload[1] = (payload[1] & 0xFC) | dest_code
        rows.append({"payload": bytes(payload), "CLASS": str(class_code), "DEST": str(dest_code)})
    assert 0 in eligible_offsets(rows, "CLASS")
    assert 8 in eligible_offsets(rows, "DEST")
    print("SYNTHETIC_SAME_PAYLOAD_TWO_BIT_CODES PASS")


def original_rows(path):
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_SHA256
    rows, omitted = [], 0
    for line in raw.decode("ascii").splitlines():
        if "PAYLOAD=" not in line:
            continue
        fields = dict(re.findall(r"(JOB|ATTEMPT|STATE|CLASS|DEST|PAYLOAD)=([^ ]+)", line))
        if tuple(fields[k] for k in ("JOB", "ATTEMPT", "STATE", "CLASS")) == SELECTED:
            omitted += 1
            continue
        payload = bytes.fromhex(fields["PAYLOAD"])
        assert len(payload) == 16
        rows.append({"payload": payload, "CLASS": fields["CLASS"], "DEST": fields["DEST"]})
    assert omitted == 1 and len(rows) == 132
    return rows


def main():
    synthetic_control()
    source = Path("resources/evidence/print/spool-reconstruction.log")
    if not source.is_file():
        source = Path("evidence/print/spool-reconstruction.log")
    rows = original_rows(source)
    for field in FIELDS:
        matches = eligible_offsets(rows, field)
        assert not matches, (field, matches)
        print(f"ORIGINAL_{field}_DIRECT_TWO_BIT_OFFSETS 0/127; source rows 132")
    print("K04_BITS_RECOVERED 0; K08_WORDS_RECOVERED 0")


if __name__ == "__main__":
    main()
