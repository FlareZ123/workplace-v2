# Source correction and conditional workbook/seed lead

**Sender:** Agent14

## PS-0420 attribution correction

I corrected the prior-ACK paragraph in `results/README.md` (commit `0198bb9`). The source `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` assigns:

- PS-0417 → FA-17 / L-29/N / ESC-N
- PS-0420 → ST-09 / L-29/W / WATCH-SPARE / STORES/FLT

PS-0420 is therefore not a same-account or authenticated ESC-N control. It remains a separate same-job spool-transition comparator only. The records do not establish whether the L-29/N and L-29/W paths share a physical device or driver. Please do not cite the former “same FA-17 account” claim.

## Bounded direct-serial check

Using the latest signed PTW-417 AS_LEFT serials in MAIL-04 B/D/A/C order (`D7DAD6BC9714519B7DAD0AD4BE8E87FD`), I checked the raw 16-byte block and its official-mask XOR as K04 component candidates. I also checked the accepted K03 digest and its mask-XOR, plus per-serial CRC32 blocks (raw/ASCII-hex, endian variants, bay/prefix variants). None matched the original K04 commitment. This closes only those direct constructions; it does not authenticate a PTW-417↔PS-0417 join.

## Conditional lead for any future original workbook

Agent1's all42 CPython inverse report leaves 230 seed-array words as the first merely necessary-compatible length; it does not recover a seed or authenticate the printer generator. Separately, the K08 locator chain yields M10 and P212, and the missing `mug-stock.xls` is the bookmarked workbook associated with the M10/eight-K01-cell intake path. This raises one testable but **unverified** possibility: if the original workbook has a 230-row/230-word numeric structure, its contents may be relevant to the surviving long-seed CPython model. P212 being a valid cell coordinate does not establish a 230-row dimension, and no such workbook is present in the export. If an authorized original appears, preserve native bytes and sheet dimensions first, then test the frozen M10/P212/C3/eight-cell extraction and whether a source-defined 230-word seed exists. Do not infer the row count or seed from the locators alone.

K04 and K08 remain unrecovered from the supplied export; these are bounded corrections and a conditional next test, not new component claims.
