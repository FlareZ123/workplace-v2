# PTW-417 LOW-IF-EVEN seal-revision side-channel

**Agent:** 9  
**Date:** 19 November 2026  
**Status:** Conditional cross-carrier calibration; not a change to accepted K03.

## Question

Does the LOW-IF-EVEN / serial-LSB operation observed in K05 and the K08 note chain also route through PTW-417's naturally paired signed as-left seal revisions?

## Source-defined inputs

- MAIL-04 states the witness walk order is **B, D, A, C** and says to use signed closed fitment records, excluding REMOVED entries and a later stores picking ticket.
- The K03 route selects the highest signed revision among CLOSED AS_LEFT records.
- The PTW-417 seal export contains signed CLOSED AS_LEFT revisions 1 and 2 for B, D and C. Bay A has two revision-1 rows and one revision-2 row; both revision-1 rows are retained below rather than silently choosing one.

## Fixed operation

For each serial, take the least significant bit of its eight-hex-digit numeric suffix (equivalently, the low bit of the final hex nibble). Pack the four bits in MAIL-04 witness-walk order, first bit as bit 0.

| Selection | Serials in B,D,A,C order | Bits | Packed value |
| --- | --- | --- | ---: |
| Official K03: highest revision at every bay | D7DAD6BC, 9714519B, 7DAD0AD4, BE8E87FD | 0,1,0,1 | 10 |
| Zero-based LOW-IF-EVEN candidate 1 | AD1D814B, 9714519B, 574A9232, BE8E87FD | 1,1,0,1 | 11 |
| Zero-based LOW-IF-EVEN candidate 2 | AD1D814B, 9714519B, 7E73B4CC, BE8E87FD | 1,1,0,1 | 11 |
| One-based parity sensitivity control | D7DAD6BC, 64B2EE4A, 7DAD0AD4, 5CB72EE5 | 0,0,0,1 | 8 |

The duplicate A/rev1 records have different serials but both end in an even hex digit, so the alternate output is invariant to that ambiguity.

The zero-based selector is the preferred exploratory convention because the other paired machine sources index latches and chunks from 0. The seal source itself does not explicitly number the four bay positions, however; the one-based control produces 8 instead. The index-base dependency must remain visible.

## Interpretation

The official K03 serial LSBs pack to 10, matching N10 as previously reported. Applying the same zero-based LOW-IF-EVEN selector to the paired revision strata yields 11, which routes to N11, the Mug shelf note. This is a new source carrier for the low/even-high/odd routing pattern, alongside the K05 alternate valid retry stratum that yields M10 and the conditional AX-7782 side-channel.

This is supportive cross-carrier consistency, not proof by itself: the output is only four bits (11 has probability 1/16 under a uniform four-bit null), and the one-based control also lands on an existing note number. It does not alter the official K03 selection, authenticate P212 as a page/cell, prove the workbook hypothesis, or recover the K08 phrase.

## Reproduction

Run:

    python work/h17_k03_low_even_seal_revision.py --evidence-root resources/evidence

The script reads MAIL-04 and the PTW-417 seal export directly, validates the per-bay revision strata, preserves both A/rev1 alternatives, and reports both zero-based and one-based selectors.
