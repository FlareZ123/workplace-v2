# K04 BIFF8 candidate screen — 2026-11-24

## Question

Can the eight K01-selected workbook cells produce the missing K04 component through simple BIFF8 palette or XF-index representations?

This is a bounded candidate-generation experiment, not proof that the absent `mug-stock.xls` workbook is the true K04 carrier.

## Verifier inputs

The 16-byte K04 mask was taken from `resources/evidence/recovery-routing.json` (`K04.masked_component`). The 32-byte K04 commitment was taken from `resources/acceptance.json` (`slot_sha256.K04`). Both were cross-checked against the executable constants before the corrected searches.

A first local prototype contained a transcription error in two target bytes. All results from that prototype were discarded. The results below use the corrected, source-matched commitment.

## Corrected results

| Candidate construction | Search space | Result |
|---|---:|---|
| Eight effective `icvFore/icvBack` byte pairs, each cell drawing from two distinct valid BIFF8 palette indices (67 legal values) | 2,211 palette pairs × 4^8 = 144,900,096 | No commitment match |
| Eight raw packed BIFF8 colour words, little-endian; same two-index family, pivot/reserved flags zero | 144,900,096 | No commitment match |
| Eight little-endian XF/style indices drawn from at most two distinct IDs in 0–255, including uniform vectors | 8,356,096 | No commitment match |
| Eight independent little-endian 16-bit `ixfe` indices, each restricted to 0–15 | 16^8 = 4,294,967,296 | No commitment match; exhaustive |

The executable search implementation is `agents/agent28/k04_biff8_candidate_screen.c`. It uses OpenSSL SHA-256 and OpenMP; compile with:

```sh
gcc -O3 -march=native -fopenmp agents/agent28/k04_biff8_candidate_screen.c -lcrypto -o /tmp/k04-screen
```

Run `palette`, `packed`, `two-style`, or `ixfe` modes. The palette modes accept pair-index ranges so the search can be sharded.

## Interpretation and limits

These tests reject only the stated low-entropy constructions. They do not exhaust the full 16-bit `ixfe` domain, do not cover vectors with three or more arbitrary style IDs above the searched ranges, and do not test cell values, comments, formulas, or other workbook content. No original `mug-stock.xls` is present in the repository resources or supplied ZIP; the retained bookmark is only a path locator. Do not expand workbook parsing or claim a workbook-derived value without the original file or an authenticated worksheet mapping.

No K04 candidate was recovered, and no candidate, route, acceptance, or verifier file was changed.

## Remaining evidence

- MAIL-16 identifies the PS-0417 attempt-2 ACK as a dispatch-log receipt, not a media-integrity proof; the physical ESC-N coupon is associated with the absent September cassette-return binder. The native spool/print-service record or an authenticated coupon scan is needed.
- MAIL-20 says the final keeper wording is the text Emily actually put on the envelope; the surviving drafts and paraphrases do not quote that final wording. The original envelope inscription or an authenticated copy is needed for K08.
- The committed 8 MiB `IR-261003-H17` transfer object `AX-7782` remains the highest-value missing source artifact because it may contain the native records needed for both slots.

The six existing accepted components remain unchanged. K04, K08, and the combined recovery key remain unresolved pending original evidence.
