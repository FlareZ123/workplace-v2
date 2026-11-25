# H-17 intake output redaction hardening — 2026-11-25

**Status:** security hardening only; not a recovery finding.

## Problem

A review of the existing passive intake path found that several high-level APIs and command-line tools could return or print recovery material directly. Affected outputs included the AX-7782 K07 chain/component, K04 binary-window component hits and route parameters, K08 phrase/HMAC hits and SQLite-carved values, M10 workbook values and component digests, and the manually verified complete candidate. The AX-7782 joint wrapper also retained subprocess stdout/stderr tails on failures, which could have copied sensitive output into its aggregate JSON.

This contradicted the repository's existing requirement that raw recovery material must not be logged or published.

## Changes

- Added `work/h17_redaction.py`, a shared recursive redactor plus `@redact_by_default`. High-level APIs now return redacted summaries by default; an authorized local caller must explicitly pass `reveal=True` in-process to receive raw results. No CLI exposes a reveal switch.
- Applied the default to:
  - `work/h17_ax7782_object_intake.py:inspect_object`
  - `work/h17_k04_binary_window_intake.py:run_scan`
- `work/h17_k04_biff8_xf_candidate.py:check_k04_commitment` and the `work/h17_k04_mug_stock_xf_probe.py` CLI
  - `work/h17_ax7782_k08_phrase_intake.py:inspect_object`
  - `work/h17_ax7782_k08_sqlite_bridge.py:scan_sqlite_members` and `inspect_object`
  - `work/h17_k08_m10_value_probe.py:evaluate_m10_values` and `inspect_workbook`
  - `work/h17_k08_m10_raw_biff_probe.py:inspect_workbook`
  - `agents/agent31/h17_verified_manual_intake.py:execute`
  - `work/h17_complete_native_recovery.py:recover_complete`
- Hardened CLI JSON output for those tools, the K04 mug-stock XF probe, the native K04 original-source scan, and the joint AX-7782 intake. The joint wrapper no longer includes subprocess stdout/stderr tails in its result.
- Removed the K04 binary scanner's embedded route-mask and target defaults. Its CLI now loads those values from the supplied local routing and acceptance resources at runtime; they are not included in the redacted output.
- Replaced K08 known-answer HMAC checks that used the live desk nonce with a synthetic nonce test vector. Corresponding M10 test fixtures now use a synthetic nonce rather than duplicating the live value.
- Added/updated tests for recursive redaction, explicit reveal in synthetic test paths, and default redaction of manual, phrase, SQLite, K04, M10 and complete-recovery results.

## Validation and limits

The changed source and test files were read back from the remote branch after commit. The targeted tests were updated but **were not executed in this invocation**; there was no available local checkout and no general-purpose unit-test workflow was present to run safely. A future local run should execute:

```sh
python -m unittest discover -s work -p 'test_*.py'
python -m unittest discover -s agents/agent31 -p 'test_*.py'
```

This change does not alter acceptance commitments, the original verifier, canonical candidates, or any recovered source evidence. It does not resolve K04 or K08, and it does not establish any new candidate relation. No recovery component, phrase, HMAC, nonce, mask, target digest, or source-text value is reproduced here.

Low-level parsing helpers remain intended for in-memory use by trusted callers. Do not log or persist their raw return values. For high-level results, use the default redacted form unless an authorized local verification step genuinely requires explicit `reveal=True`.
