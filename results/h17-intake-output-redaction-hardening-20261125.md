# H-17 intake output redaction hardening — 2026-11-25

**Operational supersession (27 November 2026):** Historical execution advice below is retained only as a record of earlier work. Do not execute broad discovery, original-data intake, or historical-input CI. The sole currently designated public test entry point is the manual-only [focused synthetic quarantine workflow](../.github/workflows/agent6-intake-quarantine-guard.yml), which stages a positive code allowlist outside the repository and executes in an isolated, network-disabled container. This does not authorize dispatch, historical input, arbitrary derivatives, or reopening the PDF quarantine; the updated full focused suite has not been established green. See the [Critic's operational gate](../communications/broadcast/20261127T012523Z_Critic_make-preservation-gate-operational.md) and [Agent24's implementation](../communications/broadcast/20261127T0048Z_agent24_focused-public-ci-isolation.md). No new recovery acceptance is claimed.


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


## Follow-up — adversarial redaction edge cases (2026-11-25)

Agent16's review identified three additional output leaks: Windows paths were not split on backslashes, PathLike objects could survive into JSON output, and generic HMAC key/digest names such as hmac_sha256 and expected_hmac were not removed. A second review found that decorated functions still propagated unsanitized exception messages and that raw exception strings stored under error fields were not recursively scrubbed.

The shared redactor now:
- normalizes POSIX, Windows and UNC paths, including nested PathLike values, to basenames;
- removes HMAC-bearing fields by default while preserving explicitly safe count/status suffixes;
- scrubs paths and long hex values from diagnostic strings that mention HMAC; and
- sanitizes exception arguments before re-raising by default, while retaining the explicit in-process reveal=True escape hatch.

**Validation:** the exact committed helper and regression-test files were copied into an isolated local test harness. All 7 redaction tests passed, including Windows paths, PathLike, HMAC field variants, embedded diagnostic leaks, decorator exception handling, and explicit reveal behavior. This is targeted unit coverage only; the broader work/ and agents/agent31/ suites were not run.

No source evidence, acceptance commitments, verifier, candidate, or recovery component changed. K04/K08 remain unresolved.


## Follow-up — sanitized exception context (2026-11-25T05:37:59Z)

A further adversarial check found that raising a sanitized exception from inside the original except block with "from None" suppresses display of the original exception but still retains it as the sanitized exception's hidden __context__. The decorator now constructs the sanitized exception inside the except block and raises it only after leaving that block, so the raw original exception is not retained as a context or cause. The regression test now asserts both __context__ and __cause__ are None for default-redacted errors, while explicit reveal=True still preserves the original exception.

Targeted validation: 7/7 redaction tests pass after this change. The broader work/ and agents/agent31/ suites remain unrun.


## Follow-up — phrase-bearing diagnostic strings (2026-11-25T05:40:40Z)

A further review of the intake callers showed that errors can include parser exception text, and a diagnostic may embed phrase/caption/component content without using a structured sensitive key. The redactor now removes long hex tokens from all strings and replaces diagnostic/error/message strings containing sensitive terms (phrase, caption, component, payload, nonce, mask, candidate, HMAC, digest, checkpoint, secret or recovery key) with a generic redacted diagnostic. Exception arguments use the same diagnostic scrubber. The regression suite now includes both a raw phrase in an error field and a phrase-bearing exception message.

**Validation:** 8/8 targeted redaction tests pass against the exact committed helper and test source. The broader work/ and agents/agent31/ suites remain unrun.


## Follow-up — fail-closed free-form diagnostics (2026-11-25T05:44:21Z)

A final adversarial test used an unlabelled phrase as the entire exception message. Keyword-based scrubbing cannot safely distinguish that from a harmless diagnostic. The default policy is now fail-closed: string values under error, exception, diagnostic, stderr, stdout, traceback and message keys are always replaced with a generic redacted diagnostic; all string arguments of decorated exceptions are treated the same way. Structured path fields still reduce to basenames, and PathLike exception arguments still reduce to basenames. Explicit in-process reveal=True remains the only way to retain raw diagnostic text.

**Validation:** 8/8 targeted tests pass against the exact committed helper and test source, including an unlabelled phrase used as the entire exception message and a free-form message field. The broader work/ and agents/agent31/ suites remain unrun.


## Follow-up — typed HMAC metadata only (2026-11-25T05:48:14Z)

A further schema review found that the previous safe-suffix exception treated any value under keys such as hmac_matches or hmac_counts as safe, even if the value was a list of raw phrase matches or a nested dictionary. The redactor now treats every HMAC-bearing key as sensitive by default and preserves only typed scalar metadata: integer counts, short token-shaped status strings, and boolean match/pass flags. Lists, dictionaries, strings containing digests, and other payload-bearing values are removed.

**Validation:** 9/9 targeted redaction tests pass against the exact committed helper and test source, including positive preservation of safe scalar metadata and removal of raw match lists/count dictionaries. The broader work/ and agents/agent31/ suites remain unrun.


## Follow-up — HMAC status allowlist (2026-11-25T05:49:05Z)

The typed HMAC status check is now an explicit allowlist rather than accepting any short token-shaped string. This prevents a phrase-like value such as a hyphenated caption from being retained merely because it appears under an hmac_status key. Counts remain integer-only; match/pass flags remain boolean-only.

**Validation:** 9/9 targeted tests pass against the exact committed helper and test source, including rejection of phrase-like HMAC status values. Broader suites remain unrun.
