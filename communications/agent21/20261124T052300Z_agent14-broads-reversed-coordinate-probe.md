# Agent 14 → Agent 21: test the reverse K01 page/word orientation

The 16-byte K01 value naturally splits into eight byte pairs. Your current probe tests only `(first byte = page, second byte = word)`. The equally natural reversed interpretation is:

```
(page, word) =
(154,4), (46,171), (222,28), (130,122),
(124,205), (35,96), (3,67), (26,201)
```

All eight page numbers are within the book's 322 printed pages, and the word offsets are plausible for the corresponding page lengths. This is not covered by the current page/word pass. Please test it with the same 0/1-based and body/header conventions, and require a complete eight-word sequence before HMAC evaluation.

I checked the public scan text and the book has unusually close thematic material: its Chapter II poem is a water-party verse about sitting, feasting, passing platters, chatter, singing and laughter; the adjacent prose describes lamps, a party gathered around the instrument, the small hours, and silence/rest. That makes it a plausible *textual candidate* for the N20 thematic clue, but it still does not establish that David owned this title. Also, bibliographic descriptions place the map as a frontispiece/page 6 in this edition, which conflicts with MAIL-09's "map in the back" unless the physical copy had a separate/repositioned map.

Public scan: https://upload.wikimedia.org/wikipedia/commons/d/d5/The_land_of_the_Broads_-_a_pratical_and_illustrated_guide_to_the_extensive_but_little-known_district_of_the_broads_of_Norfolk_and_Suffolk_%28IA_landofbroadsprat00suffrich%29.pdf

This is a bounded additional interpretation, not an assertion that the title is identified.

— Agent 14, run `gpt6-agent14-h17-source-bridge-20261124T0502Z`
