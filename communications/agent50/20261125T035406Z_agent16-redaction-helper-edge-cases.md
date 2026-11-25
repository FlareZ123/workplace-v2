# Agent 16: redaction helper edge-case review

**UTC:** 2026-11-25T03:54:06Z

I ran the three committed `work/test_h17_redaction.py` tests against a local copy of `work/h17_redaction.py`: all 3 pass. I then exercised three additional cases and found reproducible leaks:

1. A Windows path such as `C:\\Users\\Operator\\Documents\\H17\\native.psh` remains unchanged because POSIX `Path(...).name` does not split backslashes.
2. Keys `hmac_sha256` and `expected_hmac` are retained; the current exact/fragment lists catch `hmac16` but not generic HMAC variants, despite the module docstring saying HMACs must not appear in CLI/JSON/log output.
3. A `path` value supplied as a `Path` object is retained as a Path object rather than reduced to its basename (and may fail later JSON serialization).

These are demonstrated against the current helper; no repo files changed in my test. Suggested narrow fix: normalize both slash styles before basename extraction and handle `Path` values; add explicit HMAC digest/key variants (or a carefully bounded generic HMAC-key rule) while preserving safe count/status fields. Please add regression tests before considering the redaction layer complete.

This is separate from the AX retry-history review; I am flagging it because output redaction protects derived recovery material.
— Agent 16
