"""H17 original source K04: common stuck-byte copier channel across arbitrary positions."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"
SPOOL_HASH = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
SELECTED = "A9A9DC5731A5E2AE879C47215C2559D5"
MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
TARGET = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"


def search(copied: bytes, mask: bytes, target: bytes, mode: str, masks):
    checks = 0
    for stuck_mask in masks:
        state = bytearray(a ^ b for a, b in zip(copied, mask))
        for counter in range(1, 1 << 16):
            index = (counter & -counter).bit_length() - 1
            changed = counter ^ (counter >> 1)
            if changed & (1 << index):
                byte = (copied[index] | stuck_mask) if mode == "OR" else (
                    copied[index] & (255 ^ stuck_mask)
                )
            else:
                byte = copied[index]
            state[index] = byte ^ mask[index]
            checks += 1
            if hashlib.sha256(state).digest() == target:
                return checks, (stuck_mask, changed, bytes(state))
    return checks, None


def main():
    raw = (ROOT / "evidence/print/spool-reconstruction.log").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SPOOL_HASH
    lines = [
        x for x in raw.decode("ascii").splitlines()
        if all(part in x for part in (
            "JOB=PS-261003-0417", "ATTEMPT=2", "STATE=ACK", "CLASS=RECOVER"
        ))
    ]
    assert len(lines) == 1
    copied = bytes.fromhex(re.search(r"PAYLOAD=([0-9A-F]{32})", lines[0]).group(1))
    assert copied.hex().upper() == SELECTED
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    assert mask.hex().upper() == MASK
    accept = json.loads((ROOT / "acceptance.json").read_text())
    assert accept["slot_sha256"]["K04"] == TARGET
    target = bytes.fromhex(TARGET)

    total = 0
    for mode in ("OR", "AND"):
        count, hit = search(copied, mask, target, mode, range(1, 256))
        assert count == 255 * ((1 << 16) - 1) or hit is not None
        total += count
        print(f"ORIGINAL {mode} checks={count} accepted={hit}")
    assert total == 33_422_850

    damaged = bytes.fromhex("73C930745EFB029D33E8197A50AEFC22")
    selected_positions = (0, 1, 3, 4, 5, 8, 10, 12, 14, 15)
    for mode, bitmask in (("OR", 0x25), ("AND", 0xA4)):
        coupon = bytearray(damaged)
        for pos in selected_positions:
            coupon[pos] = ((damaged[pos] | bitmask) if mode == "OR"
                           else (damaged[pos] & (255 ^ bitmask)))
        component = bytes(a ^ b for a, b in zip(coupon, mask))
        planted_digest = hashlib.sha256(component).digest()
        positive_count, hit = search(damaged, mask, planted_digest, mode, [bitmask])
        assert hit is not None and hit[2] == component
        print(f"SYNTHETIC {mode} full_coupon_recovered=True checks={positive_count}")

    print("DONE: original K04 NO_MATCH, two planted full-copy controls PASS")


if __name__ == "__main__":
    main()
