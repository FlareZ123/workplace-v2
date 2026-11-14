# K08 intake correctness and snapshot hardening

**Date:** 2026-11-14T13:37:58.051Z  
**Repository:** `FlareZ123/workplace-v2`  
**Outcome:** no archive component recovered; K04 and K08 remain missing.

## Scanner defect and correction

The shared K08 phrase scanner had three embedded-run regular expressions whose byte-class escapes were double-escaped. They matched literal backslash escape sequences rather than ordinary embedded ASCII, UTF-16LE, and UTF-16BE text. The associated regression fixtures repeated the escaping error, so a positive phrase match did not prove that a binary run had been isolated.

The scanner was corrected to use actual byte-class escapes. Its tests now use binary prefixes/suffixes (`0x00`, `0xff`, and odd-length framing) and assert that each result is emitted by the specific embedded-run decoder. The encrypted-PDF test fixture now adds a title metadata field so the correct-password path yields a stream to inspect.

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

The supplemental encrypted `BX25-08.pdf` was also decrypted with the previously recorded computational password 8131. The corrected scan covered its ten decoded page-content streams, page text, metadata, and annotation; there were zero K08 commitment hits. This does not authenticate 8131 as the historic Risk-desk register entry.

The ZIP has exactly 56 local-file headers for 56 central-directory entries. The inter-record gaps are the expected 16-byte data descriptors; no unreferenced local-file record or extra payload gap was found. This is a bounded container-structure check, not proof that no separate source exists.

## SQLite snapshot integrity correction

The Sticky Notes helper previously hashed each source DB/WAL/SHM file before copying and compared source hashes before and after extraction, but did not hash the copied destination. A source could change during copy and be restored before the after-check, leaving a mixed temporary snapshot while the source appeared unchanged.

The helper now:
1. receives the original pre-copy size, mtime, and SHA-256 snapshot;
2. rejects sidecars that appear/disappear or source files that differ before copy;
3. hashes every copied destination and requires exact size and SHA-256 equality before SQLite opens it; and
4. retains the existing post-extraction source equality check.

A regression test simulates a source changing during copy and being restored byte-for-byte with its original mtime. A focused local harness passed both this race case and an ordinary copy case. The full helper test module was not run end-to-end here. Agent 13 was notified in `communications/agent13/20261114T133758Z_agent11-sqlite-snapshot-race-fix.md`.

## Recovery status and limitations

The repository's `resources/` directory contains the same retained evidence set plus the six-slot recovery script; it does not contain the 8 MiB AX-7782 object, native PS-0417 spool, profile-refresh image, original recovery envelope, or final caption source. No source component, acceptance commitment, verifier, or canonical candidate was changed.

The six verified components remain K01, K02, K03, K05, K06, and K07. K04 and K08 remain missing; combined REC8/1 acceptance remains incomplete. The corrected scanner and SQLite bridge are prepared for an authorized AX-7782/profile source if one becomes available, but no real-source recovery is claimed.
