"""Read-only provenance and REC8/1 acceptance triage for newly obtained witnesses.

Supply source originals separately from their literal transcriptions. This tool
never modifies original files, archive commitments, or candidate.json. Source
SHA-256 proves exact bytes were preserved during this intake, not authenticity.
"""

import argparse
import configparser
import hashlib
import hmac
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "resources"
sys.path.insert(0, str(RESOURCES))
from verify import evaluate, no_duplicates  # noqa: E402; the original unmodified archive verifier


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_caption(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def last_escrow_ack(evidence: Path) -> tuple[str, int, datetime]:
    label = configparser.ConfigParser()
    label.read(evidence / "archive-labels.ini", encoding="utf-8")
    route = label["printer_routes_2026-09-01_to_2026-10-03"]["ESC-N"]
    entries = []
    for line in (evidence / "print/spool-reconstruction.log").read_text(encoding="utf-8").splitlines():
        # Dispatch ACK selectors remain usable when recovered spool payload bytes are damaged.
        matched = re.match(
            r"(\S+) JOB=(\S+) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+)(?=\s|$)",
            line,
        )
        if matched is None:
            continue
        timestamp, job, attempt, state, job_class = matched.groups()
        if job == route and state == "ACK" and job_class == "RECOVER":
            entries.append((int(attempt), datetime.fromisoformat(timestamp.replace("Z", "+00:00"))))
    if not entries:
        raise ValueError("No historical ESC-N RECOVER ACK found")
    attempt, timestamp = max(entries, key=lambda value: value[0])
    return route, attempt, timestamp.astimezone(timezone.utc)


def assess(
    coupon: Path | None,
    coupon_original: Path | None,
    caption: Path | None,
    caption_original: Path | None,
    resources: Path = RESOURCES,
) -> dict:
    evidence = resources / "evidence"
    routing = json.loads((evidence / "recovery-routing.json").read_text(encoding="utf-8"))
    targets = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    candidate = json.loads((resources / "candidate.json").read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)
    if coupon is not None and coupon_original is None:
        raise ValueError("--coupon-original is required with --coupon")
    if caption is not None and caption_original is None:
        raise ValueError("--caption-original is required with --caption")
    if coupon is None and caption is None:
        raise ValueError("Provide at least one new original-source witness")
    baseline = evaluate(candidate, targets)
    previously_verified = {
        key: candidate[key] for key in ("K04", "K08") if baseline["slots"][key] == "PASS"
    }
    for key in ("K01", "K02", "K03", "K05", "K06", "K07"):
        if baseline["slots"][key] != "PASS":
            raise ValueError("Six-slot baseline changed: " + key)
    for key in ("K04", "K08"):
        if baseline["slots"][key] != "PASS":
            candidate[key] = None
    result = {"source_authenticity": "NOT_ESTABLISHED_BY_HASH_ALONE", "witnesses": {}}
    if coupon is not None:
        coupon_bytes = coupon.read_bytes()
        record = json.loads(coupon_bytes.decode("utf-8-sig"), object_pairs_hook=no_duplicates)
        if not isinstance(record, dict):
            raise ValueError("Coupon transcription must be a JSON object")
        job, attempt, timestamp = last_escrow_ack(evidence)
        try:
            recorded_time = datetime.fromisoformat(record["timestamp_utc"].replace("Z", "+00:00"))
            payload_hex = record["payload_hex"]
        except (KeyError, AttributeError, ValueError) as exc:
            raise ValueError("Invalid coupon transcription timestamp or payload field") from exc
        if recorded_time.tzinfo is None:
            raise ValueError("Coupon timestamp requires an explicit UTC offset")
        if (
            record.get("job") != job
            or type(record.get("attempt")) is not int
            or record["attempt"] != attempt
            or record.get("state") != "ACK"
            or record.get("class") != "RECOVER"
            or recorded_time.astimezone(timezone.utc) != timestamp
        ):
            raise ValueError("Coupon selector does not match the historical last RECOVER ACK")
        if not isinstance(payload_hex, str) or re.fullmatch(r"[0-9A-Fa-f]{32}", payload_hex) is None:
            raise ValueError("Expected exactly 16 opaque coupon payload bytes as hexadecimal")
        mask = bytes.fromhex(routing["K04"]["masked_component"])
        payload = bytes.fromhex(payload_hex)
        candidate["K04"] = bytes(a ^ b for a, b in zip(payload, mask)).hex().upper()
        result["witnesses"]["K04"] = {
            "original_sha256": sha256_file(coupon_original),
            "transcription_sha256": hashlib.sha256(coupon_bytes).hexdigest(),
            "job": job,
            "attempt": attempt,
            "timestamp_utc": timestamp.isoformat(),
            "derived_component": candidate["K04"],
        }
    if caption is not None:
        caption_bytes = caption.read_bytes()
        normalized = normalize_caption(caption_bytes.decode("utf-8-sig"))
        if not normalized:
            raise ValueError("Caption transcript normalizes to an empty string")
        nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
        candidate["K08"] = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16].hex().upper()
        result["witnesses"]["K08"] = {
            "original_sha256": sha256_file(caption_original),
            "transcription_sha256": hashlib.sha256(caption_bytes).hexdigest(),
            "normalized_caption": normalized,
            "derived_component": candidate["K08"],
        }
    trial = evaluate(candidate, targets)
    conflicts = []
    for key in result["witnesses"]:
        result["witnesses"][key]["slot_status"] = trial["slots"][key]
        if trial["slots"][key] != "PASS" and key in previously_verified:
            candidate[key] = previously_verified[key]
            conflicts.append(key)
    acceptance = evaluate(candidate, targets)
    result["conflicting_witnesses"] = conflicts
    result["acceptance"] = acceptance
    result["partial_candidate"] = {key: candidate[key] if acceptance["slots"][key] == "PASS" else None for key in candidate}
    if acceptance["accepted"]:
        result["candidate"] = candidate
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coupon", type=Path, help="JSON transcription with job/attempt/state/class/timestamp_utc/payload_hex")
    parser.add_argument("--coupon-original", type=Path, help="Unmodified coupon source file, image, or journal for SHA-256")
    parser.add_argument("--caption", type=Path, help="UTF-8 transcription of the exact final caption")
    parser.add_argument("--caption-original", type=Path, help="Unmodified final-caption source for SHA-256")
    args = parser.parse_args()
    try:
        result = assess(args.coupon, args.coupon_original, args.caption, args.caption_original)
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
        print(json.dumps({"error": str(exc), "accepted": False}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["acceptance"]["accepted"] and not result["conflicting_witnesses"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
