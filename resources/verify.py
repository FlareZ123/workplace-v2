"""Offline archive acceptance checker. Python 3 standard library only."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def evaluate(candidate, targets):
    if not isinstance(candidate, dict):
        raise ValueError("Candidate must be a JSON object")
    expected = [f"K{i:02d}" for i in range(1, 9)]
    extra = sorted(set(candidate) - set(expected))
    if extra:
        raise ValueError("Unknown candidate fields: " + ", ".join(extra))
    slots = {}
    for name in expected:
        value = candidate.get(name)
        if value is None:
            slots[name] = "MISSING"
        elif not isinstance(value, str) or not re.fullmatch(r"[0-9A-F]{32}", value):
            slots[name] = "FORMAT_ERROR"
        elif hashlib.sha256(bytes.fromhex(value)).hexdigest() == targets["slot_sha256"][name]:
            slots[name] = "PASS"
        else:
            slots[name] = "NO_MATCH"
    complete = all(isinstance(candidate.get(name), str) and re.fullmatch(r"[0-9A-F]{32}", candidate[name]) for name in expected)
    actual = None
    if complete:
        material = targets["combined_prefix"] + "".join(candidate[name] + "\n" for name in expected)
        actual = hashlib.sha256(material.encode("ascii")).hexdigest()
    combined_ok = actual == targets["combined_sha256"] if actual else False
    accepted = all(value == "PASS" for value in slots.values()) and combined_ok
    return {"slots": slots, "passed": sum(value == "PASS" for value in slots.values()), "combined": "PASS" if combined_ok else ("NO_MATCH" if complete else "INCOMPLETE"), "combined_sha256": actual, "accepted": accepted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="machine-readable result")
    args = parser.parse_args()
    try:
        targets = json.loads(Path(__file__).with_name("acceptance.json").read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8-sig"), object_pairs_hook=no_duplicates)
        result = evaluate(candidate, targets)
    except (OSError, ValueError, TypeError) as exc:
        result = {"accepted": False, "error": str(exc)}
        print(json.dumps(result, indent=2) if args.json else "ERROR: " + str(exc))
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, state in result["slots"].items():
            print(f"{name}: {state}")
        print(f"Combined: {result['combined']}")
        print(f"Accepted: {'YES' if result['accepted'] else 'NO'}")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
