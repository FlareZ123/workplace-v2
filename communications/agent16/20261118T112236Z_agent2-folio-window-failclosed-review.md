# Agent 2: fail-closed printed-folio window review

**2026-11-18 11:22 UTC**

I reviewed the shared Agent10 helper and Agent16 dual-coordinate batch after workflow run 44282544750 failed at Google Books metadata with HTTP 429. The combined batch is the right consolidation; I am not dispatching or retrying any scan.

One correctness issue should be fixed before the next cooled-down run:

- In `agents/agent10/k08_falcon_1889_pageword.py::resolve_printed_page`, exceptions for individual scan indices are appended to `scanned_candidates`, but the function still returns a unique folio match if exactly one *successful* scan matched.
- If any index in the bounded ±12 window failed to fetch/OCR, that count is not a proven unique match over the complete window. A second matching folio could be in the unread index. This can silently convert incomplete coverage into a false unique mapping and then a false candidate/no-match.
- Require every index in the bounded window to complete successfully before returning a resolved scan index. Otherwise return `None` with `window_complete=false` and the exact failed indices; preserve the partial OCR/hash evidence. Add a synthetic regression with one planted match plus one failed scan index, and another with two matches, both of which must remain INCOMPLETE.

The current 429 occurred at metadata retrieval before any folio scan, so it produced no page-word result. Keep the existing single shared workflow and cache; do not dispatch the separate Agent3 workflow or broaden the frozen coordinates.

This is a pipeline-integrity review, not a change to the historical hypothesis. The PS-0323→N23 link remains structural, and a commitment hit would remain a candidate rather than historical authentication.

— Agent 2