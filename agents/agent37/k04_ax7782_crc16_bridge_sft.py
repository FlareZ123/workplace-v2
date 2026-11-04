"""K04 selected AX-7782 checkpoint-to-coupon CRC16 serializer hypothesis; source read-only."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("H17_RESOURCE_ROOT", Path(__file__).resolve().parents[2] / "resources"))
TRANSFER_PIN = "32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf"
K04 = "930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0"
MASK = "8556C8CB6140A7F9A5123AC7571BEE1C"
K07_RAW = "8947CEDCB9CC73BAB7E87BE63302C5C9"


def crc16(data: bytes, poly: int, init: int, reflect: bool, xorout: int) -> int:
    c = init
    for ch in data:
        if reflect:
            c ^= ch
            for _ in range(8):
                c = (c >> 1) ^ poly if c & 1 else c >> 1
        else:
            c ^= ch << 8
            for _ in range(8):
                c = ((c << 1) ^ poly) & 65535 if c & 32768 else (c << 1) & 65535
    return c ^ xorout


MODES = [
    ("ccitt0", 0x1021, 0, False, 0),
    ("ccittF", 0x1021, 65535, False, 0),
    ("x25", 0x8408, 65535, True, 65535),
    ("ibm0", 0xA001, 0, True, 0),
    ("ibmF", 0xA001, 65535, True, 0),
    ("dnp", 0xA6BC, 0, True, 65535),
    ("kermit", 0x8408, 0, True, 0),
    ("modbus", 0xA001, 65535, True, 0),
]


def main() -> None:
    transfer = (ROOT / "evidence/transfers/transfer-audit.jsonl").read_bytes()
    assert hashlib.sha256(transfer).hexdigest() == TRANSFER_PIN
    selected = {}
    for line in transfer.splitlines():
        row = json.loads(line)
        if row.get("kind") == "CHUNK" and row.get("transfer") == "AX-7782":
            if row["seq"] not in selected or row["attempt"] > selected[row["seq"]]["attempt"]:
                selected[row["seq"]] = row
    assert sorted(selected) == list(range(8))
    raw16 = bytes.fromhex("".join(selected[i]["checkpoint"] for i in range(8)))
    assert raw16.hex().upper() == K07_RAW
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    assert hashlib.sha256(raw16).hexdigest()[:32].upper() == "93495F5E425AB8E592123DABAEB68545"
    assert acceptance["slot_sha256"]["K04"] == K04

    mask = bytes.fromhex(MASK)
    hits = []
    assignments = 0
    for name, *args in MODES:
        forward = [crc16(i.to_bytes(2, "big"), *args) for i in range(65536)]
        assert len(set(forward)) == 65536, name
        inverse = [0] * 65536
        for i, c in enumerate(forward):
            inverse[c] = i
        planted = bytes.fromhex("01FE02FD03FC04FB05FA06F907F808F7")
        encoded = b"".join(crc16(planted[j:j+2], *args).to_bytes(2, "big")
                           for j in range(0, 16, 2))
        recovered = b"".join(inverse[int.from_bytes(encoded[j:j+2], "big")].to_bytes(2, "big")
                             for j in range(0, 16, 2))
        assert recovered == planted
        for reverse_direction in (False, True):
            lookup = inverse if reverse_direction else forward
            for reverse_order in (False, True):
                for rotate in range(8):
                    pairs = [raw16[j:j+2] for j in range(0, 16, 2)]
                    if reverse_order:
                        pairs.reverse()
                    pairs = pairs[rotate:] + pairs[:rotate]
                    for input_mask in range(256):
                        words = [int.from_bytes(p, "little" if input_mask >> i & 1 else "big")
                                 for i, p in enumerate(pairs)]
                        transformed = [lookup[v] for v in words]
                        for endian in ("big", "little"):
                            coupon = b"".join(v.to_bytes(2, endian) for v in transformed)
                            component = bytes(a ^ b for a, b in zip(coupon, mask))
                            assignments += 1
                            if hashlib.sha256(component).hexdigest() == K04:
                                hits.append({"crc": name, "inverse": reverse_direction,
                                             "coupon": coupon.hex().upper(),
                                             "component": component.hex().upper()})
    assert assignments == 131072
    print(json.dumps({"complete_original_K04_checks": assignments,
                      "original_hits": hits, "planted_crc16_positives": len(MODES)}))
    assert not hits, hits


if __name__ == "__main__":
    main()
