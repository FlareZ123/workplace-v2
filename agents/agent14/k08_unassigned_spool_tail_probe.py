#!/usr/bin/env python3
"""Probe the unassigned PS-0325..0336 spool tail without treating it as K08 text."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROW = re.compile(
    r"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK CLASS=(\w+) "
    r"PAYLOAD=([0-9A-F]{32}) DEST=(\w+)"
)


def pack(bits: list[int], lsb_first: bool = True) -> bytes:
    out = []
    for i in range(0, len(bits) - 7, 8):
        group = bits[i:i + 8]
        if lsb_first:
            out.append(sum(bit << j for j, bit in enumerate(group)))
        else:
            out.append(sum(bit << (7 - j) for j, bit in enumerate(group)))
    return bytes(out)


def lowbit_selector(payload: bytes) -> tuple[str, int]:
    low = pack([byte & 1 for byte in payload])
    hex_text = low.hex().upper()
    selector = sum((ord(char) & 1) << i for i, char in enumerate(hex_text))
    return hex_text, selector


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spool",
        type=Path,
        default=Path("resources/evidence/print/spool-reconstruction.log"),
    )
    args = parser.parse_args()
    rows = {}
    for line in args.spool.read_text(encoding="utf-8").splitlines():
        match = ROW.search(line)
        if not match:
            continue
        job = int(match.group(1))
        if 325 <= job <= 336:
            rows[job] = (
                match.group(2),
                bytes.fromhex(match.group(3)),
                match.group(4),
            )
    if sorted(rows) != list(range(325, 337)):
        raise SystemExit("expected exactly PS-0325..PS-0336 ACK1 rows")

    bits = []
    selectors = []
    for job in range(325, 337):
        cls, payload, dest = rows[job]
        low_hex, selector = lowbit_selector(payload)
        selectors.append(selector)
        bits.extend(byte & 1 for byte in payload)
        print(
            f"PS-{job:04d} {cls}/{dest} low={low_hex} selector={selector}"
        )

    lsb = pack(bits, True)
    msb = pack(bits, False)
    printable = lambda data: "".join(chr(x) if 32 <= x < 127 else "." for x in data)
    print("selectors", selectors)
    print("LSB_STREAM", lsb.hex().upper(), repr(printable(lsb)))
    print("MSB_STREAM", msb.hex().upper(), repr(printable(msb)))
    print("LIMIT: PS-0325..0336 have no authenticated N25..N36 note/job mapping.")


if __name__ == "__main__":
    main()
