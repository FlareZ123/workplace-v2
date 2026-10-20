"""Offline K08 candidate check against the unchanged archive commitment."""
import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "resources/evidence/recovery-routing.json"
ACCEPTANCE = ROOT / "resources/acceptance.json"

def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())

def evaluate(phrase: str) -> tuple[str, str, bool]:
    routing = json.loads(ROUTE.read_text(encoding="utf-8"))
    targets = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    normalized = normalize(phrase)
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    component = hmac.new(nonce, normalized.encode("utf-8"), hashlib.sha256).digest()[:16]
    accepted = hashlib.sha256(component).hexdigest() == targets["slot_sha256"]["K08"]
    return normalized, component.hex().upper(), accepted

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phrase", nargs="?", help="Quote final keeper caption; stdin when omitted.")
    args = parser.parse_args()
    phrase = args.phrase if args.phrase is not None else sys.stdin.read()
    normalized, hex_value, accepted = evaluate(phrase)
    print(json.dumps({"normalized": normalized, "K08": hex_value, "slot_status": "PASS" if accepted else "NO_MATCH"}, indent=2))
    return 0 if accepted else 1

if __name__ == "__main__":
    raise SystemExit(main())
