# Agent 9: root cause of the original folio-4 failure — unsigned API placeholders

I downloaded the failed-run artifact 14463657135 (run 44380167069) and inspected its `summary.json`. The original resolver did **not** encounter multiple genuine folio-4 pages. It found zero matches because the generic unsigned image endpoint returned placeholders:

- Folio-4 scan window was `[0,16]`; `unique_match_count=0`, `failed_scan_indices=[]`.
- Scan index 0 returned 575×750 (a different front page).
- Scan indices 1–16 all returned the **same** 300×391 image, byte length 15,567, SHA256 `12557f8948b8bdc6af436e3a8b3adddd45f7f7d2b67c5832e799cdf4686f72bb`; top-margin OCR was empty and right-margin OCR was just `7`.
- The old helper requested unsigned `books/content?...zoom=2&edge=curl&source=gbs_api` URLs and accepted any `image/*` response without a dimension/size/duplicate-content guard.

By contrast, Agent 7's signed-viewer artifact 14463738331 contains a genuine page-4 scan:
- viewer URL: `https://books.google.com/books?id=fQYN_SZzCFgC&pg=PA4`
- viewer-generated signed image URL includes `zoom=3&hl=en&sig=...&w=1025`
- 122,119 bytes, 1025×1572, SHA256 `ba9de6e6b4369d1e461635d6715515eac8a79798e31f189316f2886a0b5169de`
- the printed folio 4 is visibly present.

So the primary defect is **image acquisition**, not a demonstrated duplicate folio. The existing `agents/agent7/k08_falcon_signed_pages.cjs` already shows the justified acquisition method: load each Google Books viewer page, extract its viewer-generated signed image URL, verify volume/page/signature, require a large image, and reject duplicate image hashes. The signed dual-page run used this method for the 16 frozen target pages and found no K08 HMAC match.

A corrected full-window resolver would need to use that same signed-viewer acquisition for every scan index in each frozen ±12 window, then apply the top-band folio OCR diagnostic. It must still require exactly one genuine printed-folio match and no fetch failures. The 16 target pages alone do not prove full-window uniqueness.

This is a concrete source/fetcher correction and may satisfy the Critic's exception, but I am **not** dispatching a second run. Please obtain explicit owner/reviewer agreement (and any required Critic approval) before one corrected full-window pass. No alternate offsets, new book sources, or further phrase generation.
