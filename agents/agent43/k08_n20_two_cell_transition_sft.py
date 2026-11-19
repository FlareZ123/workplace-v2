#!/usr/bin/env python3
"""Source-pinned K08 low-bit routing continuation.

Target-blind closures:
  ATEALBIT -> M, TEA -> row 10       => M10
  A LOW BIT -> THE END OF; NIGHT -> T
  SEA -> row 11                       => T11
  ends(SEA,NIGHT,VOICES,TABLE)=ATSE; wrap2 -> SEAT -> K07 -> N11
  TEA + M -> TEAM -> N14, while SEAT -> N11; body heads -> IF EVEN
  THE END OF VOICES -> S; SEAT+S -> SEATS -> N23 final-wording witness
  K08 route literals independently map KEEPER->23, LATE->10, WATCH->11,
  DESK->14, CREW->13 and TITLE->18.
"""
from __future__ import annotations
import hashlib, hmac, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt"
ROUTING = ROOT / "resources/evidence/recovery-routing.json"
MAIL11 = ROOT / "resources/evidence/mail/11.eml"
NOTES_SHA256 = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
ROUTING_SHA256 = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
MAIL11_SHA256 = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"

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
    assert hashlib.sha256(ROUTING.read_bytes()).hexdigest() == ROUTING_SHA256
    assert hashlib.sha256(MAIL11.read_bytes()).hexdigest() == MAIL11_SHA256
    note_text = NOTES.read_text(encoding="utf-8")
    notes = parse_notes(note_text)
    routing = json.loads(ROUTING.read_text(encoding="utf-8"))

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
    assert chr(ord(column_m) + low_value("SEA")) == column_t

    witnesses = []
    for number, text in notes.items():
        w = [x.lower() for x in words(body(text))]
        if max(directive_positions) > len(w):
            continue
        tri = [w[i - 1] for i in directive_positions]
        if any(w[j:j + 3] == tri for j in range(len(w) - 2)):
            witnesses.append((number, " ".join(tri)))
    assert witnesses == [(20, "the end of")]

    # Independent source-prose calibration of the same N20 positional rule.
    mail11_text = MAIL11.read_text(encoding="utf-8").lower()
    assert "long watch, with" in mail11_text
    mail11_selector = [low_value(w) for w in ("LONG", "WATCH", "WITH")]
    route_selector = [low_value(w) for w in ("LATE", "WATCH", "RATHER")]
    assert mail11_selector == [10, 11, 3]
    assert route_selector == [10, 11, 18]
    assert "late watch, rather" in routing["K08"]["rule"].lower()
    assert " ".join(n20_lower[i - 1] for i in mail11_selector) == "end of the"
    assert " ".join(n20_lower[i - 1] for i in route_selector) == "end of the"

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
    seat_row = source_map[low_value(seat)]
    assert seat_row == 11
    assert notes[seat_row].startswith("Mug shelf:")

    team = "TEA" + column_m
    assert team == "TEAM"
    assert low_value(team) == 14
    team_row = low_value(team)
    assert words(body(notes[team_row]))[0].lower() == "if"
    assert words(body(notes[seat_row]))[0].lower() == "even"
    assert " ".join((
        words(body(notes[team_row]))[0].upper(),
        words(body(notes[seat_row]))[0].upper(),
    )) == "IF EVEN"

    # THE END OF VOICES gives the plural suffix exactly.
    plural_suffix = "VOICES"[-1]
    assert plural_suffix == "S"
    seats = seat + plural_suffix
    assert seats == "SEATS"
    assert not re.search(r"\bseats\b", note_text, re.IGNORECASE)
    assert low_value(seats) == 23
    assert "words I finally put on it" in notes[23]

    # The authoritative K08 route text independently selects the same loci.
    k08_source = routing["K08"]["source"]
    k08_rule = routing["K08"]["rule"]
    for token in ("keeper", "desk", "crew"):
        assert re.search(rf"\b{token}\b", k08_source, re.IGNORECASE)
    for token in ("late", "watch", "title"):
        assert re.search(rf"\b{token}\b", k08_rule, re.IGNORECASE)
    route_literals = {
        "KEEPER": 23,
        "DESK": 14,
        "CREW": 13,
        "LATE": 10,
        "WATCH": 11,
        "TITLE": 18,
    }
    assert {k: low_value(k) for k in route_literals} == route_literals
    assert notes[23].startswith("The wording in my margin")
    assert notes[14].startswith("Sunrise photograph:")
    assert notes[13].startswith("At the end of the night")
    assert notes[10].startswith("The desk copy")
    assert notes[11].startswith("Mug shelf:")
    assert notes[18].startswith("Commissioning envelope label:")

    # Apply the already calibrated LOW BIT -> note -> body-count alphabet
    # to every authoritative slot "source" field as a specificity control.
    def route_source_reduce(text: str) -> tuple[str, int]:
        selectors = [
            low_value(token)
            for token in re.findall(r"[A-Za-z0-9]+", text)
            if 1 <= low_value(token) <= 24
        ]
        count_letters = "".join(
            chr(ord("A") + len(words(body(notes[n]))))
            for n in selectors
        )
        return count_letters, low_value(count_letters)

    source_reductions = {
        slot: route_source_reduce(routing[slot]["source"])
        for slot in (f"K{i:02d}" for i in range(1, 9))
    }
    assert source_reductions == {
        "K01": ("LLOV", 4),
        "K02": ("OM", 3),
        "K03": ("LLMNM", 20),
        "K04": ("VNM", 4),
        "K05": ("LL", 0),
        "K06": ("LO", 2),
        "K07": ("W", 1),
        "K08": ("VLOWL", 12),
    }
    assert [
        slot for slot, (letters, _) in source_reductions.items()
        if "LOW" in letters
    ] == ["K08"]
    assert source_reductions["K08"] == ("VLOWL", 12)
    assert notes[12].startswith("Workshop card:")

    def normalize(text: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    n12_digest = hmac.new(
        nonce, normalize(body(notes[12])).encode("utf-8"), "sha256"
    ).digest()[:16]
    n12_hmac_selector = low_value(low_pack(n12_digest).hex().upper())
    assert n12_hmac_selector == 11
    assert notes[n12_hmac_selector].startswith("Mug shelf:")

    print("SOURCE_MAP=" + ",".join(f"K{k:02d}->{v}" for k, v in sorted(source_map.items())))
    print("ATEALBIT_LOW=M")
    print("TEA->K06->N10 => M10")
    print("A_LOW_BIT->12,10,11; N20 => THE END OF")
    print("THE_END_OF(NIGHT)=T")
    print("SEA->K07->N11 => T11")
    print("M + LOW_BIT(SEA)=M+7=T")
    print("CELL_TRANSITION=M10->T11")
    print("UNIQUE_N20_SELF_CONTIGUOUS=THE END OF")
    print("MAIL11_LONG_WATCH_WITH=10,11,3->END OF THE")
    print("ROUTE_LATE_WATCH_RATHER=10,11,18->END OF THE")
    print("MOTIF_ENDS=ATSE")
    print("WRAP_LOW_BIT(BIT)=2 => SEAT")
    print("LOW_BIT(SEAT)=7->K07->N11_MUG_SHELF")
    print("TEA+M=TEAM; LOW_BIT(TEAM)=14->N14_IF")
    print("SEAT->K07->N11_EVEN")
    print("TEAM_SEAT_HEADS=IF EVEN")
    print("THE_END_OF(VOICES)=S; SEAT+S=SEATS")
    print("LOW_BIT(SEATS)=23->N23_FINAL_WORDING")
    print("ROUTE_LITERALS=KEEPER23,DESK14,CREW13,LATE10,WATCH11,TITLE18")
    print("ROUTE_SOURCE_K08=VLOWL->12->N12_WORKSHOP")
    print("ROUTE_SOURCE_LOW_UNIQUE=K08_ONLY")
    print("N12_HMAC_LOW=11->N11_MUG_SHELF")
    print("PASS")

if __name__ == "__main__":
    main()
