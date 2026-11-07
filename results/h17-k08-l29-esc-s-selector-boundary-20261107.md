# K08 source-boundary: L-29/S and the ESC-S veto

**Date:** 2026-11-07  
**Author:** Agent13  
**Status:** selector-boundary finding; no component recovered

## Question

The current book-cipher hypotheses use ticket suffixes from the L-29/N and L-29/S return sets as candidate page numbers. Does the source explicitly permit both sets to contribute to K08?

## Direct source evidence

1. `evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` maps:
   - `PS-261003-0417`, route `ESC-N`, to cassette return set `L-29/N`;
   - `PS-261003-0448`, route `ESC-S`, to cassette return set `L-29/S`;
   - `PS-261003-0420`, route `WATCH-SPARE`, to `L-29/W`.
2. `evidence/mail/16.eml` says ESC-S is not an input to the keeper's desk phrase and was retained on the label for service history.
3. `evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` supplies the two five-ticket page-suffix sets:
   - L-29/N: 094, 081, 106, 099, 112.
   - L-29/S: 130, 151, 121, 135, 142.
4. `evidence/mail/06.eml` identifies `5E67` as the old standby transcription's group-D ending, explicitly saying it is not the value on the signed sheet.

## Interpretation and limits

The route-level ESC-S veto is explicit. It rules out using the ESC-S printer route payload as an input to K08.

It does **not yet prove** that L-29/S ticket identifiers are unusable as independent book-page selectors. Those identifiers are carried by the return-binder records, so a book-cipher proposal that uses them must state and support the separate link from ticket identifier to book page. It must not silently equate “the route is excluded” with “every associated maintenance record is excluded”.

If a ticket-page selector is eventually established, the L-29/N set is the only five-page set directly attached to the ESC-N job. Its suffixes are 94, 81, 106, 99, and 112. This is a candidate subset for a bounded test, not evidence that the numbers are pages or that they feed K08. The L-29/S set should remain a control until its proposed role is independently justified.

Likewise, the arithmetic split `0x5E = 94`, `0x67 = 103` is not a source-defined convention. Since MAIL-06 already assigns 5E67 to a stale K01 standby transcription, treating it as a page-94 / word-103 locator is a cross-slot hypothesis only. It requires an independent physical-book and edition link.

## Research consequence

Any current or future 10-page book-cipher construction should document why the L-29/S page suffixes are allowed despite the ESC-S K08 exclusion. Any five-page North-only construction should be treated as a competing hypothesis, with its exact book edition, page text, word-counting convention, and K08 commitment test specified before extraction.

The primary K08 evidence chain remains the original envelope, Emily's WN-14 desk-note stack, and the separate photograph / galley-caption originals. The map-back book and receipt remain secondary physical locators. This report does not recover the final phrase.
