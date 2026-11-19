#!/usr/bin/env python3
"""K08 HMAC MILK/STORES cycle and N14 spool bridge."""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
NOTES = EVIDENCE / "crew/noticeboard-and-desk-notes.txt"
SPOOL = EVIDENCE / "print/spool-reconstruction.log"
ROUTING = EVIDENCE / "recovery-routing.json"

PINS = {
    NOTES: "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    SPOOL: "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    ROUTING: "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}


def low_pack(data: bytes) -> bytes:
    assert len(data) % 8 == 0
    return bytes(
        sum((data[i + j] & 1) << j for j in range(8))
        for i in range(0, len(data), 8)
    )


def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def body(text: str) -> str:
    return text.split(":", 1)[1].strip() if ":" in text else text


def parse_notes(text: str) -> dict[int, dict[str, str]]:
    pattern = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    result = {
        int(match.group(1)): {
            "author": match.group(2),
            "text": match.group(3).strip(),
        }
        for match in pattern.finditer(text)
    }
    assert sorted(result) == list(range(1, 25))
    return result


def parse_spool(text: str) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for line in text.splitlines():
        match = re.search(
            r"JOB=PS-261003-(03\d\d) ATTEMPT=1 STATE=ACK CLASS=(\S+) "
            r"PAYLOAD=([0-9A-F]{32}) DEST=(\S+)",
            line,
        )
        if match is None:
            continue
        job = int(match.group(1))
        if 301 <= job <= 324:
            result[job - 300] = {
                "class": match.group(2),
                "payload": match.group(3),
                "dest": match.group(4),
            }
    assert sorted(result) == list(range(1, 25))
    return result


def selector_from_16(raw: bytes) -> tuple[str, int]:
    packed = low_pack(raw).hex().upper()
    return packed, low_value(packed)


def main() -> None:
    for path, expected in PINS.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected

    notes = parse_notes(NOTES.read_text(encoding="utf-8"))
    spool = parse_spool(SPOOL.read_text(encoding="utf-8"))
    route = json.loads(ROUTING.read_text(encoding="utf-8"))
    key = bytes.fromhex(route["K08"]["desk_nonce"])

    hmap: dict[int, tuple[str, int]] = {}
    for number, record in notes.items():
        component = hmac.new(
            key,
            normalize(body(record["text"])).encode("utf-8"),
            hashlib.sha256,
        ).digest()[:16]
        hmap[number] = selector_from_16(component)

    cycle = (13, 9, 12, 11)
    assert [hmap[n][1] for n in cycle] == [9, 12, 11, 13]
    milk = "".join(chr(64 + n) for n in cycle)
    assert milk == "MILK"
    assert "milk" not in NOTES.read_text(encoding="utf-8").lower()

    assert [spool[n]["class"] for n in cycle] == ["STORES"] * 4
    assert [spool[n]["dest"] for n in cycle] == [
        "store",
        "store",
        "store",
        "desk",
    ]

    n14 = notes[14]["text"]
    assert n14.startswith("Sunrise photograph: If ")
    assert 14 % 2 == 0

    mask_pack, mask_selector = selector_from_16(
        bytes.fromhex(route["K04"]["masked_component"])
    )
    nonce_pack, nonce_selector = selector_from_16(key)
    assert (mask_pack, mask_selector) == ("D939", 14)
    assert (nonce_pack, nonce_selector) == ("F797", 14)
    assert hmap[20][1] == 14

    p14_pack, p14_selector = selector_from_16(
        bytes.fromhex(spool[14]["payload"])
    )
    assert (p14_pack, p14_selector) == ("5FDA", 9)
    assert notes[9]["text"].startswith("Caption for the galley board:")

    spool_map = {
        n: selector_from_16(bytes.fromhex(spool[n]["payload"]))
        for n in range(1, 25)
    }
    assert [spool_map[n][1] for n in (9, 12, 1, 4)] == [12, 1, 4, 9]

    print("HMAC_CYCLE=N13->N09->N12->N11->N13")
    print("A1Z26=MILK")
    print("SPOOL_CLASSES=STORES,STORES,STORES,STORES")
    print("SPOOL_DESTS=store,store,store,desk")
    print(f"K04_MASK_LOW={mask_pack}->14")
    print(f"K08_NONCE_LOW={nonce_pack}->14")
    print(f"N20_HMAC_LOW={hmap[20][0]}->14")
    print("N14=Sunrise photograph / body begins IF / note is EVEN")
    print(f"PS0314_LOW={p14_pack}->N09")
    print("SPOOL_CYCLE=N09->N12->N01->N04->N09")
    print("PASS")


if __name__ == "__main__":
    main()
