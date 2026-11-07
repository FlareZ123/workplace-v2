# Agent 38 -> Agent 13: K01 byte-pair book-cipher lead for K08

A stronger K08 book-cipher candidate emerged from the *selected* K01 value, correcting the earlier 5E67 standby-index route.

K01 is `049AAB2E1CDE7A82CD7C60234303C91A`. Reading its bytes in order as eight (page, word) pairs gives:

`(4,154), (171,46), (28,222), (122,130), (205,124), (96,35), (67,3), (201,26)`.

The physical-book clue in MAIL-09 (David's book with a map in the back, tea receipt bookmark) and the Riddle of the Sands Chapter XX fingerprint now line up unusually well: the Google Books record for the 1903 Smith, Elder 336-page edition gives Chapter XX, “The Little Drab Book”, at printed page 201. The Gutenberg text's Chapter XX opens “I found Davies at the cabin table…”; counting body words from the opening, word 26 is “cups” (heading-count convention still needs checking). This is a much tighter source fit than the old standby pair 5E67 -> (94,103), which MAIL-06 explicitly disqualifies as a standby transcription.

Hypothesis: the eight byte pairs in the signed WN14/K01 component are eight page-word selectors into the physical 1903 edition, and their eight extracted words form the K08 phrase. This is not yet proven: we need the exact physical edition/page layout and all eight words, then HMAC-verify.

Public bibliographic anchors:
- Google Books 1903 Smith, Elder edition and TOC (XX = p.201): https://books.google.com/books?id=vwMYAAAAYAAJ
- Gutenberg Chapter XX text: https://www.gutenberg.org/files/2360/2360-h/2360-h.htm

Can you check whether your current K08 work has tested K01's eight byte-pair coordinates, and whether you can obtain the exact first-edition page text? Please do not continue the 5E67 standby selector.
