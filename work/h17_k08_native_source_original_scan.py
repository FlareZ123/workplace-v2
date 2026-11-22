"""Check original surviving H-17 files for exact native final-margin caption text.

Read-only source scan, no candidate generation or inferred paraphrases. Short
contiguous spans and preserved long authored lines/fields use the untouched
original K08 desk nonce, normalization, HMAC16 and SHA256 commitment.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from h17_ax7782_k08_phrase_intake import (
    decode_text_variants,
    iter_text_streams,
    load_k08_rules,
    normalize,
    scan_authored_text_units,
    scan_phrase_spans,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "resources"


def main() -> None:
    nonce, target = load_k08_rules(SOURCE)
    files = 0
    streams = 0
    variants = 0
    spans = 0
    authored = 0
    errors: list[dict] = []
    hits: list[dict] = []
    budget = [0]
    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        files += 1
        for name, payload in iter_text_streams(
            str(path.relative_to(SOURCE)), path.read_bytes(),
            0, budget, errors, False, None, [],
        ):
            streams += 1
            local: set[str] = set()
            for label, text in decode_text_variants(payload, name):
                canonical = normalize(text)
                if not canonical or canonical in local:
                    continue
                local.add(canonical)
                variants += 1
                origin = f"{name} [{label}]"
                spans += scan_phrase_spans(text, nonce, target, origin, 48, hits)
                authored += scan_authored_text_units(
                    text, nonce, target, origin, hits,
                )
    print(
        "ORIGINAL_H17_K08_NEW_NATIVE_SOURCE_SCAN"
        f" files={files} text_streams={streams}"
        f" normalized_views={variants}"
        f" short_source_spans={spans}"
        f" long_authored_units={authored}"
        f" exact_commitment_hits={len(hits)}"
        f" decode_diagnostics={len(errors)}"
    )
    for hit in hits:
        component = bytes.fromhex(hit["component_hex"])
        assert hashlib.sha256(component).digest() == target
        print("ORIGINAL_K08_EXACT_HIT " + json.dumps(hit, sort_keys=True))
    for item in errors[:15]:
        print("SOURCE_DIAGNOSTIC " + json.dumps(item, sort_keys=True))
    print("ORIGINAL_K08_RECOVERY" + (" MATCH_FOUND" if hits else " STILL_MISSING"))


if __name__ == "__main__":
    main()
