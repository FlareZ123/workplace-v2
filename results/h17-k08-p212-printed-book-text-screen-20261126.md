# K08 P212 printed-book text screens

**Status:** negative candidate tests; K08 remains unresolved.

## Hypothesis

The final K08 phrase may be a contiguous normalized span in text associated with David's map-backed book and the tea-receipt bookmark (MAIL-09), with page 212 as the conditional locator. N20's brief (sea, end of night, voices at the table) gives a thematic filter. The 19 Nov P212 candidate crosscheck identifies two plausible book texts worth testing: R. Lloyd Praeger's *The Way That I Went* (1937) and Erskine Childers's *The Riddle of the Sands* (1903). Neither title is authenticated as David's physical book.

## Tests

Both tests used the exact K08 normalization from the route: lowercase; replace characters outside ASCII a–z, digits and whitespace with spaces; collapse whitespace; trim. Each candidate produced component = HMAC-SHA256(decoded desk_nonce, normalized UTF-8 phrase)[:16]; SHA256(component) was compared with acceptance.slot_sha256.K08. The final counts below are from this two-stage check. Candidate spans were contiguous, 1–48 words.

| Candidate text | Source window | Words | Spans tested | Matches |
|---|---|---:|---:|---:|
| Praeger, *The Way That I Went*, Chapter 8 excerpt | Anthology excerpt reproducing original pp. 211–218, including p. 212 | 1,389 | 65,544 | 0 |
| Childers, *The Riddle of the Sands*, Chapter XX ending | Final 821 words of Chapter XX, including its p. 212 endpoint in the 1903 pagination | 821 | 38,280 | 0 |
| **Total** | | | **103,824** | **0** |

Sources:
- Local MAIL-09 and N20 in `resources/evidence/`.
- `results/h17-k08-p212-book-candidate-crosscheck-20261119.md`.
- Praeger excerpt: *Woven Shades of Green*, “From Chapter 8: The Land of Naked Limestone,” reproducing Praeger pp. 211–218: https://dokumen.pub/woven-shades-of-green-an-anthology-of-irish-nature-literature-9781684481415.html
- Childers 1903 text: https://www.metrici.com/ebta/titles/the_riddle_of_the_sands/the_riddle_of_the_sands_pdf.pdf

## Method correction

An initial draft described the comparison imprecisely. The final counts are from the correct two-stage check: HMAC16 produces the component, then SHA256(component) is compared with the slot commitment. The earlier raw-HMAC-to-slot comparison is invalid and superseded.

## Interpretation

No tested printed-text span matches K08. The result does not test handwritten marginalia, the physical receipt/bookmark, a different edition, another book title, or a non-contiguous/paraphrased composition. The P212 locator remains conditional and the physical title remains unverified. Do not promote any phrase from these texts.

This closes these two printed-text candidate windows only. The only meaningful continuation of this book lead is an independently supplied image/transcription of the physical page and margin or a source-authenticated title/selector. K08 remains missing.
