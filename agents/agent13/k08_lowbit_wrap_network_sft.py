"""H-17 K08 low-bit wrap fixed-point SFT.

Target-blind structural test. It never reads acceptance.json.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "resources"

def pack(bits):
    return sum(bit << i for i, bit in enumerate(bits))

def low_text(text):
    return pack([ord(c) & 1 for c in text])

def parse_notes(text):
    p = re.compile(
        r"^N(\d{2}) / ([^\n]+?) \[censored\]\n(.*?)(?=\n\nN\d{2} /|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    out = {}
    for m in p.finditer(text):
        n = int(m.group(1))
        content = " ".join(m.group(3).split())
        body = content.split(":", 1)[1] if ":" in content else content
        words = re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?", body)
        out[n] = words
    return out

def main():
    notes = parse_notes((ROOT / "evidence/crew/noticeboard-and-desk-notes.txt").read_text())
    selected = [2, 6, 11, 13, 17, 18, 20, 23]
    heads = "".join(notes[n][0][0].upper() for n in selected)
    assert heads == "ATEALBIT"
    assert low_text(heads) == 0x4D  # M

    audit = [
        json.loads(line)
        for line in (ROOT / "evidence/transfers/transfer-audit.jsonl").read_text().splitlines()
        if line.strip()
    ]
    rows = {
        (r["seq"], r["attempt"]): bytes.fromhex(r["checkpoint"])
        for r in audit
        if r.get("kind") == "CHUNK" and r.get("transfer") == "AX-7782"
    }
    mixed = b"".join(rows[(seq, 1 if seq % 2 == 0 else 2)] for seq in range(8))
    packed = bytes(pack([b & 1 for b in mixed[o:o+8]]) for o in (0, 8))
    assert packed == bytes.fromhex("50D4")
    locator = chr(packed[0]) + str(packed[1])
    assert locator == "P212"

    wrap = low_text(locator)
    assert wrap == 4

    rotated = heads[wrap:] + heads[:wrap]
    assert rotated == "LBITATEA"
    assert low_text(rotated) == 0xD4
    assert low_text(rotated) == packed[1] == 212

    # The four-character pre-wrap prefix is ATEA; its low bits select MAIL-13.
    assert low_text(heads[:wrap]) == 13
    mail13 = (ROOT / "evidence/mail/13.eml").read_text()
    assert "X-Records-Reference: MAIL-13" in mail13
    assert "final custodian handoff is AX-7782" in mail13

    # Compacting AX-7782 to its alphanumeric token independently returns 13.
    assert low_text("AX7782") == 13

    # The five mail records traversed by the established source chain carry a
    # literal wrap checksum in their exact subject initials.
    chain = [10, 3, 9, 13, 4]
    subjects = []
    for n in chain:
        text = (ROOT / f"evidence/mail/{n:02d}.eml").read_text()
        m = re.search(r"(?m)^Subject:\s*(.*)$", text)
        assert m
        subjects.append(m.group(1))
    initials = "".join(s[0].upper() for s in subjects)
    assert initials == "TWRAP"
    assert low_text(initials) == 10

    print("PASS")
    print("ATEALBIT low bits = 0x4D = M")
    print("P212 low bits = 4")
    print("wrap4(ATEALBIT) = LBITATEA; low bits = 0xD4 = 212")
    print("ATEA low bits = 13 = MAIL-13")
    print("AX7782 low bits = 13")
    print("MAIL subject initials = TWRAP; low bits = 10 = N10")

if __name__ == "__main__":
    main()
