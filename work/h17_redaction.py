"""Default-safe JSON redaction for H-17 recovery intake tools.

Raw components, phrases, HMACs, nonces, masks, checkpoints and derived
component digests may be needed in memory for authorized verification, but
must not appear in CLI output, JSON artifacts, workflow logs or broadcasts.
Use reveal=True only for explicitly authorized in-process analysis.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from functools import wraps

_SENSITIVE_EXACT = {
    "candidate", "candidate_bytes", "candidate_hex",
    "component", "component_hex", "component_sha256", "expected_component_sha256",
    "chain_hex", "checkpoint_chain_hex", "selected_checkpoints", "checkpoint",
    "normalized_phrase", "normalized_caption", "raw_text", "raw_record_hex",
    "raw_payload", "payload", "payload_hex",
    "hmac", "hmac16", "nonce", "desk_nonce", "desk_nonce_hex",
    "target", "target_sha256", "k08_target_sha256",
    "route_mask", "route_mask_hex", "mask", "mask_hex",
    "formula_text", "formula_tokens_hex", "string_record_hex",
    "comment_author", "author", "text", "value", "raw_value", "cached_value",
    "context", "comment", "caption", "formula", "cell_value",
    "actual_sha256", "expected_sha256",
    "raw_hits", "text_hits", "raw_text_carving",
    "text_sha256", "normalized_text_sha256",
    "crc16", "crc32_ieee", "adler32", "md5",
}

_SENSITIVE_FRAGMENTS = (
    "component_hex", "component_sha256", "expected_component_sha256",
    "normalized_phrase", "normalized_caption", "hmac16",
    "desk_nonce", "route_mask_hex", "checkpoint_chain_hex",
    "raw_record_hex", "k08_target_sha256",
)


def _sensitive_key(key: str) -> bool:
    normalized = key.casefold()
    return normalized in _SENSITIVE_EXACT or any(
        fragment in normalized for fragment in _SENSITIVE_FRAGMENTS
    )


def _walk(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if _sensitive_key(str(key)):
                continue
            if str(key).casefold() == "path" and isinstance(item, str):
                clean[key] = Path(item).name
            else:
                clean[key] = _walk(item)
        return clean
    if isinstance(value, (list, tuple)):
        return [_walk(item) for item in value]
    if isinstance(value, bytes):
        return {"redacted": True, "byte_length": len(value)}
    return value


def redact_sensitive(value: Any) -> Any:
    """Return a recursively redacted JSON-safe copy; never mutate the input."""
    clean = _walk(value)
    if isinstance(clean, dict):
        clean["redaction_applied"] = True
    return clean


def redact_by_default(function):
    """Decorator: raw return values require an explicit in-process reveal=True."""
    @wraps(function)
    def wrapped(*args, reveal: bool = False, **kwargs):
        result = function(*args, **kwargs)
        return result if reveal else redact_sensitive(result)
    return wrapped
