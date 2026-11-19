# K05 → MAIL03/C → MAIL09 → bookmark 3 → MAIL13 loop controls (19 November 2026)

**Status:** source-pinned locator/control result. It supports a closed routing loop but does not authenticate the physical/browser-bookmark identity, recover the missing workbook, or recover the K08 phrase.

Reproducer: agents/agent9/k08_mail_bookmark_loop_controls.py

## Frozen inputs and operations

The script pins the acceptance file, recovery-routing file, all 15 mail messages, the retired browser-bookmark HTML, and the transfer audit. It verifies the accepted K01 and K05 values against their unchanged slot commitments.

The same first-bit-as-LSB packing is used throughout:

- K05 is 16 bytes; packing its byte LSBs yields 03 43. The second byte is ASCII C, giving the locator 03C.
- K01 is four source-ordered four-byte groups A/B/C/D. Packing each group's four byte LSBs yields one low nibble.

## Source-derived path

1. **K05 → MAIL03/group C.** MAIL03 explicitly identifies WN-14 groups A and C. The accepted K05 lowpack is 03 43, read as MAIL-03 / group C.
2. **K01/group C → MAIL09.** K01's group controls are:

   | Group | Source bytes | Low-bit pack | Numeric selector |
   |---|---|---|---:|
   | A | 049AAB2E | 04 | 4 |
   | B | 1CDE7A82 | 00 | 0 |
   | C | CD7C6023 | 09 | **9** |
   | D | 4303C91A | 07 | 7 |

   The selected C group yields 9, pointing to MAIL-09. MAIL-09 contains the physical tea-receipt bookmark and says the book with the map in the back belongs to David.
3. **All 15 browser bookmarks are controlled.** Applying the inferred reverse ordinal mail = 16 - bookmark_index to the entire retired-office list gives exactly one mail containing the AX-7782 transfer receipt:

   | Browser bookmark index | Bookmark title | Reverse mail | Subject | AX-7782 transfer receipt |
   |---:|---|---:|---|---|
   | 1 | September cassette returns | 15 | Saturday film and the remote | No |
   | 2 | Cassette service reference | 14 | WN-14 signed / pencil note removed | No |
   | **3** | **Tea-room stock sheets** | **13** | **Archive transfer receipt to keep with the folder** | **Yes** |
   | 4 | Posted settlement items | 12 | Tea order and the blue mugs | No |
   | 5 | Reversal register | 11 | RC-17 issue receipt | No |
   | 6 | Office letterhead index | 10 | TRP2 bench export / control words | No |
   | 7 | Bench expense apportionments | 9 | Room swap on the next rotation | No |
   | 8 | H-17 property renewal ledger | 8 | Valve gallery findings / turnaround discussion | No |
   | 9 | 2025 risk scan transfer index | 7 | Thursday boat / parcels and filters | No |
   | 10 | Desktop scanner release notes | 6 | Re: WN-14 ink copy from the night folder | No |
   | 11 | Hired equipment certificates | 5 | Laundry bag labels | No |
   | 12 | Incident desk export index | 4 | PTW-417 closeout bay order | No |
   | 13 | Blank request form | 3 | WN-14 ink copy from the night folder | No |
   | 14 | E.G. electrical group roster | 2 | Galley freezer and the soup tubs | No |
   | 15 | Profile-replacement calendar | 1 | West locker list before crew change | No |

   The selected bookmark is the third item, Tea-room stock sheets, whose cached URL is the missing file:///R:/Stores/consumables/mug-stock.xls.
4. **MAIL13 → bookmark 3.** The four retained transfer IDs are controls under the same ASCII low-bit selector on their final four digits:

   | Transfer | LOW BIT of digits |
   |---|---:|
   | AX-7778 | 7 |
   | AX-7781 | 11 |
   | AX-7782 | **3** |
   | AX-7783 | 11 |

   AX-7782 is the only transfer returning selector 3, closing the ordinal loop.

## Specificity and limitations

The deterministic path is:

K05 → 03C → MAIL03/C → K01 group C → 9 → MAIL09 → browser bookmark 3 → MAIL13 → AX-7782 → 3.

The complete control family has 15 bookmark positions and four transfer IDs; only bookmark 3 reverse-maps to the AX-7782 transfer receipt, and only AX-7782 returns selector 3. A deliberately simple uniform toy null would give 1/15 × 1/4 = 1/60, but this is **not a calibrated p-value**: the selection stages are semantically dependent and the reverse-ordinal rule is inferred.

Most importantly, MAIL-09's physical tea receipt is not established as the same object as browser bookmark 3's Tea-room stock sheets link. “Map in the back” does not explicitly instruct reversing the browser list. The missing workbook is not present in the repository; M10/T11 remain cell locators, not recovered cell contents.

This is a positive locator result to include in the full LOW BIT assessment. It does not supply the N23 margin/envelope wording and does not promote K08.
