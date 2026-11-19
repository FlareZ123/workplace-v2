#!/usr/bin/env python3
"""Source-pinned K08 low-bit two-cell and SEAT transition.

Reproduces the established source-stage LOW BIT bridge and target-blind
continuations:
  ATEALBIT -> M, TEA -> row 10       => M10
  A LOW BIT -> THE END OF; NIGHT -> T
  SEA -> row 11                       => T11
  ends(SEA,NIGHT,VOICES,TABLE)=ATSE; wrap2 -> SEAT -> K07 -> N11
"""
from __future__ import annotations
import hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt"
NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

K01 = bytes.fromhex("049AAB2E1CDE7A82CD7C60234303C91A")
K02_RAW = bytes.fromhex("E1A5E474BAD7E853A2E8C71D3317D507")
K05 = bytes.fromhex("FF8B78200A56E8586DCDA00EF01E4572")
K06 = bytes.fromhex("5DBF40EE52FAAED9A536D3326CF0D95A")
K07_RAW = bytes.fromhex("8947CEDCB9CC73BAB7E87BE63302C5C9")

def low_value(text: str) -> int:
    return sum((ord(ch) & 1) << i for i, ch in enumerate(text))

def low_pack(raw: bytes) -> bytes:
    assert len(raw) % 8 == 0
    return bytes(
        sum((raw[i + j] & 1) << j for j in range(8))
        for i in range(0, len(raw), 8)
    )

def source_selector(raw: bytes) -> int:
    return low_value(low_pack(raw).hex().upper())

def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", text)

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

def rotate_left(text: str, distance: int) -> str:
    distance %= len(text)
    return text[distance:] + text[:distance]

def main() -> None:
    assert hashlib.sha256(NOTES.read_bytes()).hexdigest() == NOTES_SHA256
    note_text = NOTES.read_text(encoding="utf-8")
    notes = parse_notes(note_text)

    source = {1: K01, 2: K02_RAW, 5: K05, 6: K06, 7: K07_RAW}
    source_map = {k: source_selector(v) for k, v in source.items()}
    assert source_map == {1: 12, 2: 11, 5: 10, 6: 10, 7: 11}

    selected = (2, 6, 11, 13, 17, 18, 20, 23)
    heads = "".join(words(body(notes[n]))[0][0].upper() for n in selected)
    assert heads == "ATEALBIT"
    column_m = chr(low_value(heads))
    assert column_m == "M"

    tea_component = low_value("TEA")
    sea_component = low_value("SEA")
    assert (tea_component, sea_component) == (6, 7)
    tea_row = source_map[tea_component]
    sea_row = source_map[sea_component]
    assert (tea_row, sea_row) == (10, 11)
    assert f"{column_m}{tea_row}" == "M10"

    directive_components = [low_value(w) for w in ("A", "LOW", "BIT")]
    assert directive_components == [1, 6, 2]
    directive_positions = [source_map[k] for k in directive_components]
    assert directive_positions == [12, 10, 11]
    n20 = words(body(notes[20]))
    n20_lower = [w.lower() for w in n20]
    extracted = " ".join(n20_lower[i - 1] for i in directive_positions)
    assert extracted == "the end of"

    assert n20_lower[8:13] == ["the", "end", "of", "the", "night"]
    column_t = n20[12][-1].upper()
    assert column_t == "T"
    assert f"{column_t}{sea_row}" == "T11"

    shifted = chr(ord(column_m) + low_value("SEA"))
    assert shifted == column_t

    witnesses = []
    for number, text in notes.items():
        w = [x.lower() for x in words(body(text))]
        if max(directive_positions) > len(w):
            continue
        tri = [w[i - 1] for i in directive_positions]
        if any(w[j:j + 3] == tri for j in range(len(w) - 2)):
            witnesses.append((number, " ".join(tri)))
    assert witnesses == [(20, "the end of")]

    # N20 fixes the four content anchors in source order.
    motifs = ("sea", "night", "voices", "table")
    positions = [n20_lower.index(motif) + 1 for motif in motifs]
    assert positions == [8, 13, 16, 19]
    ends = "".join(motif[-1] for motif in motifs).upper()
    assert ends == "ATSE"
    wrap_distance = low_value("BIT")
    assert wrap_distance == 2
    seat = rotate_left(ends, wrap_distance)
    assert seat == "SEAT"
    assert not re.search(r"\bseat\b", note_text, re.IGNORECASE)
    assert low_value(seat) == 7
    assert source_map[low_value(seat)] == 11
    assert notes[11].startswith("Mug shelf:")

    print("SOURCE_MAP=" + ",".join(f"K{k:02d}->{v}" for k, v in sorted(source_map.items())))
    print("ATEALBIT_LOW=M")
    print("TEA->K06->N10 => M10")
    print("A_LOW_BIT->12,10,11; N20 => THE END OF")
    print("THE_END_OF(NIGHT)=T")
    print("SEA->K07->N11 => T11")
    print("M + LOW_BIT(SEA)=M+7=T")
    print("CELL_TRANSITION=M10->T11")
    print("UNIQUE_N20_SELF_CONTIGUOUS=THE END OF")
    print("MOTIF_ENDS=ATSE")
    print("WRAP_LOW_BIT(BIT)=2 => SEAT")
    print("LOW_BIT(SEAT)=7->K07->N11_MUG_SHELF")
    print("PASS")

if __name__ == "__main__":
    main()
