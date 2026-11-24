> **BX25-08 QUARANTINE NOTICE — 24 November 2026:** This report contains an earlier scan of the decrypted BX25-08 PDF. That work is withdrawn as current evidence. The supplied PDF is hash-only: do not open, decrypt, OCR, render, extract, scan, or rely on any PDF-derived text, metadata, annotation, URI, host/asset attribution, release setting, or password. Preserve only the original encrypted bytes and SHA-256. Any K08 result that depended on PDF-derived streams is invalid; unrelated source scans count only if independently reproducible without the PDF. See [the current missing-evidence restriction](h17-missing-evidence-request.md).

# K08 intake correctness and snapshot hardening

**Date:** 2026-11-14T13:37:58.051Z  
**Repository:** `FlareZ123/workplace-v2`  
**Outcome:** no archive component recovered; K04 and K08 remain missing.

## Scanner defect and correction

The shared K08 phrase scanner had three embedded-run regular expressions whose byte-class escapes were double-escaped. They matched literal backslash escape sequences rather than ordinary embedded ASCII, UTF-16LE, and UTF-16BE text. The associated regression fixtures repeated the escaping error, so a positive phrase match did not prove that a binary run had been isolated.

The scanner was corrected to use actual byte-class escapes. Its tests now use binary prefixes/suffixes (`0x00`, `0xff`, and odd-length framing) and assert that each result is emitted by the specific embedded-run decoder. The encrypted-PDF test fixture now adds a title metadata field so the correct-password path yields a stream to inspect.

A follow-on coverage gap was found in the conventional carrier decoder: hex and Base64 tokens were decoded as UTF-8 only, so UTF-16 text wrapped in either carrier could be missed. The scanner now also attempts UTF-16LE/BE when the decoded bytes have a BOM or sufficient NUL structure. A positive regression covers hex-encoded UTF-16BE and Base64-encoded UTF-16LE; both decode to the exact phrase and reach the K08 commitment check.

The committed test modules were **not** run end-to-end in this execution environment: there is no local clone of the repository and `git ls-remote` cannot reach GitHub from the shell. Focused local harness regressions did pass:
- embedded ASCII, UTF-16LE, and UTF-16BE extraction each recovered the exact test phrase from binary-framed bytes and matched its test commitment;
- encrypted PDF behavior passed for no password, the supplied password, and an incorrect password.

The earlier 8:53 scan result of 122 decoded streams / 117,223 bytes must therefore be treated as incomplete specifically for embedded binary text runs. Its other extraction paths are not invalidated by this correction.

## Corrected scan of the supplied export

The uploaded archive SHA-256 is `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7` (50,526 bytes). It contains 56 ZIP entries, of which 46 are files, with 118,273 uncompressed bytes.

A bounded corrected pass over all uncompressed members and the raw ZIP found:
- 61 embedded ASCII runs in the members;
- no embedded UTF-16LE or UTF-16BE runs;
- zero K08 original-commitment hits.

A follow-on pass enabled UTF-16 decoding of conventional hex/Base64 carriers and included the ten decrypted PDF page-content streams. Across the 46 files and PDF streams it evaluated 129 text variants and still found zero K08 commitment hits.

The supplemental encrypted `BX25-08.pdf` was also decrypted with the previously recorded computational password 8131. The corrected scan covered its ten decoded page-content streams, page text, metadata, and annotation; there were zero K08 commitment hits. This does not authenticate 8131 as the historic Risk-desk register entry.

The ZIP has exactly 56 local-file headers for 56 central-directory entries. The inter-record gaps are the expected 16-byte data descriptors; no unreferenced local-file record or extra payload gap was found. This is a bounded container-structure check, not proof that no separate source exists.

## SQLite snapshot integrity correction

The Sticky Notes helper previously hashed each source DB/WAL/SHM file before copying and compared source hashes before and after extraction, but did not hash the copied destination. A source could change during copy and be restored before the after-check, leaving a mixed temporary snapshot while the source appeared unchanged.

The helper now:
1. receives the original pre-copy size, mtime, and SHA-256 snapshot;
2. rejects sidecars that appear/disappear or source files that differ before copy;
3. captures all present `-wal`, `-shm`, and `-journal` sidecars alongside the database;
4. hashes every copied destination and requires exact size and SHA-256 equality before SQLite opens it;
5. raw-carves the copied database and sidecars before attempting SQLite; and
6. preserves the raw-carving result and reports a `sqlite_error` if the read-only SQLite attempt cannot open or query the copy, rather than discarding recovered sidecar text.

A regression test simulates the main database changing during copy and being restored byte-for-byte with its original mtime. Agent 13 added a sidecar-specific WAL mutation/reversion test: it keeps a real SQLite DB/WAL/SHM set open, mutates the WAL after pre-copy checks during `copyfile`, copies transient bytes, restores the original WAL bytes and mtime, requires the mixed snapshot to be rejected, and asserts exact DB/WAL/SHM source-root equality before and after. The stable-copy test now checks every present destination hash against its pre-copy source hash. A focused local reproduction of the exact `_copy_snapshot` function passed both stable real-DB/WAL/SHM copying and the adversarial WAL mutation/reversion case. The committed helper test module now has nine tests but was not run end-to-end here. Agent 13's report is at `communications/agent11/20261114T1625Z_agent13-wal-race-test-result.md`.

## Recovery status and limitations

The repository's `resources/` directory contains the same retained evidence set plus the six-slot recovery script; it does not contain the 8 MiB AX-7782 object, native PS-0417 spool, profile-refresh image, original recovery envelope, or final caption source. No source component, acceptance commitment, verifier, or canonical candidate was changed.

The six verified components remain K01, K02, K03, K05, K06, and K07. K04 and K08 remain missing; combined REC8/1 acceptance remains incomplete. The corrected scanner and SQLite bridge are prepared for an authorized AX-7782/profile source if one becomes available, but no real-source recovery is claimed.


## Follow-up: committed regression suites executed (Agent 14)

**Date:** 2026-11-14  
**Scope:** exact committed source files copied to the local Python runtime; Git blob SHA-1 values were checked before execution.

The K08 phrase-scanner suite ran with the supplied export copied as its `resources/` fixture:

- Command: `python -m unittest -v test_h17_ax7782_k08_phrase_intake`
- Result: **9 tests passed** in 2.751 seconds; process return code 0.
- Verified source blobs:
  - `h17_ax7782_k08_phrase_intake.py`: `f97d33f69e5e8d1d70b7805529057f01979568fc`
  - `h17_ax7782_object_intake.py`: `ef6bbe0db701f5831620be69d38d6411c3f66644`
  - `test_h17_ax7782_k08_phrase_intake.py`: `7703faca8385985846ea29d379ae40f758dcfcf8`

The Sticky Notes helper suite ran from an exact local copy:

- Command: `python -m unittest -v test_h17_sticky_notes_intake`
- Result: **9 tests passed**; process return code 0.
- Verified source blobs:
  - `h17_sticky_notes_intake.py`: `0075c89f198edb6f23632a758651c94f60637d0d`
  - `test_h17_sticky_notes_intake.py`: `da9370e20cbc895e8fecc9354476cd97ea998cf2`

Together, the two committed suites passed all **18 tests**, including embedded ASCII/UTF-16 and hex/Base64 UTF-16 recovery, encrypted-PDF password handling, nested ZIP and MIME extraction, K07 transfer-chain selection, synthetic 8 MiB end-to-end phrase recovery, and Sticky Notes DB/WAL/SHM/journal snapshot and mutation-race checks. Python emitted a nonfatal spreadsheet-runtime warmup warning at startup; it did not affect either test process.

**Limit:** the 8 MiB AX-7782 object and native printer/profile sources remain absent. The end-to-end AX-7782 test uses a synthetic object; the tests validate the intake tooling, not recovery of K04 or K08 from real source material. No candidate, acceptance commitment, verifier, source evidence, or CI workflow was changed or added.


## Final candidate verification (Agent 14)

Ran the supplied export's unchanged verifier against its current `candidate.json`:

```sh
python3 verify.py --candidate candidate.json --json
```

Exact result: K01 PASS, K02 PASS, K03 PASS, K04 MISSING, K05 PASS, K06 PASS, K07 PASS, K08 MISSING; `passed=6`; `combined=INCOMPLETE`; `combined_sha256=null`; `accepted=false`. The process exit status 1 is the verifier's expected rejection of an incomplete candidate, not a runtime error. No candidate values or acceptance data were modified. No valid eight-component recovery key or combined digest can be reported from this export.
