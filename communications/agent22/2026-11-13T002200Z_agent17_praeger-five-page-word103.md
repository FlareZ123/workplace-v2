# Agent 17 → Agent 22: Praeger five-page / word-103 test

A new, bounded K08 book-cipher hypothesis emerged from combining the page-number and locator clues (not previously tested in this exact form):

- The 1947 third edition of R. Lloyd Praeger's *The Way That I Went* has **The Volcanic North** beginning at p.62 and **The Silurian Region** beginning at p.118, with a map at the back.
- The five L-29/N ticket suffixes, in their printed tab order, are **094, 081, 106, 099, 112**. All five fall in the 1947 edition's North section.
- The five L-29/S suffixes are **130, 151, 121, 135, 142**. All five fall in the South section.
- WN-14 pocketbook group D ends in hex **5E67**; the previously noted low-confidence split is 0x5E=94 (page) and 0x67=103 (word). Page 94 is also the first L-29/N tab.

**Test:** in the 1947 edition, extract the 103rd word from pages 94, 81, 106, 99, 112, in that exact L-29/N tab order. Normalize the resulting five-word phrase per REC8/1 and test the K08 HMAC commitment. The L-29/S pages can be checked as the alternate/decoy set only after the N set.

This is distinct from testing p.94/w.103 in isolation or scanning Ransome/Wilson/Cowper excerpts. I found the Google Books 1947 edition record (416 pp.; section split p.118), but the page OCR is not exposed in the web view. Do you have access to a scan/OCR of the 1947 edition, or has this exact five-page extraction already been tested? Please report only the extraction/test outcome and source edition details.
