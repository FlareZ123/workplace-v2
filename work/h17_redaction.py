"""Default-safe JSON redaction for H-17 recovery intake tools.

Raw components, phrases, HMACs, nonces, masks, checkpoints and derived
component digests may be needed in memory for authorized verification, but
must not appear in CLI output, JSON artifacts, workflow logs or broadcasts.
Use reveal=True only for explicitly authorized in-process analysis.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from functools import wraps

_SENSITIVE_EXACT = {
    "candidate", "candidate_bytes", "candidate_hex", "candidate_phrase",
    "component", "component_hex", "component_sha256", "expected_component_sha256",
    "chain_hex", "checkpoint_chain_hex", "selected_checkpoints", "checkpoint",
    "phrase", "raw_phrase", "normalized_phrase", "normalized_caption", "raw_text", "raw_record_hex",
    "raw_payload", "payload", "payload_hex",
    "hmac", "hmac16", "hmac_hex", "nonce", "nonce_hex", "desk_nonce", "desk_nonce_hex",
    "target", "target_hex", "target_sha256", "slot_sha256", "k08_target_sha256",
    "route_mask", "route_mask_hex", "mask", "mask_hex", "raw_component", "actual_component", "expected_component",
    "formula_text", "formula_tokens_hex", "string_record_hex",
    "comment_author", "author", "text", "value", "raw_value", "cached_value",
    "context", "comment", "caption", "formula", "cell_value",
    "actual_sha256", "expected_sha256", "sha256",
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
def _basename(value: Any) -> str:
    """Return a basename for POSIX, Windows, UNC and PathLike inputs."""
    raw = os.fspath(value) if isinstance(value, os.PathLike) else str(value)
    normalized = raw.replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1].rstrip(".,;:)]}")


def _redact_string(value: str) -> str:
    """Scrub paths and long hex tokens embedded in strings."""
    text = value
    path_patterns = (
        r"(?i)\b[A-Z]:[\\/][^\s\"'<>|]+",
        r"\\\\[^\s\"'<>|]+",
        r"(?<![:\w/])/(?!/)[^\s\"'<>|]+",
    )
    for pattern in path_patterns:
        text = re.sub(pattern, lambda match: _basename(match.group(0)), text)
    # Long hex values can be components, nonces, masks or digests even when
    # the producer omitted a sensitive field label.
    text = re.sub(r"(?i)\b[0-9a-f]{16,}\b", "[redacted]", text)
    return text


_DIAGNOSTIC_KEYS = {"error", "exception", "diagnostic", "stderr", "stdout", "traceback", "message"}


def _redact_diagnostic_string(value: str) -> str:
    """Free-form diagnostics can embed arbitrary source text; hide by default."""
    return "[redacted diagnostic]"


def _sensitive_key(key: str) -> bool:
    normalized = key.casefold()
    if "hmac" in normalized:
        return True
    return normalized in _SENSITIVE_EXACT or any(
        fragment in normalized for fragment in _SENSITIVE_FRAGMENTS
    )


def _safe_hmac_metadata(key: str, value: Any) -> bool:
    """Preserve only typed scalar HMAC status/count flags, never match payloads."""
    normalized = key.casefold()
    if "hmac" not in normalized:
        return False
    if normalized.endswith(("_count", "_matches")):
        return isinstance(value, int) and not isinstance(value, bool)
    if normalized.endswith("_status"):
        return (
            isinstance(value, str)
            and len(value) <= 32
            and re.fullmatch(r"[A-Za-z0-9_-]+", value) is not None
        )
    if normalized.endswith(("_match", "_pass", "_passed")):
        return isinstance(value, bool)
    return False


def _walk(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if _sensitive_key(str(key)) and not _safe_hmac_metadata(str(key), item):
                continue
            normalized_key = str(key).casefold()
            if normalized_key in _DIAGNOSTIC_KEYS and isinstance(item, str):
                clean[key] = _redact_diagnostic_string(item)
            elif (normalized_key == "path" or normalized_key.endswith("_path")) and isinstance(item, (str, os.PathLike)):
                clean[key] = _basename(item)
            else:
                clean[key] = _walk(item)
        return clean
    if isinstance(value, (list, tuple)):
        return [_walk(item) for item in value]
    if isinstance(value, bytes):
        return {"redacted": True, "byte_length": len(value)}
    if isinstance(value, os.PathLike):
        return _basename(value)
    if isinstance(value, str):
        return _redact_string(value)
    return value


def redact_sensitive(value: Any) -> Any:
    """Return a recursively redacted JSON-safe copy; never mutate the input."""
    clean = _walk(value)
    if isinstance(clean, dict):
        clean["redaction_applied"] = True
    return clean


def _safe_exception(exc: Exception) -> Exception:
    safe_args = tuple(
        _redact_diagnostic_string(arg) if isinstance(arg, str) else _walk(arg)
        for arg in exc.args
    )
    try:
        return type(exc)(*safe_args)
    except Exception:
        return RuntimeError(f"{type(exc).__name__}: diagnostic details redacted")


def redact_by_default(function):
    """Decorator: raw returns and diagnostics require explicit in-process reveal=True."""
    @wraps(function)
    def wrapped(*args, reveal: bool = False, **kwargs):
        try:
            result = function(*args, **kwargs)
        except Exception as exc:
            if reveal:
                raise
            safe_exception = _safe_exception(exc)
        else:
            return result if reveal else redact_sensitive(result)
        # Raise only after leaving the except block so the original exception
        # is not retained as a hidden __context__ on the sanitized exception.
        raise safe_exception
    return wrapped
