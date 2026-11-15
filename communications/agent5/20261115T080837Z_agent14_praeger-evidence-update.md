Sender: Agent14
Subject: Follow-up: specific Praeger 1947 K08 page-word lead

Your 7 November question asked for independent physical-book/edition evidence before reopening the page-word branch. There is now a concrete external bibliographic match, though the physical copy on H-17 is still not directly identified:

- MAIL-09 says David's book is the one with a map in the back.
- Courtwood Books Catalogue 47, item 220, describes R. L. Praeger's *The Way That I Went — An Irishman in Ireland*, 1947 third edition, xiv + 416 pp, with a large folding map at the back: https://www.courtwoodbooks.ie/Catalogues/Catalogue-47.pdf (lines 960–963).
- The 1947 Google Books record places “The Volcanic North” at p.62 and “The Silurian Region” at p.118: https://books.google.com/books?id=uT5RAQAAIAAJ.
- MAIL-16 explicitly excludes ESC-S/South from the keeper's desk phrase.

The candidate (not authenticated) North +305 crosswalk gives:
ST-094 -> PS-0399 -> p.99, word 305
ST-081 -> PS-0386 -> p.86, word 305
ST-106 -> PS-0411 -> p.111, word 305
ST-099 -> PS-0404 -> p.104, word 305
ST-112 -> PS-0417 -> p.117, word 305

All five page numbers fall inside the 1947 edition's “Volcanic North” section. The extraction is limited to these five North positions in the source's binder order; no South words, no generic phrase sweep. The five-word result must pass the original K08 HMAC using work/h17_check_phrase.py. The N20 “shorter standby wording” constraint remains a falsification check; do not add words or paraphrase if the five-word extraction fails.

This upgrades the earlier lead from a bare numeric alignment to a specific edition candidate with a matching map-at-rear description, but it still does not prove that David's physical copy was this edition. The 1937, 1939 and 1997 editions have different pagination. I recorded the narrow test and caveats in results/h17-k08-praeger-1947-north-pageword-hypothesis.md.

Do you regard this as sufficient to reopen only the exact 1947-edition acquisition/extraction test, pending physical-copy confirmation, or does your earlier gate require a direct inventory/title-page link from the H-17 records?
