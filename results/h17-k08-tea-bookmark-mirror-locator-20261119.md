# K08 tea-bookmark mirror locator fixed point

**Agent 22 | 19 November 2026 | source-local locator; K08 remains unrecovered**

## Result

Three preserved source records form a closed, target-blind locator loop:

1. `retired-office-bookmarks.html` contains exactly **15** saved links.  
   **Tea-room stock sheets** (`R:/Stores/consumables/mug-stock.xls`) is link **3** in source order.
2. MAIL-09 says David's book is “the one with the map in the back,” says a **tea receipt** is being used as a bookmark, and says Jason **left it in place**.
3. Preserve the tea bookmark's ordinal place, but read it from the **back** of the 15-link list:  
   `15 - 3 + 1 = 13`.
4. Under the already calibrated mail-number namespace used in the existing CREW4/LOW chain, **13 → MAIL-13**.
5. MAIL-13's subject is **Archive transfer receipt to keep with the folder** and its body names final handoff **AX-7782**.
6. Apply the already established **LOW BIT**, first-bit-as-LSB convention to the four decimal digits `7782`:  
   digit parities `1,1,0,0` pack to integer **3**.
7. That returns exactly to bookmark **3**, Tea-room stock sheets.

So the bounded loop is:

`Tea-room bookmark #3 → read place from the back → 13 → MAIL-13 receipt → AX-7782 → low bits of 7782 → 3 → Tea-room bookmark #3`.

The source-only reproducer is `agents/agent22/k08_tea_bookmark_mirror_sft.py`. It does not read K08 acceptance data or test any phrase.

## Why this matters

The prior deterministic K08 chain already ended at N11 **Mug shelf**, MAIL-12's small shelf card, and MAIL-09's David-owned map-back book with a tea-receipt bookmark. This new loop independently returns to the exact retired-office **Tea-room stock sheets** bookmark while using the same LOW BIT convention that already reproduces accepted K05 and returns MAIL-09 through MAIL-03/group C.

This materially strengthens `mug-stock.xls` as a source-bearing K08 locator. The workbook is absent from the supplied ZIP and current repository, so the loop does not expose its contents or recover a keeper phrase.

## Limitations

Two interpretation steps remain conditional rather than quoted encoding rules:

- “map in the back” is used as an instruction to mirror the preserved bookmark ordinal from the back of the 15-entry list;
- the resulting integer 13 is interpreted in the mail-number namespace, as prior chain steps already do for 10 and 9.

The fixed point reduces arbitrariness because MAIL-13 is itself a **receipt** record and AX-7782's digit low bits return exactly to the original tea-room bookmark index. It still does not establish that Emily copied wording from the workbook, from the physical shelf card, or from David's receipt/book.

## Recovery boundary

K08 still requires a complete normalized keeper phrase that passes the unchanged historical commitment. The newly strengthened missing carrier is the original `R:/Stores/consumables/mug-stock.xls` workbook, preferably together with the shelf card and tea receipt/book in preserved context. The final Emily margin/envelope and photo-caption material remain direct primary text carriers.

No K04 byte and no K08 final word is claimed by this result.
