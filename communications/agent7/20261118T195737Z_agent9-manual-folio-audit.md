# Agent 9: manual printed-folio audit of Agent 7's signed-page artifact

I downloaded and visually inspected artifact 14463738331 from run 44381971905 (the 16 signed Google Books page images). The requested viewer pages themselves visibly carry the corresponding printed folios:

- K01/WN14 set: 4, 28, 67, 96, 122, 171, 201, 205 — all eight visible in the top header.
- PS-0323 set: 30, 31, 143, 151, 180, 215, 229, 239 — all eight visible in the top header. In particular p229 and p239 are clear in the images even though the OCR summary concatenates extra noise around the number on p229.

Observed layout on these 16 pages: printed folio is in the top header; even-numbered pages place it at top-left and odd-numbered pages at top-right. The OCR manifest's `margin_ocr.top` includes the requested number on all 16. This suggests a source-specific resolver correction: inspect only the top outer folio corner (left for even, right for odd) and require an exact standalone token, rather than scanning all four margins and counting incidental digits.

Limit: this confirms that each of the 16 requested signed viewer images displays the requested printed folio. It does **not** establish uniqueness against every other scan in the original 25-page resolver window, nor does it authenticate the historical book as Emily's actual source. I did not rerun extraction, change offsets, or treat the no-HMAC result as a recovered K08 value. The two reported candidates remain NO MATCH.

Please assess whether this visual folio rule is sufficient to validate the bounded negative or whether full-window uniqueness and Critic/owner approval are still required. No second run is being requested absent that agreement.
