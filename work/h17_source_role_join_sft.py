#!/usr/bin/env python3
"""Source-role selector regression test for the H-17 recovery archive."""
from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1] / "resources"
EVIDENCE = ROOT / "evidence"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def paragraphs(raw: bytes) -> list[dict[str, Any]]:
    header = re.search(rb"\r?\n\r?\n", raw)
    if not header:
        return []
    body_start = header.end()
    body = raw[body_start:]
    separators = list(re.finditer(rb"\r?\n[ \t]*\r?\n", body))
    result = []
    start = 0
    for match in separators + [None]:
        end = match.start() if match else len(body)
        chunk = body[start:end]
        left, right = len(chunk) - len(chunk.lstrip()), len(chunk.rstrip())
        if right > left:
            a, b = body_start + start + left, body_start + start + right
            result.append({"start": a, "end": b, "text": raw[a:b].decode("utf-8")})
        start = match.end() if match else len(body)
    return result


def mail_unit(n: int, p: int) -> dict[str, Any]:
    path = EVIDENCE / "mail" / f"{n:02d}.eml"
    raw = path.read_bytes()
    unit = paragraphs(raw)[p - 1]
    return {"source": str(path.relative_to(ROOT)), "sha256": digest(raw), "paragraph": p, **unit}


def note_unit(n: int) -> dict[str, Any]:
    path = EVIDENCE / "crew" / "noticeboard-and-desk-notes.txt"
    raw = path.read_bytes()
    unit = next(x for x in paragraphs(raw) if x["text"].startswith(f"N{n:02d} /"))
    return {"source": str(path.relative_to(ROOT)), "sha256": digest(raw), "note": f"N{n:02d}", **unit}


def spool_rows(text: str) -> list[dict[str, Any]]:
    rows, offset = [], 0
    for line_no, raw_line in enumerate(text.splitlines(keepends=True), 1):
        line = raw_line.rstrip("\r\n")
        start, end = offset, offset + len(line.encode("utf-8"))
        offset += len(raw_line.encode("utf-8"))
        fields = dict(re.findall(r"([A-Z_]+)=([^ ]+)", line))
        if not {"JOB", "ATTEMPT", "STATE", "CLASS", "DEST"}.issubset(fields):
            continue
        rows.append({"line": line_no, "byte_start": start, "byte_end_exclusive": end,
                     "timestamp": line.split(" ", 1)[0], "job": fields["JOB"],
                     "attempt": int(fields["ATTEMPT"]), "state": fields["STATE"],
                     "class": fields["CLASS"], "dest": fields["DEST"],
                     "payload": fields.get("PAYLOAD")})
    return rows


def select_k04(spool: str) -> dict[str, Any]:
    labels = configparser.ConfigParser()
    labels.read(EVIDENCE / "archive-labels.ini")
    section = next(s for s in labels.sections() if s.startswith("printer_routes_"))
    job = labels.get(section, "ESC-N")
    candidates = [r for r in spool_rows(spool) if r["job"] == job
                  and r["class"] == "RECOVER" and r["state"] == "ACK"]
    selected = max(candidates, key=lambda r: (r["attempt"], r["timestamp"]))
    return {k: selected[k] for k in ("line", "byte_start", "byte_end_exclusive", "timestamp",
                                     "job", "attempt", "state", "class", "dest")} | {
        "payload_is_16_bytes": bool(re.fullmatch(r"[0-9A-Fa-f]{32}", (selected.get("payload") or ""))),
        "payload_integrity": "unverified_by_source_export",
    }


def select_k06(mail11: str, register: str) -> str | None:
    issued = any("RC-17 C" in line and "issued archive service sheets" in line for line in register.splitlines())
    retained = any("RC-17 C" in line and "retained in duty folder" in line for line in register.splitlines())
    draft_only = any("RC-17 D-draft" in line and "no issue authority" in line for line in register.splitlines())
    return "C" if "issue receipt for revision C of RC-17" in mail11 and issued and retained and draft_only else None


def select_k07(mail13: str, audit: str) -> dict[str, Any]:
    match = re.search(r"final custodian handoff is (AX-\d+)", mail13)
    selected = match.group(1) if match else None
    rows = [json.loads(line) for line in audit.splitlines() if line.strip()]
    commits = [r for r in rows if r.get("kind") == "COMMIT" and r.get("dry_run") is False
               and r.get("object") == "IR-261003-H17"]
    selected_rows = [r for r in commits if r.get("transfer") == selected]
    return {"selected": selected if len(selected_rows) == 1 else None,
            "non_dry_run_commit_ids": sorted({r.get("transfer") for r in commits}),
            "commit_only_ambiguous": len({r.get("transfer") for r in commits}) > 1}


def run() -> dict[str, Any]:
    spool_path = EVIDENCE / "print" / "spool-reconstruction.log"
    spool = spool_path.read_text()
    mail11 = mail_unit(11, 1)
    mail11_k08 = mail_unit(11, 3)
    mail13 = mail_unit(13, 2)
    mail13_chunks = mail_unit(13, 3)
    mail13_folder = mail_unit(13, 4)
    mail14_signed = mail_unit(14, 1)
    mail14_pencil = mail_unit(14, 2)
    mail14_folder = mail_unit(14, 3)
    mail16_route = mail_unit(16, 1)
    mail16 = mail_unit(16, 2)
    mail16_integrity = mail_unit(16, 3)
    mail16_cross_slot = mail_unit(16, 4)
    mail20 = mail_unit(20, 2)
    mail20_bundle = mail_unit(20, 3)
    register = (EVIDENCE / "procedures" / "document-register.log").read_text()
    audit_path = EVIDENCE / "transfers" / "transfer-audit.jsonl"
    audit = audit_path.read_text()
    selected_k04 = select_k04(spool)
    selected_k06 = select_k06(mail11["text"], register)
    selected_k07 = select_k07(mail13["text"], audit)
    n10, n20, n23 = note_unit(10), note_unit(20), note_unit(23)
    routing_path = EVIDENCE / "recovery-routing.json"
    routing = json.loads(routing_path.read_text())
    source_paths = [spool_path, EVIDENCE / "archive-labels.ini",
                    EVIDENCE / "procedures" / "document-register.log", audit_path,
                    EVIDENCE / "transfers" / "queue-note.txt", routing_path]
    source_hashes = {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in source_paths}

    damaged = re.sub(r"(JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=)[^ ]+",
                     r"\1<damaged>", spool)
    omitted = re.sub(r"(JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER) PAYLOAD=[^ ]+",
                     r"\1", spool)
    changed_subject = re.sub(rb"Subject:.*", b"Subject: technical-only metadata",
                             (EVIDENCE / "mail" / "11.eml").read_bytes(), count=1)
    register_later_draft = register.replace("2026-10-02", "2099-10-02")
    tests = {
        "K04_selection_survives_damaged_payload": select_k04(damaged)["attempt"] == 2,
        "K04_selection_survives_omitted_payload": select_k04(omitted)["attempt"] == 2,
        "K06_issue_authority_beats_later_draft": selected_k06 == "C",
        "K06_later_unissued_draft_stays_excluded": select_k06(mail11["text"], register_later_draft) == "C",
        "K07_receipt_selects_AX7782": selected_k07["selected"] == "AX-7782",
        "K07_commit_marker_alone_is_ambiguous": selected_k07["commit_only_ambiguous"],
        "K07_no_receipt_means_no_selection": select_k07("", audit)["selected"] is None,
        "K08_paragraph_role_survives_technical_subject": "people making room" in paragraphs(changed_subject)[2]["text"],
    }
    return {
        "archive_zip_sha256": digest(Path(args.archive).read_bytes()) if args.archive else None,
        "source_file_hashes": source_hashes,
        "selectors": {
            "K04": {"route_version_source": mail16_route, "selector_source": mail16,
                    "selected_record": selected_k04, "integrity_source": mail16_integrity,
                    "cross_slot_exclusion": mail16_cross_slot},
            "K06": {"issue_receipt": mail11, "selected_revision": selected_k06},
            "K07": {"custodian_selector": mail13, "chunk_order": mail13_chunks,
                    "folder_handoff_print": mail13_folder, "selected_transfer": selected_k07},
            "K08": {"intent": mail11_k08, "draft_input": n10, "semantic_brief": n20,
                    "final_carrier_locator": n23, "excluded_old_labels": [note_unit(17), note_unit(18)],
                    "photo_caption_inputs": [note_unit(n) for n in (1, 3, 4, 8, 14)],
                    "galley_caption_input": note_unit(9), "exact_words_boundary": mail20,
                    "bundle_context": mail20_bundle,
                    "normalization_rule": routing["K08"]["rule"],
                    "desk_nonce_hex": routing["K08"]["desk_nonce"],
                    "exact_phrase_quoted_in_intent_or_locator_units": False},
        },
        "K01_folder_context": {"signed_register": mail14_signed, "pencil_standby_exclusion": mail14_pencil,
                               "desk_notes_under_folder": mail14_folder},
        "documentary_custody_edges": [
            {"from": "AX-7782 handoff print", "to": "ordinary records folder", "source": mail13_folder,
             "scope": "handoff print only; not proof the AX-7782 data object is physically in that folder"},
            {"from": "WN-14 folder", "to": "Emily's desk notes beneath it", "source": mail14_folder,
             "scope": "notes are outside the controlled-copy sleeve"},
            {"from": "everyday notes", "to": "technical bundle 06", "source": mail20_bundle,
             "scope": "bundle inclusion; does not identify the physical folder or prove the envelope text is included"},
        ],
        "unresolved_cross_slot_edge": "No local source unit binds the FA-17 / ESC-N / L-29-N / A3 physical coupon to the ordinary-folder / WN-14 / AX-7782 handoff-paperwork chain. Keep the coupon, envelope, handoff print, and AX-7782 data object distinct until a native index or attachment proves a join.",
        "dual_role_MAIL11": {"K06": mail11, "K08": mail11_k08},
        "tests": tests,
        "all_tests_passed": all(tests.values()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    EVIDENCE = ROOT / "evidence"
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["all_tests_passed"]:
        raise SystemExit(1)