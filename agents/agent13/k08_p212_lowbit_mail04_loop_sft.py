"""H-17 K08 P212 low-bit continuation SFT.

Replays LOW-IF-EVEN -> P212, then applies LOW BIT to the locator itself.
Target-blind: acceptance.json is never read.
"""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"resources"

def pack(bits):
    return sum(bit<<i for i,bit in enumerate(bits))

def main():
    audit=[json.loads(x) for x in (ROOT/"evidence/transfers/transfer-audit.jsonl").read_text().splitlines() if x]
    rows={(r["seq"],r["attempt"]):r for r in audit if r.get("kind")=="CHUNK" and r.get("transfer")=="AX-7782"}
    raw=b"".join(bytes.fromhex(rows[(seq,1 if seq%2==0 else 2)]["checkpoint"]) for seq in range(8))
    assert raw.hex().upper()=="6224CEDCF3B873BA18887BE63DB0C5C9"
    out=bytes(pack([b&1 for b in raw[i:i+8]]) for i in (0,8))
    assert out==bytes.fromhex("50D4")
    locator=chr(out[0])+str(out[1])
    assert locator=="P212"

    bits=[ord(c)&1 for c in locator]
    assert bits==[0,0,1,0]
    mail_no=pack(bits)
    assert mail_no==4

    mail=(ROOT/f"evidence/mail/{mail_no:02d}.eml").read_text()
    assert "X-Records-Reference: MAIL-04" in mail
    assert "Subject: PTW-417 closeout bay order" in mail
    m=re.search(r"The witness walk\s+was\s+([A-D]),\s*([A-D]),\s*([A-D]),\s*([A-D])\.",mail)
    assert m and list(m.groups())==["B","D","A","C"]
    order=list(m.groups())

    receipts=[json.loads(x) for x in (ROOT/"evidence/maintenance/seal-receipts.jsonl").read_text().splitlines() if x]
    best={}
    for r in receipts:
        if r.get("permit")=="PTW-417" and r.get("state")=="CLOSED" and r.get("fitment")=="AS_LEFT" and r.get("signed") is True:
            if r["bay"] not in best or r["revision"]>best[r["bay"]]["revision"]:
                best[r["bay"]]=r
    serials=[best[b]["serial"].split("-",1)[1] for b in order]
    assert serials==["D7DAD6BC","9714519B","7DAD0AD4","BE8E87FD"]
    seal_bits=[int(s,16)&1 for s in serials]
    assert seal_bits==[0,1,0,1]
    note_no=pack(seal_bits)
    assert note_no==10

    notes=(ROOT/"evidence/crew/noticeboard-and-desk-notes.txt").read_text()
    assert "N10 / Emily" in notes and "after the last cup" in notes
    assert "N11 / David" in notes and "Mug shelf:" in notes
    print("PASS AX-7782 -> P212 -> MAIL-04 -> PTW-417 B,D,A,C -> N10")

if __name__=="__main__":
    main()
