#!/usr/bin/env python3
"""H-17 K08 HMAC low-bit routing cycle and cross-slot N14 convergence.

Target-blind routing analysis over the original crew notes, routing constants,
and three already accepted component values. It does not read K08 acceptance
data and does not mutate sources.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "resources/evidence"
NOTES = EVIDENCE / "crew/noticeboard-and-desk-notes.txt"
ROUTING = EVIDENCE / "recovery-routing.json"

NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTING_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
K02_RAW = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")

EXPECTED = {
    1: ("6772", 6), 2: ("CDE7", 13), 3: ("0EF0", 2), 4: ("6AA0", 6),
    5: ("ADBE", 9), 6: ("DA03", 10), 7: ("5922", 3), 8: ("60C3", 12),
    9: ("46CC", 12), 10: ("9BC7", 13), 11: ("C2E3", 13), 12: ("EC4C", 11),
    13: ("E2BC", 9), 14: ("AC94", 7), 15: ("18E8", 5), 16: ("D1D9", 10),
    17: ("C04A", 9), 18: ("B9DF", 2), 19: ("C019", 13), 20: ("DA53", 14),
    21: ("AD4E", 9), 22: ("5A16", 7), 23: ("C90D", 3), 24: ("7C67", 11),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_notes(text: str) -> dict[int, str]:
    pattern = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    notes = {int(m.group(1)): m.group(3).strip() for m in pattern.finditer(text)}
    assert sorted(notes) == list(range(1, 25))
    return notes


def body(text: str) -> str:
    return text.split(":", 1)[1].strip() if ":" in text else text


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text)


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())


def pack_lsb(data: bytes) -> bytes:
    assert len(data) % 8 == 0
    return bytes(
        sum(((data[offset + bit] & 1) << bit) for bit in range(8))
        for offset in range(0, len(data), 8)
    )


def low_value(text: str) -> int:
    assert 0 < len(text) <= 8
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))


def note_selector(note_text: str, key: bytes) -> tuple[str, int]:
    digest16 = hmac.new(
        key,
        normalize(body(note_text)).encode("utf-8"),
        "sha256",
    ).digest()[:16]
    packed = pack_lsb(digest16).hex().upper()
    return packed, low_value(packed)


def main() -> None:
    assert sha256(NOTES) == NOTES_SHA256
    assert sha256(ROUTING) == ROUTING_SHA256

    notes = parse_notes(NOTES.read_text(encoding="utf-8"))
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))
    key = bytes.fromhex(routing["K08"]["desk_nonce"])

    observed = {n: note_selector(notes[n], key) for n in range(1, 25)}
    assert observed == EXPECTED

    cycle = [12, 11, 13, 9]
    assert [observed[n][1] for n in cycle] == [11, 13, 9, 12]

    cycle_set = set(cycle)
    for start in range(1, 25):
        node = start
        for _ in range(24):
            if node in cycle_set:
                break
            node = observed[node][1]
        assert node in cycle_set

    heads = "".join(words(body(notes[n]))[0][0].upper() for n in cycle)
    counts = [len(words(body(notes[n]))) for n in cycle]
    count_letters = "".join(chr(ord("A") + count) for count in counts)
    assert heads == "TEAN"
    assert counts == [11, 14, 22, 13]
    assert count_letters == "LOWN"
    assert heads[:3] == "TEA"
    assert count_letters[:3] == "LOW"
    assert low_value(heads) == 6
    assert low_value(count_letters) == 6

    k04_mask = bytes.fromhex(routing["K04"]["masked_component"])
    k08_nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    k04_pack = pack_lsb(k04_mask).hex().upper()
    k08_pack = pack_lsb(k08_nonce).hex().upper()
    assert k04_pack == "D939" and low_value(k04_pack) == 14
    assert k08_pack == "F797" and low_value(k08_pack) == 14
    assert notes[14].startswith("Sunrise photograph:")

    candidate = {
        "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
        "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
        "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
    }
    current = json.loads((ROOT / "candidate.json").read_text(encoding="utf-8"))
    assert all(current[k] == v for k, v in candidate.items())
    assert hashlib.sha256(K02_RAW).digest()[:16].hex().upper() == candidate["K02"]

    component_source = {
        1: bytes.fromhex(candidate["K01"]),
        2: K02_RAW,
        6: bytes.fromhex(candidate["K06"]),
    }
    source_map = {
        k: low_value(pack_lsb(v).hex().upper())
        for k, v in component_source.items()
    }
    assert source_map == {1: 12, 2: 11, 6: 10}

    component_final = {
        1: bytes.fromhex(candidate["K01"]),
        2: bytes.fromhex(candidate["K02"]),
        6: bytes.fromhex(candidate["K06"]),
    }
    final_map = {
        k: low_value(pack_lsb(v).hex().upper())
        for k, v in component_final.items()
    }
    assert final_map == {1: 12, 2: 10, 6: 10}
    assert [low_value(word) for word in ("A", "LOW", "BIT")] == [1, 6, 2]

    def indexed_word(k: int, selector: int) -> str:
        return words(notes[selector])[k - 1]

    source_phrase = " ".join(
        indexed_word(k, source_map[k]) for k in (1, 6, 2)
    )
    final_phrase = " ".join(
        indexed_word(k, final_map[k]) for k in (1, 6, 2)
    )
    assert source_phrase == "Workshop to shelf"
    assert final_phrase == "Workshop to desk"

    print(
        "NOTE_MAP="
        + ",".join(
            f"N{n:02d}:{observed[n][0]}->{observed[n][1]}"
            for n in range(1, 25)
        )
    )
    print("CYCLE=N12->N11->N13->N09->N12")
    print(f"CYCLE_HEADS={heads} FIRST3={heads[:3]}")
    print(
        f"CYCLE_COUNTS={counts} LETTERS={count_letters} "
        f"FIRST3={count_letters[:3]}"
    )
    print("CYCLE_HEADS_LOW=6 CYCLE_COUNTS_LOW=6")
    print(f"K04_MASK_LOW={k04_pack}->14")
    print(f"K08_NONCE_LOW={k08_pack}->14")
    print("CONVERGENCE=N14 Sunrise photograph")
    print(f"SOURCE_STAGE_WORD_ROUTE={source_phrase}")
    print(f"FINAL_STAGE_WORD_ROUTE={final_phrase}")
    print("PASS")


if __name__ == "__main__":
    main()
