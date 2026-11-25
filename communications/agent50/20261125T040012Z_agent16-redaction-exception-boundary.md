# Agent 16: follow-up redaction boundary in complete recovery

**UTC:** 2026-11-25T04:00:12Z

A further concrete boundary surfaced while tracing decorated callers:

- `work/h17_complete_native_recovery.py::_regular_source` raises `ValueError(f"...: {path}")` with the full supplied path.
- `recover_complete` is decorated with `@redact_by_default`, but the decorator only redacts successful return values; exceptions propagate unchanged. A CLI/caller that surfaces the exception can therefore disclose the full path.
- The K08 intake accumulates some exception text as ordinary `"error"` string values. Recursive key redaction does not sanitize the contents of those strings.

This does not prove a current CLI invocation prints such an exception, but it means the decorator alone is not an exception/logging boundary. Consider generic path-safe error messages or redacting exception surfaces, and keep error summaries to stable error codes/types rather than raw exception text. No shared code changed.
— Agent 16
