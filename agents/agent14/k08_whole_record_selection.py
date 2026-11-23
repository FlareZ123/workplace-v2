#!/usr/bin/env python3
"""Source-grounded whole-record selection for the K08 editorial chain.

This script treats CREW4/author output as a record-set locator, never as a
word-index mask. It reports the conditional Nxx <-> PS03xx ordinal join
separately from source-authenticated editorial exclusions.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

NOTE_RE = re.compile(r"(?m)^N(\d{2}) / ([^\n]+)\n(.*?)(?=\n\nN\d{2} / |\Z)", re.S)
SPOOL_RE = re.compile(r"JOB=PS-261003-(\d{4}) ATTEMPT=1 STATE=ACK CLASS=(\w+) PAYLOAD=([0-9A-F]{32}) DEST=(\w+)")


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", type=Path, default=Path("resources/evidence"))
    ap.add_argument("--acceptance", type=Path, default=Path("resources/acceptance.json"))
    args = ap.parse_args()
    paths = {
        "notes": args.evidence_root / "crew/noticeboard-and-desk-notes.txt",
        "spool": args.evidence_root / "print/spool-reconstruction.log",
        "mail11": args.evidence_root / "mail/11.eml",
        "routing": args.evidence_root / "recovery-routing.json",
    }
    for label, path in paths.items():
        if not path.is_file():
            raise SystemExit(f"missing {label}: {path}")
    if not args.acceptance.is_file():
        raise SystemExit(f"missing acceptance: {args.acceptance}")

    note_raw = paths["notes"].read_bytes()
    spool_raw = paths["spool"].read_bytes()
    mail11_raw = paths["mail11"].read_bytes()
    routing_raw = paths["routing"].read_bytes()
    notes_text = note_raw.decode("utf-8")
    mail11 = mail11_raw.decode("utf-8")
    routing = json.loads(routing_raw)
    acceptance = json.loads(args.acceptance.read_text(encoding="utf-8"))

    notes = {}
    for m in NOTE_RE.finditer(notes_text):
        n = int(m.group(1))
        author = m.group(2).split()[0]
        body = re.sub(r"^[^:]+:\s*", "", m.group(3).strip())
        notes[n] = {"author": author, "body": body}
    if sorted(notes) != list(range(1, 25)):
        raise SystemExit("expected exactly N01..N24")

    jobs = {}
    for line in spool_raw.decode("utf-8").splitlines():
        m = SPOOL_RE.search(line)
        if not m:
            continue
        job = int(m.group(1))
        n = job - 300
        if 1 <= n <= 24:
            jobs[n] = {
                "job": job,
                "class": m.group(2),
                "payload": bytes.fromhex(m.group(3)),
                "dest": m.group(4),
            }
    if sorted(jobs) != list(range(1, 25)):
        raise SystemExit("expected ACK1 rows PS0301..PS0324")

    author_set = {"Simon", "Emily", "Gabriel"}
    selected = [n for n in range(1, 25) if notes[n]["author"] in author_set]
    if len(selected) != 14:
        raise SystemExit(f"expected 14 author-selected records, got {len(selected)}")

    excluded_n17 = "Leave the light on for the next watch" in mail11
    excluded_n18 = "Back before the first boat" in mail11
    if not (excluded_n17 and excluded_n18):
        raise SystemExit("MAIL-11 explicit label exclusions not found")
    n23_body = notes[23]["body"]
    n23_instruction = "envelope" in n23_body.lower() and "finally put on it" in n23_body.lower()

    # Conditional ordinal join only: note Nxx -> spool job PS-03xx.
    recover_store = [
        n for n in selected
        if jobs[n]["class"] == "RECOVER" and jobs[n]["dest"].lower() == "store"
    ]
    surviving = [n for n in recover_store if n not in {17, 18}]
    # No route entry for PS-0323 exists in the K08 routing object.
    ps0323_assigned_in_route = "PS-261003-0323" in json.dumps(routing)

    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    n23_norm = normalize(n23_body)
    n23_mac16 = hmac.new(nonce, n23_norm.encode("utf-8"), hashlib.sha256).digest()[:16]
    n23_digest = hashlib.sha256(n23_mac16).hexdigest()
    ps0323_payload = jobs[23]["payload"]
    ps0323_payload_digest = hashlib.sha256(ps0323_payload).hexdigest()

    print("STOW14_AUTHOR_RECORDS", selected)
    print("MAIL11_EXCLUDES_N17_STANDBY_LABEL", excluded_n17)
    print("MAIL11_EXCLUDES_N18_COMMISSIONING_LABEL", excluded_n18)
    print("N23_IDENTIFIES_FINAL_ENVELOPE_WORDING", n23_instruction)
    print("CONDITIONAL_RECOVER_STORE_RECORDS", [
        (n, f"PS-{jobs[n]['job']:04d}", jobs[n]["class"], jobs[n]["dest"])
        for n in recover_store
    ])
    print("AFTER_MAIL11_EDITORIAL_EXCLUSIONS", surviving)
    print("CONDITIONAL_PRINT_OBJECT", f"PS-{jobs[23]['job']:04d}" if surviving == [23] else None)
    print("PS0323_ASSIGNED_IN_K08_ROUTING", ps0323_assigned_in_route)
    print("N23_WHOLE_NOTE_HMAC16", n23_mac16.hex().upper())
    print("N23_WHOLE_NOTE_COMMIT_HIT", n23_digest == target)
    print("PS0323_PAYLOAD_SHA256", ps0323_payload_digest)
    print("PS0323_PAYLOAD_IS_K08_HMAC16", ps0323_payload_digest == target)
    print("DECISION: N23 is the source-supported whole-record instruction; PS0323 is a conditional retrieval target only.")
    print("LIMIT: the note/job suffix join is ordinal, not authenticated; no exact phrase is recovered.")


if __name__ == "__main__":
    main()
