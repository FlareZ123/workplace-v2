#!/usr/bin/env python3
"""Assemble and independently verify all eight H-17 components from native sources.

This read-only library accepts an independently acquired source file for each
missing component and scans complete candidates using the existing K04/K08
native input adapters. No candidate is returned unless the untouched original
REC8/1 verifier accepts every slot and the combined commitment.

The source objects are passed as paths; original evidence is never modified.
The single accepted-candidate result remains in memory for its caller to
preserve through an appropriate records-custody process.
"""
from __future__ import annotations

import json
from pathlib import Path

from h17_redaction import redact_by_default

from resources.verify import evaluate
from h17_ax7782_k08_phrase_intake import (
    decode_text_variants, iter_text_streams, normalize,
    scan_authored_text_units, scan_phrase_spans,
)
from h17_k04_binary_window_intake import run_scan

ROOT = Path(__file__).resolve().parents[1]
SOURCE_LIMIT = 256 * 1024 * 1024
TOTAL_LIMIT = 512 * 1024 * 1024


def _regular_source(path: Path) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"original source is unavailable or is a symbolic link: {path}")
    if path.stat().st_size > SOURCE_LIMIT:
        raise ValueError(f"original source exceeds {SOURCE_LIMIT} byte bound: {path}")
    return path


@redact_by_default
def recover_complete(
    k04_source: Path,
    k08_source: Path,
    *,
    targets: dict | None = None,
    routing: dict | None = None,
    six_pass: dict | None = None,
    root: Path = ROOT,
    ocr: bool = False,
) -> dict:
    """Return only an original-verifier-accepted complete candidate.

    Alternative targets/routing/baselines support synthetic, source-blind tests;
    production defaults load the unchanged official resources and candidate.
    """
    k04_source = _regular_source(Path(k04_source))
    k08_source = _regular_source(Path(k08_source))
    targets = targets if targets is not None else json.loads(
        (root / "resources" / "acceptance.json").read_text(encoding="utf-8")
    )
    routing = routing if routing is not None else json.loads(
        (root / "resources" / "evidence" / "recovery-routing.json").read_text(encoding="utf-8")
    )
    six_pass = six_pass if six_pass is not None else json.loads(
        (root / "candidate.json").read_text(encoding="utf-8")
    )

    k04_result = run_scan(
        k04_source,
        targets["slot_sha256"]["K04"],
        routing["K04"]["masked_component"],
        1, SOURCE_LIMIT, TOTAL_LIMIT, 4, 10_000, reveal=True,
    )
    k04_candidates = {
        hit["component_hex"]
        for hit in k04_result["hits"]
    }

    # The original shared K08 decoder handles nested document streams,
    # native M10 OfficeArt text, verified images and the frozen teal-bit route.
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target = bytes.fromhex(targets["slot_sha256"]["K08"])
    errors: list[dict] = []
    style_metadata: list[dict] = []
    budget = [0]
    found_phrases: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for source, data in iter_text_streams(
        k08_source.name, k08_source.read_bytes(), 0, budget, errors, ocr,
        None, style_metadata,
    ):
        local_variants: set[str] = set()
        for label, text in decode_text_variants(data, source):
            normalized = normalize(text)
            if not normalized or normalized in local_variants:
                continue
            local_variants.add(normalized)
            hits: list[dict] = []
            scan_phrase_spans(text, nonce, target, f"{source} [{label}]", 48, hits)
            scan_authored_text_units(
                text, nonce, target, f"{source} [{label}]", hits)
            for hit in hits:
                pair = (hit["normalized_phrase"], hit["component_hex"])
                if pair not in seen:
                    seen.add(pair)
                    found_phrases.append(hit)

    k08_candidates = {hit["component_hex"] for hit in found_phrases}
    complete = None
    check = None
    if len(k04_candidates) == 1 and len(k08_candidates) == 1:
        trial = dict(six_pass)
        trial["K04"] = next(iter(k04_candidates))
        trial["K08"] = next(iter(k08_candidates))
        check = evaluate(trial, targets)
        if check["accepted"]:
            complete = trial

    return {
        "accepted": complete is not None,
        "candidate": complete,
        "verification": check,
        "k04_component_hits": len(k04_candidates),
        "k08_component_hits": len(k08_candidates),
        "k08_phrase_hits": found_phrases,
        "k08_source_errors": errors,
    }
