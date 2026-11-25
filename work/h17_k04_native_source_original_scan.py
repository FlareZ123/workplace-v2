"""Run the original H-17 K04 commitment against newly supported native-media carriers.

Read-only source scan. A discovered hit must be validated with resources.verify,
then checked for independent historical provenance; synthetic tests are separate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from h17_k04_binary_window_intake import run_scan

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "resources"
ROUTE = SOURCE / "evidence" / "recovery-routing.json"
ACCEPTANCE = SOURCE / "acceptance.json"


def main() -> None:
    route = json.loads(ROUTE.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
    result = run_scan(
        SOURCE,
        acceptance["slot_sha256"]["K04"],
        route["K04"]["masked_component"],
        stride=1,
        max_member=256 * 1024 * 1024,
        max_total=512 * 1024 * 1024,
        max_depth=4,
        max_members=10_000,
        reveal=True,
    )
    hits = list(result["hits"])
    print(
        "ORIGINAL_H17_K04_NEW_NATIVE_SOURCE_SCAN"
        f" files={result['files_scanned']}"
        f" members={result['members_scanned']}"
        f" bytes={result['bytes_scanned_or_decompressed']}"
        f" exact_commitment_hits={len(hits)}"
    )
    for hit in hits:
        candidate = bytes.fromhex(hit["component_hex"])
        assert hashlib.sha256(candidate).hexdigest() == acceptance["slot_sha256"]["K04"]
        print("ORIGINAL_K04_EXACT_HIT " + json.dumps(hit, sort_keys=True))
    for skipped in result["skipped"]:
        print("SKIPPED_OR_INCOMPLETE " + json.dumps(skipped, sort_keys=True))
    for source in result["files"]:
        if source.get("scan_limit") or source.get("status") or source.get("container_error"):
            print("SOURCE_COVERAGE " + json.dumps({
                k: source[k]
                for k in ("name", "status", "scan_limit", "container_error")
                if k in source
            }, sort_keys=True))
    print("ORIGINAL_K04_RECOVERY" + (" MATCH_FOUND" if hits else " STILL_MISSING"))


if __name__ == "__main__":
    main()
