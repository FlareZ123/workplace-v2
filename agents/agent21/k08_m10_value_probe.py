#!/usr/bin/env python3
"""Read-only, exact-cell K08 candidate test for every worksheet's M10 value.

This is a narrow extension of the source-derived mug-stock.xls lead. It does
not search arbitrary workbook cells or comments. It evaluates only M10's
literal cell value and, separately, the cached result of an M10 formula.
Formula text itself is preserved as context but is never treated as the
keeper's phrase. LibreOffice-derived formula caches are explicitly provisional
because conversion may recalculate them.

Run from workplace-v2:
  python agents/agent21/k08_m10_value_probe.py --workbook /path/to/mug-stock.xls
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_N02_HMAC16 = "BF889359B0303F2B2B2FD96AE841210B"


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def k08_component(nonce: bytes, phrase: str) -> bytes:
    return hmac.new(nonce, normalize(phrase).encode("utf-8"), hashlib.sha256).digest()[:16]


def load_rules(resources: Path) -> tuple[bytes, bytes]:
    route = json.loads((resources / "evidence" / "recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((resources / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    if len(nonce) != 16 or len(target) != 32:
        raise ValueError("invalid K08 nonce or commitment width")
    control = k08_component(nonce, "A good watch leaves the room ready for the next pair of hands")
    if control.hex().upper() != EXPECTED_N02_HMAC16:
        raise ValueError("K08 normalization/HMAC known-answer control failed")
    return nonce, target


def _candidate(source: str, sheet: str, sheet_state: str, value_kind: str,
               raw_text: str, nonce: bytes, target: bytes, **extra: Any) -> dict[str, Any]:
    normalized = normalize(raw_text)
    component = k08_component(nonce, normalized)
    digest = hashlib.sha256(component).hexdigest()
    return {
        "source": source,
        "sheet": sheet,
        "sheet_state": sheet_state,
        "cell": "M10",
        "value_kind": value_kind,
        "raw_text": raw_text,
        "normalized_phrase": normalized,
        "hmac16": component.hex().upper(),
        "component_sha256": digest,
        "match": hmac.compare_digest(digest, target.hex()),
        **extra,
    }


def evaluate_m10_values(extracted: dict[str, Any], nonce: bytes,
                        target: bytes) -> dict[str, Any]:
    """Evaluate only exact M10 cell-value streams from the XLS intake adapter."""
    sheet_states = {
        str(meta.get("name", "")): str(meta.get("state", "unknown"))
        for meta in extracted.get("sheets", [])
    }
    candidates: list[dict[str, Any]] = []
    formulas: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for stream in extracted.get('text_streams', []):
        if stream.get("kind") != "cell":
            continue
        source = str(stream.get("source", ""))
        if "!" not in source:
            continue
        sheet, address = source.rsplit("!", 1)
        if address.upper() != "M10":
            continue
        state = sheet_states.get(sheet, "unknown")
        data_type = str(stream.get("data_type", "unknown"))
        raw_value = stream.get("text")
        cached_value = stream.get("converted_cached_value")

        if data_type.casefold() == "f":
            formula_record = {
                "source": source,
                "sheet": sheet,
                "sheet_state": state,
                "cell": "M10",
                "formula_text": raw_value,
                "cached_value_available": isinstance(cached_value, str) and bool(cached_value.strip()),
                "cache_provenance": "LibreOffice-converted data_only value; may have been recalculated",
            }
            formulas.append(formula_record)
            if isinstance(cached_value, str) and cached_value.strip():
                key = (source, "converted_formula_cache", cached_value)
                if key not in seen:
                    seen.add(key)
                    candidates.append(_candidate(
                        source, sheet, state, "converted_formula_cache",
                        cached_value, nonce, target,
                        formula_text=raw_value,
                        cache_provenance="LibreOffice-converted data_only value; may have been recalculated",
              ))
            continue

        if data_type.casefold() in {"e", "b"}:
            continue
        if isinstance(raw_value, str) and raw_value.strip():
            key = (source, "literal_cell_value", raw_value)
            if key not in seen:
                seen.add(key)
                candidates.append(_candidate(
                    source, sheet, state, "literal_cell_value",
                    raw_value, nonce, target, data_type=data_type,
                    value_provenance="cell value from converted read-only workbook copy",
                ))
        if isinstance(cached_value, str) and cached_value .strip() and cached_value != raw_value:
            key = (source, "converted_cached_value", cached_value)
            if key not in seen:
                seen.add(key)
                candidates.append(_candidate(
                    source, sheet, state, "converted_cached_value",
                    cached_value, nonce, target, data_type=data_type,
                    cache_provenance="LibreOffice-converted data_only value; may have been recalculated",
                ))

    matches = [item for item in candidates if item["match"]]
    status = "MATCH_REQUIRES_SOURCE_REVIEW" if matches else (
        "NO_M10_VALUE_MATCH" if candidates else
        "NO_M10_TEXT_VALUE" if not formulas else
        "M10_FORMULA_WITHOUT_TEXT_CACHE"
    )
    return {
        "status": status,
        "candidate_count": len(candidates),
        "match_count": len(matches),
        "candidates": candidates,
        "formula_records": formulas,
        "scope": [
            "Only exact M10 is evaluated on each worksheet listed by the source intake adapter.",
            "No sheet ordering, hidden-sheet priority, neighboring-cell search, or comment search is inferred.",
            "Formula text is context only and is never hashed as the keeper phrase.",
            "Formula cached values are separate provisional candidates because LibreOffice may recalculate them.",
            "A commitment hit is a candidate requiring verification against the original BIFF stream and authorship; not by itself an authenticity finding.",
            "No workbook source bytes are modified.",
        ],
    }


def inspect_workbook(workbook]\ÛÝ\Ù\Î]
HOXÝÜÝ[WNÛÜØÛÚÈHÛÜØÛÚË^[\ÙJ
KXÛÛ]J
B[ÈHÛÜØÛÚËÝ]

BYÛÜØÛÚË\×ÜÞ[[[Ê
HÜÝÛÜØÛÚË\×Ù[J
NZ\ÙH[YQ\ÜÛÜØÛÚÈ]\ÝHHYÝ[\Û\Þ[[[È[HBÛÙK\Ù]HØYÜ[\Ê\ÛÝ\Ù\ÊBÛÜ×Ù\H]
×Ù[W×ÊK\ÛÛJ
K\[ÖÌHÈÛÜÈÞ\Ë][Ù\
ÝÛÜ×Ù\JBNÛHM×Þ×Û×Ù[XÚÈ[\Ü^XÝ\È^XÝÞÂ^Ù\[\Ü\Ü\È^ÎZ\ÙH[[YQ\ÜÛÜËÚM×Þ×Û×Ù[XÚËH[]ÈÜ[Û[\[[ÚY\È\H\]Z\YHÛH^Â^XÝYH^XÝÞÊÛÜØÛÚÊBYÜHH^XÝYÙ]
ÛÝ\ÙWÜÚLMØYÜHBY\H^XÝYÙ]
ÛÝ\ÙWÜÚLMØY\BYÝ^XÝYÙ]
ÛÝ\ÙWÝ[Ú[ÙYHÜÝYÜHÜYÜHOHY\Z\ÙH[[YQ\ÜYØXÞHÈ[ZÙHYÝÛÛ\H[Ú[ÙYÛÝ\ÙH]\ÈB][X]YH][X]WÛLLÝ[Y\Ê^XÝYÛÙK\Ù]
B]\ÂÛÜØÛÚÈÂ]ÝÛÜØÛÚÊKÚ^WØ]\È[ËÝÜÚ^KÚLMØYÜHYÜKÚLMØY\Y\ÛÝ\ÙWÝ[Ú[ÙYYKÛÛ\\^XÝYÙ]
ÛÛ\\KÜ][WÝ[Y\×ÛÝH^XÝYÙ]
Ü][WÝ[Y\×ÛÝHKKÌÝ\Ù]ÜÚLM\Ù]^

KÌÙ\Ú×ÛÛÙWÚ^ÛÙK^

K\\
KÚY]Ú[[ÜH^XÝYÙ]
ÚY]È×JK
][X]YBYXZ[
HO[\Ù\H\Ü\ÙK\Ý[Y[\Ù\\ØÜ\[ÛW×ÙØ××ÊB\Ù\YØ\Ý[Y[
K]ÛÜØÛÚÈ\]Z\YUYK\OT]
B\Ù\YØ\Ý[Y[
K\\ÛÝ\Ù\È\OT]Y][T]
\ÛÝ\Ù\ÈJB\Ù\YØ\Ý[Y[
KZÛÛ[Ý]\OT]
B\ÜÈH\Ù\\ÙWØ\ÜÊ
BN\Ý[H[ÜXÝÝÛÜØÛÚÊ\ÜËÛÜØÛÚË\ÜË\ÛÝ\Ù\ÊB^Ù\^Ù\[Û\È^Î\Ù\\ÜÝ^ÊJB[ÛÙYHÛÛ[\Ê\Ý[[[LÛÜÚÙ^\ÏUYJH
ÈY\ÜËÛÛÛÝ]Ý]H\ÜËÛÛÛÝ]^[\ÙJ
KXÛÛ]J
BYÝ]OH\ÜËÛÜØÛÚË^[\ÙJ
KXÛÛ]J
N\Ù\\ÜKZÛÛ[Ý]]\ÝÝÝ\Ü]HHÛÝ\ÙHÛÜØÛÚÈBÝ]\[ZÙ\\[ÏUYK^\ÝÛÚÏUYJBÝ]Ü]WÝ^
[ÛÙY[ÛÙ[ÏH]NB[
[ÛÙY[HB]\Y×Û[YW×ÈOH×ÛXZ[×ÈZ\ÙHÞ\Ý[Q^]
XZ[
JB