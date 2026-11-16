#!/usr/bin/env python3
"""Source-pinned RC-17 revision-delta screen for the K04 commitment.

This tests only a narrow cross-slot hypothesis: an ESC-N coupon might equal
one of the four-word RC-17 revision blocks, or the per-stage XOR delta between
two revisions, serialized in the documented SERVICE_ORDER. It does not assert
that RC-17 is a K04 source.
"""
from __future__ import annotations

import configparser
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
ROUTING_PATH = RES / "evidence" / "recovery-routing.json"
ACCEPTANCE_PATH = RES / "acceptance.json"
LABELS_PATH = RES / "evidence" / "archive-labels.ini"
RC17_PATH = RES / "evidence" / "procedures" / "RC-17-scans.txt"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    routing = json.loads(ROUTING_PATH.read_text(encoding="utf-8"))
    acceptance = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))
    labels = configparser.ConfigParser()
    labels.read(LABELS_PATH, encoding="utf-8")
    service_order = [x.strip() for x in labels["archive"]["service_order"].split(",")]

    text = RC17_PATH.read_text(encoding="utf-8")
    pages: dict[str, dict[str, bytes]] = {}
    for page in text.split("\f"):
        header = re.search(r"DOCUMENT RC-17 / REV ([^ /]+) / SECTION ([A-Z]+)", page)
        footer = re.search(r"Footer control strip: ([0-9A-F]{8})", page)
        if not header or not footer:
            continue
        revision, section = header.groups()
        pages.setdefault(revision, {})[section] = bytes.fromhex(footer.group(1))

    revisions = ["B", "C", "D-draft"]
    for revision in revisions:
        missing = [s for s in service_order if s not in pages.get(revision, {})]
        if missing:
            raise SystemExit(f"{revision} missing SERVICE_ORDER sections: {missing}")

    raw_blocks = {
        revision: b"".join(pages[revision][section] for section in service_order)
        for revision in revisions
    }
    if any(len(block) != 16 for block in raw_blocks.values()):
        raise SystemExit("Expected exactly four 4-byte strips per revision")

    # Positive control: the authorized Rev C block is the accepted K06 source.
    k06_ok = sha256(raw_blocks["C"]) == acceptance["slot_sha256"]["K06"]
    if not k06_ok:
        raise SystemExit("K06 positive control failed; check source parsing/order")

    mask = bytes.fromhex(routing["K04"]["masked_component"])
    target = acceptance["slot_sha256"]["K04"]
    candidates: dict[str, bytes] = {
        f"raw_{revision}": raw_blocks[revision] for revision in revisions
    }
    for left, right in itertools.combinations(revisions, 2):
        candidates[f"delta_{left}_{right}"] = b"".join(
            bytes(a ^ b for a, b in zip(pages[left][section], pages[right][section]))
            for section in service_order
        )

    results = []
    for name, coupon in candidates.items():
        component = bytes(a ^ b for a, b in zip(coupon, mask))
        digest = sha256(component)
        results.append({
            "candidate": name,
            "coupon_hex": coupon.hex().upper(),
            "component_hex": component.hex().upper(),
            "component_sha256": digest,
            "matches_K04": digest == target,
        })

    output = {
        "source_sha256": {
            str(p.relative_to(ROOT)): sha256(p.read_bytes())
            for p in (ROUTING_PATH, ACCEPTANCE_PATH, LABELS_PATH, RC17_PATH)
        },
        "service_order": service_order,
        "revisions": {
            revision: {
                section: pages[revision][section].hex().upper()
                for section in service_order
            }
            for revision in revisions
        },
        "K06_positive_control": {
            "revC_service_order_block": raw_blocks["C"].hex().upper(),
            "sha256": sha256(raw_blocks["C"]),
            "matches_K06": k06_ok,
        },
        "K04_mask": mask.hex().upper(),
        "K04_target_sha256": target,
        "candidate_count": len(results),
        "K04_hits": sum(row["matches_K04"] for row in results),
        "results": results,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
