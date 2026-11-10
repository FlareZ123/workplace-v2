"""Source-pinned selected K04 ACK2 MT native/tempered representation probe.

Read-only: pass a resources directory or use repository resources/.
The selected spool bytes are unverified; no physical coupon is asserted.
"""
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path

SPOOL_SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
K04_SHA = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
M32 = 0xffffffff


def temper(value):
    value ^= value >> 11
    value ^= (value << 7) & 0x9d2c5680
    value ^= (value << 15) & 0xefc60000
    value ^= value >> 18
    return value & M32


def undo_right(value, shift):
    result = value
    for _ in range(5):
        result = value ^ (result >> shift)
    return result & M32


def undo_left(value, shift, mask):
    result = value
    for _ in range(5):
        result = value ^ ((result << shift) & mask)
    return result & M32


def untemper(value):
    value = undo_right(value, 18)
    value = undo_left(value, 15, 0xefc60000)
    value = undo_left(value, 7, 0x9d2c5680)
    return undo_right(value, 11)


def xor(left, right):
    return bytes(x ^ y for x, y in zip(left, right))


def main(resources):
    spool = (resources / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(spool).hexdigest() == SPOOL_SHA
    routes = json.loads((resources / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(routes["K04"]["masked_component"])
    acceptance = json.loads((resources / "acceptance.json").read_text())
    assert acceptance["slot_sha256"]["K04"] == K04_SHA
    labels = (resources / "evidence/archive-labels.ini").read_text()
    job = re.search(r"^ESC-N=(PS-[0-9-]+)$", labels, re.M).group(1)
    selected = [line for line in spool.decode().splitlines()
                if "JOB=" + job + " " in line
                and "STATE=ACK" in line and "CLASS=RECOVER" in line]
    assert len(selected) == 1
    fields = dict(re.findall(r"([A-Z]+)=([^ ]+)", selected[0]))
    assert fields["ATTEMPT"] == "2"
    copied = bytes.fromhex(fields["PAYLOAD"])
    assert len(copied) == 16
    assert all(untemper(temper(x)) == x for x in
               (0, 1, 0x12345678, 0xDEADBEEF, M32))

    operations = {"identity": lambda x: x, "temper": temper,
                  "untemper": untemper, "complement": lambda x: x ^ M32}
    seen = set()
    examples = {}
    for mask_first in (False, True):
        raw = xor(copied, mask) if mask_first else copied
        for source_endian, final_endian in itertools.product(("big", "little"), repeat=2):
            words = [int.from_bytes(raw[i:i + 4], source_endian)
                     for i in (0, 4, 8, 12)]
            for name, operator in operations.items():
                transformed = [operator(x) for x in words]
                for permutation in itertools.permutations(range(4)):
                    output = b"".join(transformed[p].to_bytes(4, final_endian)
                                      for p in permutation)
                    component = output if mask_first else xor(output, mask)
                    seen.add(component)
                    examples.setdefault(name, component)
    assert len(seen) == 574, len(seen)
    actual_hits = sorted(value.hex().upper() for value in seen
                         if hashlib.sha256(value).hexdigest() == K04_SHA)
    assert not actual_hits, actual_hits
    planted = examples["untemper"]
    synthetic_target = hashlib.sha256(planted).hexdigest()
    assert sum(hashlib.sha256(value).hexdigest() == synthetic_target
               for value in seen) == 1
    print(json.dumps({"source_sha256": SPOOL_SHA, "job": job,
                      "complete_distinct_components": len(seen),
                      "original_k04_matches": len(actual_hits),
                      "planted_complete_component_matches": 1}, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources"))
