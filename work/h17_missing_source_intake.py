#!/usr/bin/env python3
"""Read-only H-17 K04/K08 intake with default-safe output.

The route and acceptance data are loaded from the supplied resources tree.
Raw payloads, components, phrases, nonces, masks and digests stay in memory;
CLI output contains only source-selection metadata and commitment booleans.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

try:
    from h17_redaction import redact_sensitive
except ImportError:  # Import as work.h17_missing_source_intake from the repo root.
    from work.h17_redaction import redact_sensitive

K04_JOB = "PS-261003-0417"
TEXT_SUFFIXES = {".txt", ".log", ".eml", ".html", ".htm", ".json", ".jsonl", ".ini", ".csv", ".md"}
K08_PATH_HINTS = ("wn-14", "desk", "caption", "galley", "noticeboard", "crew")
K04_LOG_NAMES = {"spool-reconstruction.log", "queue.log", "queue.journal", "queue-export.txt"}


def normalize(text: str) -> str:
    """Apply the K08 ASCII lowercase/punctuation/whitespace normalization."""
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_inputs(root: Path) -> tuple[Path, dict, dict]:
    """Accept an evidence directory, export root, resources root, or repo root."""
    root = root.expanduser().resolve()
    candidates = (
        (root, root.parent),
        (root / "evidence", root),
        (root / "resources" / "evidence", root / "resources"),
    )
    for evidence_root, resource_root in candidates:
        route_path = evidence_root / "recovery-routing.json"
        acceptance_path = resource_root / "acceptance.json"
        if evidence_root.is_dir() and route_path.is_file() and acceptance_path.is_file():
            routing = json.loads(route_path.read_text(encoding="utf-8"))
            acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
            return evidence_root, routing, acceptance
    raise FileNotFoundError("expected evidence/recovery-routing.json and acceptance.json")


def print_rows(path: Path) -> list[dict]:
    """Parse exact-job spool rows; payloads remain internal to this module."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    rows = []
    for line_number, line in enumerate(lines, 1):
        if "PAYLOAD=" not in line:
            continue
        tokens = line.split()
        timestamp = tokens[0] if tokens and re.match(r"^\d{4}-\d\d-\d\dT", tokens[0]) else ""
        fields = {
            key: value
            for key, value in (token.split("=", 1) for token in tokens if "=" in token)
        }
        if fields.get("JOB") != K04_JOB:
            continue
        try:
            attempt = int(fields["ATTEMPT"])
        except (KeyError, ValueError):
            continue
        payload = fields.get("PAYLOAD", "").upper()
        if not re.fullmatch(r"[0-9A-F]{32}", payload):
            continue
        rows.append({
            "path": str(path),
            "line": line_number,
            "timestamp": timestamp,
            "job": fields.get("JOB", ""),
            "class": fields.get("CLASS", ""),
            "dest": fields.get("DEST", ""),
            "attempt": attempt,
            "state": fields.get("STATE") or fields.get("STATUS", ""),
            "payload": payload,
        })
    return rows


def select_k04_ack(rows: list[dict]) -> tuple[dict, list[dict], list[dict]]:
    """Select a unique highest-attempt RECOVER ACK or fail closed."""
    acknowledgements = [row for row in rows if row["state"] == "ACK"]
    if not acknowledgements:
        raise LookupError("no ACK rows for the exact K04 job")
    highest = max(row["attempt"] for row in acknowledgements)
    top = [row for row in acknowledgements if row["attempt"] == highest]
    if any(row["class"] != "RECOVER" for row in top):
        raise ValueError(f"highest ACK attempt {highest} includes a non-RECOVER row")
    if len({row["payload"] for row in top}) != 1:
        raise ValueError(f"highest ACK attempt {highest} has conflicting payloads")
    selected = max(top, key=lambda row: (row["timestamp"], row["path"], row["line"]))
    return selected, top, acknowledgements


def _k04(evidence_root: Path, routing: dict, acceptance: dict) -> dict:
    rows = []
    for path in evidence_root.rglob("*"):
        if path.is_file() and ("0417" in path.name.upper() or path.name.lower() in K04_LOG_NAMES):
            rows.extend(print_rows(path))
    acknowledgements = [row for row in rows if row["state"] == "ACK"]
    if not acknowledgements:
        return {"status": "not_found", "carrier_rows": len(rows), "ack_rows": 0}
    try:
        selected, top, _ = select_k04_ack(rows)
    except (LookupError, ValueError) as exc:
        return {
            "status": "ambiguous_or_invalid",
            "carrier_rows": len(rows),
            "ack_rows": len(acknowledgements),
            "selection_error": type(exc).__name__,
        }

    payload = bytes.fromhex(selected["payload"])
    mask = bytes.fromhex(routing["K04"]["masked_component"])
    if len(payload) != 16 or len(mask) != 16:
        return {"status": "invalid_length", "candidate_length_bytes": len(payload)}
    component = bytes(left ^ right for left, right in zip(payload, mask))
    matches = _sha256(component) == acceptance["slot_sha256"]["K04"]
    return {
        "status": "match" if matches else "no_match",
        "carrier_rows": len(rows),
        "ack_rows": len(acknowledgements),
        "highest_ack_rows": len(top),
        "selected_source": Path(selected["path"]).name,
        "selected_line": selected["line"],
        "selected_timestamp": selected["timestamp"],
        "selected_attempt": selected["attempt"],
        "selected_class": selected["class"],
        "selected_destination": selected["dest"],
        "candidate_length_bytes": len(component),
        "commitment_match": matches,
    }


def _k08(evidence_root: Path, routing: dict, acceptance: dict) -> dict:
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    text_carriers = 0
    matches = []
    for path in evidence_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if not any(hint in str(path).lower() for hint in K08_PATH_HINTS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        text_carriers += 1
        words = re.findall(r"[a-z0-9]+", text.lower())
        for start in range(len(words)):
            phrase = ""
            for count in range(1, min(64, len(words) - start) + 1):
                phrase = words[start] if count == 1 else phrase + " " + words[start + count - 1]
                component = hmac.new(nonce, phrase.encode("ascii"), hashlib.sha256).digest()[:16]
                if _sha256(component) == target:
                    matches.append({"source_file": path.name, "word_count": count})
    return {
        "status": "match" if matches else "no_match",
        "text_carriers": text_carriers,
        "commitment_matches": len(matches),
        "match_sources": matches,
    }


def run_intake(root: Path) -> dict:
    """Return redacted status metadata only; never return candidate material."""
    evidence_root, routing, acceptance = _load_inputs(Path(root))
    report = {
        "k04": _k04(evidence_root, routing, acceptance),
        "k08": _k08(evidence_root, routing, acceptance),
    }
    return redact_sensitive(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="evidence directory, export root, resources root, or repository root")
    args = parser.parse_args(argv)
    try:
        report = run_intake(args.root)
    except Exception as exc:
        report = redact_sensitive({"status": "error", "error_type": type(exc).__name__})
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report.get("k04", {}).get("status") == "ambiguous_or_invalid" else 0


if __name__ == "__main__":
    raise SystemExit(main())
