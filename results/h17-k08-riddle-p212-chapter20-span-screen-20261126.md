# K08 exploratory candidate screen: Riddle of the Sands, Chapter XX

**Status:** negative candidate test; K08 remains unresolved.

## Why this candidate was tested

The local source MAIL-09 says a book with a map in the back belongs to David and that a tea receipt was left in it as a bookmark. The conditional P212 book-candidate crosscheck (`results/h17-k08-p212-book-candidate-crosscheck-20261119.md`) identifies page 212 of the 1903 edition of Erskine Childers's `The Riddle of the Sands` as the final page of Chapter XX, “The Little Drab Book.” That chapter has a maritime cabin-table scene, books and cocoa, a late-night conversation, and a guidebook/map clue. This is a plausible thematic candidate for N20's brief (sea, end of night, voices at the table), not proof that David's physical book was this title.

## Test

- Source text: public 1903 edition text extraction at https://www.metrici.com/ebta/titles/the_riddle_of_the_sands/the_riddle_of_the_sands_pdf.pdf, Chapter XX ending.
- Tested text: the final 821 normalized source words from the chapter ending, including the end of Chapter XX and therefore its page-212 endpoint in the 1903 pagination.
- Candidate family: every contiguous normalized span of 1–48 words (38,280 spans).
- Normalization: lowercase; replace every character outside ASCII a–z, digits, and whitespace with a space; collapse whitespace; trim. This matches the K08 route rule.
- Check: compute component = HMAC-SHA256(decoded desk_nonce, normalized UTF-8 phrase)[:16], then compare SHA256(component) with acceptance.slot_sha256.K08. The final 38,280-span count is from this two-stage check.
- Result: **0/38,280 matches**. Several obvious chapter-end sentences were also checked directly; none matched.

## Interpretation and limits

The printed text in the chapter-ending window does not supply the K08 phrase as a contiguous span under the specified normalization. This does **not** test handwritten marginalia, the physical receipt/bookmark, a different edition/page layout, or another book with a rear map. The physical title remains unverified; do not promote a phrase or claim this was David's book.

This closes only the printed Chapter-XX-span hypothesis. Reopen the book branch only if a genuinely new selector or a physical/source-native page or margin image appears. K08 remains missing.
