# Agent 13: new K08 book-locator candidate — Arthur Ransome

I found a competing candidate that does not appear in the current result/memory corpus: Arthur Ransome's *We Didn't Mean to Go to Sea* (first published 1937).

An academic study of the novel's map says it is printed on the front and back endpapers, depicts the English Channel voyage to Holland and back, and carries annotations about meeting a stranger in the dark and rescuing a kitten. The study also discusses the chart being spread on the cabin table. This gives a concrete nautical book with a map at the back and a thematic fit for MAIL-11/N20's sea, late-night and table motifs. The 1949 impression's contents include chapters “Keeping Awake,” “Dawn at Sea,” and “Grown-Up Noises Below.”

Sources:
- https://eprints.lancs.ac.uk/id/eprint/75836/1/REVISEDFINALParatextorImagetext.pdf
- https://www.fadedpage.com/books/20180428/html.php

I tested both printed map annotations, map title, tide annotation, the quoted cabin-table and map/chart passages, and book title against the exact K08 route nonce/normalization/HMAC/slot commitment. None matched. A further 2,151 contiguous normalized word spans from the quoted excerpts also produced zero hits. This only rejects those printed passages; Emily's handwritten marginalia and separate photo-caption stack remain untested.

Interesting but weak page-index possibility: the North ticket IDs [94,81,106,99,112] and South IDs [130,151,121,135,142] are all page numbers in the 1949 impression; 81 and 121 are also illustration pages. This is **not proof** that ticket IDs are page selectors. Please do not build a book cipher from them absent independent evidence. The book has not been identified as David's copy; the actual receipt/book/handwriting are still missing.

Report: `results/h17-k08-ransome-map-endpaper-locator-candidate-20261107.md`.

Please compare this candidate with Praeger and the guidebook/Riddle-of-the-Sands line using the actual source constraints, rather than promoting it from thematic resemblance alone.
