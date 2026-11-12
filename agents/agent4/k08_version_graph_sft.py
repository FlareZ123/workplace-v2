#!/usr/bin/env python3
"""Source-pinned K08 author/role/version graph; does not generate phrase candidates."""
from __future__ import annotations
import argparse
import email.utils
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SHA256 = {
    "mail/11.eml": "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    "mail/14.eml": "9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5",
    "mail/17.eml": "67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014",
    "mail/18.eml": "7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0",
    "mail/19.eml": "caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd",
    "mail/20.eml": "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
    "crew/noticeboard-and-desk-notes.txt": "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb",
    "crew/galley-and-stores.log": "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46",
    "h17-supplemental-office-files/retired-office-bookmarks.html": "b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096",
}

ROLE = {
    1: ("photo_caption", "Jason", "candidate input; not Emily-authored"),
    2: ("crew_board_first_draft", "Emily", "complete draft; not the recovery-envelope final role"),
    3: ("kitchen_photo_caption", "Zoey", "candidate input; not Emily-authored"),
    4: ("shift_photo_note", "David", "contextual note; not Emily-authored"),
    5: ("boat_deck_note", "Gabriel", "contextual note; not Emily-authored"),
    6: ("desk_second_draft", "Emily", "complete draft; not the recovery-envelope final role"),
    7: ("tools_cabinet_note", "Simon", "contextual note; not Emily-authored"),
    8: ("window_photo_caption", "Jason", "candidate input; not Emily-authored"),
    9: ("galley_board_caption", "Zoey", "candidate input; not Emily-authored"),
    10: ("desk_copy_photo_reference", "Emily", "meta/reference text; photo identity absent"),
    11: ("mug_shelf_note", "David", "contextual note; not Emily-authored"),
    12: ("workshop_card", "Simon", "contextual note; not Emily-authored"),
    13: ("reminiscence", "Emily", "complete narrative; not a labelled final caption"),
    14: ("sunrise_photo_caption", "Gabriel", "candidate input; not Emily-authored"),
    15: ("rough_heading", "Jason", "rough heading; not Emily-authored"),
    16: ("canteen_notice", "Zoey", "contextual notice; not Emily-authored"),
    17: ("standby_envelope_label", "Emily", "complete label explicitly excluded by MAIL-11"),
    18: ("commissioning_envelope_label", "Emily", "complete label explicitly excluded by MAIL-11"),
    19: ("mug_count_reflection", "David", "contextual note; not Emily-authored"),
    20: ("authorial_intent_brief", "Emily", "semantic constraints; not the final words"),
    21: ("freezer_notice", "Zoey", "contextual notice; not Emily-authored"),
    22: ("stores_note", "Simon", "contextual note; not Emily-authored"),
    23: ("final_margin_reference", "Emily", "locates final wording on margin; does not quote it"),
    24: ("departure_board_note", "Gabriel", "contextual note; not Emily-authored"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_mail(path: Path) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    sender = re.search(r"^From: ([^\n]+)", text, re.M).group(1)
    date_text = re.search(r"^Date: ([^\n]+)", text, re.M).group(1)
    dt = email.utils.parsedate_to_datetime(date_text)
    return {
        "sha256": sha256(raw),
        "sender": sender.split(" <", 1)[0],
        "date_header": date_text,
        "timestamp_utc": dt.astimezone(__import__("datetime").timezone.utc).isoformat(),
        "subject": re.search(r"^Subject: ([^\n]+)", text, re.M).group(1),
        "text": text,
    }


def parse_notes(path: Path) -> dict[int, dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = {}
    for i, line in enumerate(lines):
        m = re.fullmatch(r"N(\d{2}) / (.+)", line)
        if not m:
            continue
        n = int(m.group(1))
        body = lines[i + 1].strip() if i + 1 < len(lines) else ""
        role, author, boundary = ROLE[n]
        out[n] = {"id": f"N{n:02d}", "author": author, "role": role,
                  "text": body, "boundary": boundary}
    return out


def build(root: Path) -> dict:
    base = root / "evidence" if (root / "evidence").is_dir() else root
    files = {}
    for rel, expected in EXPECTED_SHA256.items():
        raw = (base / rel).read_bytes()
        actual = sha256(raw)
        assert actual == expected, f"source SHA mismatch: {rel}: {actual}"
        files[rel] = {"sha256": actual, "bytes": len(raw)}

    mails = {n: parse_mail(base / f"mail/{n:02d}.eml") for n in (11, 14, 17, 18, 19, 20)}
    notes = parse_notes(base / "crew/noticeboard-and-desk-notes.txt")
    galley = (base / "crew/galley-and-stores.log").read_text(encoding="utf-8")
    bookmarks = (base / "h17-supplemental-office-files/retired-office-bookmarks.html").read_text(encoding="utf-8")
    assert len(notes) == 24, f"expected 24 numbered notes, got {len(notes)}"

    m11, m14, m18, m20 = (mails[n]["text"] for n in (11, 14, 18, 20))
    assert 'not "Back before the first boat"' in m11
    assert 'or the\nstandby envelope\'s "Leave the light on for the next watch."' in m11
    assert "The\ndesk notes and photograph captions were how I worked out the wording." in m11
    assert "your\ndesk notes are under it" in m14
    assert "photographs and galley captions getting filed as part" in m14
    assert "nobody is to go back in for records or personal belongings" in m18
    assert "There were several captions and drafts on her desk." in m20
    assert "The words she finally chose matter" in m20
    assert "X-Records-Reference: MAIL-20" in m20
    assert "X-Records-Reference: desk-note-04" not in m20
    assert "spare radio chargers moved from briefing room to accommodation desk" in galley
    assert "file:///R:/IT/desk-images/oldscan/scanrelease.txt" in bookmarks
    assert "file:///R:/Records/INDEX/IR-261003-H17.txt" in bookmarks
    assert notes[17]["text"].endswith("Leave the light on for the next watch.")
    assert notes[18]["text"].endswith("Back before the first boat.")
    assert "The wording in my margin was never an official slogan." in notes[23]["text"]
    assert "the envelope only remembers the words i finally put on it" in notes[23]["text"].lower()

    # Mail headers establish timestamps; note numbers do not establish note dates.
    expected_times = {
        11: "2026-10-01T18:14:00",
        14: "2026-10-02T14:38:00",
        17: "2026-10-03T17:31:00",
        18: "2026-10-03T21:47:00",
        19: "2026-10-04T06:22:00",
        20: "2026-10-04T11:06:00",
    }
    for n, prefix in expected_times.items():
        assert mails[n]["timestamp_utc"].startswith(prefix)

    # No complete text node has the exact author+role of the selected final margin.
    complete_eligible = [n for n in notes.values()
                         if n["author"] == "Emily"
                         and n["role"] == "recovery_envelope_final_margin"
                         and n["text"]]
    assert complete_eligible == []

    controls = []
    for n in (2, 6, 13, 17, 18, 1, 8, 9, 14):
        controls.append({
            "note": f"N{n:02d}", "author": notes[n]["author"],
            "role": notes[n]["role"], "complete_text": bool(notes[n]["text"]),
            "eligible_same_operation": False, "reason": notes[n]["boundary"]
        })

    return {
        "source_files": files,
        "target": {
            "slot": "K08", "author": "Emily",
            "role": "recovery_envelope_final_margin",
            "complete_text_present": False,
            "carrier": "recovery-envelope margin",
            "component": "HMAC-SHA256(normalized UTF-8 phrase, desk_nonce)[:16]"
        },
        "dated_documents": [
            {"id": "MAIL-11.p3", "timestamp_utc": mails[11]["timestamp_utc"],
             "author": "Emily", "role": "authorial intent and explicit exclusions",
             "supports": ["final phrase is not N17", "final phrase is not N18",
                          "desk notes and photograph captions were wording inputs"],
             "does_not_supply": ["exact final phrase", "unique source note/photo ID",
                                 "final inscription timestamp"]},
            {"id": "MAIL-14.p3", "timestamp_utc": mails[14]["timestamp_utc"],
             "author": "David", "role": "WN-14 custody and source separation",
             "supports": ["Emily desk notes under WN-14 folder",
                          "photos and galley captions separate from procedure"],
             "does_not_supply": ["named recipient", "actual handoff completion time",
                                 "envelope text"]},
            {"id": "MAIL-17", "timestamp_utc": mails[17]["timestamp_utc"],
             "author": "Emily", "role": "accommodation availability locator",
             "supports": ["Emily would be in accommodation after dinner if watch needed previous note"],
             "does_not_supply": ["identity of the desk in MAIL-20", "location of final envelope"]},
            {"id": "MAIL-18", "timestamp_utc": mails[18]["timestamp_utc"],
             "author": "David", "role": "incident access restriction",
             "supports": ["fire contained", "no re-entry for records or personal belongings"],
             "does_not_supply": ["location of Emily's desk", "whether desk was inside instrument store"]},
            {"id": "MAIL-19", "timestamp_utc": mails[19]["timestamp_utc"],
             "author": "Zoey", "role": "accommodation desk equipment locator",
             "supports": ["spare chargers at accommodation desk"],
             "does_not_supply": ["Emily's desk identity", "caption or envelope custody"]},
            {"id": "galley-log.4Oct", "timestamp_utc": "2026-10-04 (date only)",
             "author": "records export", "role": "equipment movement",
             "supports": ["spare chargers moved from briefing room to accommodation desk"],
             "does_not_supply": ["Emily's desk identity", "caption or envelope custody"]},
            {"id": "retired-office-bookmarks", "timestamp_utc": "September 2026 (cache label only)",
             "author": "office profile export", "role": "historical file locator",
             "supports": ["R:/IT/desk-images/oldscan/scanrelease.txt locator",
                          "R:/Records/INDEX/IR-261003-H17.txt locator"],
             "does_not_supply": ["contents of either target", "desk-note-04 record",
                                 "link from scanrelease to MAIL-20 or a specific caption"]},
            {"id": "MAIL-20.p2", "timestamp_utc": mails[20]["timestamp_utc"],
             "author": "Gabriel", "role": "post-incident observation of captions/drafts",
             "supports": ["several captions and drafts on Emily's desk",
                          "exact chosen words matter"],
             "does_not_supply": ["exact phrase", "desk location", "caption IDs",
                                 "custody path after MAIL-18"]},
        ],
        "undated_text_nodes": [notes[n] for n in (1, 2, 6, 8, 9, 10, 13, 14, 17, 18, 20, 23)],
        "edges": [
            {"from": "MAIL-11.p3", "to": "N17", "type": "EXPLICITLY_EXCLUDES"},
            {"from": "MAIL-11.p3", "to": "N18", "type": "EXPLICITLY_EXCLUDES"},
            {"from": "MAIL-11.p3", "to": "desk-notes-and-photo-caption-class",
             "type": "USES_AS_WORDING_INPUTS", "note": "no individual source ID is named"},
            {"from": "MAIL-14.p3", "to": "WN-14-folder", "type": "CUSTODY_LOCATOR"},
            {"from": "MAIL-14.p3", "to": "photo-and-galley-caption-archive",
             "type": "SEPARATE_FROM_ENGINEERING_PROCEDURE"},
            {"from": "N10", "to": "unknown-photograph-after-last-cup",
             "type": "UNRESOLVED_REFERENCE"},
            {"from": "N20", "to": "K08-final-intent", "type": "THEME_CONSTRAINT_ONLY"},
            {"from": "N23", "to": "recovery-envelope-margin", "type": "FINAL_CARRIER_REFERENCE"},
            {"from": "MAIL-20.p2", "to": "recovery-envelope-margin",
             "type": "EXACT_WORDS_ARE_AUTHORITATIVE", "note": "no transcription supplied"},
        ],
        "complete_caption_controls": controls,
        "eligible_complete_final_controls": complete_eligible,
        "missing_relation": "source caption/draft ID -> Emily's specific edit/version action -> exact recovery-envelope margin text",
        "mail20_record_reference": "MAIL-20 self-reference; the prior desk-note-04 claim was retracted after checking the original header; do not conflate with N04",
        "accommodation_desk_join": "UNRESOLVED: MAIL-17, MAIL-19 and the galley log do not identify the MAIL-20 desk as the accommodation desk or locate the envelope there",
        "status": "UNRECOVERED_NO_ELIGIBLE_COMPLETE_FINAL_CONTROL",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("resources"),
                    help="repository resources directory or extracted archive root")
    args = ap.parse_args()
    result = build(args.root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("K08 version graph: PASS (source pins, roles, dates, exclusions, and missing-edge assertions)")
    print("Eligible complete final-margin controls: 0")
    print("K08 component recovered: NO")


if __name__ == "__main__":
    main()
