# K08 book identity: Messum's estuary guide and the separate Cowper volume (7 November 2026)

## Executive finding

A useful two-book hypothesis now fits the source clues better than treating every book reference as one object:

1. The unidentified "Little Drab Book" in Chapter XX of The Riddle of the Sands has a strong real-world analogue in S.V.S.C. Messum's East Coast Rivers (1903). Messum's title page identifies him as "Lieut., R.N."; the book is explicitly a set of charts and sailing directions for the East Coast rivers from the Thames to Southwold.
2. Cowper's Sailing Tours is a separate book in Davies's ordinary library. Part I (1892) remains a plausible match for the H-17 map-back book because an antiquarian listing describes a previous owner's name on the reverse of its frontispiece map. Cowper also remains the exploratory source for the frozen North/South ticket-page construction.
3. T.G. Cuthill's 1893 A Sailing Guide to the Solent and Poole Harbour is a weaker alternative for the fictional estuary guide. It fits the yachtsman's-guide subject, but its author is a Lieutenant-Colonel rather than a Royal Navy lieutenant.

This is a bibliographic hypothesis, not a confirmed identification. The Messum frontispiece and any Dollmann inscription have not been inspected.

## 1. What the novel actually describes

Chapter XX describes an old, cheap-cloth guide for yachtsmen to a British estuary. Its title page is attributed to "Lieut. X——, R.N.", and the frontispiece is described as a reproduction of a photograph of a yacht and its owner. Davies identifies the man as Dollmann.

Primary text: [Project Gutenberg, The Riddle of the Sands, Chapter XX](https://dev.gutenberg.org/cache/epub/2360/pg2360-images.html).

The novel also distinguishes this "particular volume" from Cowper's Sailing Tours, which is one of Davies's ordinary library books. That distinction matters: Cowper should not be used as the identification of the separate Lieut. X—— guide.

## 2. Strongest analogue for the Little Drab Book: Messum, 1903

S.V.S.C. Messum, Lieut., R.N., East Coast Rivers. Charts and Sailing Directions for the Rivers Crouch, Roach, Blackwater, Colne, Stour, Orwell, Deben, Ore, and Alde; together with General Charts from the Thames to Southwold. London: J.D. Potter, 1903.

Evidence:

- The author is explicitly identified as S.V.S.C. Messum, Lieut., R.N.
- The title describes sailing directions for a series of East Coast rivers and estuaries.
- A first-edition bookseller description records 11 coloured charts, mostly folding, 24 numbered pages, 10 following unpaginated leaves containing buoys, lights and tide tables, and an 8-page Potter nautical catalogue.
- The same description records original green grained cloth lettered in gilt.
- A 2026 history of the East Coast Rivers title independently identifies Messum's 1903 book as an early foundational publication for this cruising area.

Sources:
- [Bristow & Garland first-edition description and cover image](https://www.abebooks.com/first-edition/East-Coast-Rivers-Charts-Sailing-Directions/30908629368/bd)
- [Nick Ardley, history of East Coast Rivers, 7 October 2026](https://nickardley.com/ditch-crawler-acclaims-imminent-arrival-of-70th-anniversary-edition-of-the-famous-east-coast-rivers/)

### Fit and mismatch

| Novel clue | Messum evidence | Assessment |
|---|---|---|
| Guide for yachtsmen to a British estuary | East Coast rivers and charts from the Thames to Southwold | Strong |
| "Lieut. X——, R.N." | Messum is explicitly "Lieut., R.N." | Strong |
| Little, chart-heavy book | 24 pages plus 10 unpaginated leaves and 11 folding charts | Strong |
| Cheap, antiquated cloth | Original green grained cloth, gilt lettering | Possible, not exact |
| Yacht-and-owner photographic frontispiece | Not mentioned in the inspected bookseller description | Unverified |
| Dollmann name on the back | No evidence in the listing | Unverified |
| Old book | Published in 1903, the same year as the novel | Chronology needs explanation |

The rank and subject match are unusually close. The publication date and unverified frontispiece prevent identification. The photograph could be an older image in a contemporary guide, but that is only a possibility.

## 3. Weaker alternative: Cuthill, 1893

T.G. Cuthill, Lieut.-Col., A Sailing Guide to the Solent and Poole Harbour, with Practical Hints as to Living and Cooking on, and Working a Small Yacht (1893).

A GetArchive page for the British Library scan identifies this title and advertises a full-volume PDF and OCR-derived text in plain-text and JSON forms. Its indexed scan pages include 29, 74, 86 and 136. A bookseller description records 100 pages plus 16 pages of advertisements and four charts.

Source: [GetArchive scan record](https://timelessmoon.getarchive.net/amp/media/29-of-a-sailing-guide-to-the-solent-and-poole-harbour-with-practical-hints-77127b).

Cuthill fits the small yachtsman's-guide subject and covers Poole Harbour. It is a weaker match because the author is a Lieutenant-Colonel, not a Royal Navy lieutenant. The date is 1893, and the frontispiece photograph and any Dollmann inscription remain unverified.

The full PDF/OCR links were advertised in the indexed record but could not be resolved with the available retrieval tools. The British Library's legacy Hugging Face OCR dataset viewer returned HTTP 500; the tested 1890s archive download and DSpace endpoints returned 404. These are access failures in this investigation, not proof that the underlying files no longer exist.

## 4. Keep Cowper separate

The Cowper branch remains relevant to the archive's physical map clue and the exploratory page-word construction:

- Part I, The Coasts of Essex and Suffolk (1892), is a 168-page volume with six charts and seven plates.
- A PBFA listing describes a copy with a previous owner's name on the reverse of its frontispiece map. This is a notable match to the H-17 map-back inscription clue.
- Part II's frozen South word-103 extraction is Solent / yards / sailing / the / even. This is only a partial exploratory fragment.
- The Part I page images remain inaccessible through the tested automated routes. The current repository stop rule is to seek an authorized scan or the physical book, rather than generate more viewer variants.

References:
- [PBFA Cowper Part I listing](https://www.pbfa.org/books/sailing-tours-the-yachtsmans-guide-to-the-cruising-waters-of-the-english-and-adjacent-coasts-part-i-the-coasts-of-essex-and-suffolk)
- [Cowper Part II extraction and its limitations](h17-k08-cowper-part2-word103-extraction-20261107.md)
- [K08 book-identity correction](h17-k08-envelope-bx25-retrieval-chain-20261107.md)

The working two-book model is therefore: Cowper Part I may be the map-back object; Messum's East Coast Rivers may be the separate Lieut. R.N. estuary guide described in the novel. Both identifications still require physical confirmation.

## 5. Separate negative result: Riddle page-word hypothesis

A separate experiment tested the speculative interpretation of standby value 5E67 as printed page 94, word 103, with the ten ticket suffixes used in binder-tab order, against the public 1903 Thomas Nelson scan of The Riddle of the Sands.

- PDF pagination was cross-checked: PDF page 13 corresponds to printed roman page ix, and PDF page 19 begins printed page 15. The resulting Arabic-page offset is +4.
- The scan has no embedded OCR text, so the ten target pages were rendered at 300 DPI and OCRed with Tesseract.
- The exact ticket order was [94, 81, 106, 99, 112, 130, 151, 121, 135, 142].
- Word positions 103 and 104 were tested with apostrophe-preserving and punctuation-splitting tokenizers.
- None of the four derived candidates matched the published K08 slot commitment.

Reproducible artifacts:
- agents/agent32/k08_riddle_pageword_ocr_sft.py
- .github/workflows/agent32-k08-riddle-ocr-manual.yml
- [Workflow run](https://github.com/FlareZ123/workplace-v2/actions/runs/42365497743)

This rejects the page-word interpretation for this Nelson scan and this OCR/counting setup only. It does not reject the Messum or Cuthill guides, Cowper, another edition, or the physical envelope transcription.

## 6. What remains worth doing

1. Obtain a physical or high-resolution scan of the 1903 Messum first edition. Inspect the frontispiece, the back of the frontispiece, the chart sequence, and any handwritten name. The yacht-and-owner photograph is the decisive missing comparison.
2. If Messum does not fit the frontispiece evidence, compare the Cuthill 1893 scan and physical copy.
3. Preserve the distinction between the possible Cowper map-back object and the separate estuary guide.
4. For K08 itself, prioritize the exact physical envelope/WN-14 evidence and the missing Cowper Part I pages. Do not change the expected commitment, page order, word position or normalization to force a match.

**Status:** Messum is the strongest bibliographic analogue for the novel's Lieut. R.N. estuary guide. Cuthill is a secondary analogue. Cowper remains a separate possible physical map-back book and exploratory cipher source. K08 remains unresolved.
